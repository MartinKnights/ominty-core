"""Ollama provider adapter — local model runner (docs/ai/00 §7, §15).

Provides a fully local, offline-capable AI path through the Ollama HTTP
API (default endpoint http://localhost:11434).

Readiness: binary in PATH + server reachable (/api/tags). Asks use the
generate API with streaming disabled.

The default model and endpoint are configurable:

    [ai.providers.ollama]
    endpoint = "http://127.0.0.1:11434"
    model = "gemma3:4b"
    think = false

The endpoint resolves in order: user config endpoint →
``OMINTY_OLLAMA_ENDPOINT`` → ``OLLAMA_HOST`` → the default above. A bare
``host:port`` value is accepted (``http://`` is prepended). ``think`` is
forwarded to ``/api/generate`` only when set, so reasoning-capable models
(e.g. qwen3.5) can skip the reasoning tax for quick desktop asks.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from ...config import load_ai_config
from .base import available, binary_available, misconfigured, unavailable

NAME = "ollama"

DEFAULT_ENDPOINT = "http://localhost:11434"
DEFAULT_MODEL = "gemma3:4b"

# Default ask timeout in seconds.
DEFAULT_TIMEOUT = 120.0


def _configured_endpoint() -> str | None:
    """Return the configured endpoint, or None (docs/12 §configuration).

    Precedence: user ``[ai.providers.ollama] endpoint`` →
    ``OMINTY_OLLAMA_ENDPOINT`` → ``OLLAMA_HOST``.
    """
    cfg = load_ai_config()
    endpoint = cfg.get("providers", {}).get("ollama", {}).get("endpoint")
    if endpoint:
        return str(endpoint)
    for var in ("OMINTY_OLLAMA_ENDPOINT", "OLLAMA_HOST"):
        value = os.environ.get(var)
        if value:
            return value
    return None


def _endpoint() -> str:
    """Resolve the Ollama base URL (config → env → default)."""
    endpoint = _configured_endpoint()
    if not endpoint:
        return DEFAULT_ENDPOINT
    endpoint = endpoint.rstrip("/")
    if not endpoint.startswith(("http://", "https://")):
        endpoint = "http://" + endpoint
    return endpoint


def _configured_model() -> str | None:
    """Return the configured model name, or None."""
    cfg = load_ai_config()
    model = cfg.get("providers", {}).get("ollama", {}).get("model")
    return str(model) if model else None


def _configured_think() -> bool | None:
    """Return the configured ``think`` flag, or None when unset.

    Reasoning-capable models (e.g. ``qwen3.5``, ``deepseek-r1``) default to
    emitting reasoning tokens, which slows a quick desktop ask. Set
    ``think = false`` to skip that tax; leave unset to keep the model default.
    """
    cfg = load_ai_config()
    value = cfg.get("providers", {}).get("ollama", {}).get("think")
    if isinstance(value, bool):
        return value
    return None


def _server_models() -> list[str]:
    """Return model names from the running server, or [] if unreachable."""
    try:
        with urllib.request.urlopen(f"{_endpoint()}/api/tags", timeout=3) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, OSError, ValueError):
        return []
    return [str(m.get("name", "")) for m in data.get("models", []) if m.get("name")]


def status() -> dict:
    """Determine Ollama availability (available/unavailable/misconfigured)."""
    if not binary_available("ollama"):
        return unavailable(NAME, "ollama binary not found in PATH")
    models = _server_models()
    if not models:
        return misconfigured(NAME, f"ollama server not reachable at {_endpoint()}")
    return available(NAME, f"server running, {len(models)} model(s)")


def ask(prompt: str, timeout: float | None = None) -> dict:
    """Ask a local model via the Ollama generate API."""
    if not binary_available("ollama"):
        return {
            "success": False,
            "error": {
                "code": "PROVIDER_UNAVAILABLE",
                "message": "ollama binary not found in PATH",
            },
        }

    models = _server_models()
    if not models:
        return {
            "success": False,
            "error": {
                "code": "PROVIDER_UNAVAILABLE",
                "message": f"ollama server not reachable at {_endpoint()}",
            },
        }

    chosen = _configured_model() or models[0] or DEFAULT_MODEL
    body: dict = {"model": chosen, "prompt": prompt, "stream": False}
    think = _configured_think()
    if think is not None:
        body["think"] = think
    payload = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{_endpoint()}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout or DEFAULT_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": {
                "code": "PROVIDER_FAILED",
                "message": f"ollama HTTP {e.code}: {e.reason}",
            },
        }
    except urllib.error.URLError as e:
        if isinstance(e.reason, TimeoutError):
            return {
                "success": False,
                "error": {
                    "code": "PROVIDER_TIMEOUT",
                    "message": "ollama did not respond within the timeout",
                },
            }
        return {
            "success": False,
            "error": {"code": "PROVIDER_FAILED", "message": str(e.reason)},
        }
    except OSError as e:
        return {
            "success": False,
            "error": {"code": "PROVIDER_FAILED", "message": str(e)},
        }

    response = str(data.get("response", "")).strip()
    if not response:
        return {
            "success": False,
            "error": {
                "code": "PROVIDER_FAILED",
                "message": "ollama returned an empty response",
            },
        }
    return {"success": True, "response": response, "model": chosen}