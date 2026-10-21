"""User-defined function-row key map (docs/14-gks-keyboard-grammar.md §22).

Physical keyboards differ wildly in what their F-row does, especially with
and without the ``Fn`` key.  Instead of baking one laptop's layout into the
cheat-sheet labels, the user defines their own map — 24 entries (F1–F12
without Fn, F1–F12 with Fn) — in ``~/.config/ominty/function-keys.toml``::

    [function_keys]
    F1   = { label = "refresh",   keysyms = ["F1"] }
    F1_fn = { label = "brightness down", keysyms = ["XF86MonBrightnessDown"] }

The cheat sheet then renders the physical key (``F5`` / ``Fn+F5``) for any
binding whose keysym matches an entry, and shows the 24 labelled entries
itself in the Hardware tab.  A missing or empty map is fine — hardware keys
then fall back to their raw token.
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path

from .registry import user_config_dir

# Ordered set of the 24 user-defined keys.
FK_PLAIN: tuple[str, ...] = tuple(f"F{i}" for i in range(1, 13))
FK_NAMES: tuple[str, ...] = tuple(
    sum(([plain, f"{plain}_fn"] for plain in FK_PLAIN), [])
)

# Sensible default keysyms for the Fn layer (very common laptop layout).
# The user is expected to edit these for their own keyboard.
FN_LAYER_DEFAULTS: dict[str, list[str]] = {
    "F1": ["F1"],
    "F2": ["F2"],
    "F3": ["F3"],
    "F4": ["F4"],
    "F5": ["F5"],
    "F6": ["F6"],
    "F7": ["F7"],
    "F8": ["F8"],
    "F9": ["F9"],
    "F10": ["F10"],
    "F11": ["F11"],
    "F12": ["F12"],
    "F1_fn": ["XF86MonBrightnessDown"],
    "F2_fn": ["XF86MonBrightnessUp"],
    "F3_fn": ["XF86AudioPlay", "XF86AudioPause"],
    "F4_fn": ["XF86AudioMute"],
    "F5_fn": ["XF86AudioLowerVolume"],
    "F6_fn": ["XF86AudioRaiseVolume"],
    "F7_fn": ["Print"],
    "F8_fn": [],
    "F9_fn": ["Home"],
    "F10_fn": ["End"],
    "F11_fn": ["Page_Up"],
    "F12_fn": [],
}


def default_keysyms(name: str) -> list[str]:
    """Default keysyms for a function-key entry."""
    return list(FN_LAYER_DEFAULTS.get(name, []))


def physical_name(name: str) -> str:
    """``F1`` → ``"F1"``, ``F1_fn`` → ``"Fn+F1"``."""
    if name.endswith("_fn"):
        return f"Fn+{name[:-3]}"
    return name


def config_path() -> Path:
    """``~/.config/ominty/function-keys.toml``."""
    return user_config_dir() / "function-keys.toml"


def load_function_keys(path: Path | None = None) -> dict[str, dict]:
    """Load the user's function-key map, merged over the defaults.

    The returned dict maps every ``F1``…``F12_fn`` entry to
    ``{"label": str, "keysyms": [str, ...]}``; entries missing from the file
    keep their default keysyms and an empty label.  A missing or unreadable
    file yields the default map.
    """
    import tomllib

    data = {name: {"label": "", "keysyms": default_keysyms(name)} for name in FK_NAMES}
    path = Path(path) if path else config_path()
    if not path.is_file():
        return data
    try:
        with open(path, "rb") as f:
            raw = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError):
        return data
    for name, entry in raw.get("function_keys", {}).items():
        if name not in data or not isinstance(entry, dict):
            continue
        label = str(entry.get("label", "") or "")
        keysyms = [str(k) for k in entry.get("keysyms", []) or default_keysyms(name)]
        data[name] = {"label": label, "keysyms": keysyms}
    return data


def physical_map(data: dict[str, dict]) -> dict[str, dict]:
    """Invert the 24 entries into ``keysym → {"physical": str, "fn": bool}``."""
    out: dict[str, dict] = {}
    for name, entry in data.items():
        fn = name.endswith("_fn")
        phys = name[:-3] if fn else name
        for ks in entry.get("keysyms", []) or []:
            if ks:
                out[ks] = {"physical": phys, "fn": fn}
    return out


def rows(data: dict[str, dict]) -> list[dict]:
    """Cheat-sheet rows for every labelled function key (Hardware tab).

    Only entries with a non-empty label are shown — the sheet is noisier
    than useful otherwise.  ``Fn+`` rows sort next to their plain partner
    (both carry the same ``F(\\d+)`` sort token).
    """
    out: list[dict] = []
    for name in FK_NAMES:
        entry = data.get(name) or {}
        label = str(entry.get("label", "") or "").strip()
        if not label:
            continue
        phys = physical_name(name)
        out.append(
            {
                "key": phys,
                "domain": "Hardware",
                "action": label,
                "source": "Function keys",
                "managed_by": "function-keys",
                "shadowed": False,
                "custom": False,
                "change": "unchanged",
                "key_label": phys,
                "action_label": label,
                "fn": name.endswith("_fn"),
            }
        )
    return out


def _toml_str(value: str) -> str:
    """Minimal TOML basic-string quoting (no multi-line/newlines expected)."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def template() -> str:
    """A commented, fully-populated default template for the user to edit."""
    lines = [
        "# ominty function-keys.toml — what each physical F-key does on this keyboard.",
        "#",
        "# The cheat sheet renders bindings as the physical key (F5 / Fn+F5) and",
        "# lists these definitions in its Hardware tab. Fill in `label` for the",
        "# keys that exist on YOUR keyboard; leave the rest blank. `keysyms` are",
        "# the logical key names that key sends when pressed — edit them if your",
        "# keyboard differs from the defaults (you can find names with `niri msg`,",
        "# or leave them and use the setup wizard, which guesses for you).",
        "",
        "[function_keys]",
    ]
    for name in FK_NAMES:
        ks = default_keysyms(name)
        ks_str = ", ".join(_toml_str(k) for k in ks) or "[]"
        label = ""
        lines.append(f"{name} = {{ label = {_toml_str(label)}, keysyms = [{ks_str}] }}")
    lines += ["", "# Run `ominty function-keys setup` to fill this in interactively."]
    return "\n".join(lines) + "\n"


