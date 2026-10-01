"""Inspection report tests (AGENTS.md §29).

The probes touch the host, so the tests monkeypatch the probe layer and assert
on the report-building logic rather than on this machine's real state.
"""

from __future__ import annotations

import json

import pytest

from omintylib import inspect as insp
from omintylib.inspect import (
    LAYERS,
    SCHEMA_VERSION,
    _check_configs,
    _check_hardware,
    _check_layers,
    _check_platform,
    _check_session,
    _dpkg_status,
    format_text,
    inspect,
)

LMDE = {
    "ID": "linuxmint",
    "ID_LIKE": "debian",
    "PRETTY_NAME": "Linux Mint 7",
    "VERSION_ID": "7",
    "VERSION_CODENAME": "gigi",
}


def test_manifest_is_well_formed():
    """Every layer needs a unique id, and every package a non-empty name."""
    ids = [layer.id for layer in LAYERS]
    assert len(ids) == len(set(ids)), "duplicate layer id"

    names = [pkg.name for layer in LAYERS for pkg in layer.packages]
    assert len(names) == len(set(names)), "package listed in two layers"

    for layer in LAYERS:
        assert layer.label, f"layer {layer.id} has no label"
        for pkg in layer.packages:
            assert pkg.purpose, f"{layer.id}/{pkg.name} has no purpose"
            assert pkg.source in ("apt", "obs", "local")


def test_dpkg_status_ignores_architecture_suffix(monkeypatch):
    """Multi-arch packages report as name:amd64 from ${binary:Package}.

    The manifest holds architecture-less names, so the parser must key on
    ${Package}. Regression guard for libseat1/pipewire being wrongly reported
    as missing.
    """
    monkeypatch.setattr(
        insp.shutil, "which", lambda name: "/usr/bin/dpkg-query" if name == "dpkg-query" else None
    )
    monkeypatch.setattr(
        insp,
        "_run",
        lambda argv: (
            0,
            "libseat1\tinstalled\t0.9.1-1\n"
            "pipewire\tinstalled\t1.4.2-1\n"
            "jq\tconfig-files\t1.7.1-3\n",
        ),
    )
    got = _dpkg_status(("libseat1", "pipewire", "jq"))
    assert got == {"libseat1": "0.9.1-1", "pipewire": "1.4.2-1"}
    # A package that is merely unpacked/config-files is not installed.
    assert "jq" not in got


def test_dpkg_status_without_dpkg(monkeypatch):
    monkeypatch.setattr(insp.shutil, "which", lambda name: None)
    assert _dpkg_status(("niri",)) == {}


def test_dpkg_status_handles_total_failure(monkeypatch):
    monkeypatch.setattr(
        insp.shutil, "which", lambda name: "/usr/bin/dpkg-query" if name == "dpkg-query" else None
    )
    monkeypatch.setattr(insp, "_run", lambda argv: (127, ""))
    assert _dpkg_status(("niri",)) == {}


def test_check_platform_supported(monkeypatch):
    monkeypatch.setattr(insp, "detect_platform", lambda: "debian")
    info, findings = _check_platform(LMDE)
    assert info["distro_id"] == "linuxmint"
    assert info["is_lmde"] is True
    assert info["supported"] is True  # LMDE 7 reports the base codename 'gigi'
    assert [f.status for f in findings] == ["pass"]


def test_check_platform_unsupported_codename(monkeypatch):
    monkeypatch.setattr(insp, "detect_platform", lambda: "debian")
    osr = dict(LMDE, VERSION_CODENAME="bookworm")
    info, findings = _check_platform(osr)
    assert info["supported"] is False
    assert findings[0].status == "warn"
    # An untested distro must warn, never block.
    assert findings[0].severity != "blocking"


def test_check_platform_unknown_blocks(monkeypatch):
    monkeypatch.setattr(insp, "detect_platform", lambda: "unknown")
    _, findings = _check_platform({"ID": "arch", "PRETTY_NAME": "Arch"})
    assert findings[0].status == "fail"
    assert findings[0].severity == "blocking"


def _stub_layer_deps(monkeypatch, installed: dict, sources=None, pins=None):
    monkeypatch.setattr(insp, "_dpkg_status", lambda names: installed)
    monkeypatch.setattr(
        insp, "_apt_sources", lambda: sources if sources is not None else {}
    )
    monkeypatch.setattr(
        insp, "_apt_pins", lambda: pins if pins is not None else []
    )


