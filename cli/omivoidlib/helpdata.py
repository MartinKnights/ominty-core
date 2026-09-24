"""Registry-derived help data for the `Super+K` Interaction Explorer.

docs/10 §15, docs/02 §10–12, docs/03 §50.

Proves the chain:

    registry
       ↓
    discoverability

The help data is derived from the action registry at runtime — there is no
separately authored cheat sheet (docs/02 §12). The JSON structure is the data
contract for the future Super+K UI (Quickshell/DMS component, Stage 12–13).

Each entry exposes at minimum:
- action name;
- category;
- primary binding;
- description.
"""

from __future__ import annotations

from .registry import Registry


def build_help_data(registry: Registry) -> dict:
    """Build the registry-derived help data structure.

    Actions with discoverable = false are excluded (docs/03 §226).
    Entries are grouped by category, categories sorted alphabetically.
    """
    categories: dict[str, list[dict]] = {}
    for action in sorted(registry.actions.values(), key=lambda a: a.id):
        if not action.discoverable:
            continue
        binding = action.primary_key or (action.keys[0] if action.keys else None)
        entry = {
            "id": action.id,
            "name": action.name,
            "description": action.description,
            "binding": binding,
            "keywords": action.keywords,
        }
        categories.setdefault(action.category, []).append(entry)

    return {
        "source": "action registry",
        "categories": [
            {"name": name, "actions": entries}
            for name, entries in sorted(categories.items())
        ],
    }


def _entry_text(entry: dict) -> str:
    """Lowercased searchable text for a help entry."""
    parts = [
        entry["id"],
        entry["name"],
        entry["description"],
        entry["category"] if "category" in entry else "",
    ]
    parts.extend(entry.get("keywords", []))
    if entry.get("binding"):
        parts.append(entry["binding"])
    return " ".join(parts).lower()


def search_help_data(help_data: dict, query: str) -> list[dict]:
    """Search help entries by name, keywords, category, description, binding.

    Multi-term queries require every term to match (AND), so "move window"
    locates window actions even when the user does not know the action ID
    (docs/02 §11).
    """
    terms = [t for t in query.lower().split() if t]
    if not terms:
        return []

    results = []
    for category in help_data["categories"]:
        for entry in category["actions"]:
            text = _entry_text(entry)
            if all(term in text for term in terms):
                results.append(entry)
    return results


def format_help_text(help_data: dict) -> str:
    """Render the help data as human-readable text (explorer-style)."""
    lines = []
    for category in help_data["categories"]:
        lines.append(category["name"])
        lines.append("─" * len(category["name"]))
        for entry in category["actions"]:
            binding = entry["binding"] or "-"
            lines.append(
                f"{entry['name']:<28} {binding:<18} {entry['description']}"
            )
        lines.append("")
    return "\n".join(lines).rstrip()