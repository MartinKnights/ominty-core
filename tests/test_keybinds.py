"""GKS keybinding aggregation tests (docs/14-gks-keyboard-grammar.md)."""

from __future__ import annotations

from omivoidlib.keybinds import (
    UNIVERSAL_CONVENTIONS,
    classify_domain,
    collect,
    normalize_key,
    parse_kdl_binds,
    registry_bindings,
)
from omivoidlib.registry import Action, Registry


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
    assert classify_domain("Mod+Alt+L") == "Window state"
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
    data = collect(None, sources=[("Niri", niri), ("OmiVoid", gen)])
    winners = [b for b in data["bindings"] if b["key"] == "Mod+K" and not b["shadowed"]]
    assert len(winners) == 1
    assert winners[0]["source"] == "OmiVoid"


def test_universal_conventions_present():
    keys = {k for k, _ in UNIVERSAL_CONVENTIONS}
    assert "Ctrl+C" in keys and "Ctrl+S" in keys
