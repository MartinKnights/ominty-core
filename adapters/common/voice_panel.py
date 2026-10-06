"""voice.panel adapter — show or hide the dictation panel.

docs/ai/11-voice-integration.md, ADR-007.

The panel is a presentation surface: this flips the shared status file's
``panel`` flag so the Quickshell component (`shell/quickshell/ominty-voice`)
knows to stay visible, letting the user toggle dictation with the mouse.
"""

from __future__ import annotations

from omintylib.voice import panel


def run(action, args: dict) -> dict:
    """Toggle the panel's visibility."""
    return panel()