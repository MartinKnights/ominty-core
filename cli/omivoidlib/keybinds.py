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

# ---- Human-readable labels (cheat sheet) --------------------------------
# Both columns must read as plain English: no XF86 codes, no spawn commands,
# no native Niri verbs.
#
# Physical F-row of the target machine (Microsoft Surface Book):
#   F1 Brightness Down  F2 Brightness Up  F3 Play/Pause  F4 Mute
#   F5 Volume Down      F6 Volume Up      F7 Print Screen
#   F8 Home             F9 End            F10 Page Up    F11 Page Down
KEY_LABELS: dict[str, str] = {
    "XF86MonBrightnessDown": "F1",
    "XF86MonBrightnessUp": "F2",
    "XF86AudioPlay": "F3",
    "XF86AudioPause": "F3",
    "XF86AudioMute": "F4",
    "XF86AudioLowerVolume": "F5",
    "XF86AudioRaiseVolume": "F6",
    "Print": "F7",
    "Home": "F8",
    "End": "F9",
    "Page_Up": "F10",
    "Page_Down": "F11",
    "grave": "`",
    "BracketLeft": "[",
    "BracketRight": "]",
    "Comma": ",",
    "Period": ".",
    "Minus": "-",
    "Equal": "=",
    "Return": "Enter",
    "Escape": "Esc",
    "WheelScrollUp": "Scroll Up",
    "WheelScrollDown": "Scroll Down",
    "WheelScrollLeft": "Scroll Left",
    "WheelScrollRight": "Scroll Right",
}

_MOD_LABELS: dict[str, str] = {
    "Mod": "Super",
    "Ctrl": "Ctrl",
    "Alt": "Alt",
    "Shift": "Shift",
}

# Keys with no physical equivalent on the target keyboard are hidden entirely.
HIDDEN_KEYS: frozenset[str] = frozenset(
    {"XF86AudioPrev", "XF86AudioNext", "XF86AudioMicMute", "XF86Launch1"}
)

ACTION_LABELS: dict[str, str] = {
    'spawn "dms" "ipc" "call" "audio" "increment" "3"': "Volume Up",
    'spawn "dms" "ipc" "call" "audio" "decrement" "3"': "Volume Down",
    'spawn "dms" "ipc" "call" "audio" "mute"': "Mute",
    'spawn "dms" "ipc" "call" "audio" "micmute"': "Mute Microphone",
    'spawn "dms" "ipc" "call" "brightness" "increment" "5" ""': "Brightness Up",
    'spawn "dms" "ipc" "call" "brightness" "decrement" "5" ""': "Brightness Down",
    'spawn "dms" "ipc" "call" "clipboard" "toggle"': "Clipboard",
    'spawn "dms" "ipc" "call" "dash" "toggle" "wallpaper"': "Wallpapers",
    'spawn "dms" "ipc" "call" "lock" "lock"': "Lock Screen",
    'spawn "dms" "ipc" "call" "mpris" "increment" "3"': "Media Volume Up",
    'spawn "dms" "ipc" "call" "mpris" "decrement" "3"': "Media Volume Down",
    'spawn "dms" "ipc" "call" "mpris" "next"': "Next Track",
    'spawn "dms" "ipc" "call" "mpris" "previous"': "Previous Track",
    'spawn "dms" "ipc" "call" "mpris" "playPause"': "Play/Pause",
    'spawn "dms" "ipc" "call" "notepad" "toggle"': "Notepad",
    'spawn "dms" "ipc" "call" "notifications" "toggle"': "Notifications",
    'spawn "dms" "ipc" "call" "omivoidKeybinds" "toggle"': "Keybindings Cheat Sheet",
    'spawn "dms" "ipc" "call" "powermenu" "toggle"': "Power Menu",
    'spawn "dms" "ipc" "call" "processlist" "focusOrToggle"': "Task Manager",
    'spawn "dms" "ipc" "call" "settings" "focusOrToggle"': "Settings",
    'spawn "dms" "ipc" "call" "spotlight" "openQuery" "!!"': "Interaction Explorer",
    'spawn "dms" "ipc" "call" "spotlight" "openQuery" "!ai "': "AI Menu",
    'spawn "dms" "ipc" "call" "spotlight" "toggle"': "App Launcher",
    'spawn "dms" "ipc" "call" "spotlight-bar" "toggle"': "Spotlight Bar",
    'spawn "dms" "ipc" "call" "wallpaperCarousel" "toggle"': "Wallpaper Carousel",
    'spawn "dms" "ipc" "call" "window-rules" "toggle"': "Window Rules",
    'spawn "dms" "ipc" "call" "workspace-rename" "open"': "Rename Workspace",
    'spawn "dms" "ipc" "outputs" "cycleProfile"': "Cycle Display Profile",
    'spawn "dms" "screenshot"': "Screenshot: Region",
    'spawn "dms" "screenshot" "full"': "Screenshot: Full Screen",
    'spawn "dms" "screenshot" "window"': "Screenshot: Window",
    'spawn "ghostty"': "Terminal",
}

