"""AI-aware action execution (docs/ai/02 §19, docs/ai/10 §19, AI-13).

Composes the AI policy gate with the single action runner:

    AI request
        ↓
    policy (ai/policy)
        ↓
    runner (cli/omivoidlib/runner.py)

There is one execution path — the AI layer does not re-implement
adapters or command execution (docs/ai/10 §25).
"""

from __future__ import annotations

from ..registry import Registry, load_registry
from ..runner import run_action
from . import policy


def run_action_as_ai(
    action_id: str,
    confirmed: bool = False,
    registry: Registry | None = None,
) -> dict:
    """Run an action on behalf of AI, enforcing policy (AI-13/AI-14).

    Returns the runner's structured result, or a policy refusal:

        ACTION_NOT_FOUND       unknown action
        PERMISSION_DENIED      policy refused (see ``error.reason``)
        CONFIRMATION_REQUIRED  explicit user confirmation needed

    ``confirmed`` means the user approved the request. The AI provider
    must never set it on its own (docs/ai/09 §10).
    """
    registry = registry or load_registry()
    action = registry.actions.get(action_id)
    if action is None:
        return {
            "action": action_id,
            "success": False,
            "error": {
                "code": "ACTION_NOT_FOUND",
                "message": f"no action '{action_id}'",
            },
        }

    decision = policy.evaluate(action)
    if decision["decision"] == "deny":
        return {
            "action": action_id,
            "success": False,
            "error": {
                "code": decision["code"],
                "message": decision["message"],
                "reason": decision["reason"],
            },
        }

    if decision["decision"] == "confirm" and not confirmed:
        return {
            "action": action_id,
            "success": False,
            "confirmation_required": True,
            "error": {
                "code": "CONFIRMATION_REQUIRED",
                "message": decision["message"],
                "reason": decision["reason"],
            },
        }

    return run_action(action_id, registry)