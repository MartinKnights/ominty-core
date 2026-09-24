"""app.launch adapter — resolve a role to an application and launch it.

docs/10 §11, docs/03 §26, docs/05 §384.

First proof of: intent → registry → adapter → implementation.
"""

from __future__ import annotations

import shutil
import subprocess

from omivoidlib.config import load_apps_config


def run(action, args: dict) -> dict:
    """Launch the application configured for the requested role."""
    role = args.get("role")
    if not role:
        return {
            "success": False,
            "error": {
                "code": "INVALID_ARGUMENT",
                "message": "missing 'role' argument",
            },
        }

    apps = load_apps_config()
    app = apps.get(role)
    if not app:
        return {
            "success": False,
            "error": {
                "code": "ACTION_UNAVAILABLE",
                "message": f"no application configured for role '{role}'",
            },
        }

    exe = shutil.which(app)
    if exe is None:
        return {
            "success": False,
            "error": {
                "code": "DEPENDENCY_MISSING",
                "message": (
                    f"application '{app}' for role '{role}' not found in PATH"
                ),
            },
        }

    try:
        # Detach the app from the caller's stdio so the CLI never blocks
        # on the spawned process holding a pipe open.
        subprocess.Popen(
            [exe],
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

    return {"success": True, "state": {"role": role, "app": app}}