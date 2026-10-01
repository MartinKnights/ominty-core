"""Clipboard-context AI actions (docs/ai/10 §31, AI-25).

Composes the clipboard collector with the provider layer for the
explain/summarise actions. Lives in the ai layer (not the adapters
directory) so adapters can import it absolutely — the adapters/
directory is not a Python package.

Flow:

    action invoked
        ↓
    collect_clipboard()          (context collector)
        ↓
    ask(instruction, context=[clipboard])   (provider layer)
        ↓
    response
"""

from __future__ import annotations

from . import ask as ai_ask
from .context import collect_clipboard


def run_with_clipboard(instruction: str) -> dict:
    """Collect the clipboard and ask the default provider about it.

    Returns the provider result, or a structured context failure
    (CONTEXT_UNAVAILABLE / CONTEXT_TOO_LARGE) when the clipboard cannot
    be used (AGENTS.md §19 — no stale or guessed context).
    """
    collected = collect_clipboard()
    if not collected["success"]:
        return {"success": False, "error": collected["error"]}

    ctx = collected["context"]
    result = ai_ask(instruction, context=[ctx])
    if not result["success"]:
        return {"success": False, "error": result["error"]}

    return {"success": True, "state": {"response": result["response"]}}