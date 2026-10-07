"""Ominty TTS — document to speech (docs/ai/11-voice-integration.md).

Format-aware text extraction, cleaning and chunking used by the document
player and the MP3 exporter. Synthesising is a separate layer (the Piper
stack); this module only turns a document into speech-ready chunks.

Supported: .md, .txt, .pdf, .doc, .docx, .epub.
Tools used externally: pandoc, pdftotext, catdoc (all present on the
reference machine).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt", ".pdf", ".doc", ".docx", ".epub"}

DEFAULT_CHUNK_CHARS = 2400


class TTSError(Exception):
    """Raised when a document cannot be converted to text."""


def _run(argv: list[str]) -> str:
    """Run an extractor; return stdout or raise TTSError."""
    proc = subprocess.run(argv, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise TTSError(
            f"{argv[0]} failed: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return proc.stdout


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


def _pandoc_plain(path: Path, fmt: str) -> str:
    if shutil.which("pandoc") is None:
        raise TTSError("pandoc not found (needed for .md/.txt/.docx/.epub)")
    return _run(["pandoc", "-f", fmt, "-t", "plain", "--wrap=none", str(path)])


def extract_text(path: str | Path) -> str:
    """Extract plain text from a document by extension."""
    p = Path(path)
    ext = p.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise TTSError(f"unsupported document type: {ext or '(none)'}")

    if ext in (".md", ".markdown"):
        return _pandoc_plain(p, "markdown")
    if ext == ".txt":
        return p.read_text(errors="replace")
    if ext == ".pdf":
        if shutil.which("pdftotext") is None:
            raise TTSError("pdftotext not found (needed for .pdf)")
        return _run(["pdftotext", "-layout", str(p), "-"])
    if ext == ".doc":
        if shutil.which("catdoc") is None:
            raise TTSError("catdoc not found (needed for .doc)")
        return _run(["catdoc", "-w", str(p)])
    if ext == ".docx":
        return _pandoc_plain(p, "docx")
    if ext == ".epub":
        return _pandoc_plain(p, "epub")
    raise TTSError(f"unsupported document type: {ext}")


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------


def clean_text(text: str) -> str:
    """Normalise extracted text for speech synthesis.

    Handles the junk the extractors tend to leave behind: control characters,
    long dash/heading noise, lone page numbers, and ragged whitespace. The
    Markdown cleaner used by `read-selection` is not needed here because
    pandoc already emits plain text; this is the generic pass on top.
    """
    # Normalise line endings and control characters (keep newlines/tabs).
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or ord(ch) >= 32)

    # Drop the pandoc/decoration horizontal-rule lines (---, ***, ===, ###).
    text = re.sub(r"^[ \t]*(?:\*|_|-|\#|\=){3,}[ \t]*$\n?", "", text, flags=re.M)

    # Drop standalone page-number-like lines (digits, "Page N", "p. N", roman).
    text = re.sub(
        r"^[ \t]*(?:(?:(?:page|p\.)\s*)?\d{1,4}|(?:i{1,3}|iv|v|vi{0,3}|ix|x{1,2}iv?))\s*$\n?",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Collapse runs of 3+ blank lines to one.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def _split_sentences(paragraph: str) -> list[str]:
    """Split a paragraph on sentence boundaries, keeping the punctuation."""
    parts = re.split(r"(?<=[.!?\u201d\u2019])\s+", paragraph)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str, max_chars: int = DEFAULT_CHUNK_CHARS) -> list[str]:
    """Split text into sentence-aware chunks not exceeding ``max_chars``.

    Paragraphs are broken into sentences, which are then accumulated into
    chunks. A sentence longer than ``max_chars`` is hard-split.
    """
    chunks: list[str] = []
    current: list[str] = []

    def flush() -> None:
        if current:
            chunks.append(" ".join(current))
            current.clear()

    def push(sentence: str) -> None:
        if len(sentence) > max_chars:
            flush()
            for i in range(0, len(sentence), max_chars):
                chunks.append(sentence[i : i + max_chars])
            return
        if sum(len(s) for s in current) + len(sentence) + len(current) > max_chars:
            flush()
        current.append(sentence)

    for paragraph in text.split("\n\n"):
        for sentence in _split_sentences(paragraph):
            push(sentence)
    flush()

    return [c for c in chunks if c.strip()]


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------


@dataclass
class PreparedDocument:
    path: str
    title: str
    extension: str
    text: str
    chunks: list[str]

    @property
    def total(self) -> int:
        return len(self.chunks)


def prepare_document(path: str | Path, max_chars: int = DEFAULT_CHUNK_CHARS) -> PreparedDocument:
    """Extract, clean and chunk a document for speech."""
    p = Path(path)
    if not p.is_file():
        raise TTSError(f"file not found: {p}")
    text = clean_text(extract_text(p))
    if not text:
        raise TTSError(f"no readable text in {p.name}")
    chunks = chunk_text(text, max_chars)
    if not chunks:
        raise TTSError(f"no speechable chunks in {p.name}")
    return PreparedDocument(
        path=str(p),
        title=p.stem,
        extension=p.suffix.lower(),
        text=text,
        chunks=chunks,
    )


# ---------------------------------------------------------------------------
# Synthesis (Piper) and MP3 export
# ---------------------------------------------------------------------------


def piper_bin(venv: str | None = None) -> str:
    """Path to the Piper executable inside its virtualenv."""
    venv = venv or os.environ.get("OMINTY_PIPER_VENV") or str(Path.home() / ".piper-venv")
    bin_path = Path(venv) / "bin" / "piper"
    if not bin_path.is_file():
        raise TTSError(f"piper not found in venv: {bin_path}")
    return str(bin_path)


def default_voice() -> str:
    """The voice to use, overridable via OMINTY_TTS_VOICE."""
    return (
        os.environ.get("OMINTY_TTS_VOICE")
        or str(
            Path.home()
            / ".local/share/piper/voices/en_GB-northern_english_male-medium.onnx"
        )
    )


def synth_chunk(
    text: str,
    wav_path: str | Path,
    voice: str | None = None,
    venv: str | None = None,
) -> str:
    """Synthesise one chunk to a WAV file. Returns the WAV path."""
    voice = voice or default_voice()
    if not Path(voice).is_file():
        raise TTSError(f"piper voice not found: {voice}")
    proc = subprocess.run(
        [piper_bin(venv), "-m", voice, "--output_file", str(wav_path)],
        input=text,
        text=True,
        capture_output=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise TTSError(f"piper failed: {proc.stderr.strip() or 'no stderr'}")
    return str(wav_path)


def synthesize_segments(
    doc_path: str | Path,
    out_dir: str | Path,
    voice: str | None = None,
    venv: str | None = None,
) -> list[str]:
    """Synthesise every chunk to numbered WAVs; returns their paths in order."""
    prep = prepare_document(doc_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    wavs: list[str] = []
    for i, chunk in enumerate(prep.chunks):
        wav = out / f"seg-{i:04d}.wav"
        synth_chunk(chunk, wav, voice, venv)
        wavs.append(str(wav))
    return wavs


def export_mp3(
    doc_path: str | Path,
    out_path: str | Path,
    bitrate: str = "192k",
    voice: str | None = None,
    venv: str | None = None,
) -> str:
    """Synthesise the whole document and encode a single MP3."""
    import tempfile

    with tempfile.TemporaryDirectory(prefix="ominty-tts-mp3-") as td:
        wavs = synthesize_segments(doc_path, td, voice, venv)
        list_file = Path(td) / "concat.txt"
        list_file.write_text(
            "".join(f"file '{Path(w).resolve()}'\n" for w in wavs)
        )
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
                "-c:a", "libmp3lame", "-b:a", bitrate, str(out),
            ],
            capture_output=True,
            text=True,
            timeout=3600,
        )
        if proc.returncode != 0:
            raise TTSError(f"ffmpeg failed: {proc.stderr.strip()[:400]}")
        return str(out)


# ---------------------------------------------------------------------------
# Player runtime (shared with the UI popup)
# ---------------------------------------------------------------------------


def run_dir() -> Path:
    """Runtime directory shared with the player process and the popup."""
    base = os.environ.get("XDG_RUNTIME_DIR") or "/tmp"
    d = Path(base) / "ominty-tts"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _require_player() -> dict:
    """Error envelope used when no player is running."""
    return {
        "success": False,
        "error": {"code": "ACTION_UNAVAILABLE", "message": "no TTS player is running"},
    }


def send_command(cmd: str) -> dict:
    """Write a control command (next/prev/pause/resume/stop) to the player FIFO."""
    fifo = run_dir() / "cmd"
    if not fifo.exists():
        return _require_player()
    try:
        with open(fifo, "w") as fh:
            fh.write(cmd + "\n")
    except OSError as e:
        return {
            "success": False,
            "error": {"code": "ADAPTER_FAILED", "message": str(e)},
        }
    return {"success": True, "state": {"command": cmd}}


def read_state() -> dict:
    """Read the player's state file; empty when no player is active."""
    try:
        return json.loads((run_dir() / "state.json").read_text())
    except (OSError, json.JSONDecodeError):
        return {"status": "none"}


def start_player(doc_path: str | Path) -> dict:
    """Validate a document and launch the (detached) player process."""
    # Surface extraction errors before spawning, so `tts say` is not silent.
    prepare_document(doc_path)
    cli_dir = str(Path(__file__).resolve().parents[1])  # <repo>/cli
    env = dict(os.environ)
    env["PYTHONPATH"] = cli_dir + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "omintylib.tts_player", str(doc_path)],
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as e:
        return {
            "success": False,
            "error": {"code": "ADAPTER_FAILED", "message": str(e)},
        }
    return {"success": True, "state": {"pid": proc.pid, "doc": str(doc_path)}}