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


def load_ai_config() -> dict:
    """Load the [ai] configuration table (docs/ai/10 §9, docs/ai/02 §16).

    Precedence: config/ai.toml < ~/.config/omivoid/ai.toml.
    Per-provider tables merge so a user override of one provider keeps
    the other provider's core defaults.
    """
    cfg: dict = {}
    for path in (
        repo_root() / "config" / "ai.toml",
        user_config_dir() / "ai.toml",
    ):
        if not path.is_file():
            continue
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except (tomllib.TOMLDecodeError, OSError):
            continue
        ai = data.get("ai", {})
        if "providers" in ai:
            merged = dict(cfg.get("providers", {}))
            merged.update(
                {str(k): dict(v) for k, v in ai["providers"].items()}
            )
            ai = {**ai, "providers": merged}
        cfg.update({str(k): v for k, v in ai.items()})
    return cfg