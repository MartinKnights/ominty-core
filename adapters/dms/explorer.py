"""shell.explorer adapter — open the Ominty interaction explorer (Super+K).

ADR-006 §12: the explorer is presented through the DMS launcher provider.
The registry declares the presentation command as:

    arguments = { command = ["dms", "ipc", "call", "spotlight", "openQuery", "!"] }

The command is run detached so opening a UI surface never blocks the caller.
The registry remains authoritative for the action's identity and metadata.
"""

from __future__ import annotations

import shutil
import subprocess


def run(action, args: dict) -> dict:
    """Launch the interaction explorer command declared by the action."""
    command = args.get("command")
    if not command:
        return {
            "success": False,
            "error": {
                "code": "INVALID_ARGUMENT",
                "message": "shell.explorer requires an 'arguments.command'",
            },
        }

    if not shutil.which(command[0]):
        return {
            "success": False,
            "error": {
                "code": "DEPENDENCY_MISSING",
                "message": f"{command[0]} is not available",
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
