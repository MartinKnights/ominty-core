"""Runner and adapter tests — docs/11 §7–8, §17–18.

Covers:
- action lookup (ACTION_NOT_FOUND)
- platform check (PLATFORM_UNSUPPORTED)
- missing implementation (ACTION_UNAVAILABLE)
- missing requirements (DEPENDENCY_MISSING)
- app.launch role resolution (valid, missing role, missing app, missing binary)
- command adapter
- niri.native adapter (invalid argument)
- structured error codes
"""

from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest

from omivoidlib.registry import Action, Registry, load_registry
from omivoidlib.runner import run_action


def make_action(**overrides) -> Action:
    base = dict(
        id="app.test.open",
        name="Test",
        description="d",
        category="c",
        risk="routine",
        confirmation="never",
        keywords=[],
        keys=[],
        adapter=None,
        arguments={},
        command=None,
        contexts=["global"],
        platforms=["common"],
        requires=[],
        discoverable=True,
        palette=True,
        ai_accessible=False,
        voice_accessible=False,
    )
    base.update(overrides)
    return Action(**base)


def registry_with(*actions: Action) -> Registry:
    reg = Registry()
    for a in actions:
        reg.actions[a.id] = a
    return reg


# ── Lookup ─────────────────────────────────────────────────────────────────

def test_action_not_found():
    result = run_action("app.missing.open", registry_with())
    assert result["success"] is False
    assert result["error"]["code"] == "ACTION_NOT_FOUND"


def test_platform_unsupported():
    action = make_action(platforms=["void"])
    with patch("omivoidlib.runner.detect_platform", return_value="debian"):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "PLATFORM_UNSUPPORTED"


def test_no_implementation():
    action = make_action(adapter=None, command=None)
    result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "ACTION_UNAVAILABLE"


def test_missing_requirement():
    action = make_action(adapter="command", command=["true"], requires=["matugen"])
    with patch("omivoidlib.runner._requirement_available", return_value=False):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "DEPENDENCY_MISSING"


def test_unavailable_adapter():
    action = make_action(adapter="does.not.exist")
    result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "ACTION_UNAVAILABLE"


# ── app.launch ─────────────────────────────────────────────────────────────

def test_app_launch_missing_role():
    action = make_action(adapter="app.launch", arguments={})
    result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "INVALID_ARGUMENT"


def test_app_launch_no_configured_app():
    action = make_action(adapter="app.launch", arguments={"role": "browser"})
    with patch("omivoidlib.config.load_apps_config", return_value={}):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "ACTION_UNAVAILABLE"


def test_app_launch_binary_missing():
    action = make_action(adapter="app.launch", arguments={"role": "browser"})
    with patch("omivoidlib.config.load_apps_config", return_value={"browser": "no-such-browser-xyz"}):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "DEPENDENCY_MISSING"


def test_app_launch_success():
    action = make_action(adapter="app.launch", arguments={"role": "browser"})
    with patch("omivoidlib.config.load_apps_config", return_value={"browser": "true"}):
        with patch("subprocess.Popen") as popen:
            result = run_action(action.id, registry_with(action))
    assert result["success"] is True
    assert result["state"] == {"role": "browser", "app": "true"}
    popen.assert_called_once()


# ── command adapter ────────────────────────────────────────────────────────

def test_command_adapter_success():
    action = make_action(adapter="command", command=["true"])
    with patch("subprocess.Popen") as popen:
        result = run_action(action.id, registry_with(action))
    assert result["success"] is True
    popen.assert_called_once_with(
        ["true"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def test_command_adapter_empty_command():
    action = make_action(adapter="command", command=[])
    result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "INVALID_ARGUMENT"


# ── niri.native ────────────────────────────────────────────────────────────

def test_niri_native_missing_action_arg():
    action = make_action(adapter="niri.native", arguments={})
    result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "INVALID_ARGUMENT"


def test_niri_native_success():
    action = make_action(adapter="niri.native", arguments={"action": "close-window"})
    with patch("subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stderr = ""
        result = run_action(action.id, registry_with(action))
    assert result["success"] is True
    assert result["state"] == {"niri_action": "close-window"}


def test_niri_native_failure():
    action = make_action(adapter="niri.native", arguments={"action": "close-window"})
    with patch("subprocess.run") as run:
        run.return_value.returncode = 1
        run.return_value.stderr = "niri: no compositor running"
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "ADAPTER_FAILED"


# ── dms.ipc ────────────────────────────────────────────────────────────────

def test_dms_ipc_missing_argument():
    action = make_action(adapter="dms.ipc", arguments={})
    result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "INVALID_ARGUMENT"


def test_dms_ipc_success():
    action = make_action(
        adapter="dms.ipc",
        arguments={"dms": {"target": "audio", "function": "increment", "args": ["3"]}},
    )
    with patch("subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stdout = "85%"
        run.return_value.stderr = ""
        result = run_action(action.id, registry_with(action))
    assert result["success"] is True
    assert result["state"]["dms"] == {"target": "audio", "function": "increment"}
    run.assert_called_once_with(
        ["dms", "ipc", "call", "audio", "increment", "3"],
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_dms_ipc_failure():
    action = make_action(
        adapter="dms.ipc",
        arguments={"dms": {"target": "audio", "function": "increment"}},
    )
    with patch("subprocess.run") as run:
        run.return_value.returncode = 1
        run.return_value.stdout = ""
        run.return_value.stderr = "dms: no service running"
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "ADAPTER_FAILED"


def test_dms_ipc_dependency_missing():
    action = make_action(
        adapter="dms.ipc",
        arguments={"dms": {"target": "audio", "function": "increment"}},
    )
    with patch("subprocess.run", side_effect=FileNotFoundError("dms")):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "DEPENDENCY_MISSING"


# ── shell.explorer ─────────────────────────────────────────────────────────

def test_shell_explorer_missing_command():
    action = make_action(adapter="shell.explorer", arguments={})
    result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "INVALID_ARGUMENT"


def test_shell_explorer_success():
    action = make_action(
        adapter="shell.explorer",
        arguments={"command": ["dms", "ipc", "call", "spotlight", "openQuery", "!!"]},
    )
    with patch("shutil.which", return_value="/usr/bin/dms"), \
         patch("subprocess.Popen") as popen:
        result = run_action(action.id, registry_with(action))
    assert result["success"] is True
    assert result["state"]["command"] == [
        "dms", "ipc", "call", "spotlight", "openQuery", "!!",
    ]
    popen.assert_called_once_with(
        ["dms", "ipc", "call", "spotlight", "openQuery", "!!"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def test_shell_explorer_dependency_missing():
    action = make_action(
        adapter="shell.explorer",
        arguments={"command": ["dms", "ipc", "call", "spotlight", "openQuery", "!!"]},
    )
    with patch("shutil.which", return_value=None):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "DEPENDENCY_MISSING"