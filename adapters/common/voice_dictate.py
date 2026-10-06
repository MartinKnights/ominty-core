"""voice.dictate / voice.stop adapter — local STT dictation.

docs/ai/11-voice-integration.md, ADR-007.

Dictation is a toggle because Niri has no key-release bindings:

* the first invocation starts microphone capture;
* the next stops, transcribes with whisper.cpp and injects the text into the
  focused window with `wtype`.

`voice.stop` forces the stop half regardless of state.
"""

from __future__ import annotations

from omintylib.voice import dictate, stop_recording


def run(action, args: dict) -> dict:
    """Toggle dictation; `voice.stop` always stops."""
    if action.id == "voice.stop":
        return stop_recording()
    return dictate()
