"""Action runner (docs/10 §10, docs/03 §31–32).

Executes an action through its resolved adapter and returns a
structured result:

    {"action": ..., "success": bool, "state": {...} | "error": {...}}
"""

from __future__ import annotations

import shutil
import subprocess

from .adapters import load_adapter
from .platform import detect_platform
from .registry import Action, Registry, load_registry


def _requirement_available(req: str) -> bool:
    """Check whether a named requirement is available (binary in PATH)."""
    return shutil.which(req) is not None


def _run_command(command: list[str]) -> dict:
    """Run a raw command (user-defined actions, docs/03 §27)."""
    try:
        subprocess.Popen(command)
    except OSError as e:
        return {
            "success": False,
            "error": {"code": "ADAPTER_FAILED", "message": str(e)},
        }
    return {"success": True, "state": {"command": command}}


def run_action(action_id: str, registry: Registry | None = None) -> dict:
    """Run an action, returning a structured result."""
    registry = registry or load_registry()
    action = registry.actions.get(action_id)
    if action is None:
        return {
            "action": action_id,
            "success": False,
            "error": {
                "code": "ACTION_NOT_FOUND",
                "message": f"no action '{action_id}'",
            },
        }

    # Platform check.
    platform = detect_platform()
    if "common" not in action.platforms and platform not in action.platforms:
        return {
            "action": action_id,
            "success": False,
            "error": {
                "code": "PLATFORM_UNSUPPORTED",
                "message": (
                    f"action '{action_id}' does not support platform "
                    f"'{platform}'"
                ),
            },
        }

    # Implementation availability.
    if action.adapter is None and action.command is None:
        return {
            "action": action_id,
            "success": False,
            "error": {
                "code": "ACTION_UNAVAILABLE",
                "message": f"action '{action_id}' has no implementation",
            },
        }

    # Requirements.
    missing = [r for r in action.requires if not _requirement_available(r)]
    if missing:
        return {
            "action": action_id,
            "success": False,
            "error": {
                "code": "DEPENDENCY_MISSING",
                "message": f"missing requirements: {', '.join(missing)}",
            },
        }

    # Execute.
    try:
        if action.adapter:
            module = load_adapter(action.adapter)
            result = module.run(action, dict(action.arguments))
        else:
            result = _run_command(action.command or [])
    except KeyError:
        return {
            "action": action_id,
            "success": False,
            "error": {
                "code": "ACTION_UNAVAILABLE",
                "message": f"adapter '{action.adapter}' is not available",
            },
        }
    except Exception as e:  # noqa: BLE001 — adapter failures are reported
        return {
            "action": action_id,
            "success": False,
            "error": {"code": "ADAPTER_FAILED", "message": str(e)},
        }

    result.setdefault("action", action_id)
    return result