def test_check_layers_all_present(monkeypatch):
    everything = {pkg.name: "1.0" for layer in LAYERS for pkg in layer.packages}
    _stub_layer_deps(monkeypatch, everything)

    info, findings = _check_layers(LMDE)
    assert info["layers"]["desktop"]["satisfied"] is True
    for layer in LAYERS:
        assert info["layers"][layer.id]["missing"] == []
    desktop = next(f for f in findings if f.id == "layer.desktop")
    assert desktop.status == "pass"


def test_check_layers_missing_required_blocks(monkeypatch):
    _stub_layer_deps(monkeypatch, {})
    info, findings = _check_layers(LMDE)

    desktop = info["layers"]["desktop"]
    assert desktop["satisfied"] is False
    assert "niri" in desktop["missing"]

    finding = next(f for f in findings if f.id == "layer.desktop")
    assert finding.status == "fail"
    assert finding.severity == "blocking"


def test_unprovisioned_layer_warns_but_never_blocks(monkeypatch):
    """A layer install.sh cannot yet provide must not block the install."""
    _stub_layer_deps(monkeypatch, {})
    _, findings = _check_layers(LMDE)

    for layer in LAYERS:
        finding = next(f for f in findings if f.id == f"layer.{layer.id}")
        if layer.provisioned:
            assert finding.severity == "blocking"
        else:
            assert finding.status == "warn"
            assert finding.severity == "info"


def test_missing_package_reason_distinguishes_source(monkeypatch):
    """A package absent because its repo is missing is a different problem."""
    _stub_layer_deps(monkeypatch, {})
    info, _ = _check_layers(LMDE)
    by_name = {
        p["name"]: p
        for layer in info["layers"].values()
        for p in layer["packages"]
    }

    assert "Open Build Service" in by_name["dms"]["reason"]
    assert by_name["dms"]["fix"]

    assert "local .deb" in by_name["niri"]["reason"]

    # With no OBS sources, quickshell's real cause is the missing backports.
    assert "backports" in by_name["quickshell"]["reason"]


def test_obs_configured_clears_repository_reason(monkeypatch):
    _stub_layer_deps(
        monkeypatch,
        {},
        sources={
            "danklinux.list": ["home:AvengeMedia:danklinux/Debian_13/"],
            "dms.list": ["home:AvengeMedia:dms/Debian_13/"],
        },
    )
    info, _ = _check_layers(LMDE)
    by_name = {
        p["name"]: p
        for layer in info["layers"].values()
        for p in layer["packages"]
    }
    assert "Open Build Service" not in by_name["dms"]["reason"]
    assert info["apt"]["obs_dms_enabled"] is True
    assert info["apt"]["obs_danklinux_enabled"] is True


def test_check_configs_reports_symlink_state(tmp_path, monkeypatch):
    home = tmp_path / "home"
    (home / ".local" / "bin").mkdir(parents=True)
    config_home = home / ".config"

    monkeypatch.setattr(Path := insp.Path, "home", staticmethod(lambda: home))
    from omintylib import registry

    monkeypatch.setattr(registry, "xdg_config_home", lambda: config_home)

    _configs, findings = _check_configs()
    by_id = {f.id: f for f in findings}

    assert by_id["config.ominty_cli"].status == "fail"
    assert by_id["config.ominty_cli"].severity == "blocking"

    # A real symlink to an existing target must pass.
    target = tmp_path / "cli" / "ominty"
    target.parent.mkdir()
    target.write_text("#!/bin/sh\n")
    (home / ".local" / "bin" / "ominty").symlink_to(target)
    _configs, findings = _check_configs()
    assert {f.id: f for f in findings}["config.ominty_cli"].status == "pass"


def test_check_configs_flags_broken_symlink(tmp_path, monkeypatch):
    home = tmp_path / "home"
    (home / ".local" / "bin").mkdir(parents=True)
    (home / ".local" / "bin" / "ominty").symlink_to(tmp_path / "nope")

    monkeypatch.setattr(insp.Path, "home", staticmethod(lambda: home))
    from omintylib import registry

    monkeypatch.setattr(registry, "xdg_config_home", lambda: home / ".config")

    _configs, findings = _check_configs()
    finding = {f.id: f for f in findings}["config.ominty_cli"]
    assert finding.status == "fail"
    assert "broken" in finding.message or "missing" in finding.fix.lower()


def test_check_session_outside_graphical_session(monkeypatch):
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
    monkeypatch.delenv("XDG_CURRENT_DESKTOP", raising=False)
    info, findings = _check_session()
    assert info["type"] == ""
    assert findings[0].status == "warn"


def test_check_session_inside_niri_with_dms(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "niri")
    monkeypatch.setattr(insp, "_run", lambda argv: (0, "active\n"))
    _info, findings = _check_session()
    by_id = {f.id: f for f in findings}
    assert by_id["session"].status == "pass"
    assert by_id["session.dms"].status == "pass"


