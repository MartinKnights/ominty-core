"""command adapter — run a raw command.

Used by user-defined actions (docs/03 §27). Core Ominty actions
should prefer purpose-built adapters.
"""

from __future__ import annotations

import subprocess


def run(action, args: dict) -> dict:
    """Run the action's raw command."""
    command = action.command
    if not command:
        return {
            "success": False,
            "error": {
                "code": "INVALID_ARGUMENT",
                "message": "no command defined for this action",
            },
        }
    try:
        subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as e:
        return {
            "success": False,
            "error": {"code": "ADAPTER_FAILED", "message": str(e)},
        }
    return {"success": True, "state": {"command": command}}