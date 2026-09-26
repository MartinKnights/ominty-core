"""package.install adapter — Void/xbps implementation (docs/05 §10–11).

Installs packages non-interactively with `xbps-install -y`. Mirror of the Debian
adapter at the same boundary; implemented as the Void-sided reference for the
Void port (not yet exercised on a Void host — see void-portability-review.md).

Names are taken verbatim; distribution-specific name mapping is a registry /
configuration concern above the adapter (docs/05 §11).
"""

from __future__ import annotations

import os
import subprocess

_TIMEOUT_S = 600


def _invalid(message: str) -> dict:
    return {"success": False, "error": {"code": "INVALID_ARGUMENT", "message": message}}


def build_command(args: dict) -> list[str] | dict:
    """Return the `xbps-install` argv, or a structured error/unsupported result."""
    names = args.get("names")
    if not names or not isinstance(names, list):
        return _invalid("missing 'names' list")
    for name in names:
        if not isinstance(name, str) or not name.strip():
            return _invalid("names must be non-empty strings")
    return ["xbps-install", "-y", *[n.strip() for n in names]]


def run(action, args: dict) -> dict:
    """Install the requested packages via xbps (root required)."""
    command = build_command(args)
    if isinstance(command, dict):
        return command
    if os.geteuid() != 0:
        return {
            "success": False,
            "error": {
                "code": "PERMISSION_DENIED",
                "message": "package install requires root; run the action with elevated privileges",
            },
        }
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_S,
        )
    except FileNotFoundError:
        return {
            "success": False,
            "error": {"code": "DEPENDENCY_MISSING", "message": "xbps-install is not available"},
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": {"code": "ADAPTER_FAILED", "message": "package install timed out"},
        }
    if result.returncode != 0:
        return {
            "success": False,
            "error": {
                "code": "ADAPTER_FAILED",
                "message": result.stderr.strip()
                or result.stdout.strip()
                or f"xbps-install exited with {result.returncode}",
            },
        }
    return {"success": True, "state": {"command": command}}