def test_check_session_inside_niri_dms_inactive(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "niri")
    monkeypatch.setattr(insp, "_run", lambda argv: (3, "inactive\n"))
    _info, findings = _check_session()
    assert {f.id: f for f in findings}["session.dms"].status == "warn"


def test_check_session_non_niri_is_informational(monkeypatch):
    """Inspecting from Cinnamon must not look like a failure."""
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "X-Cinnamon")
    _info, findings = _check_session()
    assert findings[0].status == "pass"


def test_check_hardware_unsupported_arch(monkeypatch):
    monkeypatch.setattr(insp.platform, "machine", lambda: "riscv64")
    monkeypatch.setattr(insp.platform, "processor", lambda: "")
    _info, findings = _check_hardware()
    assert any(f.id == "hardware.arch" and f.status == "warn" for f in findings)


def test_report_shape_is_json_serialisable(monkeypatch):
    """The agent consumes this as JSON, so the contract must hold."""
    monkeypatch.setattr(insp, "_dpkg_status", lambda names: {})
    monkeypatch.setattr(insp, "_apt_sources", lambda: {})
    monkeypatch.setattr(insp, "_apt_pins", lambda: [])
    monkeypatch.setattr(insp, "_have_sudo", lambda: True)
    monkeypatch.setattr(insp, "_os_release", lambda: LMDE)

    report = inspect()
    # Round-trips without a custom encoder.
    assert json.loads(json.dumps(report))["schema_version"] == SCHEMA_VERSION

    for key in (
        "schema_version", "tool", "platform", "hardware", "session",
        "privilege", "layers", "apt", "configs", "findings", "summary",
    ):
        assert key in report, f"missing top-level key: {key}"

    assert report["summary"]["ready"] is (not report["summary"]["blocking"])
    for finding in report["findings"]:
        assert finding["status"] in ("pass", "warn", "fail")
        assert set(finding) == {"id", "status", "severity", "message", "fix"}


def test_report_findings_have_unique_ids(monkeypatch):
    monkeypatch.setattr(insp, "_dpkg_status", lambda names: {})
    monkeypatch.setattr(insp, "_apt_sources", lambda: {})
    monkeypatch.setattr(insp, "_apt_pins", lambda: [])
    ids = [f["id"] for f in inspect()["findings"]]
    assert len(ids) == len(set(ids))


def test_format_text_renders_layers(monkeypatch):
    monkeypatch.setattr(insp, "_dpkg_status", lambda names: {})
    monkeypatch.setattr(insp, "_apt_sources", lambda: {})
    monkeypatch.setattr(insp, "_apt_pins", lambda: [])
    text = format_text(inspect())
    for layer in LAYERS:
        assert layer.label in text
    assert "Niri + DMS desktop" in text


@pytest.mark.parametrize("flag", ["--json", "--layer"])
def test_main_accepts_flags(flag, monkeypatch, capsys):
    monkeypatch.setattr(insp, "_dpkg_status", lambda names: {})
    monkeypatch.setattr(insp, "_apt_sources", lambda: {})
    monkeypatch.setattr(insp, "_apt_pins", lambda: {})
    argv = [flag, "desktop"] if flag == "--layer" else [flag]
    insp.main(argv)
    assert capsys.readouterr().out.strip()


def test_main_layer_filter_narrows_report(monkeypatch, capsys):
    monkeypatch.setattr(insp, "_dpkg_status", lambda names: {})
    monkeypatch.setattr(insp, "_apt_sources", lambda: {})
    monkeypatch.setattr(insp, "_apt_pins", lambda: [])
    insp.main(["--json", "--layer", "cli"])
    report = json.loads(capsys.readouterr().out)

    assert list(report["layers"]) == ["cli"]
    layer_findings = [f for f in report["findings"] if f["id"].startswith("layer.")]
    assert [f["id"] for f in layer_findings] == ["layer.cli"]
    # Global findings survive the filter.
    assert any(f["id"].startswith("config.") for f in report["findings"])


def test_main_rejects_unknown_layer(monkeypatch):
    with pytest.raises(SystemExit):
        insp.main(["--layer", "does-not-exist"])


def test_main_exit_code_reflects_readiness(monkeypatch, capsys):
    monkeypatch.setattr(insp, "_dpkg_status", lambda names: {})
    monkeypatch.setattr(insp, "_apt_sources", lambda: {})
    monkeypatch.setattr(insp, "_apt_pins", lambda: {})
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "X-Cinnamon")
    # Missing CLI symlinks are blocking, so a bare machine must exit non-zero.
    code = insp.main(["--layer", "editor"])
    capsys.readouterr()
    assert code == 1