"""ai.pi.open adapter — open Pi in the configured terminal (docs/ai/10 §8).

Flow:

    Ominty
     ↓
    configured terminal (role)
     ↓
    Pi

This action explicitly targets Pi and is therefore allowed to be
provider-specific (docs/ai/02 §12).
"""

from __future__ import annotations

import shutil
import subprocess

from omintylib.config import load_apps_config

# Terminal flag used to run a command. alacritty/kitty/xterm use -e;
# wezterm and gnome-terminal differ. Unknown terminals default to -e.
_TERMINAL_EXEC_FLAGS: dict[str, list[str]] = {
    "alacritty": ["-e"],
    "kitty": ["-e"],
    "xterm": ["-e"],
    "wezterm": ["start", "--"],
    "gnome-terminal": ["--"],
}


def run(action, args: dict) -> dict:
    """Launch Pi inside the configured terminal role."""
    apps = load_apps_config()
    terminal = apps.get("terminal")
    if not terminal:
        return {
            "success": False,
            "error": {
                "code": "ACTION_UNAVAILABLE",
                "message": "no application configured for role 'terminal'",
            },
        }

    exe = shutil.which(terminal)
    if exe is None:
        return {
            "success": False,
            "error": {
                "code": "DEPENDENCY_MISSING",
                "message": f"terminal '{terminal}' not found in PATH",
            },
        }

    if shutil.which("pi") is None:
        return {
            "success": False,
            "error": {
                "code": "DEPENDENCY_MISSING",
                "message": "pi binary not found in PATH",
            },
        }

    flags = _TERMINAL_EXEC_FLAGS.get(terminal, ["-e"])
    try:
        # Detach from the caller's stdio so the CLI never blocks on the
        # spawned process holding a pipe open.
        subprocess.Popen(
            [exe, *flags, "pi"],
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

    return {"success": True, "state": {"terminal": terminal, "app": "pi"}}