# Registry action IDs (chords, and omivoid-run spawns).
REGISTRY_ACTION_LABELS: dict[str, str] = {
    "app.browser.open": "Open Browser",
    "app.terminal.open": "Open Terminal",
    "ai.pi.open": "Open AI Prompt",
    "ai.ask": "Ask AI",
    "ai.clipboard.explain": "Explain Clipboard",
    "ai.clipboard.summarise": "Summarise Clipboard",
    "ai.menu.open": "AI Menu",
    "help.keys.open": "Interaction Explorer",
    "help.keybinds.open": "Keybindings Cheat Sheet",
    "help.actions.search": "App Launcher",
    "theme.wallpaper.select": "Wallpapers",
}

NATIVE_LABELS: dict[str, str] = {
    "close-window": "Close Window",
    "maximize-column": "Maximize Column",
    "fullscreen-window": "Toggle Fullscreen",
    "toggle-window-floating": "Toggle Floating",
    "switch-focus-between-floating-and-tiling": "Switch Floating/Tiling",
    "toggle-column-tabbed-display": "Toggle Tabbed Display",
    "focus-column-left": "Focus Column Left",
    "focus-column-right": "Focus Column Right",
    "focus-column-first": "Focus First Column",
    "focus-column-last": "Focus Last Column",
    "focus-window-up": "Focus Window Up",
    "focus-window-down": "Focus Window Down",
    "focus-workspace-down": "Focus Workspace Down",
    "focus-workspace-up": "Focus Workspace Up",
    "focus-monitor-left": "Focus Monitor Left",
    "focus-monitor-right": "Focus Monitor Right",
    "focus-monitor-up": "Focus Monitor Up",
    "focus-monitor-down": "Focus Monitor Down",
    "move-column-left": "Move Column Left",
    "move-column-right": "Move Column Right",
    "move-window-up": "Move Window Up",
    "move-window-down": "Move Window Down",
    "move-column-to-first": "Move Column to First",
    "move-column-to-last": "Move Column to Last",
    "move-column-to-workspace-down": "Move Column to Workspace Down",
    "move-column-to-workspace-up": "Move Column to Workspace Up",
    "move-workspace-down": "Move Workspace Down",
    "move-workspace-up": "Move Workspace Up",
    "move-column-to-monitor-left": "Move Column to Monitor Left",
    "move-column-to-monitor-right": "Move Column to Monitor Right",
    "move-column-to-monitor-up": "Move Column to Monitor Up",
    "move-column-to-monitor-down": "Move Column to Monitor Down",
    "consume-or-expel-window-left": "Consume/Expel Window Left",
    "consume-or-expel-window-right": "Consume/Expel Window Right",
    "expel-window-from-column": "Expel Window from Column",
    "center-column": "Center Column",
    "center-visible-columns": "Center Visible Columns",
    "expand-column-to-available-width": "Expand Column",
    "switch-preset-column-width": "Cycle Column Width",
    "switch-preset-window-height": "Cycle Window Height",
    "reset-window-height": "Reset Window Height",
    "power-off-monitors": "Power Off Monitors",
    "toggle-keyboard-shortcuts-inhibit": "Inhibit Shortcuts",
    "quit": "Quit",
    "show-hotkey-overlay": "Show Hotkeys",
    "toggle-overview": "Overview",
    'next-window scope="output"': "Next Window",
    'previous-window scope="output"': "Previous Window",
    'next-window filter="app-id"': "Next Window (Same App)",
    'previous-window filter="app-id"': "Previous Window (Same App)",
}


