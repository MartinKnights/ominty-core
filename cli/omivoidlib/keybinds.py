"""GKS keybindings aggregation (docs/14-gks-keyboard-grammar.md).

Merges the live keybinding sources into one GKS-tagged list so the cheat
sheet can group by domain (tab):

    registry actions  +  Niri base  +  DMS binds  +  generated fragment

Plus the universal application conventions (``Ctrl+S`` etc.), which GKS
does not own but the cheat sheet displays as reference.

Each binding carries:

    {key, domain, action, source, shadowed}

``shadowed`` marks a binding that is defined but loses to another layer for
the same key (GKS collision priority, docs/14 §17).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

# GKS domains (cheat-sheet tabs), in presentation order.
GKS_DOMAINS: tuple[str, ...] = (
    "Application",
    "Navigation",
    "Desktop",
    "Window state",
    "Workspace topology",
    "System",
    "AI",
    "Projects",
    "Hardware",
)

# Modifier display order (docs/14 §18).
_MOD_ORDER = ("Ctrl", "Mod", "Alt", "Shift")

# Universal application conventions — reference only (docs/14 §2, §16).
UNIVERSAL_CONVENTIONS: tuple[tuple[str, str], ...] = (
    ("Ctrl+S", "Save"),
    ("Ctrl+O", "Open"),
    ("Ctrl+N", "New"),
    ("Ctrl+W", "Close document/tab"),
    ("Ctrl+Z", "Undo"),
    ("Ctrl+Shift+Z", "Redo"),
    ("Ctrl+X", "Cut"),
    ("Ctrl+C", "Copy"),
    ("Ctrl+V", "Paste"),
    ("Ctrl+A", "Select all"),
    ("Ctrl+F", "Find"),
    ("Ctrl+P", "Print"),
    ("Ctrl+Q", "Quit"),
)

# Source priority: later sources win a key collision (docs/14 §17).
_SOURCE_ORDER = {"Niri": 0, "DMS": 1, "OmiVoid": 2}


def normalize_key(key: str) -> str:
    """Normalise a key combo: ``Super`` → ``Mod``, canonical modifier order."""
    parts = key.replace("Super", "Mod").split("+")
    if len(parts) == 1:
        return key
    mods = sorted(
        parts[:-1], key=lambda m: _MOD_ORDER.index(m) if m in _MOD_ORDER else 99
    )
    return "+".join(mods + [parts[-1]])


def classify_domain(key: str) -> str:
    """Return the GKS domain for a key combo (docs/14 §1, §19)."""
    if "," in key:
        # Chord (e.g. "Mod+A,A") — domain comes from the prefix.
        prefix = normalize_key(key.split(",")[0].strip())
        return classify_domain(prefix)
    parts = normalize_key(key).split("+")
    mods, base = set(parts[:-1]), parts[-1]
    if "Ctrl" in mods and "Alt" in mods:
        return "System"
    if "Mod" in mods and "Ctrl" in mods:
        return "Workspace topology"
    if "Mod" in mods and "Alt" in mods:
        return "Window state"
    if "Ctrl" in mods:
        return "Application"
    if "Alt" in mods:
        return "Navigation"
    if "Mod" in mods:
        return "AI" if base.upper() == "A" else "Desktop"
    return "Hardware"


def parse_kdl_binds(text: str, source: str) -> list[dict]:
    """Parse every ``binds { … }`` block in a KDL document.

    Handles nesting (e.g. ``recent-windows { binds { … } }``). Returns raw
    bindings with normalised keys.
    """
    out: list[dict] = []
    for m0 in re.finditer(r"binds\s*\{", text):
        start = m0.end() - 1
        depth, end = 0, start
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        block = text[start : end + 1]
        for m in re.finditer(
            r"(?m)^\s*([A-Za-z0-9_+]+)\s+(?:[^\n{]*?)\{([^{}]*)\}", block
        ):
            key = normalize_key(m.group(1))
            action = " ".join(m.group(2).split()).rstrip(";").strip()
            domain = classify_domain(key)
            # Capture actions group under Hardware regardless of modifier
            # (Print / Ctrl+Print / Alt+Print are one family).
            if "screenshot" in action.lower():
                domain = "Hardware"
            out.append(
                {
                    "key": key,
                    "domain": domain,
                    "action": action,
                    "source": source,
                    "shadowed": False,
                }
            )
    return out


def parse_kdl_file(path: Path, source: str) -> list[dict]:
    """Parse a KDL file, returning [] when it is missing."""
    try:
        text = path.read_text()
    except OSError:
        return []
    return parse_kdl_binds(text, source)


def registry_bindings(registry) -> list[dict]:
    """Extract declared keys from registry actions (including chords)."""
    out: list[dict] = []
    for action in sorted(registry.actions.values(), key=lambda a: a.id):
        for key in action.keys or []:
            norm = normalize_key(key)
            out.append(
                {
                    "key": norm,
                    "domain": classify_domain(norm),
                    "action": action.id,
                    "source": "OmiVoid",
                    "shadowed": False,
                }
            )
    return out


def _default_sources() -> list[tuple[str, Path]]:
    config = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return [
        ("Niri", config / "niri" / "config.kdl"),
        ("DMS", config / "niri" / "dms" / "binds.kdl"),
        ("OmiVoid", config / "omivoid" / "generated" / "niri" / "bindings.kdl"),
    ]


def _mark_shadowed(bindings: list[dict]) -> None:
    """Mark all but the highest-priority binding for each key."""
    best: dict[str, int] = {}
    for i, b in enumerate(bindings):
        rank = _SOURCE_ORDER.get(b["source"], 99)
        if b["key"] not in best or rank >= _SOURCE_ORDER.get(
            bindings[best[b["key"]]]["source"], 99
        ):
            best[b["key"]] = i
    for i, b in enumerate(bindings):
        b["shadowed"] = best.get(b["key"]) != i


def collect(registry, sources: list[tuple[str, Path]] | None = None) -> dict:
    """Collect and tag all keybindings for the cheat sheet.

    Returns ``{"domains": [...], "bindings": [...]}`` where each binding is
    ``{key, domain, action, source, shadowed}``.
    """
    sources = sources if sources is not None else _default_sources()
    bindings: list[dict] = []
    for label, path in sources:
        bindings.extend(parse_kdl_file(path, label))
    if registry is not None:
        # Only chords come from the registry: non-chord keys are either
        # emitted into the generated fragment (already parsed) or owned by
        # DMS. Adding them again would double-count.
        bindings.extend(b for b in registry_bindings(registry) if "," in b["key"])

    _mark_shadowed(bindings)

    # Universal conventions are reference-only, never shadowed.
    for key, action in UNIVERSAL_CONVENTIONS:
        norm = normalize_key(key)
        bindings.append(
            {
                "key": norm,
                "domain": "Application",
                "action": action,
                "source": "Universal",
                "shadowed": False,
            }
        )

    bindings.sort(key=lambda b: (GKS_DOMAINS.index(b["domain"]), b["key"]))
    return {"domains": list(GKS_DOMAINS), "bindings": bindings}


def keybinds(registry=None, sources=None) -> dict:
    """Public entry point. Loads the registry when none is supplied."""
    if registry is None:
        from .registry import load_registry

        registry = load_registry()
    return collect(registry, sources)
