"""dms.theme adapter — Omivoid theme operations via DMS (docs/08 §27).

`regenerate` re-runs the DMS matugen pipeline from the **current**
wallpaper without changing it (docs/08 §27 — useful after editing
templates, installing an adapter, or recovering from a failed update).

DMS's `theme` IPC target only exposes dark/light/getMode/toggle, so this
adapter composes two IPC reads (current wallpaper, current mode) with the
`dms matugen generate` subcommand. DMS state/config directories follow the
XDG base directories; the shell installation directory is discovered from
`DMS_SHELL_DIR` or the packaged location.

Action arguments:

    arguments = { theme = { action = "regenerate" } }
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

# Packaged DMS shell location (overridable via DMS_SHELL_DIR).
_DEFAULT_SHELL_DIR = "/usr/share/quickshell/dms"

_READ_TIMEOUT = 10.0
_GENERATE_TIMEOUT = 60.0

_VALID_MODES = ("dark", "light", "smart")

# DMS exits non-zero when nothing changed; that is a successful no-op, not
# a failure (observed: exit 2, "No color changes detected, skipping refresh").
_NO_CHANGE_MARKER = "No color changes detected"


def _error(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


def _xdg_dir(env_var: str, fallback: str, child: str) -> Path:
    """Resolve an XDG base directory with a sensible fallback."""
    base = os.environ.get(env_var) or os.path.expanduser(fallback)
    return Path(base) / child


def _shell_dir() -> Path:
    """Resolve the DMS shell installation directory."""
    override = os.environ.get("DMS_SHELL_DIR")
    return Path(override) if override else Path(_DEFAULT_SHELL_DIR)


def _run(command: list[str], timeout: float) -> tuple[int, str, str] | None:
    """Run a command; return (rc, stdout, stderr), or None if dms is absent."""
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return (-1, "", "timed out")
    return (result.returncode, result.stdout, result.stderr)


def _current_wallpaper() -> str | dict:
    """Return the current wallpaper value, or an error dict."""
    result = _run(["dms", "ipc", "call", "wallpaper", "get"], _READ_TIMEOUT)
    if result is None:
        return _error("DEPENDENCY_MISSING", "dms is not available")
    rc, out, err = result
    if rc != 0:
        return _error(
            "ADAPTER_FAILED",
            err.strip() or out.strip() or "could not read the current wallpaper",
        )
    value = out.strip()
    if not value:
        return _error("CONTEXT_UNAVAILABLE", "no wallpaper is configured")
    return value


def _current_mode() -> str:
    """Return the current light/dark mode (best-effort; defaults to dark)."""
    result = _run(["dms", "ipc", "call", "theme", "getMode"], _READ_TIMEOUT)
    if result is None or result[0] != 0:
        return "dark"
    mode = result[1].strip()
    return mode if mode in _VALID_MODES else "dark"


def run(action, args: dict) -> dict:
    """Run the requested DMS theme operation."""
    theme = args.get("theme")
    if not isinstance(theme, dict) or theme.get("action") != "regenerate":
        return _error("INVALID_ARGUMENT", "dms.theme supports action='regenerate'")

    if shutil.which("dms") is None:
        return _error("DEPENDENCY_MISSING", "dms is not available")

    wallpaper = _current_wallpaper()
    if isinstance(wallpaper, dict):  # error dict
        return wallpaper

    mode = _current_mode()
    kind = "hex" if wallpaper.startswith("#") else "image"

    command = [
        "dms", "matugen", "generate",
        "--value", wallpaper,
        "--kind", kind,
        "--mode", mode,
        "--state-dir", str(
            _xdg_dir("XDG_STATE_HOME", "~/.local/state", "DankMaterialShell")
        ),
        "--shell-dir", str(_shell_dir()),
        "--config-dir", str(
            _xdg_dir("XDG_CONFIG_HOME", "~/.config", "DankMaterialShell")
        ),
    ]

    result = _run(command, _GENERATE_TIMEOUT)
    if result is None:
        return _error("DEPENDENCY_MISSING", "dms is not available")
    rc, out, err = result
    if rc != 0 and _NO_CHANGE_MARKER not in (out + err):
        return _error(
            "ADAPTER_FAILED",
            err.strip() or out.strip() or f"dms matugen generate exited with {rc}",
        )

    return {
        "success": True,
        "state": {
            "action": "regenerate",
            "value": wallpaper,
            "mode": mode,
            "output": out.strip(),
        },
    }
