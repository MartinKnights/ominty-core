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

from omintylib.ai import ask, capabilities, default_provider, provider_status
from omintylib.ai import policy
from omintylib.ai.actions import run_action_as_ai
from omintylib.ai.capabilities import list_capabilities
from omintylib.ai.providers import resolve_provider
from omintylib.registry import Action, Registry
from omintylib.runner import run_action


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
        patch("omintylib.ai.providers.pi.binary_available", return_value=True),
        patch("omintylib.ai.providers.pi._auth_ready", return_value=True),
        patch("omintylib.ai.providers.pi._base_reachable", return_value=True),
        patch("omintylib.ai.providers.pi._key_plausible", return_value=True),
    ):
        st = provider_status("pi")
    assert st["state"] == "available"


def test_pi_status_unavailable():
    with patch("omintylib.ai.providers.pi.binary_available", return_value=False):
        st = provider_status("pi")
    assert st["state"] == "unavailable"


def test_pi_status_misconfigured():
    with (
        patch("omintylib.ai.providers.pi.binary_available", return_value=True),
        patch("omintylib.ai.providers.pi._auth_ready", return_value=False),
        patch("omintylib.ai.providers.pi._base_reachable", return_value=True),
        patch("omintylib.ai.providers.pi._key_plausible", return_value=False),
    ):
        st = provider_status("pi")
    assert st["state"] == "misconfigured"


def test_pi_status_unreachable_base():
    with (
        patch("omintylib.ai.providers.pi.binary_available", return_value=True),
        patch("omintylib.ai.providers.pi._base_reachable", return_value=False),
    ):
        st = provider_status("pi")
    assert st["state"] == "misconfigured"


def test_pi_key_plausible():
    from omintylib.ai.providers.pi import _key_plausible

    with patch.dict("os.environ", {"OPENAI_API_KEY": "anything"}):
        assert _key_plausible() is False
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-" + "x" * 40}):
        assert _key_plausible() is True
    with patch.dict("os.environ", {}, clear=True):
        assert _key_plausible() is False


def test_ollama_status_available():
    with (
        patch("omintylib.ai.providers.ollama.binary_available", return_value=True),
        patch(
            "omintylib.ai.providers.ollama._server_models",
            return_value=["gemma3:4b"],
        ),
    ):
        st = provider_status("ollama")
    assert st["state"] == "available"


def test_ollama_status_misconfigured():
    with (
        patch("omintylib.ai.providers.ollama.binary_available", return_value=True),
        patch("omintylib.ai.providers.ollama._server_models", return_value=[]),
    ):
        st = provider_status("ollama")
    assert st["state"] == "misconfigured"


def test_ollama_status_unavailable():
    with patch("omintylib.ai.providers.ollama.binary_available", return_value=False):
        st = provider_status("ollama")
    assert st["state"] == "unavailable"


# ── Generic ask ────────────────────────────────────────────────────────────

def test_ask_provider_not_found():
    result = ask("hello", provider="no-such-provider")
    assert result["success"] is False
    assert result["error"]["code"] == "PROVIDER_NOT_FOUND"


def test_ask_provider_unavailable():
    with patch("omintylib.ai.providers.pi.binary_available", return_value=False):
        result = ask("hello", provider="pi")
    assert result["success"] is False
    assert result["error"]["code"] == "PROVIDER_UNAVAILABLE"


def test_ask_pi_success():
    with (
        patch("omintylib.ai.providers.pi.binary_available", return_value=True),
        patch("omintylib.ai.providers.pi._auth_ready", return_value=True),
        patch("omintylib.ai.providers.pi._base_reachable", return_value=True),
        patch("omintylib.ai.providers.pi._key_plausible", return_value=True),
        patch(
            "omintylib.ai.providers.pi.ask",
            return_value={"success": True, "response": "hi"},
        ),
    ):
        result = ask("hello", provider="pi")
    assert result["success"] is True
    assert result["response"] == "hi"


def test_ask_ollama_success():
    with (
        patch("omintylib.ai.providers.ollama.binary_available", return_value=True),
        patch(
            "omintylib.ai.providers.ollama._server_models",
            return_value=["gemma3:4b"],
        ),
        patch(
            "omintylib.ai.providers.ollama.ask",
            return_value={"success": True, "response": "hi"},
        ),
    ):
        result = ask("hello", provider="ollama")
    assert result["success"] is True
    assert result["response"] == "hi"


