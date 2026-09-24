"""AI provider, adapter and capability tests — docs/ai/10 §6–16.

Covers:
- provider resolution (resolve_provider)
- provider status (pi, ollama, unknown)
- generic ask (success, PROVIDER_NOT_FOUND, PROVIDER_UNAVAILABLE,
  PROVIDER_FAILED, PROVIDER_TIMEOUT)
- ai.ask adapter (missing prompt, success, provider error)
- ai.pi.open adapter (missing role, missing terminal, missing pi, success)
- capability catalogue (ai_accessible filter, ai.* exclusion, sorting)
"""

from __future__ import annotations

import subprocess
import urllib.error
from unittest.mock import MagicMock, patch

from omivoidlib.ai import ask, capabilities, default_provider, provider_status
from omivoidlib.ai import policy
from omivoidlib.ai.actions import run_action_as_ai
from omivoidlib.ai.capabilities import list_capabilities
from omivoidlib.ai.providers import resolve_provider
from omivoidlib.registry import Action, Registry
from omivoidlib.runner import run_action


def make_action(**overrides) -> Action:
    base = dict(
        id="ai.test.ask",
        name="Test",
        description="d",
        category="c",
        risk="routine",
        confirmation="never",
        keywords=[],
        keys=[],
        adapter=None,
        arguments={},
        command=None,
        contexts=["global"],
        platforms=["common"],
        requires=[],
        discoverable=True,
        palette=True,
        ai_accessible=False,
        voice_accessible=False,
    )
    base.update(overrides)
    return Action(**base)


def registry_with(*actions: Action) -> Registry:
    reg = Registry()
    for a in actions:
        reg.actions[a.id] = a
    return reg


# ── Provider resolution ────────────────────────────────────────────────────

def test_resolve_provider_pi():
    assert resolve_provider("pi") is not None


def test_resolve_provider_ollama():
    assert resolve_provider("ollama") is not None


def test_resolve_provider_unknown():
    assert resolve_provider("no-such-provider") is None


# ── Provider status ────────────────────────────────────────────────────────

def test_provider_status_unknown():
    st = provider_status("no-such-provider")
    assert st["state"] == "unknown"


def test_pi_status_available():
    with (
        patch("omivoidlib.ai.providers.pi.binary_available", return_value=True),
        patch("omivoidlib.ai.providers.pi._auth_ready", return_value=True),
        patch("omivoidlib.ai.providers.pi._base_reachable", return_value=True),
        patch("omivoidlib.ai.providers.pi._key_plausible", return_value=True),
    ):
        st = provider_status("pi")
    assert st["state"] == "available"


def test_pi_status_unavailable():
    with patch("omivoidlib.ai.providers.pi.binary_available", return_value=False):
        st = provider_status("pi")
    assert st["state"] == "unavailable"


def test_pi_status_misconfigured():
    with (
        patch("omivoidlib.ai.providers.pi.binary_available", return_value=True),
        patch("omivoidlib.ai.providers.pi._auth_ready", return_value=False),
        patch("omivoidlib.ai.providers.pi._base_reachable", return_value=True),
        patch("omivoidlib.ai.providers.pi._key_plausible", return_value=False),
    ):
        st = provider_status("pi")
    assert st["state"] == "misconfigured"


def test_pi_status_unreachable_base():
    with (
        patch("omivoidlib.ai.providers.pi.binary_available", return_value=True),
        patch("omivoidlib.ai.providers.pi._base_reachable", return_value=False),
    ):
        st = provider_status("pi")
    assert st["state"] == "misconfigured"


def test_pi_key_plausible():
    from omivoidlib.ai.providers.pi import _key_plausible

    with patch.dict("os.environ", {"OPENAI_API_KEY": "anything"}):
        assert _key_plausible() is False
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-" + "x" * 40}):
        assert _key_plausible() is True
    with patch.dict("os.environ", {}, clear=True):
        assert _key_plausible() is False


def test_ollama_status_available():
    with (
        patch("omivoidlib.ai.providers.ollama.binary_available", return_value=True),
        patch(
            "omivoidlib.ai.providers.ollama._server_models",
            return_value=["gemma3:4b"],
        ),
    ):
        st = provider_status("ollama")
    assert st["state"] == "available"


def test_ollama_status_misconfigured():
    with (
        patch("omivoidlib.ai.providers.ollama.binary_available", return_value=True),
        patch("omivoidlib.ai.providers.ollama._server_models", return_value=[]),
    ):
        st = provider_status("ollama")
    assert st["state"] == "misconfigured"


def test_ollama_status_unavailable():
    with patch("omivoidlib.ai.providers.ollama.binary_available", return_value=False):
        st = provider_status("ollama")
    assert st["state"] == "unavailable"


