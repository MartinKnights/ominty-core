"""AI action policy (docs/ai/09, docs/ai/10 §20, AI-14/AI-16).

Evaluates whether an AI provider may invoke a registry action. This is
the gate between an AI request and the action runner (docs/ai/09 §2).

Decisions:

    allow    — permitted; proceed to the runner
    deny     — refused (code PERMISSION_DENIED)
    confirm  — requires user confirmation (code CONFIRMATION_REQUIRED)

AI output is untrusted input (docs/ai/09 §3); policy failure favours
deny (docs/ai/09 §37).
"""

from __future__ import annotations

from ...registry import Action

# Risk classes AI must not invoke in Phase 1 (docs/ai/09 §8).
FORBIDDEN_RISKS = {"privileged", "destructive", "critical"}

# Confirmation policies that require an AI-initiated confirmation.
# `interactive` is scoped to human surfaces (docs/03 §17); `never`
# requires none. AI therefore confirms for `ai-only` and `always`.
AI_CONFIRMATION_POLICIES = {"ai-only", "always"}

# AI-invoking actions are never exposed back to AI (AGENTS.md §18).
_AI_RECURSIVE_PREFIX = "ai."


def _result(action: Action, decision: str, code: str | None,
            reason: str, message: str) -> dict:
    return {
        "action": action.id,
        "decision": decision,
        "code": code,
        "reason": reason,
        "message": message,
        "risk": action.risk,
        "confirmation": action.confirmation,
    }


def evaluate(action: Action) -> dict:
    """Evaluate AI policy for an action (docs/ai/09 §6–9).

    Recursion is checked first so an AI-invoking action is always
    refused, regardless of its other metadata (AI-16).
    """
    if action.id.startswith(_AI_RECURSIVE_PREFIX):
        return _result(
            action, "deny", "PERMISSION_DENIED", "ai_recursion",
            f"action '{action.id}' invokes AI and may not be requested by AI",
        )
    if not action.ai_accessible:
        return _result(
            action, "deny", "PERMISSION_DENIED", "not_ai_accessible",
            f"action '{action.id}' is not AI-accessible",
        )
    if action.risk in FORBIDDEN_RISKS:
        return _result(
            action, "deny", "PERMISSION_DENIED", "risk_not_permitted",
            f"risk '{action.risk}' is not permitted for AI in Phase 1",
        )
    if action.confirmation in AI_CONFIRMATION_POLICIES:
        return _result(
            action, "confirm", "CONFIRMATION_REQUIRED",
            "confirmation_required",
            f"action '{action.id}' requires confirmation",
        )
    return _result(
        action, "allow", None, "allowed",
        f"action '{action.id}' is permitted",
    )