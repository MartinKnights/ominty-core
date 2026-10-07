#!/usr/bin/env python3
"""Ominty TTS document player — chunked, overlapping synthesis + playback.

docs/ai/11-voice-integration.md (TTS milestone).

A producer thread synthesises chunk *i* (Piper) while the GStreamer player is
already playing chunk *i-1*, so audio starts almost immediately and keeps
playing while the rest of the document is generated.

Contract with the UI:
  run dir   : $XDG_RUNTIME_DIR/ominty-tts/
  state.json: {title, doc, total, current, current0, status, ready, producing,
               error}   status: synthesizing|playing|paused|stopped|done|error
  cmd FIFO  : one command per line —
              next | prev | pause | resume | play | stop | quit

Semantics:
  stop   stops playback and resets to segment 1 (the player stays alive so the
         user can navigate again or press play).
  play   starts/resumes from the current segment (restarts the document from
         segment 1 when it had finished).
  quit   fully stops and exits (used by the panel's close button).
"""

from __future__ import annotations

import fcntl
import json
import os
import signal
import sys
import threading
from pathlib import Path

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

from omintylib.tts import TTSError, prepare_document, synth_chunk, default_voice


def run_dir() -> Path:
    base = os.environ.get("XDG_RUNTIME_DIR") or "/tmp"
    d = Path(base) / "ominty-tts"
    d.mkdir(parents=True, exist_ok=True)
    return d


