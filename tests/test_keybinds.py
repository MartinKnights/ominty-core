"""GKS keybinding aggregation tests (docs/14-gks-keyboard-grammar.md)."""

from __future__ import annotations

from omintylib.keybinds import (
    UNIVERSAL_CONVENTIONS,
    _collect_files,
    action_label,
    classify_domain,
    collect,
    key_label,
    normalize_key,
    parse_kdl_binds,
    registry_bindings,
)
from omintylib.registry import Action, Registry


def make_action(**overrides) -> Action:
    base = dict(
        id="ai.test", name="n", description="d", category="c", risk="routine",
        confirmation="never", keywords=[], keys=[], adapter=None, arguments={},
        command=None, contexts=["global"], platforms=["common"], requires=[],
        discoverable=True, palette=True, ai_accessible=False,
        voice_accessible=False,
    )
    base.update(overrides)
    return Action(**base)


def test_normalize_key():
    assert normalize_key("Super+Q") == "Mod+Q"
    assert normalize_key("Mod+Ctrl+C") == "Ctrl+Mod+C"
    assert normalize_key("Mod+Shift+Ctrl+Left") == "Ctrl+Mod+Shift+Left"
    assert normalize_key("Print") == "Print"


def test_classify_domain():
    assert classify_domain("Ctrl+S") == "Application"
    assert classify_domain("Alt+Left") == "Navigation"
    assert classify_domain("Mod+Left") == "Desktop"
    assert classify_domain("Mod+Shift+Left") == "Desktop"
    assert classify_domain("Mod+Alt+L") == "Desktop"
    assert classify_domain("Mod+Ctrl+N") == "Workspace topology"
    assert classify_domain("Ctrl+Alt+Delete") == "System"
    assert classify_domain("Mod+A") == "AI"
    assert classify_domain("Mod+A,E") == "AI"
    assert classify_domain("Print") == "Hardware"


def test_parse_kdl_binds():
    text = (
        'binds {\n'
        '    Mod+T { spawn "ghostty"; }\n'
        '    Mod+Ctrl+C { center-visible-columns; }\n'
        '}\n'
    )
    rows = parse_kdl_binds(text, "DMS")
    assert rows[0]["key"] == "Mod+T"
    assert rows[0]["action"] == 'spawn "ghostty"'
    assert rows[1]["key"] == "Ctrl+Mod+C"


def test_parse_kdl_binds_screenshot_domain():
    text = 'binds {\n    Alt+Print { spawn "dms" "screenshot" "window"; }\n}\n'
    rows = parse_kdl_binds(text, "DMS")
    assert rows[0]["domain"] == "Hardware"


def test_registry_bindings_chords():
    reg = Registry(actions={"ai.ask": make_action(id="ai.ask", keys=["Super+A,A"])})
    rows = registry_bindings(reg)
    assert rows[0]["key"] == "Mod+A,A"
    assert rows[0]["domain"] == "AI"


def test_collect_merges_and_tags(tmp_path):
    niri = tmp_path / "config.kdl"
    niri.write_text('binds {\n    Mod+Q { close-window; }\n}\n')
    dms = tmp_path / "binds.kdl"
    dms.write_text('binds {\n    Mod+T { spawn "ghostty"; }\n}\n')
    reg = Registry(actions={"ai.ask": make_action(id="ai.ask", keys=["Super+A,A"])})

    data = collect(reg, sources=[("Niri", niri), ("DMS", dms)])
    keys = {b["key"]: b for b in data["bindings"]}
    assert keys["Mod+Q"]["source"] == "Niri"
    assert keys["Mod+T"]["source"] == "DMS"
    assert keys["Mod+A,A"]["domain"] == "AI"
    assert keys["Ctrl+S"]["source"] == "Universal"
    assert len(keys["Ctrl+S"]["action"]) > 0


def test_collect_marks_shadowed(tmp_path):
    niri = tmp_path / "config.kdl"
    niri.write_text('binds {\n    Mod+K { focus-window-up; }\n}\n')
    gen = tmp_path / "gen.kdl"
    gen.write_text(
        'binds {\n    Mod+K { spawn "dms" "ipc" "call" "spotlight" "openQuery" "!!"; }\n}\n'
    )
    data = collect(None, sources=[("Niri", niri), ("Ominty", gen)])
    winners = [b for b in data["bindings"] if b["key"] == "Mod+K" and not b["shadowed"]]
    assert len(winners) == 1
    assert winners[0]["source"] == "Ominty"


def test_universal_conventions_present():
    keys = {k for k, _ in UNIVERSAL_CONVENTIONS}
    assert "Ctrl+C" in keys and "Ctrl+S" in keys


def test_key_labels():
    assert key_label("Mod+Q") == "Super + Q"
    # No function-key map → hardware tokens stay neutral (machine-independent).
    assert key_label("XF86MonBrightnessUp") == "XF86MonBrightnessUp"
    assert key_label("Mod+Home") == "Super + Home"
    assert key_label("Mod+BracketLeft") == "Super + ["
    assert key_label("Mod+A,A") == "Super + A, A"
    assert (
        key_label("Ctrl+Mod+Shift+WheelScrollDown")
        == "Ctrl + Super + Shift + Scroll Down"
    )


