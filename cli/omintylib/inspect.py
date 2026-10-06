"""Machine-readable installation audit — `ominty inspect --json`.

Purpose
-------
An installing agent needs to know, without guessing:

* what this machine is (distro, codename, session, hardware);
* which parts of the Ominty layer are already present;
* what is missing, and *why* it might be missing (wrong source);
* which choices still need a human answer.

`ominty inspect --json` answers all of that in one machine-readable document
so the agent never has to parse human-readable installer output.

Design constraints
------------------
* **Read-only.** Nothing here writes, and nothing requires ``sudo``. Inspection
  must be safe to run before the user has agreed to any change.
* **Stdlib only** (AGENTS.md §34). Probing the host means touching
  ``dpkg-query``/``apt``/``systemctl``, which is distribution-specific, so all
  of it is confined to this module — the boundary required by AGENTS.md §21.
* **Stable schema.** ``SCHEMA_VERSION`` is bumped on breaking changes so an
  agent can detect a mismatch instead of misreading the payload.

The layer manifest below is the single source of truth for "what does the
Ominty layer consist of". Adding a layer is a data change, not a code change.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .platform import detect_platform, family_from_os_release

SCHEMA_VERSION = 1

#: Codenames this project is validated against. `faye` is LMDE 7's release
#: codename; `gigi` is its base Debian 13 codename (some LMDE images report it).
SUPPORTED_CODENAMES = ("trixie", "faye", "gigi")


# ---------------------------------------------------------------------------
# Layer manifest
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Package:
    """A single expected package."""

    name: str
    #: "apt" (Debian repo), "obs" (AvengeMedia Open Build Service),
    #: "local" (shipped .deb in packages/).
    source: str = "apt"
    #: Purpose, so the agent can explain *why* it wants the package.
    purpose: str = ""
    #: False when a package is desirable but not required for a working
    #: desktop — inspect reports these as `optional`, never as a blocker.
    required: bool = True
    #: Executable that also proves the package is present when it is *not* a
    #: dpkg package. Ubuntu-family systems build quickshell/dms/matugen from
    #: source (see docs/UBUNTU.md), so a missing dpkg entry is not evidence of
    #: absence — the binary is. Empty means "dpkg only".
    binary: str = ""


@dataclass(frozen=True)
class Layer:
    """A group of packages installed together."""

    id: str
    label: str
    packages: tuple[Package, ...]
    #: True when install.sh provisions this layer today. Inspect reports
    #: `provisioned: false` layers honestly rather than implying they are
    #: installable.
    provisioned: bool = True
    description: str = ""


_DESKTOP = Layer(
    id="desktop",
    label="Niri + DMS desktop",
    description="Compositor, shell, theming, audio and portals.",
    packages=(
        Package("quickshell", "apt", "DMS Quickshell runtime", binary="quickshell"),
        Package("dms", "obs", "DankMaterialShell", binary="dms"),
        Package("matugen", "obs", "wallpaper-driven dynamic theming", binary="matugen"),
        Package("niri", "local", "scrollable-tiling Wayland compositor"),
        Package("xwayland-satellite", "local", "XWayland for Niri"),
        Package("libseat1", "apt", "seat library required by niri"),
        Package("fuzzel", "apt", "launcher used for keybinding dispatch"),
        Package("pipewire", "apt", "audio server"),
        Package("pipewire-pulse", "apt", "PulseAudio compatibility"),
        Package("wireplumber", "apt", "PipeWire session manager"),
        Package("xwayland", "apt", "XWayland server"),
        Package("xdg-desktop-portal", "apt", "desktop portal interface"),
        Package("xdg-desktop-portal-gtk", "apt", "GTK portal backend"),
        Package("network-manager", "apt", "network management"),
        Package("nemo", "apt", "file manager (LMDE's Cinnamon file manager)"),
    ),
)

_TERMINAL = Layer(
    id="terminal",
    label="Terminal and shell",
    provisioned=False,
    description="Terminal emulators, shell, and terminal multiplexer.",
    packages=(
        Package("alacritty", "apt", "GPU-accelerated terminal"),
        Package("ghostty", "obs", "fast terminal (alternative to alacritty)"),
        Package("zellij", "apt", "terminal multiplexer"),
        Package("starship", "apt", "cross-shell prompt"),
        Package("bash-completion", "apt", "shell completions"),
    ),
)

_EDITOR = Layer(
    id="editor",
    label="Editor",
    provisioned=False,
    description="Modal editor and its integrations.",
    packages=(
        Package("neovim", "apt", "modal editor"),
        Package("fzf", "apt", "fuzzy finder"),
    ),
)

_CLI = Layer(
    id="cli",
    label="Command-line tooling",
    provisioned=False,
    description="Package management and everyday CLI utilities.",
    packages=(
        Package("nala", "apt", "APT front-end used in place of raw apt"),
        Package("git", "apt", "version control"),
        Package("curl", "apt", "HTTP client"),
        Package("wget", "apt", "HTTP client"),
        Package("jq", "apt", "JSON processor"),
        Package("ripgrep", "apt", "recursive search"),
        Package("fd-find", "apt", "find alternative"),
        Package("bat", "apt", "cat with syntax highlighting"),
        Package("tree", "apt", "directory listing"),
        Package("htop", "apt", "process monitor"),
        Package("fastfetch", "apt", "system information"),
        Package("unzip", "apt", "archive extraction"),
    ),
)

_CONTAINERS = Layer(
    id="containers",
    label="Containers",
    provisioned=False,
    description="Rootless containers and development environments.",
    packages=(
        Package("podman", "apt", "rootless container engine"),
        Package("distrobox", "apt", "containerised development environments"),
    ),
)

_BROWSER = Layer(
    id="browser",
    label="Browser",
    provisioned=False,
    description="Default browser.",
    packages=(
        Package("firefox-esr", "apt", "web browser"),
    ),
)

LAYERS: tuple[Layer, ...] = (
    _DESKTOP,
    _TERMINAL,
    _EDITOR,
    _CLI,
    _CONTAINERS,
    _BROWSER,
)


# ---------------------------------------------------------------------------
# Probes (all read-only, none require root)
# ---------------------------------------------------------------------------


def _run(argv: list[str]) -> tuple[int, str]:
    """Run a command, returning (returncode, stdout). Never raises."""
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return (127, "")
    return (proc.returncode, proc.stdout)


def _dpkg_status(names: tuple[str, ...]) -> dict[str, str]:
    """Map package name -> installed version, in a single dpkg-query call.

    Uses ``${Package}`` rather than ``${binary:Package}`` deliberately: the
    latter includes the multi-arch qualifier (``libseat1:amd64``), which would
    not match the architecture-less name in the manifest. Packages that are
    not installed produce no output line, so they are simply absent.
    """
    if not names or shutil.which("dpkg-query") is None:
        return {}
    fmt = "${Package}\t${db:Status-Status}\t${Version}\n"
    code, out = _run(["dpkg-query", "-W", "-f", fmt, *names])
    if code != 0 and not out.strip():
        return {}
    found: dict[str, str] = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[1] == "installed":
            found[parts[0]] = parts[2]
    return found


def _on_path(binary: str) -> str | None:
    """Resolve an executable, or return None.

    PATH is checked first, then the usual per-user and local prefixes, because
    ``inspect`` can run in an environment whose PATH omits ``~/.local/bin``
    even though a package was source-built there.
    """
    if not binary:
        return None
    found = shutil.which(binary)
    if found:
        return found
    for prefix in (Path.home() / ".local/bin", Path("/usr/local/bin")):
        candidate = prefix / binary
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _os_release() -> dict[str, str]:
    """Parse /etc/os-release into a dict."""
    data: dict[str, str] = {}
    for candidate in ("/etc/os-release", "/usr/lib/os-release"):
        try:
            text = Path(candidate).read_text()
        except OSError:
            continue
        for line in text.splitlines():
            if "=" not in line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            data[key.strip()] = value.strip().strip('"')
        break
    return data


def _have_sudo() -> bool:
    """True if passwordless sudo is available."""
    if shutil.which("sudo") is None:
        return False
    code, _ = _run(["sudo", "-n", "true"])
    return code == 0


def _apt_sources() -> dict[str, list[str]]:
    """Map APT source file name -> declared suites, from /etc/apt.

    Reading the files directly avoids `apt-cache policy`, which is slow and
    needs an up-to-date package index.
    """
    roots = (Path("/etc/apt/sources.list"), Path("/etc/apt/sources.list.d"))
    found: dict[str, list[str]] = {}
    for root in roots:
        files = [root] if root.is_file() else sorted(root.glob("*.list"))
        for path in files:
            suites: list[str] = []
            try:
                text = path.read_text()
            except OSError:
                continue
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) < 3:
                    continue
                # e.g. "deb [signed-by=...] https://host/ trixie main"
                suite = parts[2].strip("/")
                if suite not in suites:
                    suites.append(suite)
            found[path.name] = suites
    return found


def _apt_pins() -> list[str]:
    """Names of APT preference/pin files."""
    pins = Path("/etc/apt/preferences.d")
    if not pins.is_dir():
        return []
    return sorted(p.name for p in pins.iterdir() if p.suffix in (".pref", ""))


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    """One audit result: pass, warn, or fail."""

    id: str
    status: str  # "pass" | "warn" | "fail"
    message: str
    #: Actionable next step for the agent, when one exists.
    fix: str = ""
    #: Only failures block the install.
    severity: str = "info"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "fix": self.fix,
        }


@dataclass
class Check:
    """A layer/package/config expectation resolved into findings."""

    findings: list[Finding] = field(default_factory=list)

    def add(self, *args, **kwargs) -> None:
        self.findings.append(Finding(*args, **kwargs))


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------


def _check_platform(osr: dict[str, str]) -> tuple[dict, list[Finding]]:
    codename = osr.get("VERSION_CODENAME", "")
    distro_id = osr.get("ID", "unknown")
    pretty = osr.get("PRETTY_NAME", "")
    is_lmde = "linuxmint" in osr.get("ID_LIKE", "") or "Mint" in pretty
    platform_id = detect_platform()
    family = family_from_os_release(osr)

    info = {
        "id": platform_id,
        "distro_id": distro_id,
        "pretty_name": pretty,
        "version_id": osr.get("VERSION_ID", ""),
        "codename": codename,
        "is_lmde": is_lmde,
        "family": family,
        "support_level": "unsupported",
        "supported": codename in SUPPORTED_CODENAMES,
    }

    findings: list[Finding] = []
    if platform_id == "unknown":
        findings.append(
            Finding(
                "platform",
                "fail",
                f"Unsupported distribution: {pretty or distro_id} is not Debian-based.",
                "Ominty targets Debian-family systems only.",
                "blocking",
            )
        )
    elif family in ("ubuntu", "mint-ubuntu"):
        # Ubuntu-family systems share apt/systemd but not the Debian 13
        # package set, so the desktop layers are provisioned by source build.
        # Promoted from "experimental" once source-built packages became
        # visible to inspect (G1) and the path was validated end-to-end.
        info["support_level"] = "supported"
        info["supported"] = True
        findings.append(
            Finding(
                "platform",
                "pass",
                f"{pretty or distro_id} ({family}) is supported via the source-build path.",
            )
        )
    elif platform_id != "debian":
        findings.append(
            Finding(
                "platform",
                "fail",
                f"Detected platform '{platform_id}', which Ominty does not support yet.",
                "Ominty is validated on Debian-family systems (Debian 13 / LMDE 7).",
                "blocking",
            )
        )
    elif not codename:
        info["support_level"] = "unvalidated"
        findings.append(
            Finding(
                "platform",
                "warn",
                f"{pretty or distro_id} reports no VERSION_CODENAME.",
                "Expected Debian 13 (trixie) or LMDE 7; confirm before installing.",
            )
        )
    elif codename not in SUPPORTED_CODENAMES:
        info["support_level"] = "unvalidated"
        findings.append(
            Finding(
                "platform",
                "warn",
                f"Untested distribution codename '{codename}'.",
                "Expected Debian 13 (trixie) or LMDE 7. "
                "Proceed only after the user accepts the risk.",
            )
        )
    else:
        info["support_level"] = "validated"
        findings.append(
            Finding(
                "platform",
                "pass",
                f"{pretty or distro_id} ({codename}) is a supported target.",
            )
        )
    return info, findings


def _check_hardware() -> tuple[dict, list[Finding]]:
    gpu = "unknown"
    for card in sorted(Path("/sys/class/drm").glob("card*")):
        try:
            driver = Path(card / "device" / "driver").resolve().name
        except OSError:
            continue
        try:
            vendor = card / "device" / "vendor"
            if vendor.exists():
                # 0x8086 = Intel, 0x1002 = AMD, 0x10de = NVIDIA
                code = vendor.read_text().strip().lower()
                name = {
                    "0x8086": "Intel",
                    "0x1002": "AMD",
                    "0x10de": "NVIDIA",
                }.get(code, "unknown")
                gpu = f"{name} ({driver})"
                break
        except OSError:
            continue

    info = {
        "arch": platform.machine(),
        "cpu": platform.processor() or platform.machine(),
        "gpu": gpu,
    }
    findings: list[Finding] = []
    if info["arch"] not in ("x86_64", "aarch64"):
        findings.append(
            Finding(
                "hardware.arch",
                "warn",
                f"Unsupported architecture '{info['arch']}'.",
                "Validated on x86_64 only.",
            )
        )
    if gpu == "unknown":
        findings.append(
            Finding(
                "hardware.gpu",
                "warn",
                "Could not determine the GPU.",
                "Niri needs a working DRM driver; verify before installing.",
            )
        )
    else:
        findings.append(Finding("hardware.gpu", "pass", f"GPU: {gpu}."))
    return info, findings


def _check_layers(osr: dict[str, str]) -> tuple[dict, list[Finding]]:
    """Resolve every layer's packages against dpkg."""
    wanted: list[str] = []
    for layer in LAYERS:
        wanted.extend(pkg.name for pkg in layer.packages)
    installed = _dpkg_status(tuple(dict.fromkeys(wanted)))

    codename = osr.get("VERSION_CODENAME", "")
    suite = codename if codename else "Debian_13"
    sources = _apt_sources()
    flat = [s for suites in sources.values() for s in suites]
    has_backports = any("backports" in s for s in flat)
    has_obs_danklinux = any("AvengeMedia:danklinux" in s for s in flat)
    has_obs_dms = any("AvengeMedia:dms" in s for s in flat)
    obs_ready = "danklinux" in suite or "dms" in suite or bool(suite)

    layers: dict[str, dict] = {}
    findings: list[Finding] = []

    for layer in LAYERS:
        entries = []
        for pkg in layer.packages:
            version = installed.get(pkg.name)
            built = _on_path(pkg.binary) if (not version and pkg.binary) else None
            if version:
                entries.append(
                    {
                        "name": pkg.name,
                        "state": "installed",
                        "version": version,
                        "source": pkg.source,
                        "required": pkg.required,
                    }
                )
            elif built:
                # Source-built (Ubuntu-family): not a dpkg package, but the
                # binary proves the package is present. See docs/UBUNTU.md.
                entries.append(
                    {
                        "name": pkg.name,
                        "state": "installed",
                        "version": None,
                        "source": "build",
                        "required": pkg.required,
                        "detail": f"source-built ({built})",
                    }
                )
            else:
                # Explain *why* it may be missing — an unavailable package is a
                # different problem from an uninstalled one.
                if pkg.source == "obs" and not (has_obs_danklinux or has_obs_dms):
                    reason = "The AvengeMedia Open Build Service repositories are not configured."
                    fix = f"Run install.sh, which adds the OBS sources for suite {suite}."
                elif pkg.source == "obs":
                    reason = "Not installed; the OBS repository is configured."
                    fix = "Install from OBS."
                elif pkg.source == "local":
                    reason = "Not installed; ships as a local .deb in packages/."
                    fix = "Run install.sh to install the bundled .deb."
                elif pkg.name == "quickshell" and not has_backports:
                    reason = "Not installed; trixie-backports is not enabled."
                    fix = "Enable trixie-backports, then install quickshell."
                else:
                    reason = "Not installed."
                    fix = f"Install the '{pkg.name}' package."
                entries.append(
                    {
                        "name": pkg.name,
                        "state": "missing",
                        "version": None,
                        "source": pkg.source,
                        "required": pkg.required,
                        "reason": reason,
                        "fix": fix,
                    }
                )

        missing_required = [
            e["name"] for e in entries if e["state"] == "missing" and e["required"]
        ]
        layers[layer.id] = {
            "id": layer.id,
            "label": layer.label,
            "description": layer.description,
            "provisioned": layer.provisioned,
            "packages": entries,
            "satisfied": not missing_required,
            "missing": missing_required,
        }

        if not layer.provisioned:
            findings.append(
                Finding(
                    f"layer.{layer.id}",
                    "warn",
                    f"Layer '{layer.label}' has {len(missing_required)} missing package(s) "
                    "and is not yet provisioned by install.sh.",
                    f"Add the '{layer.id}' layer to install.sh before offering it.",
                )
            )
        elif missing_required:
            findings.append(
                Finding(
                    f"layer.{layer.id}",
                    "fail",
                    f"Layer '{layer.label}' is missing {len(missing_required)} required "
                    f"package(s): {', '.join(missing_required)}.",
                    "Run install.sh, or install the missing packages individually.",
                    "blocking",
                )
            )
        else:
            findings.append(
                Finding(
                    f"layer.{layer.id}",
                    "pass",
                    f"Layer '{layer.label}' is complete.",
                )
            )

    return (
        {
            "layers": layers,
            "apt": {
                "sources": sources,
                "pins": _apt_pins(),
                "backports_enabled": has_backports,
                "obs_danklinux_enabled": has_obs_danklinux,
                "obs_dms_enabled": has_obs_dms,
            },
        },
        findings,
    )


