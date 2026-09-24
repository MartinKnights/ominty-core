"""ai.clipboard.explain adapter — explain the clipboard via AI (AI-25).

Clipboard-based alternative to selection explain (docs/ai/10 §31).
"""

from __future__ import annotations

from omivoidlib.ai.clipboard_actions import run_with_clipboard


def run(action, args: dict) -> dict:
    """Explain the current clipboard content."""
    return run_with_clipboard("Explain the following text.")