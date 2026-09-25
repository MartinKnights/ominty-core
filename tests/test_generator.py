"""Tests for the Niri fragment generator (docs/10 §13–14, docs/12 §16–17)."""

from pathlib import Path

from omivoidlib.generator import (
    DMS_CLAIMED_KEYS,
    OVERRIDE_KEYS,
    binding_to_kdl,
    build_fragment,
    dms_claimed_keys,
    generate_niri_fragment,
    is_chord,
    validate_fragment,
)
from omivoidlib.registry import Action, Registry


def make_registry() -> Registry:
    actions = [
        Action(
            id="window.close",
            name="Close window",
            description="Close the focused window",
            category="window",
            risk="low",
            confirmation="none",
            keywords=["close", "quit"],
            keys=["Super+Q"],
            primary_key="Super+Q",
            adapter="niri.native",
            arguments={"action": "close-window"},
            contexts=["window"],
            platforms=["niri"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="app.terminal.open",
            name="Open terminal",
            description="Open the terminal",
            category="app",
            risk="low",
            confirmation="none",
            keywords=["terminal", "console"],
            keys=["Super+Enter"],
            primary_key="Super+Enter",
            adapter="app.launch",
            arguments={"role": "terminal"},
            contexts=["desktop"],
            platforms=["all"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="help.keys.open",
            name="Show keybindings",
            description="Show the keybindings help",
            category="help",
            risk="low",
            confirmation="none",
            keywords=["help", "keys"],
            keys=["Super+K"],
            primary_key="Super+K",
            adapter="shell.explorer",
            arguments={"command": ["dms", "ipc", "call", "spotlight", "openQuery", "!!"]},
            contexts=["desktop"],
            platforms=["all"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="workspace.next",
            name="Next workspace",
            description="Switch to the next workspace",
            category="workspace",
            risk="low",
            confirmation="none",
            keywords=["next", "workspace"],
            keys=["Super+Page_Down"],
            primary_key="Super+Page_Down",
            adapter="niri.native",
            arguments={"action": "focus-workspace-down"},
            contexts=["desktop"],
            platforms=["niri"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="app.files.open",
            name="Open files",
            description="Open the file manager",
            category="app",
            risk="low",
            confirmation="none",
            keywords=["files", "manager"],
            keys=["Super+Shift+D"],
            primary_key="Super+Shift+D",
            adapter="app.launch",
            arguments={"role": "files"},
            contexts=["desktop"],
            platforms=["all"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="help.actions.search",
            name="Search actions",
            description="Search all actions",
            category="help",
            risk="low",
            confirmation="none",
            keywords=["search", "actions"],
            keys=["Super+Space"],
            primary_key="Super+Space",
            adapter="shell.palette",
            arguments={"command": ["dms", "ipc", "call", "spotlight", "toggle"]},
            contexts=["desktop"],
            platforms=["all"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="window.focus.left",
            name="Focus left",
            description="Focus the window to the left",
            category="window",
            risk="low",
            confirmation="none",
            keywords=["focus", "left"],
            keys=["Super+Left"],
            primary_key="Super+Left",
            adapter="niri.native",
            arguments={"action": "focus-column-left"},
            contexts=["window"],
            platforms=["niri"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="window.toggle-floating",
            name="Toggle floating",
            description="Toggle the floating state of the focused window",
            category="window",
            risk="low",
            confirmation="none",
            keywords=["floating", "toggle"],
            keys=["Super+Shift+Q"],
            primary_key="Super+Shift+Q",
            adapter="niri.native",
            arguments={"action": "toggle-window-floating"},
            contexts=["window"],
            platforms=["niri"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="theme.wallpaper.next",
            name="Next wallpaper",
            description="Cycle to the next wallpaper",
            category="theme",
            risk="low",
            confirmation="none",
            keywords=["wallpaper", "next"],
            keys=["Super+A,W"],
            primary_key="Super+A,W",
            adapter="theme.wallpaper",
            arguments={},
            contexts=["desktop"],
            platforms=["all"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
    ]
    return Registry(actions={a.id: a for a in actions})


def test_binding_to_kdl():
    assert binding_to_kdl("Super+Enter") == "Mod+Return"
    assert binding_to_kdl("Super+Shift+B") == "Mod+Shift+B"
    assert binding_to_kdl("Print") == "Print"
    assert binding_to_kdl("Shift+Print") == "Shift+Print"
    assert binding_to_kdl("Super+Space") == "Mod+space"


def test_is_chord():
    assert is_chord("Super+A,W")
    assert not is_chord("Super+Enter")


def test_generate_native_binding():
    fragment = generate_niri_fragment(make_registry(), "/opt/omivoid", claimed_keys=DMS_CLAIMED_KEYS)
    assert "Mod+Shift+Q {" in fragment
    assert "toggle-window-floating" in fragment
    assert "// window.toggle-floating" in fragment


def test_generate_app_launch_binding():
    fragment = generate_niri_fragment(make_registry(), "/opt/omivoid", claimed_keys=DMS_CLAIMED_KEYS)
    assert "Mod+Return {" in fragment
    assert 'spawn "/opt/omivoid" "action" "run" "app.terminal.open"' in fragment


def test_shell_adapters_with_command_generated():
    fragment = generate_niri_fragment(make_registry(), "/opt/omivoid", claimed_keys=DMS_CLAIMED_KEYS)
    # shell.explorer with a command argument generates a spawn.
    assert 'spawn "dms" "ipc" "call" "spotlight" "openQuery" "!!"' in fragment
    assert "Mod+K {" in fragment
    # Super+Space is claimed by DMS (spotlight) and must not be generated.
    assert "Mod+space {" not in fragment


def test_command_adapter_top_level_command_generated():
    """The `command` adapter declares a top-level command (Super+A AI menu)."""
    action = Action(
        id="ai.menu.open",
        name="AI Menu",
        description="Open the AI menu",
        category="AI",
        risk="routine",
        confirmation="never",
        keywords=["ai"],
        keys=["Super+A"],
        adapter="command",
        command=["dms", "ipc", "call", "spotlight", "openQuery", "!ai "],
        arguments={},
        contexts=["global"],
        platforms=["common"],
        discoverable=True,
        palette=True,
        ai_accessible=False,
        voice_accessible=False,
        source_file="test",
    )
    fragment = generate_niri_fragment(
        Registry(actions={action.id: action}),
        "/opt/omivoid",
        claimed_keys=DMS_CLAIMED_KEYS,
    )
    assert "Mod+A {" in fragment
    assert 'spawn "dms" "ipc" "call" "spotlight" "openQuery" "!ai "' in fragment


def test_dms_ipc_adapter_binding_generated():
    """A dms.ipc action with keys emits `dms ipc call <target> <function>`."""
    action = Action(
        id="theme.wallpaper.select",
        name="Select Wallpaper",
        description="Toggle the wallpaper carousel",
        category="Appearance",
        risk="state-change",
        confirmation="never",
        keywords=["wallpaper"],
        keys=["Super+Ctrl+P"],
        adapter="dms.ipc",
        arguments={"dms": {"target": "wallpaperCarousel", "function": "toggle"}},
        contexts=["global"],
        platforms=["common"],
        discoverable=True,
        palette=True,
        ai_accessible=True,
        voice_accessible=False,
        source_file="test",
    )
    fragment = generate_niri_fragment(
        Registry(actions={action.id: action}),
        "/opt/omivoid",
        claimed_keys=DMS_CLAIMED_KEYS,
    )
    assert "Mod+Ctrl+P {" in fragment
    assert 'spawn "dms" "ipc" "call" "wallpaperCarousel" "toggle"' in fragment
    assert "// theme.wallpaper.select" in fragment


def test_dms_claimed_keys_excluded():
    fragment = generate_niri_fragment(make_registry(), "/opt/omivoid", claimed_keys=DMS_CLAIMED_KEYS)
    # DMS owns these keys (dms-evaluation.md §4.2); the generator must not bind them.
    assert "Mod+Q {" not in fragment
    assert "Mod+space {" not in fragment
    assert "Mod+Page_Down {" not in fragment
    assert "Mod+Left {" not in fragment
    assert "XF86AudioRaiseVolume" not in fragment


def test_chords_not_generated():
    fragment = generate_niri_fragment(make_registry(), "/opt/omivoid", claimed_keys=DMS_CLAIMED_KEYS)
    assert "theme.wallpaper.next" not in fragment
    assert "Mod+A,W" not in fragment


def test_generated_header_present():
    fragment = generate_niri_fragment(make_registry(), "/opt/omivoid", claimed_keys=DMS_CLAIMED_KEYS)
    assert "Generated by Omivoid." in fragment
    assert "Source: Action Registry." in fragment
    assert "Do not edit directly." in fragment


def test_fragment_wrapped_in_binds():
    fragment = generate_niri_fragment(make_registry(), "/opt/omivoid", claimed_keys=DMS_CLAIMED_KEYS)
    assert fragment.startswith("// Generated by Omivoid.")
    assert "binds {" in fragment
    assert fragment.rstrip().endswith("}")


def test_build_fragment_dry_run_writes_nothing(tmp_path):
    ok, message = build_fragment(make_registry(), output=tmp_path / "x.kdl", dry_run=True)
    assert ok
    assert "Mod+Shift+Q" in message
    assert not (tmp_path / "x.kdl").exists()


def test_build_fragment_writes_and_validates(tmp_path, monkeypatch):
    # Fake niri validate so the test does not depend on the compositor.
    def fake_validate(path):
        return True, "config is valid"

    monkeypatch.setattr("omivoidlib.generator.validate_fragment", fake_validate)
    out = tmp_path / "bindings.kdl"
    ok, message = build_fragment(make_registry(), output=out)
    assert ok
    assert out.exists()
    assert "wrote" in message


def test_build_fragment_removes_invalid_output(tmp_path, monkeypatch):
    def fake_validate(path):
        return False, "syntax error"

    monkeypatch.setattr("omivoidlib.generator.validate_fragment", fake_validate)
    out = tmp_path / "bindings.kdl"
    ok, message = build_fragment(make_registry(), output=out)
    assert not ok
    assert not out.exists()
    assert "failed validation" in message


def test_validate_fragment_missing_niri(tmp_path, monkeypatch):
    def fake_run(*args, **kwargs):
        raise FileNotFoundError("niri")

    monkeypatch.setattr("omivoidlib.generator.subprocess.run", fake_run)
    ok, message = validate_fragment(tmp_path / "frag.kdl")
    assert not ok
    assert "niri is not available" in message


def test_dms_claimed_keys_from_live_file(tmp_path):
    binds = tmp_path / "binds.kdl"
    binds.write_text(
        "binds {\n"
        '    Mod+Space { spawn "dms" "ipc" "call" "spotlight" "toggle"; }\n'
        "    Mod+WheelScrollDown cooldown-ms=150 { focus-workspace-down; }\n"
        "}\n"
    )
    claimed = dms_claimed_keys(binds)
    assert "Mod+space" in claimed
    assert "Mod+WheelScrollDown" in claimed


def test_dms_claimed_keys_modifier_order_normalised(tmp_path):
    # DMS writes Mod+Ctrl+P; the generator must recognise it regardless of order.
    binds = tmp_path / "binds.kdl"
    binds.write_text("binds {\n    Mod+Ctrl+P { spawn \"dms\"; }\n}\n")
    assert "Ctrl+Mod+P" in dms_claimed_keys(binds)


def test_dms_claimed_keys_override_removed(tmp_path):
    binds = tmp_path / "binds.kdl"
    binds.write_text("binds {\n    Mod+K { focus-window-up; }\n}\n")
    assert binding_to_kdl("Mod+K") in OVERRIDE_KEYS
    assert "Mod+K" not in dms_claimed_keys(binds)


def test_dms_claimed_keys_fallback_missing(tmp_path):
    assert dms_claimed_keys(tmp_path / "missing.kdl") == DMS_CLAIMED_KEYS


def test_dms_claimed_keys_fallback_empty(tmp_path):
    binds = tmp_path / "binds.kdl"
    binds.write_text("// no binds here\n")
    assert dms_claimed_keys(binds) == DMS_CLAIMED_KEYS


def test_generate_respects_injected_claimed_keys():
    # Injecting a claim on an otherwise-free key excludes it from the fragment.
    claimed = frozenset({binding_to_kdl("Super+Shift+Q")})
    fragment = generate_niri_fragment(
        make_registry(), "/opt/omivoid", claimed_keys=claimed
    )
    assert "Mod+Shift+Q {" not in fragment