def _check_configs() -> tuple[dict, list[Finding]]:
    """Check the deployed configuration and CLI wiring."""
    from .registry import xdg_config_home

    config_home = xdg_config_home()
    home = Path.home()

    targets = {
        "niri_config": config_home / "niri" / "config.kdl",
        "dms_settings": config_home / "DankMaterialShell" / "settings.json",
        "ominty_config_dir": config_home / "ominty",
        "ominty_generated": config_home / "ominty" / "generated" / "niri" / "bindings.kdl",
    }
    links = {
        "ominty_cli": home / ".local" / "bin" / "ominty",
        "ominty_hook": home / ".local" / "bin" / "ominty-hook",
    }
    plugins = {
        "omintyActions": config_home
        / "DankMaterialShell"
        / "plugins"
        / "omintyActions",
        "omintyKeybinds": config_home
        / "DankMaterialShell"
        / "plugins"
        / "omintyKeybinds",
    }

    findings: list[Finding] = []
    configs: dict[str, dict] = {}

    for name, path in targets.items():
        present = path.exists()
        configs[name] = {"path": str(path), "present": present}
        findings.append(
            Finding(
                f"config.{name}",
                "pass" if present else "warn",
                f"{path} {'found' if present else 'is missing'}.",
                "" if present else f"install.sh deploys {path}.",
            )
        )

    for name, path in links.items():
        if path.is_symlink():
            target = str(path.resolve()) if path.exists() else "broken"
            state = "pass" if path.exists() else "fail"
            detail = f"{path} -> {target}"
            fix = "" if path.exists() else "The symlink target is missing; rerun install.sh."
        else:
            state = "fail"
            detail = f"{path} is not a symlink"
            fix = "Run install.sh to create the CLI symlinks."
        configs[name] = {"path": str(path), "present": state == "pass", "state": state}
        findings.append(
            Finding(
                f"config.{name}",
                state,
                detail,
                fix,
                "blocking" if state == "fail" else "info",
            )
        )

    for name, path in plugins.items():
        present = path.exists()
        configs[name] = {"path": str(path), "present": present}
        findings.append(
            Finding(
                f"plugin.{name}",
                "pass" if present else "warn",
                f"DMS plugin '{name}' {'is linked' if present else 'is not linked'}.",
                "" if present else "Run install.sh, or use --no-plugins to skip plugins.",
            )
        )

    return (configs, findings)


