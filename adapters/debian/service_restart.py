"""service.restart adapter — restart services via the platform service manager.

This is the LMDE/Debian implementation (systemd).

Arguments:

    arguments = { scope = "user", units = ["wireplumber", "pipewire"] }

`scope = "user"` → `systemctl --user restart <units>`;
`scope = "system"` → `systemctl restart <units>`.

The action never names `systemctl`; the service manager is selected by platform
resolution (this module on Debian, `adapters/void/service_restart.py` on Void).
See docs/05 (platform abstraction) and void-portability-review.md §5.2.
"""

from __future__ import annotations

import subprocess

_SCOPES = ("user", "system")
_TIMEOUT_S = 15


def build_command(args: dict) -> list[str] | dict:
    """Return the systemctl argv, or a structured INVALID_ARGUMENT error."""
    units = args.get("units")
    if not units or not isinstance(units, list):
        return {
            "success": False,
            "error": {
                "code": "INVALID_ARGUMENT",
                "message": "missing 'units' list",
            },
        }
    scope = args.get("scope", "user")
    if scope not in _SCOPES:
        return {
            "success": False,
            "error": {
                "code": "INVALID_ARGUMENT",
                "message": f"scope must be one of {_SCOPES}",
            },
        }
    base = ["systemctl", "--user"] if scope == "user" else ["systemctl"]
    return [*base, "restart", *[str(u) for u in units]]


def run(action, args: dict) -> dict:
    """Restart the requested services via systemd."""
    command = build_command(args)
    if isinstance(command, dict):
        return command
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
            "error": {
                "code": "DEPENDENCY_MISSING",
                "message": "systemctl is not available",
            },
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": {
                "code": "ADAPTER_FAILED",
                "message": "service restart timed out",
            },
        }
    if result.returncode != 0:
        return {
            "success": False,
            "error": {
                "code": "ADAPTER_FAILED",
                "message": result.stderr.strip()
                or result.stdout.strip()
                or f"systemctl exited with {result.returncode}",
            },
        }
    return {"success": True, "state": {"command": command}}
