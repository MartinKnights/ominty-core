"""Tests for the platform-resolved `package.install` adapter (docs/05 §10–11)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from omintylib.adapters import load_adapter, resolve_adapter_path

REPO = Path(__file__).resolve().parents[1]
DEBIAN = REPO / "adapters" / "debian" / "package_install.py"
VOID = REPO / "adapters" / "void" / "package_install.py"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"pkg_{path.stem}_{path.parent.name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Result:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


# ── Debian / apt ──────────────────────────────────────────────────────────


def test_debian_builds_install_command():
    m = _load(DEBIAN)
    assert m.build_command({"names": ["neovim", "git"]}) == [
        "apt-get",
        "install",
        "-y",
        "neovim",
        "git",
    ]


def test_debian_invalid_arguments():
    m = _load(DEBIAN)
    assert m.build_command({})["error"]["code"] == "INVALID_ARGUMENT"
    assert m.build_command({"names": "neovim"})["error"]["code"] == "INVALID_ARGUMENT"
    assert m.build_command({"names": [""]})["error"]["code"] == "INVALID_ARGUMENT"


def test_debian_denies_unprivileged_run(monkeypatch):
    m = _load(DEBIAN)
    monkeypatch.setattr(m.os, "geteuid", lambda: 1000)
    res = m.run(None, {"names": ["neovim"]})
    assert not res["success"]
    assert res["error"]["code"] == "PERMISSION_DENIED"


def test_debian_run_success_as_root(monkeypatch):
    m = _load(DEBIAN)
    monkeypatch.setattr(m.os, "geteuid", lambda: 0)
    captured = {}

    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        return _Result(0)

    monkeypatch.setattr(m.subprocess, "run", fake_run)
    res = m.run(None, {"names": ["neovim"]})
    assert res["success"]
    assert captured["cmd"] == ["apt-get", "install", "-y", "neovim"]


def test_debian_dependency_missing(monkeypatch):
    m = _load(DEBIAN)
    monkeypatch.setattr(m.os, "geteuid", lambda: 0)

    def fake_run(cmd, **kw):
        raise FileNotFoundError("apt-get")

    monkeypatch.setattr(m.subprocess, "run", fake_run)
    res = m.run(None, {"names": ["neovim"]})
    assert not res["success"]
    assert res["error"]["code"] == "DEPENDENCY_MISSING"


# ── Void / xbps ───────────────────────────────────────────────────────────


def test_void_builds_xbps_install_command():
    m = _load(VOID)
    assert m.build_command({"names": ["neovim"]}) == ["xbps-install", "-y", "neovim"]


def test_void_invalid_arguments():
    m = _load(VOID)
    assert m.build_command({})["error"]["code"] == "INVALID_ARGUMENT"


def test_void_denies_unprivileged_run(monkeypatch):
    m = _load(VOID)
    monkeypatch.setattr(m.os, "geteuid", lambda: 1000)
    res = m.run(None, {"names": ["neovim"]})
    assert not res["success"]
    assert res["error"]["code"] == "PERMISSION_DENIED"


def test_void_run_success_as_root(monkeypatch):
    m = _load(VOID)
    monkeypatch.setattr(m.os, "geteuid", lambda: 0)
    captured = {}

    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        return _Result(0)

    monkeypatch.setattr(m.subprocess, "run", fake_run)
    res = m.run(None, {"names": ["neovim"]})
    assert res["success"]
    assert captured["cmd"] == ["xbps-install", "-y", "neovim"]


# ── Resolution ────────────────────────────────────────────────────────────


def test_package_adapter_resolves_by_platform():
    path = resolve_adapter_path("package.install")
    assert path is not None
    assert path.name == "package_install.py"
    assert load_adapter("package.install") is not None