def _check_session() -> tuple[dict, list[Finding]]:
    """Identify the active session and whether DMS is running."""
    info = {
        "type": os.environ.get("XDG_SESSION_TYPE", ""),
        "desktop": os.environ.get("XDG_CURRENT_DESKTOP", ""),
        "wayland_display": os.environ.get("WAYLAND_DISPLAY", ""),
    }

    findings: list[Finding] = []
    session_type = info["type"].lower()
    # Niri sets XDG_CURRENT_DESKTOP=niri while XDG_SESSION_TYPE is only
    # "wayland", so the desktop field is what identifies the compositor.
    in_niri = "niri" in info["desktop"].lower() or "niri" in session_type

    if in_niri:
        findings.append(
            Finding("session", "pass", "Running inside Niri.", "dms should be active.")
        )
        code, out = _run(
            ["systemctl", "--user", "is-active", "dms.service"],
        )
        active = out.strip().splitlines()[0] if out.strip() else f"exit {code}"
        if active == "active":
            findings.append(
                Finding("session.dms", "pass", "dms.service is active in this session.")
            )
        else:
            findings.append(
                Finding(
                    "session.dms",
                    "warn",
                    f"dms.service reports '{active}' inside Niri.",
                    "Check `systemctl --user status dms` after logging in.",
                )
            )
    elif session_type:
        # Expected before first login, and normal when inspecting from a
        # Cinnamon session. Informational only.
        findings.append(
            Finding(
                "session",
                "pass",
                f"Active session is '{info['desktop'] or session_type}', not Niri.",
                "Inspect is usually run from a normal session; Niri starts at next login.",
            )
        )
    else:
        findings.append(
            Finding(
                "session",
                "warn",
                "No XDG_SESSION_TYPE set; inspected from outside a graphical session.",
                "Re-run inspect from a desktop session for accurate session data.",
            )
        )

    return (info, findings)


