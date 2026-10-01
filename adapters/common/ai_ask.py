"""ai.ask adapter — generic ask through the default provider (docs/ai/10 §9).

Resolves the configured default provider and returns its response.
The generic action must not hard-code Pi semantics (docs/ai/02 §13).
"""

from __future__ import annotations

from omintylib.ai import ask as ai_ask


def run(action, args: dict) -> dict:
    """Ask the default AI provider."""
    prompt = args.get("prompt")
    if not prompt:
        return {
            "success": False,
            "error": {
                "code": "INVALID_ARGUMENT",
                "message": "missing 'prompt' argument",
            },
        }

    result = ai_ask(prompt)
    if not result["success"]:
        return {"success": False, "error": result["error"]}

    return {"success": True, "state": {"response": result["response"]}}