# ── Generic ask ────────────────────────────────────────────────────────────

def test_ask_provider_not_found():
    result = ask("hello", provider="no-such-provider")
    assert result["success"] is False
    assert result["error"]["code"] == "PROVIDER_NOT_FOUND"


def test_ask_provider_unavailable():
    with patch("omivoidlib.ai.providers.pi.binary_available", return_value=False):
        result = ask("hello", provider="pi")
    assert result["success"] is False
    assert result["error"]["code"] == "PROVIDER_UNAVAILABLE"


def test_ask_pi_success():
    with (
        patch("omivoidlib.ai.providers.pi.binary_available", return_value=True),
        patch("omivoidlib.ai.providers.pi._auth_ready", return_value=True),
        patch("omivoidlib.ai.providers.pi._base_reachable", return_value=True),
        patch("omivoidlib.ai.providers.pi._key_plausible", return_value=True),
        patch(
            "omivoidlib.ai.providers.pi.ask",
            return_value={"success": True, "response": "hi"},
        ),
    ):
        result = ask("hello", provider="pi")
    assert result["success"] is True
    assert result["response"] == "hi"


def test_ask_ollama_success():
    with (
        patch("omivoidlib.ai.providers.ollama.binary_available", return_value=True),
        patch(
            "omivoidlib.ai.providers.ollama._server_models",
            return_value=["gemma3:4b"],
        ),
        patch(
            "omivoidlib.ai.providers.ollama.ask",
            return_value={"success": True, "response": "hi"},
        ),
    ):
        result = ask("hello", provider="ollama")
    assert result["success"] is True
    assert result["response"] == "hi"


def test_pi_ask_failed():
    with (
        patch("omivoidlib.ai.providers.pi.binary_available", return_value=True),
        patch("omivoidlib.ai.providers.pi._auth_ready", return_value=True),
        patch("omivoidlib.ai.providers.pi._base_reachable", return_value=True),
        patch("omivoidlib.ai.providers.pi._key_plausible", return_value=True),
        patch(
            "omivoidlib.ai.providers.pi.subprocess.run",
            return_value=MagicMock(returncode=1, stdout="", stderr="boom"),
        ),
    ):
        result = ask("hello", provider="pi")
    assert result["success"] is False
    assert result["error"]["code"] == "PROVIDER_FAILED"


def test_pi_ask_timeout():
    with (
        patch("omivoidlib.ai.providers.pi.binary_available", return_value=True),
        patch("omivoidlib.ai.providers.pi._auth_ready", return_value=True),
        patch("omivoidlib.ai.providers.pi._base_reachable", return_value=True),
        patch("omivoidlib.ai.providers.pi._key_plausible", return_value=True),
        patch(
            "omivoidlib.ai.providers.pi.subprocess.run",
            side_effect=subprocess.TimeoutExpired("pi", 1),
        ),
    ):
        result = ask("hello", provider="pi")
    assert result["success"] is False
    assert result["error"]["code"] == "PROVIDER_TIMEOUT"


def test_ollama_ask_timeout():
    with (
        patch("omivoidlib.ai.providers.ollama.binary_available", return_value=True),
        patch(
            "omivoidlib.ai.providers.ollama._server_models",
            return_value=["gemma3:4b"],
        ),
        patch(
            "omivoidlib.ai.providers.ollama.urllib.request.urlopen",
            side_effect=urllib.error.URLError(TimeoutError("timeout")),
        ),
    ):
        result = ask("hello", provider="ollama")
    assert result["success"] is False
    assert result["error"]["code"] == "PROVIDER_TIMEOUT"


def test_default_provider():
    with patch(
        "omivoidlib.ai.load_ai_config",
        return_value={"default_provider": "ollama"},
    ):
        assert default_provider() == "ollama"


# ── ai.ask adapter ─────────────────────────────────────────────────────────

def test_ai_ask_adapter_missing_prompt():
    action = make_action(adapter="ai.ask", arguments={})
    result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "INVALID_ARGUMENT"


def test_ai_ask_adapter_success():
    action = make_action(adapter="ai.ask", arguments={"prompt": "hello"})
    with patch(
        "omivoidlib.ai.ask",
        return_value={"success": True, "response": "hi"},
    ):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is True
    assert result["state"]["response"] == "hi"


def test_ai_ask_adapter_provider_error():
    action = make_action(adapter="ai.ask", arguments={"prompt": "hello"})
    with patch(
        "omivoidlib.ai.ask",
        return_value={
            "success": False,
            "error": {"code": "PROVIDER_UNAVAILABLE", "message": "down"},
        },
    ):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "PROVIDER_UNAVAILABLE"


# ── ai.pi.open adapter ─────────────────────────────────────────────────────