# ---------------------------------------------------------------------------
# Choice points
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChoiceOption:
    """One answer a user can give to a choice point."""

    value: str
    label: str
    detail: str = ""
    #: Filled in at report time — whether this option is viable on this host.
    available: bool = True
    #: Why it is unavailable, when it is not.
    unavailable_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "label": self.label,
            "detail": self.detail,
            "available": self.available,
            "unavailable_reason": self.unavailable_reason,
        }


@dataclass(frozen=True)
class Choice:
    """A question the agent must put to the user before applying changes."""

    id: str
    question: str
    options: tuple[ChoiceOption, ...]
    #: A single value for single-select choices; a list for multi-select ones.
    default: str | list[str]
    #: Why this needs a human, and why it cannot be defaulted silently.
    rationale: str
    #: True when the install genuinely cannot proceed without an answer.
    required: bool = False
    #: True when more than one option may be chosen at once.
    multiple: bool = False
    #: True when the environment already answers this choice, so the agent
    #: records the detected answer instead of asking. A resolved required
    #: choice is *not* reported as outstanding. This is what makes migration
    #: work: on an existing desktop most answers already exist in the
    #: environment, so re-asking them is the install→migration gap.
    resolved: bool = False

    def to_dict(self, detected: dict | None = None) -> dict:
        return {
            "id": self.id,
            "question": self.question,
            "required": self.required,
            "resolved": self.resolved,
            "multiple": self.multiple,
            "rationale": self.rationale,
            "default": self.default,
            "detected": detected or {},
            "options": [o.to_dict() for o in self.options],
        }


