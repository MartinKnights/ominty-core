"""Provider registry (docs/ai/01 §2).

Each provider is a module exposing:

    NAME: str
    status() -> dict
    ask(prompt: str, timeout: float | None = None) -> dict

status() returns a status-shaped dict:

    {"provider": name, "state": "available"|"unavailable"|"misconfigured",
     "detail": str}

ask() returns a structured result:

    {"success": True, "response": str}
    {"success": False, "error": {"code": str, "message": str}}
"""

from __future__ import annotations

from . import ollama, pi

PROVIDERS: dict[str, object] = {
    "pi": pi,
    "ollama": ollama,
}


def resolve_provider(name: str):
    """Return the provider module for a name, or None if unknown."""
    return PROVIDERS.get(name)


def provider_status(name: str) -> dict:
    """Return the status dict for a provider (unknown if not registered)."""
    provider = resolve_provider(name)
    if provider is None:
        return {
            "provider": name,
            "state": "unknown",
            "detail": f"no provider '{name}'",
        }
    return provider.status()


def list_providers() -> list[dict]:
    """Return status for every registered provider."""
    return [provider_status(name) for name in sorted(PROVIDERS)]