def test_pi_ask_failed():
    with (
        patch("omintylib.ai.providers.pi.binary_available", return_value=True),
        patch("omintylib.ai.providers.pi._auth_ready", return_value=True),
        patch("omintylib.ai.providers.pi._base_reachable", return_value=True),
        patch("omintylib.ai.providers.pi._key_plausible", return_value=True),
        patch(
            "omintylib.ai.providers.pi.subprocess.run",
            return_value=MagicMock(returncode=1, stdout="", stderr="boom"),
        ),
    ):
        result = ask("hello", provider="pi")
    assert result["success"] is False
    assert result["error"]["code"] == "PROVIDER_FAILED"


def test_pi_ask_timeout():
    with (
        patch("omintylib.ai.providers.pi.binary_available", return_value=True),
        patch("omintylib.ai.providers.pi._auth_ready", return_value=True),
        patch("omintylib.ai.providers.pi._base_reachable", return_value=True),
        patch("omintylib.ai.providers.pi._key_plausible", return_value=True),
        patch(
            "omintylib.ai.providers.pi.subprocess.run",
            side_effect=subprocess.TimeoutExpired("pi", 1),
        ),
    ):
        result = ask("hello", provider="pi")
    assert result["success"] is False
    assert result["error"]["code"] == "PROVIDER_TIMEOUT"


def test_ollama_ask_timeout():
    with (
        patch("omintylib.ai.providers.ollama.binary_available", return_value=True),
        patch(
            "omintylib.ai.providers.ollama._server_models",
            return_value=["gemma3:4b"],
        ),
        patch(
            "omintylib.ai.providers.ollama.urllib.request.urlopen",
            side_effect=urllib.error.URLError(TimeoutError("timeout")),
        ),
    ):
        result = ask("hello", provider="ollama")
    assert result["success"] is False
    assert result["error"]["code"] == "PROVIDER_TIMEOUT"


def test_default_provider():
    with patch(
        "omintylib.ai.load_ai_config",
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
        "omintylib.ai.ask",
        return_value={"success": True, "response": "hi"},
    ):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is True
    assert result["state"]["response"] == "hi"