def _provider_availability() -> dict[str, dict]:
    """Live status per registered AI provider, reusing the AI layer's owners.

    Imported lazily and defensively: inspect must still produce a report if
    the AI layer is broken or partially unavailable.
    """
    try:
        from .ai import list_providers

        return {st["provider"]: st for st in list_providers()}
    except Exception:  # pragma: no cover - defensive
        return {}


def _choice_llm_provider() -> tuple[Choice, dict]:
    """Which LLM backs the AI actions, if any."""
    status = _provider_availability()
    try:
        from .ai import default_provider

        current = default_provider()
    except Exception:  # pragma: no cover - defensive
        current = ""

    def option(value: str, label: str, detail: str) -> ChoiceOption:
        st = status.get(value)
        if st is None:
            # Not probed (e.g. the AI layer failed to import). Do not claim
            # it is unavailable — that would wrongly steer the user.
            return ChoiceOption(value, label, detail)
        state = st.get("state")
        ok = state == "available"
        reason = ""
        if not ok:
            reason = st.get("detail") or f"provider status: {state}"
            detail = f"{detail} — {reason}"
        return ChoiceOption(value, label, detail, ok, reason)

    choice = Choice(
        id="llm.provider",
        question=(
            "Which LLM should power the AI actions (Super+A), or should AI be "
            "left unconfigured?"
        ),
        required=True,
        # Already configured on this machine, so the answer is known.
        resolved=bool(current),
        rationale=(
            "AI actions need a provider before the configuration can be "
            "written. The choice determines ~/.config/ominty/ai.toml and "
            "whether any model is downloaded, so it must not be guessed."
        ),
        default="ollama",
        options=(
            option(
                "ollama",
                "Ollama (local models)",
                "Runs models on this machine. Private and offline; needs RAM "
                "for the chosen model.",
            ),
            option(
                "pi",
                "pi",
                "The pi agent/provider already present in this environment.",
            ),
            option(
                "none",
                "No LLM",
                "Install the desktop without AI. The AI keybinding is left "
                "inactive and can be enabled later.",
            ),
        ),
    )
    detected = {
        "configured_provider": current,
        "config_file": str(Path.home() / ".config" / "ominty" / "ai.toml"),
        "provider_status": status,
    }
    return choice, detected


