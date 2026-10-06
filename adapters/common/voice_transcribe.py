"""voice.transcribe adapter — transcribe an audio file to text.

docs/ai/11-voice-integration.md, ADR-007.

Non-interactive counterpart of `voice.dictate`: no capture, no injection —
just whisper.cpp over a file. Useful for scripting and for testing the engine.
"""

from __future__ import annotations

from omintylib.voice import transcribe_file


def run(action, args: dict) -> dict:
    """Transcribe the file named by `file` (or `path`)."""
    path = args.get("file") or args.get("path")
    if not path:
        return {
            "success": False,
            "error": {
                "code": "INVALID_ARGUMENT",
                "message": "no audio file given (pass file=…)",
            },
        }
    return transcribe_file(str(path))
