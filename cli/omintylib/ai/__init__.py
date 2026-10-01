"""Ominty AI layer — public interface (docs/ai/00, docs/ai/01).

    provider_status(name) -> dict
    list_providers() -> list[dict]
    ask(prompt, provider=None, timeout=None) -> dict
    capabilities() -> list[dict]
    default_provider() -> str

The AI layer resolves providers and routes asks. Provider-specific
invocation details live inside each provider adapter (docs/ai/01 §4).
"""

from __future__ import annotations

from ..config import load_ai_config
from . import capabilities as _capabilities
from . import providers
from .context import ContextObject, build_prompt


def default_provider() -> str:
    """Return the configured default provider name (docs/ai/10 §9)."""
    cfg = load_ai_config()
    return str(cfg.get("default_provider", "pi"))


def provider_status(name: str) -> dict:
    """Return the status dict for a provider."""
    return providers.provider_status(name)


def list_providers() -> list[dict]:
    """Return status for every registered provider."""
    return providers.list_providers()


def capabilities() -> list[dict]:
    """Return the AI-accessible capability list (docs/ai/04 §26).

    Derived from the Action Registry — filtered by ``ai_accessible``
    with ``ai.*`` recursion excluded (AGENTS.md §17–18).
    """
    return _capabilities.list_capabilities()


def ask(
    prompt: str,
    provider: str | None = None,
    timeout: float | None = None,
    context: list[ContextObject] | None = None,
) -> dict:
    """Ask a provider and return a structured result.

    Resolution: explicit provider argument → configured default.

    ``context`` is a list of structured context objects (docs/ai/05 §5).
    The AI layer composes them into the provider prompt (docs/ai/05 §38);
    providers themselves remain plain-prompt based in Phase 1.

    Returns:
        {"success": True, "response": str}
        {"success": False, "error": {"code", "message"}}
    """
    name = provider or default_provider()
    module = providers.resolve_provider(name)
    if module is None:
        return {
            "success": False,
            "error": {
                "code": "PROVIDER_NOT_FOUND",
                "message": f"no provider '{name}'",
            },
        }

    st = module.status()
    if st["state"] != "available":
        return {
            "success": False,
            "error": {
                "code": "PROVIDER_UNAVAILABLE",
                "message": (
                    f"provider '{name}' is {st['state']}: "
                    f"{st.get('detail', '')}"
                ),
            },
        }

    if context:
        prompt = build_prompt(prompt, context)

    return module.ask(prompt, timeout=timeout)