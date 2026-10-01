"""dms.ipc adapter — invoke DMS capabilities via `dms ipc call`.

docs/07 §29: DMS is infrastructure; Ominty actions invoke DMS through
its stable IPC surface. The registry remains authoritative for identity,
binding, and metadata (Contract 1–2).

Action arguments:

    arguments = { dms = { target = "audio", function = "increment", args = ["3"] } }

Used for low-frequency invocation (CLI/AI). High-frequency shell keys
(launcher, clipboard, notifications, lock, media keys) are bound directly
to `dms ipc call` in DMS's own binds.kdl (dms-evaluation.md §4.2).
"""

from __future__ import annotations

import subprocess


def run(action, args: dict) -> dict:
    """Invoke a DMS IPC command via `dms ipc call`."""
    dms = args.get("dms")
    if not dms or not isinstance(dms, dict):
        return {
            "success": False,
            "error": {
                "code": "INVALID_ARGUMENT",
                "message": "missing 'dms' argument (target/function/args)",
            },
        }
    target = dms.get("target")
    function = dms.get("function")
    if not target or not function:
        return {
            "success": False,
            "error": {
                "code": "INVALID_ARGUMENT",
                "message": "dms argument requires 'target' and 'function'",
            },
        }
    dms_args = [str(a) for a in dms.get("args", [])]
    command = ["dms", "ipc", "call", target, function, *dms_args]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        return {
            "success": False,
            "error": {
                "code": "DEPENDENCY_MISSING",
                "message": "dms is not available",
            },
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": {
                "code": "ADAPTER_FAILED",
                "message": "dms ipc call timed out",
            },
        }
    if result.returncode != 0:
        return {
            "success": False,
            "error": {
                "code": "ADAPTER_FAILED",
                "message": result.stderr.strip()
                or result.stdout.strip()
                or f"dms ipc call exited with {result.returncode}",
            },
        }
    return {
        "success": True,
        "state": {
            "dms": {"target": target, "function": function},
            "output": result.stdout.strip(),
        },
    }