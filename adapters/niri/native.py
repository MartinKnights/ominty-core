"""niri.native adapter — execute native Niri actions via IPC.

docs/03 §23: Niri remains authoritative for execution.
The registry remains authoritative for identity, binding, and metadata.

Used for low-frequency invocation (CLI/AI). High-frequency navigation
should use native Niri bindings generated from the registry (Stage 9–10).
"""

from __future__ import annotations

import subprocess


def run(action, args: dict) -> dict:
    """Invoke a native Niri action via `niri msg action`."""
    niri_action = args.get("action")
    if not niri_action:
        return {
            "success": False,
            "error": {
                "code": "INVALID_ARGUMENT",
                "message": "missing 'action' argument",
            },
        }
    try:
        result = subprocess.run(
            ["niri", "msg", "action", niri_action],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        return {
            "success": False,
            "error": {
                "code": "DEPENDENCY_MISSING",
                "message": "niri is not available",
            },
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": {
                "code": "ADAPTER_FAILED",
                "message": "niri msg timed out",
            },
        }
    if result.returncode != 0:
        return {
            "success": False,
            "error": {
                "code": "ADAPTER_FAILED",
                "message": result.stderr.strip()
                or f"niri msg exited with {result.returncode}",
            },
        }
    return {"success": True, "state": {"niri_action": niri_action}}