def _base_token(key: str) -> str:
    """Return the key without modifiers (first chord step)."""
    first = key.split(",")[0].strip()
    return first.split("+")[-1]


def key_label(key: str) -> str:
    """Render a normalised key combo as plain English."""
    parts = key.split("+")
    mods, base = parts[:-1], parts[-1]
    mod_labels = [_MOD_LABELS.get(m, m) for m in mods]
    base_label = ", ".join(
        KEY_LABELS.get(tok.strip(), tok.strip()) for tok in base.split(",")
    )
    return " + ".join(mod_labels + [base_label])


def action_label(action: str) -> str:
    """Render an action as plain English."""
    if action in ACTION_LABELS:
        return ACTION_LABELS[action]
    m = re.search(r'"action" "run" "([^"]+)"', action)
    if m:
        return REGISTRY_ACTION_LABELS.get(m.group(1), m.group(1))
    if action in REGISTRY_ACTION_LABELS:
        return REGISTRY_ACTION_LABELS[action]
    m = re.fullmatch(r"focus-workspace (\d+)", action)
    if m:
        return f"Switch to Workspace {m.group(1)}"
    m = re.fullmatch(r"move-column-to-workspace (\d+)", action)
    if m:
        return f"Move Column to Workspace {m.group(1)}"
    m = re.fullmatch(r'set-column-width "([+-]\d+)%"', action)
    if m:
        return (
            "Grow Column Width" if m.group(1).startswith("+") else "Shrink Column Width"
        )
    m = re.fullmatch(r'set-window-height "([+-]\d+)%"', action)
    if m:
        return (
            "Grow Window Height" if m.group(1).startswith("+") else "Shrink Window Height"
        )
    return NATIVE_LABELS.get(action, action)


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
        # Lock (Mod+Alt+L) is grouped under Desktop; no separate tab.
        return "Desktop"
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

    # Drop keys with no physical equivalent on the target keyboard, then add
    # plain-English labels (raw key/action are preserved).
    bindings = [b for b in bindings if _base_token(b["key"]) not in HIDDEN_KEYS]
    for b in bindings:
        b["key_label"] = key_label(b["key"])
        b["action_label"] = action_label(b["action"])

    # Collapse rows that render identically (e.g. XF86AudioPlay/Pause → F3).
    seen: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for b in bindings:
        sig = (b["key_label"], b["action_label"])
        if sig in seen:
            continue
        seen.add(sig)
        deduped.append(b)
    bindings = deduped

    def _sort_key(b: dict) -> tuple:
        idx = GKS_DOMAINS.index(b["domain"])
        if b["domain"] == "Hardware":
            m = re.search(r"F(\d+)", b["key_label"])
            return (idx, 0, int(m.group(1)) if m else 999, b["key_label"])
        return (idx, 1, 0, b["key"])

    bindings.sort(key=_sort_key)
    return {"domains": list(GKS_DOMAINS), "bindings": bindings}


def keybinds(registry=None, sources=None) -> dict:
    """Public entry point. Loads the registry when none is supplied."""
    if registry is None:
        from .registry import load_registry

        registry = load_registry()
    return collect(registry, sources)
