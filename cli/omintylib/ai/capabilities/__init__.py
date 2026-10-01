"""AI capability catalogue (docs/ai/04, docs/ai/10 §15–16).

Derives the AI-accessible capability set from the Action Registry.

Filtering (docs/ai/04 §9, AGENTS.md §17–18):

* actions must declare ``ai_accessible = true``;
* actions that invoke AI (``ai.*``) are excluded to avoid recursive
  tool invocation (AGENTS.md §18);
* platform/availability filtering is delegated to the action runner
  at execution time (docs/ai/04 §9).

The registry remains the source of truth — no independent hand-written
AI tool catalogue (docs/ai/02 §18).
"""

from __future__ import annotations

from ...registry import Registry, load_registry

# Actions invoking AI must not be exposed as AI tools (AGENTS.md §18).
_AI_RECURSIVE_PREFIX = "ai."


def _is_ai_recursive(action_id: str) -> bool:
    """True for actions that invoke AI (recursion protection)."""
    return action_id.startswith(_AI_RECURSIVE_PREFIX)


def list_capabilities(registry: Registry | None = None) -> list[dict]:
    """Return the AI-accessible capability list (docs/ai/04 §26).

    Each entry carries the policy metadata the provider bridge needs:

        {"id", "name", "description", "risk", "confirmation"}

    Sorted by id for stable machine-readable output.
    """
    registry = registry or load_registry()
    capabilities = []
    for action in registry.actions.values():
        if not action.ai_accessible:
            continue
        if _is_ai_recursive(action.id):
            continue
        capabilities.append(
            {
                "id": action.id,
                "name": action.name,
                "description": action.description,
                "risk": action.risk,
                "confirmation": action.confirmation,
            }
        )
    return sorted(capabilities, key=lambda c: c["id"])