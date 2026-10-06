"""Ominty voice — local STT dictation (docs/ai/11-voice-integration.md, ADR-007).

Speech-to-text is implemented with local whisper.cpp. This module holds the
implementation shared by the voice adapters and the ``ominty voice`` CLI:

* configuration loading (``~/.config/ominty/voice.toml``);
* engine and model resolution;
* PipeWire capture (``pw-record``);
* transcription (whisper.cpp);
* text injection (``wtype``);
* the recording state used by the indicator.

Dictation is a *toggle* because Niri has no key-release bindings: the first
invocation starts recording, the second stops, transcribes and injects.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import tempfile
import time
import tomllib
from pathlib import Path

#: Engine binary names to look for, in order.
_ENGINE_NAMES = ("whisper-cli", "main", "whisper")

#: Extra directories to search for a source-built engine (Phase 1 build).
_ENGINE_DIRS = (
    "~/.cache/ominty/build/whisper.cpp/build/bin",
    "~/.local/bin",
)

_DEFAULT_CONFIG = {
    "voice": {
        "enabled": True,
        "stt": {
            "engine": "whisper.cpp",
            "binary": "whisper-cli",
            "model": "~/.local/share/ominty/models/ggml-base.en.bin",
            "language": "en",
            "threads": 0,
            "capture": {
                "command": "pw-record",
                "sample_rate": 16000,
                "channels": 1,
            },
            "inject": {"method": "wtype"},
        },
    }
}


def _err(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def _shipped_config() -> Path:
    """The default config shipped with the repository."""
    return Path(__file__).resolve().parents[2] / "config" / "voice.toml"


def config_path() -> Path:
    """The active user config path."""
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "ominty" / "voice.toml"


def _merge(base: dict, overlay: dict) -> dict:
    """Recursively merge ``overlay`` into ``base`` (overlay wins)."""
    out = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config() -> dict:
    """Load voice config: built-in ← shipped ← user (later wins)."""
    cfg = _DEFAULT_CONFIG
    for path in (_shipped_config(), config_path()):
        try:
            with open(path, "rb") as fh:
                cfg = _merge(cfg, tomllib.load(fh))
        except (OSError, tomllib.TOMLDecodeError):
            continue
    return cfg


def _stt(cfg: dict) -> dict:
    return cfg.get("voice", {}).get("stt", {})


# ---------------------------------------------------------------------------
# Engine / model resolution
# ---------------------------------------------------------------------------


def resolve_engine(cfg: dict | None = None) -> str | None:
    """Resolve the whisper.cpp binary, or None when it is not installed."""
    cfg = cfg or load_config()
    binary = _stt(cfg).get("binary") or "whisper-cli"

    # An absolute path in the config wins.
    candidate = Path(binary).expanduser()
    if candidate.is_absolute():
        return str(candidate) if os.access(candidate, os.X_OK) else None

    found = shutil.which(binary)
    if found:
        return found
    for d in _ENGINE_DIRS:
        for name in _ENGINE_NAMES:
            p = Path(d).expanduser() / name
            if p.is_file() and os.access(p, os.X_OK):
                return str(p)
    return None


def resolve_model(cfg: dict | None = None) -> str | None:
    """Resolve the whisper model file, or None when it is absent."""
    cfg = cfg or load_config()
    model = _stt(cfg).get("model")
    if not model:
        return None
    path = Path(model).expanduser()
    return str(path) if path.is_file() else None


# ---------------------------------------------------------------------------
# Recording state (shared with the indicator)
# ---------------------------------------------------------------------------


def state_dir() -> Path:
    """Runtime directory for the voice state files."""
    base = os.environ.get("XDG_RUNTIME_DIR") or "/tmp"
    d = Path(base) / "ominty-voice"
    d.mkdir(parents=True, exist_ok=True)
    return d


def status_path() -> Path:
    return state_dir() / "status.json"


def write_status(state: str, **extra) -> None:
    """Publish recording state for the indicator to poll (docs/ai/11 §8)."""
    payload = {"state": state, "ts": time.time()}
    payload.update(extra)
    try:
        status_path().write_text(json.dumps(payload))
    except OSError:
        pass


def read_status() -> dict:
    try:
        return json.loads(status_path().read_text())
    except (OSError, json.JSONDecodeError):
        return {"state": "idle"}


# ---------------------------------------------------------------------------
# Transcription
# ---------------------------------------------------------------------------


def _normalize_wav(path: str) -> tuple[str | None, str | None]:
    """Convert any audio to a whisper-readable 16 kHz mono s16 WAV.

    ``pw-record`` writes WAV files that whisper.cpp's miniaudio decoder rejects
    ("Invalid argument" while reading frames); ffmpeg produces a header it
    accepts. Returns (temp_path, None) on success, (None, error) otherwise.
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return None, "ffmpeg not found (needed to normalise audio)"

    fd, tmp = tempfile.mkstemp(prefix="ominty-voice-", suffix=".wav")
    os.close(fd)
    try:
        proc = subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error", "-i", path,
             "-ar", "16000", "-ac", "1", "-f", "wav", tmp],
            capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)
    if proc.returncode != 0:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        return None, proc.stderr.strip() or "ffmpeg conversion failed"
    return tmp, None