def test_ai_pi_open_missing_role():
    action = make_action(adapter="ai.pi.open")
    with patch("omivoidlib.config.load_apps_config", return_value={}):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "ACTION_UNAVAILABLE"


def test_ai_pi_open_terminal_missing():
    action = make_action(adapter="ai.pi.open")
    with (
        patch(
            "omivoidlib.config.load_apps_config",
            return_value={"terminal": "no-such-term"},
        ),
        patch("shutil.which", return_value=None),
    ):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "DEPENDENCY_MISSING"


def test_ai_pi_open_pi_missing():
    action = make_action(adapter="ai.pi.open")
    with (
        patch(
            "omivoidlib.config.load_apps_config",
            return_value={"terminal": "alacritty"},
        ),
        patch(
            "shutil.which",
            side_effect=lambda name: (
                "/usr/bin/alacritty" if name == "alacritty" else None
            ),
        ),
    ):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "DEPENDENCY_MISSING"


def test_ai_pi_open_success():
    action = make_action(adapter="ai.pi.open")
    with (
        patch(
            "omivoidlib.config.load_apps_config",
            return_value={"terminal": "alacritty"},
        ),
        patch(
            "shutil.which",
            side_effect=lambda name: (
                "/usr/bin/alacritty" if name == "alacritty" else "/usr/bin/pi"
            ),
        ),
        patch("subprocess.Popen") as popen,
    ):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is True
    popen.assert_called_once()


# ── Capability catalogue (docs/ai/04, docs/ai/10 §15–16) ──────────────────

def test_capabilities_filters_ai_accessible():
    """Only actions with ai_accessible=True appear."""
    a1 = make_action(id="x.open", ai_accessible=True)
    a2 = make_action(id="x.close", ai_accessible=False)
    caps = list_capabilities(registry_with(a1, a2))
    assert len(caps) == 1
    assert caps[0]["id"] == "x.open"


def test_capabilities_excludes_ai_recursive():
    """Actions whose IDs start with 'ai.' are excluded (AGENTS.md §18)."""
    a1 = make_action(id="ai.ask", ai_accessible=True)
    a2 = make_action(id="app.browser.open", ai_accessible=True)
    caps = list_capabilities(registry_with(a1, a2))
    assert len(caps) == 1
    assert caps[0]["id"] == "app.browser.open"


def test_capabilities_sorted_by_id():
    """Output is sorted by action id for stable machine-readable output."""
    a1 = make_action(id="z.last", ai_accessible=True)
    a2 = make_action(id="a.first", ai_accessible=True)
    caps = list_capabilities(registry_with(a1, a2))
    assert [c["id"] for c in caps] == ["a.first", "z.last"]


def test_capabilities_empty_registry():
    """An empty registry yields an empty capability list."""
    caps = list_capabilities(Registry())
    assert caps == []


def test_capabilities_includes_policy_metadata():
    """Each capability entry carries risk and confirmation metadata."""
    a = make_action(
        id="test.action",
        ai_accessible=True,
        risk="state-change",
        confirmation="ask",
    )
    caps = list_capabilities(registry_with(a))
    assert caps[0]["risk"] == "state-change"
    assert caps[0]["confirmation"] == "ask"
    assert caps[0]["name"] == "Test"


def test_capabilities_public_interface():
    """The public ai.capabilities() delegates to list_capabilities."""
    a = make_action(id="test.action", ai_accessible=True)
    reg = registry_with(a)
    with patch("omivoidlib.ai._capabilities.list_capabilities", return_value=[{"id": "x"}]):
        result = capabilities()
    assert result == [{"id": "x"}]


# ── AI policy (docs/ai/09, AI-14/AI-16) ───────────────────────────────────

def test_policy_allows_routine_action():
    a = make_action(id="x.open", ai_accessible=True, risk="routine",
                    confirmation="never")
    decision = policy.evaluate(a)
    assert decision["decision"] == "allow"
    assert decision["code"] is None


def test_policy_denies_not_ai_accessible():
    a = make_action(id="x.close", ai_accessible=False)
    decision = policy.evaluate(a)
    assert decision["decision"] == "deny"
    assert decision["code"] == "PERMISSION_DENIED"
    assert decision["reason"] == "not_ai_accessible"


def test_policy_denies_ai_recursion():
    """AI-invoking actions are refused even if marked ai_accessible."""
    a = make_action(id="ai.ask", ai_accessible=True)
    decision = policy.evaluate(a)
    assert decision["decision"] == "deny"
    assert decision["reason"] == "ai_recursion"


def test_policy_denies_forbidden_risk():
    a = make_action(id="x.wipe", ai_accessible=True, risk="destructive")
    decision = policy.evaluate(a)
    assert decision["decision"] == "deny"
    assert decision["reason"] == "risk_not_permitted"


