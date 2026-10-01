"""ai.clipboard.summarise adapter — summarise the clipboard via AI (AI-25).

Clipboard-based alternative to selection summarise (docs/ai/10 §31).
"""

from __future__ import annotations

from omintylib.ai.clipboard_actions import run_with_clipboard


def run(action, args: dict) -> dict:
    """Summarise the current clipboard content."""
    return run_with_clipboard("Summarise the following text.")