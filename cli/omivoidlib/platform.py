"""Platform detection — single source of truth (docs/11 §23).

LMDE (Linux Mint Debian Edition) is Debian-based and reports "debian"
for Phase 1 purposes. The eventual Void target reports "void".
"""

from __future__ import annotations

from pathlib import Path


def detect_platform() -> str:
    """Detect the current OS platform from /etc/os-release."""
    try:
        data = Path("/etc/os-release").read_text()
    except OSError:
        return "unknown"
    if "ID=linuxmint" in data or "ID=debian" in data:
        return "debian"
    if "ID=void" in data:
        return "void"
    return "unknown"