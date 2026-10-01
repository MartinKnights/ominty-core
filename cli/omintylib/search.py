"""Universal action search backend (docs/10 §16, docs/03 §318).

UI-independent: the Quickshell/DMS palette consumes this via the CLI.
The search backend remains independent of the UI (docs/10 §16).

Supports:
- action names;
- keywords;
- category;
- application actions (app.* namespace).
"""

from __future__ import annotations

from .registry import Action, Registry


def search_actions(
    registry: Registry,
    query: str,
    *,
    palette_only: bool = False,
) -> list[dict]:
    """Search the registry for actions matching the query.

    Args:
        registry: the loaded registry.
        query: space-separated search terms.
        palette_only: if True, restrict to palette-eligible actions.

    Returns:
        Ranked list of dicts (id, name, description, category, binding, keywords).
        Multi-term queries require every term to match (AND semantics).
    """
    terms = [t for t in query.lower().split() if t]
    if not terms:
        return []

    actions = sorted(registry.actions.values(), key=lambda a: a.id)
    if palette_only:
        actions = [a for a in actions if a.palette]
    else:
        actions = [a for a in actions if a.discoverable]

    results: list[tuple[float, Action]] = []
    for action in actions:
        score = _score(action, terms)
        if score > 0:
            results.append((score, action))

    results.sort(key=lambda x: (-x[0], x[1].id))
    return [_to_entry(a) for _, a in results]


def _score(action: Action, terms: list[str]) -> float:
    """Score an action against search terms (AND semantics)."""
    searchable = " ".join([
        action.id,
        action.name,
        action.description,
        action.category,
        " ".join(action.keywords),
        action.primary_key or "",
    ]).lower()

    all_match = all(term in searchable for term in terms)
    if not all_match:
        return 0.0

    score = 0.0
    for term in terms:
        if term == action.id.lower():
            score += 100
        elif term in action.id.lower():
            score += 50
        if term in action.name.lower():
            score += 40
        if term in " ".join(action.keywords).lower():
            score += 30
        if term in action.category.lower():
            score += 20
        if term in action.description.lower():
            score += 10
    return score


def _to_entry(action: Action) -> dict:
    return {
        "id": action.id,
        "name": action.name,
        "description": action.description,
        "category": action.category,
        "binding": action.primary_key or (action.keys[0] if action.keys else None),
        "keywords": action.keywords,
    }
