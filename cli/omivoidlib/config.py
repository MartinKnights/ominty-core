"""Omivoid configuration loading (docs/12-configuration-layout.md).

Phase 1 loads application roles with precedence:

    core defaults (config/apps.toml)
        ↓
    user configuration (~/.config/omivoid/apps.toml)
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from .registry import repo_root, user_config_dir


def load_apps_config() -> dict[str, str]:
    """Load application roles (role name → executable)."""
    apps: dict[str, str] = {}
    for path in (
        repo_root() / "config" / "apps.toml",
        user_config_dir() / "apps.toml",
    ):
        if not path.is_file():
            continue
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except (tomllib.TOMLDecodeError, OSError):
            continue
        apps.update({str(k): str(v) for k, v in data.get("apps", {}).items()})
    return apps