def transcribe_file(path: str, cfg: dict | None = None) -> dict:
    """Transcribe an audio file to text with whisper.cpp."""
    cfg = cfg or load_config()
    stt = _stt(cfg)

    engine = resolve_engine(cfg)
    if not engine:
        return _err("DEPENDENCY_MISSING", "whisper.cpp engine not found")
    model = resolve_model(cfg)
    if not model:
        return _err("DEPENDENCY_MISSING", "whisper model not found")
    if not Path(path).is_file():
        return _err("INVALID_ARGUMENT", f"audio file not found: {path}")

    wav, err = _normalize_wav(path)
    if err:
        return _err("ADAPTER_FAILED", err)
    try:
        cmd = [
            engine, "-m", model, "-f", wav,
            "-l", str(stt.get("language") or "en"),
            "-nt",  # no timestamps: we only want the text
            "-np",  # no prints: keep stdout to the transcript
        ]
        threads = int(stt.get("threads") or 0)
        if threads > 0:
            cmd += ["-t", str(threads)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return _err("ADAPTER_FAILED", "transcription timed out")
    except OSError as e:
        return _err("ADAPTER_FAILED", str(e))
    finally:
        try:
            os.unlink(wav)
        except OSError:
            pass

    if proc.returncode != 0:
        return _err("ADAPTER_FAILED", proc.stderr.strip() or "transcription failed")

    text = " ".join(proc.stdout.split()).strip()
    return {"success": True, "state": {"text": text}}


# ---------------------------------------------------------------------------
# Text injection
# ---------------------------------------------------------------------------


def inject_text(text: str, cfg: dict | None = None) -> dict:
    """Type text into the focused window (wtype)."""
    cfg = cfg or load_config()
    if not text:
        return {"success": True, "state": {"injected": False, "reason": "empty"}}

    method = _stt(cfg).get("inject", {}).get("method", "wtype")
    if method != "wtype":
        return _err("PLATFORM_UNSUPPORTED", f"injection method '{method}' is not supported")

    wtype = shutil.which("wtype")
    if not wtype:
        return _err("DEPENDENCY_MISSING", "wtype not found (Wayland text input)")

    if os.environ.get("OMINTY_VOICE_DRY_RUN"):
        return {"success": True, "state": {"injected": False, "dry_run": True, "text": text}}

    try:
        proc = subprocess.run(
            [wtype, "-"], input=text, text=True, capture_output=True, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return _err("ADAPTER_FAILED", str(e))
    if proc.returncode != 0:
        return _err("ADAPTER_FAILED", proc.stderr.strip() or "wtype failed")
    return {"success": True, "state": {"injected": True, "chars": len(text)}}


# ---------------------------------------------------------------------------
# Capture / dictation toggle
# ---------------------------------------------------------------------------


def _recording_path() -> Path:
    return state_dir() / "recording.wav"


def _pid_path() -> Path:
    return state_dir() / "recording.pid"


def _recording_active() -> bool:
    try:
        pid = int(_pid_path().read_text().strip())
    except (OSError, ValueError):
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def start_recording(cfg: dict | None = None) -> dict:
    """Start capturing the microphone."""
    cfg = cfg or load_config()
    if _recording_active():
        return _err("INVALID_ARGUMENT", "already recording")

    capture = _stt(cfg).get("capture", {})
    command = capture.get("command", "pw-record")
    exe = shutil.which(command) or command
    wav = _recording_path()
    try:
        wav.unlink()
    except OSError:
        pass

    cmd = [
        exe,
        "--rate", str(capture.get("sample_rate", 16000)),
        "--channels", str(capture.get("channels", 1)),
        "--format", "s16",
        str(wav),
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as e:
        return _err("ADAPTER_FAILED", f"could not start capture: {e}")

    _pid_path().write_text(str(proc.pid))
    write_status("recording", pid=proc.pid)
    return {"success": True, "state": {"recording": True, "pid": proc.pid, "file": str(wav)}}


def stop_recording(cfg: dict | None = None) -> dict:
    """Stop capture, transcribe, and inject the result."""
    cfg = cfg or load_config()
    if not _recording_active():
        write_status("idle")
        return _err("INVALID_ARGUMENT", "not recording")

    write_status("transcribing")
    try:
        pid = int(_pid_path().read_text().strip())
        os.kill(pid, signal.SIGINT)
        for _ in range(50):  # wait up to ~5 s for a clean finalise
            time.sleep(0.1)
            try:
                os.kill(pid, 0)
            except OSError:
                break
        else:
            os.kill(pid, signal.SIGKILL)  # unreachable in time — force stop
    except (OSError, ValueError):
        pass

    for p in (_pid_path(),):
        try:
            p.unlink()
        except OSError:
            pass

    wav = _recording_path()
    result = transcribe_file(str(wav), cfg)
    wav_size = wav.stat().st_size if wav.is_file() else 0
    if not result["success"]:
        write_status("idle")
        _save_debug("", wav_size, {"success": False, "error": result.get("error")})
        return result

    text = result["state"]["text"]
    injected = inject_text(text, cfg)
    write_status("idle")
    _save_debug(text, wav_size, injected)
    return {
        "success": injected["success"],
        "state": {"text": text, "injected": injected.get("state", {}).get("injected", False)},
        **({} if injected["success"] else {"error": injected.get("error")}),
    }


def _save_debug(text: str, wav_size: int, inject: dict) -> None:
    """Persist the last dictation outcome so failures are diagnosable."""
    try:
        d = state_dir()
        (d / "last_transcript.txt").write_text(text if text else "<empty>")
        (d / "last_wav_bytes").write_text(str(wav_size))
        (d / "last_inject.json").write_text(json.dumps(inject))
    except OSError:
        pass


def dictate(cfg: dict | None = None) -> dict:
    """Toggle dictation: start recording, or stop + transcribe + inject."""
    if not (cfg := cfg or load_config()).get("voice", {}).get("enabled", True):
        return _err("ACTION_UNAVAILABLE", "voice is disabled in voice.toml")
    if _recording_active():
        return stop_recording(cfg)
    return start_recording(cfg)


def panel(cfg: dict | None = None) -> dict:
    """Toggle the standalone dictation panel (shown by the indicator).

    The panel is a presentation surface: this just flips the ``panel`` flag in
    the shared status file so the Quickshell component (`shell/quickshell/
    ominty-voice`) knows whether to stay visible for mouse control.
    """
    if not (cfg := cfg or load_config()).get("voice", {}).get("enabled", True):
        return _err("ACTION_UNAVAILABLE", "voice is disabled in voice.toml")
    status = read_status()
    on = not status.get("panel", False)
    state = status.get("state", "idle")
    if on and state == "idle":
        state = "panel"
    elif not on and state == "panel":
        state = "idle"
    write_status(state, panel=on)
    return {"success": True, "state": {"panel": on, "state": state}}