def test_policy_confirms_ai_only():
    a = make_action(id="x.next", ai_accessible=True, risk="state-change",
                    confirmation="ai-only")
    decision = policy.evaluate(a)
    assert decision["decision"] == "confirm"
    assert decision["code"] == "CONFIRMATION_REQUIRED"


def test_policy_confirms_always():
    a = make_action(id="x.next", ai_accessible=True, confirmation="always")
    decision = policy.evaluate(a)
    assert decision["decision"] == "confirm"


def test_policy_interactive_is_not_ai_confirmed():
    """`interactive` scopes confirmation to human surfaces (docs/03 §17)."""
    a = make_action(id="x.next", ai_accessible=True,
                    confirmation="interactive")
    decision = policy.evaluate(a)
    assert decision["decision"] == "allow"


# ── AI action execution (docs/ai/10 §19, AI-13) ───────────────────────────

def test_run_action_as_ai_unknown():
    result = run_action_as_ai("no.such.action", registry=Registry())
    assert result["success"] is False
    assert result["error"]["code"] == "ACTION_NOT_FOUND"


def test_run_action_as_ai_denied_recursion():
    a = make_action(id="ai.ask", ai_accessible=True)
    result = run_action_as_ai("ai.ask", registry=registry_with(a))
    assert result["success"] is False
    assert result["error"]["code"] == "PERMISSION_DENIED"
    assert result["error"]["reason"] == "ai_recursion"


def test_run_action_as_ai_confirmation_required():
    a = make_action(id="x.next", ai_accessible=True, risk="state-change",
                    confirmation="ai-only")
    result = run_action_as_ai("x.next", registry=registry_with(a))
    assert result["success"] is False
    assert result["confirmation_required"] is True
    assert result["error"]["code"] == "CONFIRMATION_REQUIRED"


def test_run_action_as_ai_confirmed_executes():
    a = make_action(id="x.next", ai_accessible=True, risk="state-change",
                    confirmation="ai-only")
    with patch(
        "omivoidlib.ai.actions.run_action",
        return_value={"action": "x.next", "success": True, "state": {}},
    ) as runner:
        result = run_action_as_ai("x.next", confirmed=True,
                                  registry=registry_with(a))
    assert result["success"] is True
    runner.assert_called_once()


def test_run_action_as_ai_allowed_executes():
    a = make_action(id="x.open", ai_accessible=True)
    with patch(
        "omivoidlib.ai.actions.run_action",
        return_value={"action": "x.open", "success": True, "state": {}},
    ):
        result = run_action_as_ai("x.open", registry=registry_with(a))
    assert result["success"] is True


def test_run_action_as_ai_unavailable_passthrough():
    """Runner-level failures (e.g. ACTION_UNAVAILABLE) pass through."""
    a = make_action(id="x.open", ai_accessible=True)
    with patch(
        "omivoidlib.ai.actions.run_action",
        return_value={
            "action": "x.open",
            "success": False,
            "error": {"code": "ACTION_UNAVAILABLE", "message": "no impl"},
        },
    ):
        result = run_action_as_ai("x.open", registry=registry_with(a))
    assert result["error"]["code"] == "ACTION_UNAVAILABLE"


def test_wallpaper_next_is_ai_confirmed_in_real_registry():
    """Integration: the AI-15 confirmation action is configured (real registry)."""
    from omivoidlib.registry import load_registry

    registry = load_registry()
    action = registry.actions.get("theme.wallpaper.next")
    assert action is not None
    assert action.confirmation == "ai-only"
    assert policy.evaluate(action)["decision"] == "confirm"


# ── Super+A AI namespace (docs/ai/10 §23–25, AI-18/19/20) ─────────────────

def test_ai_namespace_in_real_registry():
    """Integration: the Super+A AI namespace is declared."""
    from omivoidlib.registry import load_registry

    registry = load_registry()
    assert "ai" in registry.groups
    assert registry.groups["ai"].prefix == "Super+A"

    menu = registry.actions.get("ai.menu.open")
    assert menu is not None
    assert menu.keys == ["Super+A"]
    assert menu.command == ["dms", "ipc", "call", "spotlight", "openQuery", "!ai "]
    assert menu.ai_accessible is False

    # Chord notation is declared as intent; Niri cannot bind chords
    # (docs/implementation/ai-dms-evaluation.md §6).
    assert "Super+A,A" in registry.actions["ai.ask"].keys
    assert "Super+A,P" in registry.actions["ai.pi.open"].keys

    # AI-invoking actions are not AI-accessible (AGENTS.md §18).
    assert registry.actions["ai.ask"].ai_accessible is False
    assert registry.actions["ai.pi.open"].ai_accessible is False