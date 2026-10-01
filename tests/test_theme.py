"""Theme action tests — carousel wallpaper actions + palette regeneration.

Covers:
- the DMS Wallpaper Carousel wallpaper actions (dms.ipc)
- the dms.theme regeneration adapter (success, dependency, context, failure)
- registry integration for the Appearance actions

Phase 1 #15 (docs/08 §27, docs/13 §15).
"""

from __future__ import annotations

import subprocess
from unittest.mock import patch

from omintylib.adapters import load_adapter
from omintylib.registry import load_registry
from omintylib.runner import run_action


def _load_theme_adapter():
    return load_adapter("dms.theme")


def _fake_dms(wallpaper: str, mode: str = "light",
              generate_rc: int = 0, generate_err: str = ""):
    """Build a fake `_run` for the dms.theme adapter."""
    def fake_run(command, timeout):
        if command[:5] == ["dms", "ipc", "call", "wallpaper", "get"]:
            return (0, wallpaper, "")
        if command[:5] == ["dms", "ipc", "call", "theme", "getMode"]:
            return (0, mode, "")
        if command[:3] == ["dms", "matugen", "generate"]:
            return (generate_rc, "Done" if generate_rc == 0 else "", generate_err)
        return (1, "", f"unexpected command: {command}")
    return fake_run


# ── dms.theme adapter ──────────────────────────────────────────────────

def test_dms_theme_regenerate_success():
    mod = _load_theme_adapter()
    calls = []

    def fake_run(command, timeout):
        calls.append(command)
        return _fake_dms(
            "/tmp/wallpapers/Dune.jpg", "light"
        )(command, timeout)

    with (
        patch("shutil.which", return_value="/usr/bin/dms"),
        patch.object(mod, "_run", side_effect=fake_run),
    ):
        result = mod.run(None, {"theme": {"action": "regenerate"}})

    assert result["success"] is True
    assert result["state"]["mode"] == "light"
    assert result["state"]["value"].endswith("Dune.jpg")

    gen = calls[-1]
    assert gen[:3] == ["dms", "matugen", "generate"]
    assert gen[gen.index("--value") + 1] == "/tmp/wallpapers/Dune.jpg"
    assert gen[gen.index("--kind") + 1] == "image"
    assert gen[gen.index("--mode") + 1] == "light"
    for flag in ("--state-dir", "--shell-dir", "--config-dir"):
        assert flag in gen


def test_dms_theme_invalid_action():
    mod = _load_theme_adapter()
    result = mod.run(None, {})
    assert result["success"] is False
    assert result["error"]["code"] == "INVALID_ARGUMENT"


def test_dms_theme_missing_dms():
    mod = _load_theme_adapter()
    with patch("shutil.which", return_value=None):
        result = mod.run(None, {"theme": {"action": "regenerate"}})
    assert result["success"] is False
    assert result["error"]["code"] == "DEPENDENCY_MISSING"


def test_dms_theme_no_wallpaper():
    mod = _load_theme_adapter()
    with (
        patch("shutil.which", return_value="/usr/bin/dms"),
        patch.object(mod, "_run", side_effect=_fake_dms("")),
    ):
        result = mod.run(None, {"theme": {"action": "regenerate"}})
    assert result["success"] is False
    assert result["error"]["code"] == "CONTEXT_UNAVAILABLE"


def test_dms_theme_generate_failure():
    mod = _load_theme_adapter()
    with (
        patch("shutil.which", return_value="/usr/bin/dms"),
        patch.object(
            mod, "_run",
            side_effect=_fake_dms("/wp.jpg", generate_rc=1, generate_err="boom"),
        ),
    ):
        result = mod.run(None, {"theme": {"action": "regenerate"}})
    assert result["success"] is False
    assert result["error"]["code"] == "ADAPTER_FAILED"
    assert "boom" in result["error"]["message"]


def test_dms_theme_no_change_is_success():
    """A benign no-op (exit 2, 'No color changes detected') is success."""
    mod = _load_theme_adapter()
    with (
        patch("shutil.which", return_value="/usr/bin/dms"),
        patch.object(
            mod, "_run",
            side_effect=_fake_dms(
                "/wp.jpg", generate_rc=2,
                generate_err="INFO  go: No color changes detected, skipping refresh",
            ),
        ),
    ):
        result = mod.run(None, {"theme": {"action": "regenerate"}})
    assert result["success"] is True
    assert result["state"]["action"] == "regenerate"


def test_dms_theme_hex_wallpaper():
    mod = _load_theme_adapter()
    calls = []

    def fake_run(command, timeout):
        calls.append(command)
        return _fake_dms("#1e1e2e")(command, timeout)

    with (
        patch("shutil.which", return_value="/usr/bin/dms"),
        patch.object(mod, "_run", side_effect=fake_run),
    ):
        result = mod.run(None, {"theme": {"action": "regenerate"}})
    assert result["success"] is True
    gen = calls[-1]
    assert gen[gen.index("--kind") + 1] == "hex"


def test_dms_theme_mode_falls_back_to_dark():
    mod = _load_theme_adapter()
    with (
        patch("shutil.which", return_value="/usr/bin/dms"),
        patch.object(mod, "_run", side_effect=_fake_dms("/wp.jpg", mode="weird")),
    ):
        result = mod.run(None, {"theme": {"action": "regenerate"}})
    assert result["success"] is True
    assert result["state"]["mode"] == "dark"


# ── Carousel wallpaper actions ─────────────────────────────────────────

def test_wallpaper_select_invokes_carousel():
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "", "")

    with (
        patch("shutil.which", return_value="/usr/bin/dms"),
        patch("subprocess.run", side_effect=fake_run),
    ):
        result = run_action("theme.wallpaper.select")

    assert result["success"] is True
    assert captured["command"] == [
        "dms", "ipc", "call", "wallpaperCarousel", "toggle"
    ]


# ── Registry integration ───────────────────────────────────────────────

def test_theme_actions_in_real_registry():
    registry = load_registry()

    select = registry.actions["theme.wallpaper.select"]
    assert select.adapter == "dms.ipc"
    assert select.arguments["dms"] == {
        "target": "wallpaperCarousel", "function": "toggle"
    }
    assert select.keys == ["Super+Ctrl+P"]

    nxt = registry.actions["theme.wallpaper.next"]
    assert nxt.arguments["dms"]["function"] == "cycleNext"

    prev = registry.actions["theme.wallpaper.previous"]
    assert prev.arguments["dms"]["function"] == "cyclePrevious"

    regen = registry.actions["theme.palette.regenerate"]
    assert regen.adapter == "dms.theme"
    assert regen.arguments["theme"]["action"] == "regenerate"

    mode = registry.actions["theme.mode.toggle"]
    assert mode.arguments["dms"] == {"target": "theme", "function": "toggle"}
