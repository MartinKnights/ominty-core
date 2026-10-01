"""Pi provider adapter (docs/ai/02-pi-integration.md §10).

All Pi-specific invocation details live here. Ominty interacts with Pi
through the provider contract (docs/ai/01 §1).

Readiness: binary in PATH + provider ready (`pi auth check`) with a
plausible key and a reachable base URL. Asks use non-interactive mode:

    pi --print --mode text --no-session --no-tools "<prompt>"

--no-tools keeps Phase A asks read-only (least capability, AGENTS.md §16).

Discrepancy note (docs/ai/10 §5): `pi auth check` reports "ready" merely
because a key env var exists. A placeholder key (e.g. "anything") or an
unreachable OPENAI_API_BASE still fails real requests, so status() also
validates key plausibility and base reachability.
"""

from __future__ import annotations

import os
import subprocess
import urllib.error
import urllib.request

from .base import available, binary_available, misconfigured, unavailable

NAME = "pi"

# Provider name probed by `pi auth check`.
PI_PROVIDER = "openai"

# Default ask timeout in seconds.
DEFAULT_TIMEOUT = 120.0

# Known placeholder key values that must never be treated as credentials.
_PLACEHOLDER_KEYS = {
    "anything",
    "your-api-key",
    "your_key_here",
    "sk-xxx",
    "changeme",
    "placeholder",
}


def _key_plausible() -> bool:
    """Return True if OPENAI_API_KEY looks like a real credential."""
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return False
    if key.lower() in _PLACEHOLDER_KEYS:
        return False
    return len(key) >= 20


def _base_reachable() -> bool:
    """Return True if OPENAI_API_BASE (when set) is reachable."""
    base = os.environ.get("OPENAI_API_BASE")
    if not base:
        return True  # no custom base configured
    try:
        urllib.request.urlopen(base, timeout=3)
        return True
    except urllib.error.HTTPError:
        return True  # server responded (any status) → reachable
    except (urllib.error.URLError, OSError):
        return False


def _auth_ready() -> bool:
    """Return True if Pi reports the configured provider ready."""
    try:
        result = subprocess.run(
            ["pi", "auth", "check", "--provider", PI_PROVIDER],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0 and "ready" in result.stdout.lower()
    except (OSError, subprocess.TimeoutExpired):
        return False


def status() -> dict:
    """Determine Pi availability (available/unavailable/misconfigured)."""
    if not binary_available("pi"):
        return unavailable(NAME, "pi binary not found in PATH")
    if not _base_reachable():
        return misconfigured(
            NAME,
            f"OPENAI_API_BASE '{os.environ.get('OPENAI_API_BASE')}' is not reachable",
        )
    if _auth_ready() and _key_plausible():
        return available(NAME, f"provider '{PI_PROVIDER}' ready")
    if _key_plausible():
        return available(NAME, "OPENAI_API_KEY set")
    return misconfigured(
        NAME,
        "pi present but no usable provider credentials "
        "(check OPENAI_API_KEY / provider auth)",
    )


def ask(prompt: str, timeout: float | None = None) -> dict:
    """Ask Pi non-interactively and return the text response."""
    if not binary_available("pi"):
        return {
            "success": False,
            "error": {
                "code": "PROVIDER_UNAVAILABLE",
                "message": "pi binary not found in PATH",
            },
        }

    cmd = [
        "pi",
        "--print",
        "--mode", "text",
        "--no-session",
        "--no-tools",
        prompt,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout or DEFAULT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": {
                "code": "PROVIDER_TIMEOUT",
                "message": "pi did not respond within the timeout",
            },
        }
    except OSError as e:
        return {
            "success": False,
            "error": {"code": "PROVIDER_FAILED", "message": str(e)},
        }

    if result.returncode != 0:
        return {
            "success": False,
            "error": {
                "code": "PROVIDER_FAILED",
                "message": result.stderr.strip() or f"pi exited with {result.returncode}",
            },
        }

    return {"success": True, "response": result.stdout.strip()}