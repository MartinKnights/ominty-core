"""service.restart adapter — Void/runit implementation.

Void uses runit. runit is **system-level**; there is no standard user service
manager, and the PipeWire stack on Void runs as a session process rather than a
runit service. Phase 1 therefore:

* implements `scope = "system"` → `sv restart <units>` (best-effort; not yet
  verified on a Void host);
* reports `PLATFORM_UNSUPPORTED` for `scope = "user"` so the action fails
  explicitly instead of silently doing nothing (docs/04 §19, AGENTS.md §25).

Resolving this properly (session-process restart or a user runsvdir) is Void
phase work — see void-portability-review.md §5.2/§5.10.
"""

from __future__ import annotations

import subprocess

_TIMEOUT_S = 15


def _invalid(message: str) -> dict:
    return {"success": False, "error": {"code": "INVALID_ARGUMENT", "message": message}}


def build_command(args: dict) -> list[str] | dict:
    """Return the `sv` argv, or a structured error/unsupported result."""
    units = args.get("units")
    if not units or not isinstance(units, list):
        return _invalid("missing 'units' list")
    scope = args.get("scope", "user")
    if scope not in ("user", "system"):
        return _invalid("scope must be 'user' or 'system'")
    if scope == "user":
        return {
            "success": False,
            "error": {
                "code": "PLATFORM_UNSUPPORTED",
                "message": (
                    "user-scope service restart is not implemented for Void/runit "
                    "(runit is system-level; session processes are Void-phase work)"
                ),
            },
        }
    return ["sv", "restart", *[str(u) for u in units]]


def run(action, args: dict) -> dict:
    """Restart the requested system services via runit."""
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
            "error": {"code": "DEPENDENCY_MISSING", "message": "sv is not available"},
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": {"code": "ADAPTER_FAILED", "message": "service restart timed out"},
        }
    if result.returncode != 0:
        return {
            "success": False,
            "error": {
                "code": "ADAPTER_FAILED",
                "message": result.stderr.strip()
                or result.stdout.strip()
                or f"sv exited with {result.returncode}",
            },
        }
    return {"success": True, "state": {"command": command}}