def test_ai_ask_adapter_provider_error():
    action = make_action(adapter="ai.ask", arguments={"prompt": "hello"})
    with patch(
        "omintylib.ai.ask",
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
    with patch("omintylib.config.load_apps_config", return_value={}):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "ACTION_UNAVAILABLE"


def test_ai_pi_open_terminal_missing():
    action = make_action(adapter="ai.pi.open")
    with (
        patch(
            "omintylib.config.load_apps_config",
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
            "omintylib.config.load_apps_config",
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
            "omintylib.config.load_apps_config",
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
    with patch("omintylib.ai._capabilities.list_capabilities", return_value=[{"id": "x"}]):
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
        "omintylib.ai.actions.run_action",
        return_value={"action": "x.next", "success": True, "state": {}},
    ) as runner:
        result = run_action_as_ai("x.next", confirmed=True,
                                  registry=registry_with(a))
    assert result["success"] is True
    runner.assert_called_once()


def test_run_action_as_ai_allowed_executes():
    a = make_action(id="x.open", ai_accessible=True)
    with patch(
        "omintylib.ai.actions.run_action",
        return_value={"action": "x.open", "success": True, "state": {}},
    ):
        result = run_action_as_ai("x.open", registry=registry_with(a))
    assert result["success"] is True


def test_run_action_as_ai_unavailable_passthrough():
    """Runner-level failures (e.g. ACTION_UNAVAILABLE) pass through."""
    a = make_action(id="x.open", ai_accessible=True)
    with patch(
        "omintylib.ai.actions.run_action",
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
    from omintylib.registry import load_registry

    registry = load_registry()
    action = registry.actions.get("theme.wallpaper.next")
    assert action is not None
    assert action.confirmation == "ai-only"
    assert policy.evaluate(action)["decision"] == "confirm"


# ── Super+A AI namespace (docs/ai/10 §23–25, AI-18/19/20) ─────────────────

def test_ai_namespace_in_real_registry():
    """Integration: the Super+A AI namespace is declared."""
    from omintylib.registry import load_registry

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


# ── Context system (docs/ai/05, AI-22) ─────────────────────────────────

def test_context_object_to_dict():
    from omintylib.ai.context import ContextObject

    ctx = ContextObject(
        type="clipboard", content="hello", source="clipboard",
        metadata={"bytes": 5},
    )
    d = ctx.to_dict()
    assert d["type"] == "clipboard"
    assert d["content"] == "hello"
    assert d["source"] == "clipboard"
    assert d["metadata"] == {"bytes": 5}


def test_collect_clipboard_missing_wl_paste():
    from omintylib.ai.context import collect_clipboard

    with patch("omintylib.ai.context.shutil.which", return_value=None):
        result = collect_clipboard()
    assert result["success"] is False
    assert result["error"]["code"] == "CONTEXT_UNAVAILABLE"


def test_collect_clipboard_empty():
    from omintylib.ai.context import collect_clipboard

    with (
        patch("omintylib.ai.context.shutil.which", return_value="/usr/bin/wl-paste"),
        patch(
            "omintylib.ai.context.subprocess.run",
            return_value=MagicMock(returncode=1, stdout="", stderr=""),
        ),
    ):
        result = collect_clipboard()
    assert result["success"] is False
    assert result["error"]["code"] == "CONTEXT_UNAVAILABLE"


def test_collect_clipboard_success():
    from omintylib.ai.context import collect_clipboard

    with (
        patch("omintylib.ai.context.shutil.which", return_value="/usr/bin/wl-paste"),
        patch(
            "omintylib.ai.context.subprocess.run",
            return_value=MagicMock(returncode=0, stdout="selected text", stderr=""),
        ),
    ):
        result = collect_clipboard()
    assert result["success"] is True
    assert result["context"].type == "clipboard"
    assert result["context"].content == "selected text"
    assert result["context"].source == "clipboard"


def test_collect_clipboard_too_large():
    from omintylib.ai.context import collect_clipboard

    big = "x" * (32 * 1024 + 1)
    with (
        patch("omintylib.ai.context.shutil.which", return_value="/usr/bin/wl-paste"),
        patch(
            "omintylib.ai.context.subprocess.run",
            return_value=MagicMock(returncode=0, stdout=big, stderr=""),
        ),
    ):
        result = collect_clipboard()
    assert result["success"] is False
    assert result["error"]["code"] == "CONTEXT_TOO_LARGE"


def test_collect_selection_unavailable():
    """Selection is CLIPBOARD FALLBACK — never faked (AI-24)."""
    from omintylib.ai.context import collect_selection

    result = collect_selection()
    assert result["success"] is False
    assert result["error"]["code"] == "CONTEXT_UNAVAILABLE"


def test_build_prompt_no_context():
    from omintylib.ai.context import build_prompt

    assert build_prompt("hello", []) == "hello"


def test_build_prompt_with_context():
    from omintylib.ai.context import ContextObject, build_prompt

    ctx = ContextObject(type="clipboard", content="abc", source="clipboard")
    prompt = build_prompt("Explain this.", [ctx])
    assert "[CLIPBOARD CONTEXT]" in prompt
    assert "abc" in prompt
    assert prompt.endswith("Explain this.")


def test_ask_with_context_composes_prompt():
    """ask() renders context blocks into the provider prompt (docs/ai/05 §38)."""
    from omintylib.ai.context import ContextObject

    ctx = ContextObject(type="clipboard", content="abc", source="clipboard")
    with (
        patch("omintylib.ai.providers.pi.binary_available", return_value=True),
        patch("omintylib.ai.providers.pi._auth_ready", return_value=True),
        patch("omintylib.ai.providers.pi._base_reachable", return_value=True),
        patch("omintylib.ai.providers.pi._key_plausible", return_value=True),
        patch("omintylib.ai.providers.pi.ask") as pi_ask,
    ):
        pi_ask.return_value = {"success": True, "response": "ok"}
        result = ask("Explain this.", provider="pi", context=[ctx])
    assert result["success"] is True
    prompt_arg = pi_ask.call_args[0][0]
    assert "[CLIPBOARD CONTEXT]" in prompt_arg
    assert prompt_arg.endswith("Explain this.")


# ── ai.clipboard.* adapters (docs/ai/10 §31, AI-25) ────────────────────

def test_clipboard_explain_context_unavailable():
    action = make_action(adapter="ai.clipboard.explain")
    with patch("omintylib.ai.context.shutil.which", return_value=None):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is False
    assert result["error"]["code"] == "CONTEXT_UNAVAILABLE"


def test_clipboard_explain_success():
    action = make_action(adapter="ai.clipboard.explain")
    with (
        patch("omintylib.ai.context.shutil.which", return_value="/usr/bin/wl-paste"),
        patch(
            "omintylib.ai.context.subprocess.run",
            return_value=MagicMock(returncode=0, stdout="some code", stderr=""),
        ),
        patch(
            "omintylib.ai.clipboard_actions.ai_ask",
            return_value={"success": True, "response": "explanation"},
        ),
    ):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is True
    assert result["state"]["response"] == "explanation"


def test_clipboard_summarise_success():
    action = make_action(adapter="ai.clipboard.summarise")
    with (
        patch("omintylib.ai.context.shutil.which", return_value="/usr/bin/wl-paste"),
        patch(
            "omintylib.ai.context.subprocess.run",
            return_value=MagicMock(returncode=0, stdout="long text", stderr=""),
        ),
        patch(
            "omintylib.ai.clipboard_actions.ai_ask",
            return_value={"success": True, "response": "summary"},
        ),
    ):
        result = run_action(action.id, registry_with(action))
    assert result["success"] is True
    assert result["state"]["response"] == "summary"


def test_clipboard_actions_in_real_registry():
    """Integration: the clipboard explain/summarise actions are declared."""
    from omintylib.registry import load_registry

    registry = load_registry()
    explain = registry.actions.get("ai.clipboard.explain")
    assert explain is not None
    assert explain.keys == ["Super+A,E"]
    assert explain.adapter == "ai.clipboard.explain"
    assert explain.contexts == ["clipboard"]
    assert explain.ai_accessible is False

    summarise = registry.actions.get("ai.clipboard.summarise")
    assert summarise is not None
    assert summarise.keys == ["Super+A,S"]
    assert summarise.adapter == "ai.clipboard.summarise"
    assert summarise.contexts == ["clipboard"]
    assert summarise.ai_accessible is False


# ── Project discovery + context (docs/ai/06, AI-26/27) ─────────────────

def test_is_secret():
    """Obvious credential material is recognised (docs/ai/06 §29)."""
    from omintylib.ai.project import is_secret

    assert is_secret(".env")
    assert is_secret(".env.production")
    assert is_secret("id_rsa")
    assert is_secret("credentials.json")
    assert is_secret("server.key")
    assert is_secret("secrets")
    assert not is_secret("AGENTS.md")
    assert not is_secret("main.py")
    assert not is_secret("docs")


def test_discover_project_explicit(tmp_path):
    """Explicit root always wins (docs/ai/06 §6)."""
    from omintylib.ai.project import discover_project

    root = tmp_path / "ominty-core"
    root.mkdir()
    result = discover_project(cwd="/tmp", explicit=str(root))
    assert result["success"] is True
    assert result["method"] == "explicit"
    assert result["name"] == "ominty-core"


def test_discover_project_explicit_invalid():
    from omintylib.ai.project import discover_project

    result = discover_project(cwd="/tmp", explicit="/nonexistent/xyz")
    assert result["success"] is False
    assert result["error"]["code"] == "INVALID_ARGUMENT"


def test_discover_project_agents_walkup(tmp_path):
    """Nearest AGENTS.md defines the project boundary (docs/ai/06 §8–9)."""
    from omintylib.ai.project import discover_project

    root = tmp_path / "proj"
    root.mkdir()
    (root / "AGENTS.md").write_text("# rules\n")
    sub = root / "src" / "deep"
    sub.mkdir(parents=True)

    result = discover_project(cwd=str(sub))
    assert result["success"] is True
    assert result["method"] == "AGENTS.md"
    assert result["root"] == root


def test_discover_project_git(tmp_path):
    from omintylib.ai.project import discover_project

    root = tmp_path / "repo"
    root.mkdir()
    with (
        patch("omintylib.ai.project._find_agents_md", return_value=None),
        patch("omintylib.ai.project._git_root", return_value=root),
    ):
        result = discover_project(cwd=str(root))
    assert result["success"] is True
    assert result["method"] == "git"
    assert result["root"] == root


def test_discover_project_cwd_fallback(tmp_path):
    from omintylib.ai.project import discover_project

    d = tmp_path / "plain"
    d.mkdir()
    with (
        patch("omintylib.ai.project._find_agents_md", return_value=None),
        patch("omintylib.ai.project._git_root", return_value=None),
    ):
        result = discover_project(cwd=str(d))
    assert result["success"] is True
    assert result["method"] == "cwd"
    assert result["root"] == d


def test_collect_project_secret_exclusion(tmp_path):
    """Project context never auto-ingests secret material (AI-28)."""
    from omintylib.ai.project import collect_project

    root = tmp_path / "proj"
    root.mkdir()
    (root / "AGENTS.md").write_text("# rules\n")
    (root / "main.py").write_text("print('hi')\n")
    (root / ".env").write_text("API_KEY=super-secret\n")
    (root / "server.key").write_text("PRIVATE KEY\n")
    (root / "credentials.json").write_text('{"token": "x"}\n')
    (root / "docs").mkdir()

    with patch("omintylib.ai.project._git_state", return_value=None):
        result = collect_project(cwd=str(root))
    assert result["success"] is True
    ctx = result["context"]
    assert ctx.type == "project"
    content = ctx.content
    # identity + instructions present
    assert "Project: proj" in content
    assert "# rules" in content
    # structure lists main.py and docs/ but never secret files
    assert "- main.py" in content
    assert "- docs/" in content
    assert ".env" not in content
    assert "server.key" not in content
    assert "credentials.json" not in content
    # secret content never appears
    assert "super-secret" not in content
    assert "PRIVATE KEY" not in content


def test_collect_project_no_git_degrades(tmp_path):
    """Git absence degrades gracefully (docs/ai/06 §17)."""
    from omintylib.ai.project import collect_project

    root = tmp_path / "proj"
    root.mkdir()
    (root / "AGENTS.md").write_text("# rules\n")
    with patch("omintylib.ai.project._git_state", return_value=None):
        result = collect_project(cwd=str(root))
    assert result["success"] is True
    assert result["context"].metadata["git"] is None
    assert "Git:" not in result["context"].content


def test_collect_project_git_state(tmp_path):
    from omintylib.ai.project import collect_project

    root = tmp_path / "proj"
    root.mkdir()
    (root / "AGENTS.md").write_text("# rules\n")
    with patch(
        "omintylib.ai.project._git_state",
        return_value={"branch": "main", "clean": True},
    ):
        result = collect_project(cwd=str(root))
    assert result["success"] is True
    assert result["context"].metadata["git"] == {"branch": "main", "clean": True}
    assert "Git: main (clean)" in result["context"].content


def test_read_agents_md_truncation(tmp_path):
    """Large AGENTS.md is bounded with an explicit pointer (AI-27)."""
    from omintylib.ai.project import MAX_INSTRUCTIONS_BYTES, _read_agents_md

    p = tmp_path / "AGENTS.md"
    p.write_text("x" * (MAX_INSTRUCTIONS_BYTES + 500))
    out = _read_agents_md(p)
    assert out is not None
    assert "truncated" in out
    assert str(p) in out
    assert len(out.encode("utf-8")) < MAX_INSTRUCTIONS_BYTES + 200


def test_ask_with_project_context(tmp_path):
    """ask() renders project context into the provider prompt (AI-27)."""
    from omintylib.ai.project import collect_project

    root = tmp_path / "proj"
    root.mkdir()
    (root / "AGENTS.md").write_text("# rules\n")
    with (
        patch("omintylib.ai.providers.pi.binary_available", return_value=True),
        patch("omintylib.ai.providers.pi._auth_ready", return_value=True),
        patch("omintylib.ai.providers.pi._base_reachable", return_value=True),
        patch("omintylib.ai.providers.pi._key_plausible", return_value=True),
        patch("omintylib.ai.providers.pi.ask") as pi_ask,
    ):
        pi_ask.return_value = {"success": True, "response": "ok"}
        collected = collect_project(cwd=str(root))
        assert collected["success"] is True
        result = ask(
            "What is this project?", provider="pi",
            context=[collected["context"]],
        )
    assert result["success"] is True
    prompt_arg = pi_ask.call_args[0][0]
    assert "[PROJECT CONTEXT]" in prompt_arg
    assert "Project: proj" in prompt_arg
    assert prompt_arg.endswith("What is this project?")


# ── Security validation (docs/ai/09 §48, AI-29) ────────────────────────

def test_command_adapter_hostile_argument_not_shell_interpreted(tmp_path):
    """AI-supplied hostile arguments are data, never shell fragments (§33)."""
    marker = tmp_path / "pwned"
    hostile = f"$(touch {marker})"
    action = make_action(
        adapter="command",
        command=["printf", "%s", hostile],
    )
    result = run_action(action.id, registry_with(action))
    assert result["success"] is True
    assert result["state"]["command"] == ["printf", "%s", hostile]
    assert not marker.exists()