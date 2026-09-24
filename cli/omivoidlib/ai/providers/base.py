"""Provider interface contract (docs/ai/01-provider-interface.md).

Each provider module exposes:

    NAME: str
    status() -> dict
    ask(prompt: str, timeout: float | None = None) -> dict

status() returns:

    {"provider": name, "state": "available"|"unavailable"|"misconfigured",
     "detail": str}

ask() returns:

    {"success": True, "response": str}
    {"success": False, "error": {"code": str, "message": str}}

Shared helpers for building status dicts.
"""

from __future__ import annotations

import shutil


def binary_available(name: str) -> bool:
    """Return True if the named binary is in PATH."""
    return shutil.which(name) is not None


def available(provider: str, detail: str = "") -> dict:
    """Build an 'available' status dict."""
    return {"provider": provider, "state": "available", "detail": detail}


def unavailable(provider: str, detail: str) -> dict:
    """Build an 'unavailable' status dict."""
    return {"provider": provider, "state": "unavailable", "detail": detail}


def misconfigured(provider: str, detail: str) -> dict:
    """Build a 'misconfigured' status dict."""
    return {"provider": provider, "state": "misconfigured", "detail": detail}