def test_key_label_with_function_map():
    fk = {"XF86MonBrightnessUp": {"physical": "F2", "fn": True}}
    assert key_label("XF86MonBrightnessUp", fk) == "Fn+F2"
    fk5 = {"XF86AudioLowerVolume": {"physical": "F5", "fn": True}}
    assert key_label("Mod+XF86AudioLowerVolume", fk5) == "Super + Fn+F5"
    fk_plain = {"F5": {"physical": "F5", "fn": False}}
    assert key_label("F5", fk_plain) == "F5"


def test_action_labels():
    assert (
        action_label('spawn "dms" "ipc" "call" "workspace-rename" "open"')
        == "Rename Workspace"
    )
    assert (
        action_label('spawn "dms" "ipc" "call" "mpris" "decrement" "3"')
        == "Media Volume Down"
    )
    assert action_label("close-window") == "Close Window"
    assert action_label("focus-workspace 3") == "Switch to Workspace 3"
    assert action_label("ai.ask") == "Ask AI"
    assert action_label("something-unknown") == "something-unknown"


def test_collect_hides_absent_keys_and_adds_labels(tmp_path):
    niri = tmp_path / "config.kdl"
    niri.write_text(
        "binds {\n"
        "    Mod+Q { close-window; }\n"
        '    XF86AudioPrev { spawn "dms" "ipc" "call" "mpris" "previous"; }\n'
        "}\n"
    )
    data = collect(None, sources=[("Niri", niri)])
    keys = {b["key"] for b in data["bindings"]}
    assert "Mod+Q" in keys
    assert "XF86AudioPrev" not in keys
    row = next(b for b in data["bindings"] if b["key"] == "Mod+Q")
    assert row["key_label"] == "Super + Q"
    assert row["action_label"] == "Close Window"


def test_collect_include_walk(tmp_path):
    """Bindings inside included fragments are captured and tagged correctly."""
    cfg = tmp_path / "niri"
    (cfg / "frag").mkdir(parents=True)
    (cfg / "dms").mkdir()
    (cfg / "config.kdl").write_text(
        'include "frag/a.kdl" optional=true\n'
        'include "dms/binds.kdl"\n'
        "binds {\n    Mod+Q { close-window; }\n}\n"
    )
    (cfg / "frag" / "a.kdl").write_text("binds {\n    Mod+W { close-window; }\n}\n")
    (cfg / "dms" / "binds.kdl").write_text(
        'binds {\n    Mod+T { spawn "ghostty"; }\n}\n'
    )

    data = collect(None, sources=_collect_files(tmp_path))
    by_action = {b["action"]: b for b in data["bindings"]}
    assert by_action["close-window"]["key"] == "Mod+W"
    assert by_action["close-window"]["source"] == "Niri"
    assert by_action["close-window"]["managed_by"] == "niri"
    assert by_action['spawn "ghostty"']['source'] == "DMS"
    assert by_action['spawn "ghostty"']['managed_by'] == "dms-settings"


def test_include_walk_skips_missing_optional(tmp_path):
    (tmp_path / "niri").mkdir()
    (tmp_path / "niri" / "config.kdl").write_text(
        'include "missing.kdl" optional=true\nbinds {\n    Mod+Q { close-window; }\n}\n'
    )
    files = _collect_files(tmp_path)
    assert {p for _, p in files} == {(tmp_path / "niri" / "config.kdl").resolve()}


def test_function_key_rows_in_collect(tmp_path):
    niri = tmp_path / "config.kdl"
    niri.write_text(
        "binds {\n"
        '    XF86AudioLowerVolume { spawn "dms" "ipc" "call" "audio" "decrement" "3"; }\n'
        "}\n"
    )
    fk = {
        "F1": {"label": "first", "keysyms": ["F1"]},
        "F5": {"label": "volume down", "keysyms": ["F5"]},
        "F5_fn": {"label": "media volume down", "keysyms": ["XF86AudioLowerVolume"]},
    }
    data = collect(None, sources=[("Niri", niri)], function_keys=fk)
    hw = [b for b in data["bindings"] if b["domain"] == "Hardware"]
    labels = {b["key_label"]: b for b in hw}
    assert "Fn+F5" in labels
    assert labels["Fn+F5"]["action_label"] == "media volume down"
    assert labels["Fn+F5"]["managed_by"] == "function-keys"
    # The media binding renders its physical key, so both collapse to one row.
    assert "F5" in labels
    assert labels["F5"]["action_label"] == "volume down"


def test_custom_diff_remap_and_add(tmp_path):
    base = tmp_path / "niri"
    (base / "dms").mkdir(parents=True)
    (base / "config.kdl").write_text('binds {\n    Mod+T { spawn "ghostty"; }\n}\n')
    live = tmp_path / "live"
    live.mkdir()
    (live / "a.kdl").write_text('binds {\n    Mod+X { spawn "ghostty"; }\n}\n')
    (live / "b.kdl").write_text(
        'binds {\n    Mod+Y { spawn "/home/user/bin/mytool"; }\n}\n'
    )

    data = collect(
        None,
        sources=[("Niri", live / "a.kdl"), ("Niri", live / "b.kdl")],
        baseline_dir=base,
    )
    rows = {b["action"]: b for b in data["bindings"]}
    remapped = rows['spawn "ghostty"']
    assert remapped["custom"] is True and remapped["change"] == "remapped"
    added = rows['spawn "/home/user/bin/mytool"']
    assert added["custom"] is True and added["change"] == "added"
    # Universal rows are never custom.
    uni = [b for b in data["bindings"] if b["source"] == "Universal"][0]
    assert uni["custom"] is False and uni["change"] == "unchanged"