def _choice_layers() -> tuple[Choice, dict]:
    """Which layers to install beyond the mandatory desktop."""
    optional = [layer for layer in LAYERS if not layer.provisioned]
    return (
        Choice(
            id="layers",
            question=(
                "The desktop layer is the desktop itself. Which of these "
                "optional groups should be installed too?"
            ),
            required=False,
            multiple=True,
            rationale=(
                "These layers reflect a personal preference set, not a "
                "requirement of a working desktop, so the user chooses."
            ),
            default=[layer.id for layer in optional],
            options=tuple(
                ChoiceOption(
                    layer.id,
                    layer.label,
                    f"{layer.description} "
                    f"({sum(len(l2.packages) for l2 in LAYERS if l2.id == layer.id)} packages)",
                )
                for layer in optional
            ),
        ),
        {
            "required_layer": "desktop",
            "optional_layers": [layer.id for layer in optional],
            "provisioned_layers": [layer.id for layer in LAYERS if layer.provisioned],
        },
    )


def _login_default_session() -> str:
    """Best-effort: the session the display manager starts by default.

    Reads LightDM's configuration (the last definition wins, so conf.d
    fragments override lightdm.conf), then falls back to ``~/.dmrc`` — the
    session the user last chose. Returns "" when neither is readable. Used to
    resolve the ``session.default`` choice once Niri is already the default.
    """
    session = ""
    paths = [Path("/etc/lightdm/lightdm.conf")]
    conf_d = Path("/etc/lightdm/lightdm.conf.d")
    if conf_d.is_dir():
        paths += sorted(conf_d.glob("*.conf"))
    for path in paths:
        try:
            text = path.read_text()
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("user-session="):
                session = line.split("=", 1)[1].strip()
    if session:
        return session
    try:
        for line in (Path.home() / ".dmrc").read_text().splitlines():
            line = line.strip()
            if line.lower().startswith("session="):
                session = line.split("=", 1)[1].strip()
    except OSError:
        pass
    return session


def _choice_default_session() -> tuple[Choice, dict]:
    """Whether to make Niri the default login session."""
    current = _login_default_session()
    is_niri = current.lower() == "niri"
    return (
        Choice(
            id="session.default",
            question=(
                "Should Niri become the session started on login, or should "
                "the current session stay the default?"
            ),
            required=True,
            # Already Niri, so there is nothing left to change.
            resolved=is_niri,
            rationale=(
                "Changing the default session alters how the machine boots "
                "into a desktop and is easy to get wrong over SSH, so it "
                "needs explicit consent and a stated fallback."
            ),
            default="keep",
            options=(
                ChoiceOption(
                    "set",
                    "Set Niri as default",
                    "Available from the next login. Keep the current session "
                    "selectable as a fallback.",
                ),
                ChoiceOption(
                    "keep",
                    "Leave the default unchanged",
                    "Pick Niri manually at the login screen. Safest.",
                ),
            ),
        ),
        {
            "current_default": current or None,
            "note": "The existing session must remain selectable as a fallback.",
        },
    )


def _choice_existing_configs() -> tuple[Choice, dict]:
    """What to do about configuration already on the machine."""
    from .registry import xdg_config_home

    config_home = xdg_config_home()
    detected: dict[str, object] = {}
    # Pre-rebrand installs used ~/.config/omivoid and omivoid* plugin names.
    legacy_config = config_home / "omivoid"
    legacy_present = legacy_config.exists()
    deployed = (config_home / "ominty").exists()
    detected["legacy_config_dir"] = {
        "path": str(legacy_config),
        "present": legacy_present,
    }
    detected["active_config_dirs"] = {
        name: (config_home / name).exists()
        for name in ("niri", "DankMaterialShell", "ominty")
    }
    detected["ominty_deployed"] = deployed

    return (
        Choice(
            id="config.migration",
            question=(
                "Configuration already exists on this machine. Replace it "
                "with Ominty's defaults, or keep it and change only what is "
                "missing?"
            ),
            required=True,
            # Ominty's own config is already deployed, so the replace/keep
            # decision is settled. A leftover ~/.config/omivoid is treated as
            # a rollback backup, not an install to migrate (cleaning it up is
            # gap G4, tracked separately), so it must not reopen this question.
            resolved=deployed,
            rationale=(
                "Overwriting user configuration is destructive. AGENTS.md §30 "
                "requires a tested rollback path, so the user chooses whether "
                "to replace or preserve."
            ),
            default="keep",
            options=(
                ChoiceOption(
                    "keep",
                    "Keep existing configuration",
                    "Only write files that do not exist yet. Nothing is lost.",
                ),
                ChoiceOption(
                    "backup",
                    "Back up, then replace",
                    "Copy existing files to a timestamped .bak-ominty-* "
                    "sibling before writing Ominty's defaults.",
                ),
            ),
        ),
        detected,
    )