class TTSPlayer:
    """Owns Piper synthesis (producer) and GStreamer playback (player)."""

    def __init__(self, doc_path: str):
        self.prep = prepare_document(doc_path)
        self.title = self.prep.title
        self.total = self.prep.total
        self.doc_path = str(Path(doc_path).resolve())
        self.voice = default_voice()

        self.current = 0  # the segment about to play (0-based)
        self.status = "synthesizing"  # synthesizing|playing|paused|stopped|done|error
        self.error = ""
        self._stop = False
        self._wavs: dict[int, str] = {}
        self._lock = threading.Lock()
        self._producing = True
        self._lock_fd = None
        self._loop: GLib.MainLoop | None = None

        self.dir = run_dir()
        self.fifo = self.dir / "cmd"

        Gst.init(None)
        self.player = Gst.ElementFactory.make("playbin", "player")
        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message::eos", self._on_eos)
        self.bus.connect("message::error", self._on_error)

        for stale in self.dir.glob("seg-*.wav"):
            try:
                stale.unlink()
            except OSError:
                pass
        try:
            self.fifo.unlink()
        except OSError:
            pass
        self._write_state()

    # --- state ----------------------------------------------------------

    def _ready_count(self) -> int:
        with self._lock:
            return len(self._wavs)

    def _write_state(self) -> None:
        data = {
            "title": self.title,
            "doc": self.doc_path,
            "total": self.total,
            "current": self.current + 1,  # 1-based for the UI
            "current0": self.current,
            "status": self.status,
            "ready": self._ready_count(),
            "producing": self._producing,
            "error": self.error,
        }
        try:
            (self.dir / "state.json").write_text(json.dumps(data))
        except OSError:
            pass

    def _ready(self, i: int) -> bool:
        with self._lock:
            return i in self._wavs

    def _wav_for(self, i: int) -> str | None:
        with self._lock:
            return self._wavs.get(i)

    # --- GStreamer ------------------------------------------------------

    def _play_segment(self, i: int) -> None:
        wav = self._wav_for(i)
        if wav is None:
            return
        self.player.set_property("uri", "file://" + os.path.abspath(wav))
        self.player.set_state(Gst.State.PLAYING)
        self.status = "playing"
        self.current = i
        self._write_state()

    def _on_eos(self, bus, msg) -> None:
        self.player.set_state(Gst.State.NULL)
        if self.current + 1 >= self.total:
            self.status = "done"
            self._write_state()  # stay alive so the user can replay/close
        else:
            self.current += 1
            self.status = "synthesizing"
            self._write_state()

    def _on_error(self, bus, msg) -> None:
        err, _dbg = msg.parse_error()
        self.player.set_state(Gst.State.NULL)
        self.status = "error"
        self.error = f"playback error: {err.message}"
        self._write_state()

    # --- producer -------------------------------------------------------

    def _producer(self) -> None:
        for i, chunk in enumerate(self.prep.chunks):
            if self._stop:
                break
            wav = self.dir / f"seg-{i:04d}.wav"
            try:
                synth_chunk(chunk, wav, self.voice)
            except TTSError as e:
                self._fail_runtime(str(e))
                return
            with self._lock:
                self._wavs[i] = str(wav)
            self._write_state()  # keep `ready` fresh for the UI pulse
        self._producing = False
        self._write_state()

    def _fail_runtime(self, message: str) -> None:
        self.player.set_state(Gst.State.NULL)
        self.status = "error"
        self.error = message
        self._write_state()

    # --- tick: start the next ready segment -----------------------------

    def _tick(self) -> bool:
        if self._stop or self.status in (
            "playing", "paused", "stopped", "done", "error",
        ):
            return True
        if self.status == "synthesizing" and self.current < self.total and self._ready(self.current):
            self._play_segment(self.current)
        return True

    # --- commands (from the UI FIFO) ------------------------------------

    def _nav_status(self) -> str:
        if self.status == "playing":
            return "synthesizing"
        if self.status == "paused":
            return "paused"
        return "stopped"

    def _handle_command(self, cmd: str) -> None:
        cmd = cmd.strip()
        if cmd == "next":
            if self.current + 1 < self.total:
                self.player.set_state(Gst.State.NULL)
                self.current += 1
                self.status = self._nav_status()
                self._write_state()
        elif cmd == "prev":
            self.player.set_state(Gst.State.NULL)
            if self.current > 0:
                self.current -= 1
            self.status = self._nav_status()
            self._write_state()
        elif cmd == "pause":
            if self.status == "playing":
                self.player.set_state(Gst.State.PAUSED)
                self.status = "paused"
                self._write_state()
        elif cmd in ("play", "resume"):
            if self.status == "paused":
                self.player.set_state(Gst.State.PLAYING)
                self.status = "playing"
                self._write_state()
            elif self.status in ("stopped", "done", "synthesizing"):
                if self.status == "done":
                    self.current = 0
                self.status = "synthesizing"
                self._write_state()
        elif cmd == "stop":
            self.player.set_state(Gst.State.NULL)
            self.current = 0
            self.status = "stopped"
            self._write_state()
        elif cmd == "quit":
            self._quit()

    def _fifo_reader(self) -> None:
        try:
            os.mkfifo(self.fifo)
        except FileExistsError:
            pass
        while not self._stop:
            try:
                with open(self.fifo) as fh:
                    for line in fh.read().splitlines():
                        GLib.idle_add(self._handle_command, line)
            except OSError:
                break

    # --- lifecycle ------------------------------------------------------

    def _quit(self) -> None:
        self._stop = True
        self.player.set_state(Gst.State.NULL)
        try:
            (self.dir / "state.json").unlink()
        except OSError:
            pass
        if self._loop:
            GLib.idle_add(self._loop.quit)

    def _cleanup(self) -> None:
        try:
            self.fifo.unlink()
        except OSError:
            pass
        try:
            self._lock_fd.close()
        except OSError:
            pass

    def run(self) -> int:
        lock_path = self.dir / "player.lock"
        try:
            self._lock_fd = open(lock_path, "w")
            fcntl.flock(self._lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            print("another TTS player is already running", file=sys.stderr)
            self._cleanup()
            return 1

        threading.Thread(target=self._producer, daemon=True).start()
        threading.Thread(target=self._fifo_reader, daemon=True).start()
        GLib.timeout_add(200, self._tick)
        signal.signal(signal.SIGINT, lambda *a: self._quit())
        signal.signal(signal.SIGTERM, lambda *a: self._quit())

        self._write_state()
        self._loop = GLib.MainLoop()
        self._loop.run()
        self._cleanup()
        return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: tts-player <document>", file=sys.stderr)
        return 2
    try:
        return TTSPlayer(sys.argv[1]).run()
    except TTSError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())