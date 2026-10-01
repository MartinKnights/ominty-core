"""Tests for the platform-resolved `service.restart` adapter (docs/05)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from omintylib.adapters import load_adapter, resolve_adapter_path

REPO = Path(__file__).resolve().parents[1]
DEBIAN = REPO / "adapters" / "debian" / "service_restart.py"
VOID = REPO / "adapters" / "void" / "service_restart.py"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"svc_{path.stem}_{path.parent.name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Result:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


# ── Debian / systemd ──────────────────────────────────────────────────────


def test_debian_builds_user_and_system_commands():
    m = _load(DEBIAN)
    assert m.build_command({"scope": "user", "units": ["a", "b"]}) == [
        "systemctl",
        "--user",
        "restart",
        "a",
        "b",
    ]
    assert m.build_command({"scope": "system", "units": ["c"]}) == [
        "systemctl",
        "restart",
        "c",
    ]
    # user is the default scope
    assert m.build_command({"units": ["d"]}) == [
        "systemctl",
        "--user",
        "restart",
        "d",
    ]


def test_debian_invalid_arguments():
    m = _load(DEBIAN)
    assert m.build_command({})["error"]["code"] == "INVALID_ARGUMENT"
    assert m.build_command({"units": "x"})["error"]["code"] == "INVALID_ARGUMENT"
    assert (
        m.build_command({"units": ["a"], "scope": "bogus"})["error"]["code"]
        == "INVALID_ARGUMENT"
    )


def test_debian_run_success(monkeypatch):
    m = _load(DEBIAN)
    captured = {}

    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        return _Result(0, stdout="ok")

    monkeypatch.setattr(m.subprocess, "run", fake_run)
    res = m.run(None, {"scope": "user", "units": ["wireplumber", "pipewire"]})
    assert res["success"]
    assert captured["cmd"] == [
        "systemctl",
        "--user",
        "restart",
        "wireplumber",
        "pipewire",
    ]


def test_debian_dependency_missing(monkeypatch):
    m = _load(DEBIAN)

    def fake_run(cmd, **kw):
        raise FileNotFoundError("systemctl")

    monkeypatch.setattr(m.subprocess, "run", fake_run)
    res = m.run(None, {"units": ["a"]})
    assert not res["success"]
    assert res["error"]["code"] == "DEPENDENCY_MISSING"


def test_debian_failure_surfaces_stderr(monkeypatch):
    m = _load(DEBIAN)
    monkeypatch.setattr(m.subprocess, "run", lambda *a, **k: _Result(1, stderr="boom"))
    res = m.run(None, {"units": ["a"]})
    assert not res["success"]
    assert res["error"]["code"] == "ADAPTER_FAILED"
    assert "boom" in res["error"]["message"]


# ── Void / runit ──────────────────────────────────────────────────────────


def test_void_user_scope_unsupported():
    m = _load(VOID)
    res = m.run(None, {"scope": "user", "units": ["pipewire"]})
    assert not res["success"]
    assert res["error"]["code"] == "PLATFORM_UNSUPPORTED"


def test_void_system_scope_uses_sv(monkeypatch):
    m = _load(VOID)
    captured = {}

    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        return _Result(0)

    monkeypatch.setattr(m.subprocess, "run", fake_run)
    res = m.run(None, {"scope": "system", "units": ["networking"]})
    assert res["success"]
    assert captured["cmd"] == ["sv", "restart", "networking"]


def test_void_invalid_arguments():
    m = _load(VOID)
    assert m.build_command({})["error"]["code"] == "INVALID_ARGUMENT"


# ── Resolution ────────────────────────────────────────────────────────────


def test_service_adapter_resolves_by_platform():
    path = resolve_adapter_path("service.restart")
    assert path is not None
    # On the LMDE/Debian host this resolves to the systemd implementation.
    assert path.name == "service_restart.py"
    assert load_adapter("service.restart") is not None
