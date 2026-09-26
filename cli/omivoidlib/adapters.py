"""Adapter resolution and loading (docs/03 §22, docs/05).

Resolution precedence:

    machine-specific adapter
        ↓
    platform adapter
        ↓
    common adapter

Phase 1 implements platform → common (machine-specific adapters deferred).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from .platform import detect_platform
from .registry import repo_root

# Adapter name → (directory, module file).
# The first segment names the adapter family (common/niri/dms/debian/void).
ADAPTER_LOCATIONS: dict[str, tuple[str, str]] = {
    "app.launch": ("common", "app_launch.py"),
    "command": ("common", "command.py"),
    "niri.native": ("niri", "native.py"),
    "dms.ipc": ("dms", "ipc.py"),
    "dms.theme": ("dms", "theme.py"),
    # Shell components arrive with DMS integration (Stage 11–14).
    "shell.explorer": ("dms", "explorer.py"),
    "shell.palette": ("dms", "palette.py"),
    # AI actions (docs/ai/10 §8–9).
    "ai.pi.open": ("common", "ai_pi_open.py"),
    "ai.ask": ("common", "ai_ask.py"),
    # AI clipboard context actions (docs/ai/10 §31, AI-25).
    "ai.clipboard.explain": ("common", "ai_clipboard_explain.py"),
    "ai.clipboard.summarise": ("common", "ai_clipboard_summarise.py"),
}

# Adapters resolved by the platform → common convention below (no fixed
# location): the file is `adapters/<platform>/<name_underscored>.py`.
CONVENTION_ADAPTERS = {
    "service.restart",
}

KNOWN_ADAPTERS = set(ADAPTER_LOCATIONS) | CONVENTION_ADAPTERS


def resolve_adapter_path(adapter_name: str) -> Path | None:
    """Resolve an adapter name to a module file, or None if unavailable."""
    if adapter_name in ADAPTER_LOCATIONS:
        subdir, filename = ADAPTER_LOCATIONS[adapter_name]
        return repo_root() / "adapters" / subdir / filename

    # Fallback convention: name.first → adapters/<platform|common>/name_first.py
    filename = adapter_name.replace(".", "_") + ".py"
    for d in (
        repo_root() / "adapters" / detect_platform(),
        repo_root() / "adapters" / "common",
    ):
        p = d / filename
        if p.is_file():
            return p
    return None


def load_adapter(adapter_name: str):
    """Load an adapter module by name.

    Raises KeyError if the adapter is not available.
    """
    path = resolve_adapter_path(adapter_name)
    if path is None or not path.is_file():
        raise KeyError(adapter_name)
    spec = importlib.util.spec_from_file_location(
        f"omivoid_adapter_{adapter_name.replace('.', '_')}", path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module