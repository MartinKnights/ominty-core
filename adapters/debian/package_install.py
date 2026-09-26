"""package.install adapter — Debian/apt implementation (docs/05 §10–11).

Installs packages non-interactively with `apt-get install -y`. Package
installation is not surfaced by any Phase 1 action (docs/04 catalogues no
package.* action); this adapter is the platform boundary that a future
`package.install` action resolves through (docs/05 §10).

Names are taken verbatim; distribution-specific name mapping is a registry /
configuration concern above the adapter (docs/05 §11) and does not belong here.
"""

from __future__ import annotations

import os
import subprocess

_TIMEOUT_S = 600


def _invalid(message: str) -> dict:
    return {"success": False, "error": {"code": "INVALID_ARGUMENT", "message": message}}


def build_command(args: dict) -> list[str] | dict:
    """Return the `apt-get` argv, or a structured error/unsupported result."""
    names = args.get("names")
    if not names or not isinstance(names, list):
        return _invalid("missing 'names' list")
    for name in names:
        if not isinstance(name, str) or not name.strip():
            return _invalid("names must be non-empty strings")
    return ["apt-get", "install", "-y", *[n.strip() for n in names]]


def run(action, args: dict) -> dict:
    """Install the requested packages via apt (root required)."""
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
            "error": {"code": "DEPENDENCY_MISSING", "message": "apt-get is not available"},
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
                or f"apt-get exited with {result.returncode}",
            },
        }
    return {"success": True, "state": {"command": command}}