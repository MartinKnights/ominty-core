"""Platform detection — single source of truth (docs/11 §23).

``detect_platform`` collapses the Debian family (Debian, LMDE, Ubuntu, Linux
Mint) to ``"debian"`` because they share apt and systemd; the eventual Void
target reports ``"void"``.

``detect_family`` / ``family_from_os_release`` keep the finer distinction the
installer and ``ominty inspect`` need to choose a provisioning path:

    debian | mint-debian | ubuntu | mint-ubuntu | void | unknown
"""

from __future__ import annotations

from pathlib import Path


def _parse_os_release(text: str) -> dict[str, str]:
    """Parse os-release KEY=VALUE lines (surrounding quotes stripped)."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip().strip('"')
    return out


def _read_os_release() -> dict[str, str]:
    try:
        return _parse_os_release(Path("/etc/os-release").read_text())
    except OSError:
        return {}


def detect_platform() -> str:
    """Detect the current OS platform from /etc/os-release."""
    try:
        data = Path("/etc/os-release").read_text()
    except OSError:
        return "unknown"
    if "ID=linuxmint" in data or "ID=debian" in data or "ID=ubuntu" in data:
        return "debian"
    if "ID=void" in data:
        return "void"
    return "unknown"


def family_from_os_release(osr: dict[str, str]) -> str:
    """Classify a parsed os-release into an Ominty family.

    Returns one of: ``debian``, ``mint-debian``, ``ubuntu``, ``mint-ubuntu``,
    ``void``, ``unknown``. Kept separate from ``detect_platform`` so the
    platform abstraction (apt/systemd) is unchanged while the installer can
    still tell the two Mint editions apart.
    """
    distro_id = osr.get("ID", "").lower()
    id_like = osr.get("ID_LIKE", "").lower()
    if distro_id == "void":
        return "void"
    if distro_id == "linuxmint":
        return "mint-ubuntu" if "ubuntu" in id_like else "mint-debian"
    if distro_id == "ubuntu":
        return "ubuntu"
    if distro_id == "debian":
        return "debian"
    if "ubuntu" in id_like:
        return "ubuntu"
    if "debian" in id_like:
        return "debian"
    return "unknown"


def detect_family() -> str:
    """Detect the current Ominty family from /etc/os-release."""
    return family_from_os_release(_read_os_release())