def _choice_dms_plugins() -> tuple[Choice, dict]:
    """Whether to enable the third-party DMS plugins."""
    return (
        Choice(
            id="plugins.dms",
            question=(
                "Install the third-party DankMaterialShell plugins "
                "(KDE Connect, launcher keys, quick capture, wallpaper "
                "carousel)?"
            ),
            required=False,
            rationale=(
                "These come from the DMS plugin registry rather than from "
                "Ominty itself, so installing them is a separate decision."
            ),
            default="yes",
            options=(
                ChoiceOption("yes", "Install plugins", "Adds the DMS plugin symlinks."),
                ChoiceOption(
                    "no",
                    "Ominty plugins only",
                    "Keeps omintyActions and omintyKeybinds, skips the rest.",
                ),
            ),
        ),
        {"plugins": ["dankHooks", "dankKDEConnect", "dankLauncherKeys",
                     "quickCapture", "wallpaperCarousel"]},
    )


CHOICE_BUILDERS = (
    _choice_llm_provider,
    _choice_layers,
    _choice_default_session,
    _choice_existing_configs,
    _choice_dms_plugins,
)


def _build_choices() -> tuple[list[dict], list[Finding]]:
    """Build every choice point plus findings for unanswered required ones."""
    choices: list[dict] = []
    findings: list[Finding] = []

    for build in CHOICE_BUILDERS:
        try:
            choice, detected = build()
        except Exception as exc:  # pragma: no cover - defensive
            findings.append(
                Finding(
                    f"choice.{build.__name__.lstrip('_choice_')}",
                    "warn",
                    f"Could not evaluate choice point: {exc}",
                    "Ask the user this question directly.",
                )
            )
            continue

        choices.append(choice.to_dict(detected))

        if choice.required and not choice.resolved:
            findings.append(
                Finding(
                    f"choice.{choice.id}",
                    "warn",
                    f"Required decision outstanding: {choice.id}",
                    f"Ask the user: {choice.question}",
                )
            )

    return choices, findings


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def inspect() -> dict:
    """Build the full inspection report."""
    osr = _os_release()

    platform_info, f_platform = _check_platform(osr)
    hardware, f_hardware = _check_hardware()
    layers_info, f_layers = _check_layers(osr)
    configs, f_configs = _check_configs()
    session, f_session = _check_session()
    choices, f_choices = _build_choices()

    all_findings = (
        f_platform + f_hardware + f_layers + f_configs + f_session + f_choices
    )
    blocking = [f.id for f in all_findings if f.severity == "blocking"]
    warnings = [f.id for f in all_findings if f.status == "warn"]

    sudo_ok = _have_sudo()
    outstanding = [c["id"] for c in choices if c["required"] and not c["resolved"]]

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": "ominty",
        "platform": platform_info,
        "hardware": hardware,
        "session": session,
        "privilege": {"sudo": sudo_ok, "required": True},
        "layers": layers_info["layers"],
        "apt": layers_info["apt"],
        "configs": configs,
        "choices": choices,
        "findings": [f.to_dict() for f in all_findings],
        "summary": {
            # A machine is installable when nothing blocks it. Outstanding
            # choices are questions to ask, not failures.
            "ready": not blocking,
            "blocking": blocking,
            "warnings": warnings,
            "required_choices": outstanding,
            "counts": {
                "pass": sum(1 for f in all_findings if f.status == "pass"),
                "warn": sum(1 for f in all_findings if f.status == "warn"),
                "fail": sum(1 for f in all_findings if f.status == "fail"),
            },
        },
    }