def save_function_keys(
    data: dict[str, dict], path: Path | None = None
) -> Path:
    """Write the map as TOML, backing up any existing file (.bak-ominty-*)."""
    path = Path(path) if path else config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = path.with_name(f"{path.name}.bak-ominty-{stamp}")
        backup.write_text(path.read_text())
    lines = [
        "# ominty function-keys.toml — what each physical F-key does on this keyboard.",
        "# Generated by `ominty function-keys setup`; edit freely and re-run setup.",
        "",
        "[function_keys]",
    ]
    for name in FK_NAMES:
        entry = data.get(name) or {}
        label = str(entry.get("label", "") or "")
        ks = entry.get("keysyms") or default_keysyms(name)
        ks_str = ", ".join(_toml_str(str(k)) for k in ks) or "[]"
        lines.append(f"{name} = {{ label = {_toml_str(label)}, keysyms = [{ks_str}] }}")
    path.write_text("\n".join(lines) + "\n")
    return path


def display(data: dict[str, dict]) -> str:
    """Human-readable rendering of the current map (for `ominty function-keys`)."""
    lines: list[str] = []
    for name in FK_NAMES:
        entry = data.get(name) or {}
        label = str(entry.get("label", "") or "").strip()
        ks = ", ".join(entry.get("keysyms", []) or [])
        if label:
            lines.append(f"  {physical_name(name):<8} {label:<24} ({ks})")
        else:
            lines.append(f"  {physical_name(name):<8} (unset)              ({ks})")
    return "\n".join(lines)


def interactive_setup(path: Path | None = None) -> dict:
    """Walk F1→F12 (plain and Fn layer) and let the user label each key.

    Blank input skips an entry; Ctrl+C aborts without saving.  Returns the
    updated data dict (and saves when at least one label was entered).
    """
    import sys

    current = load_function_keys(path)
    print("Function-key setup — label what each physical key does on your")
    print("keyboard. Blank = skip. Ctrl+C = abort without saving.\n")
    try:
        for name in FK_NAMES:
            entry = current.get(name) or {}
            ks_hint = ", ".join(entry.get("keysyms", []) or []) or "(none)"
            print(f"  {physical_name(name):<8} sends: {ks_hint}")
            try:
                label = input("       what does it do? ").strip()
            except EOFError:
                break
            if label:
                current[name] = {"label": label, "keysyms": entry.get("keysyms") or default_keysyms(name)}
    except KeyboardInterrupt:
        print("\nAborted — nothing saved.")
        raise SystemExit(1)
    print()
    entered = sum(1 for e in current.values() if (e.get("label") or "").strip())
    if entered == 0:
        print("Nothing entered — no changes.")
        return current
    target = save_function_keys(current, path)
    print(f"Saved {entered} label(s) to {target} (old file backed up).")
    return current


def _keyed_sort(r: dict) -> tuple:
    m = re.search(r"F(\d+)", r["key_label"])
    return (int(m.group(1)) if m else 999, r.get("fn", False))