def layers_payload() -> dict:
    """The layer manifest, independent of the host.

    This is the single source of truth for what each layer contains.
    install.sh consumes it so the installer and the audit cannot drift apart.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "layers": {
            layer.id: {
                "id": layer.id,
                "label": layer.label,
                "description": layer.description,
                "provisioned": layer.provisioned,
                "packages": [
                    {
                        "name": pkg.name,
                        "source": pkg.source,
                        "required": pkg.required,
                        "purpose": pkg.purpose,
                    }
                    for pkg in layer.packages
                ],
            }
            for layer in LAYERS
        },
        "order": [layer.id for layer in LAYERS],
    }


def cmd_layers(args) -> int:
    """`ominty layers` — print the layer manifest."""
    payload = layers_payload()
    selected = getattr(args, "layer", None)
    if selected:
        unknown = set(selected) - set(payload["layers"])
        if unknown:
            print(
                f"unknown layer id(s): {', '.join(sorted(unknown))}; "
                f"choose from {', '.join(payload['order'])}",
                file=sys.stderr,
            )
            return 2
        payload["layers"] = {
            k: v for k, v in payload["layers"].items() if k in selected
        }

    if getattr(args, "format", "text") == "json":
        print(json.dumps(payload, indent=2))
        return 0

    if getattr(args, "format", "text") == "ids":
        # One layer id per line, for shell error messages.
        for layer_id in payload["layers"]:
            print(layer_id)
        return 0

    if getattr(args, "format", "text") == "shell":
        # Tab-separated so install.sh can read it without a JSON parser.
        for layer in payload["layers"].values():
            for pkg in layer["packages"]:
                if pkg["required"]:
                    print(f"{pkg['source']}\t{pkg['name']}")
        return 0

    for layer_id in payload["order"]:
        layer = payload["layers"].get(layer_id)
        if layer is None:
            continue
        tag = "" if layer["provisioned"] else "  (not yet installed by install.sh)"
        print(f"\n{layer['label']} [{layer_id}]{tag}")
        print(f"  {layer['description']}")
        for pkg in layer["packages"]:
            flag = "" if pkg["required"] else "  (optional)"
            print(f"    {pkg['name']:<22} {pkg['source']:<6} {pkg['purpose']}{flag}")
    return 0


def format_text(report: dict) -> str:
    """Render the report for humans."""
    lines: list[str] = []
    p = report["platform"]
    lines.append(f"Platform:   {p['pretty_name'] or p['distro_id']} ({p['codename']})")
    h = report["hardware"]
    lines.append(f"Hardware:   {h['arch']} / {h['gpu']}")
    s = report["session"]
    lines.append(f"Session:    {s['desktop'] or 'none'} ({s['type'] or 'none'})")
    lines.append(f"sudo:       {'yes' if report['privilege']['sudo'] else 'no'}")
    lines.append("")

    for layer in report["layers"].values():
        mark = "ok " if layer["satisfied"] else "MISSING"
        lines.append(f"[{mark}] {layer['label']} ({layer['id']})")
        for pkg in layer["packages"]:
            if pkg["state"] == "installed":
                lines.append(f"    + {pkg['name']:<24} {pkg['version']}")
            else:
                lines.append(f"    - {pkg['name']:<24} {pkg.get('reason', 'missing')}")
        lines.append("")

    lines.append("Findings:")
    for f in report["findings"]:
        if f["status"] == "pass":
            continue
        lines.append(f"  {f['status'].upper():<5} {f['id']}: {f['message']}")
        if f["fix"]:
            lines.append(f"        -> {f['fix']}")

    lines.append("")
    lines.append("Choices:")
    for choice in report.get("choices", []):
        flag = "required" if choice["required"] else "optional"
        multi = ", multi-select" if choice.get("multiple") else ""
        lines.append(f"  [{flag}{multi}] {choice['id']}")
        lines.append(f"      {choice['question']}")
        chosen = choice["default"]
        if not isinstance(chosen, list):
            chosen = [chosen]
        for option in choice["options"]:
            mark = " " if option["available"] else "x"
            note = (
                f"  ({option['unavailable_reason']})"
                if not option["available"]
                else ""
            )
            is_default = " (default)" if option["value"] in chosen else ""
            lines.append(
                f"        {mark} {option['value']:<10} {option['label']}{is_default}{note}"
            )

    counts = report["summary"]["counts"]
    outstanding = report["summary"].get("required_choices") or []
    lines.append("")
    lines.append(
        f"{counts['pass']} pass, {counts['warn']} warn, {counts['fail']} fail — "
        f"{'ready' if report['summary']['ready'] else 'NOT ready'} to install"
    )
    if outstanding:
        lines.append(f"ask the user about: {', '.join(outstanding)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI handler for `ominty inspect`."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="ominty inspect",
        description="Audit this machine for the Ominty layer (read-only).",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument(
        "--layer",
        action="append",
        help="restrict findings to these layer ids (repeatable)",
    )
    args = parser.parse_args(argv)

    report = inspect()

    if args.layer:
        # --layer narrows the report to the named layers. Findings that are
        # not layer-scoped (platform, hardware, session, configs) are global
        # and are always kept, because they affect any install.
        wanted = set(args.layer)
        unknown = wanted - set(report["layers"])
        if unknown:
            parser.error(
                f"unknown layer id(s): {', '.join(sorted(unknown))}; "
                f"choose from {', '.join(report['layers'])}"
            )
        report["layers"] = {k: v for k, v in report["layers"].items() if k in wanted}
        keep = {f"layer.{k}" for k in wanted}
        report["findings"] = [
            f
            for f in report["findings"]
            if f["id"] in keep or not f["id"].startswith("layer.")
        ]
        blocking = [f["id"] for f in report["findings"] if f["severity"] == "blocking"]
        warnings = [f["id"] for f in report["findings"] if f["status"] == "warn"]
        report["summary"]["blocking"] = blocking
        report["summary"]["warnings"] = warnings
        report["summary"]["ready"] = not blocking
        report["summary"]["counts"] = {
            "pass": sum(1 for f in report["findings"] if f["status"] == "pass"),
            "warn": sum(1 for f in report["findings"] if f["status"] == "warn"),
            "fail": sum(1 for f in report["findings"] if f["status"] == "fail"),
        }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_text(report))

    return 0 if report["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())