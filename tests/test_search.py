"""Tests for the universal action search backend (docs/10 §16)."""

from omivoidlib.registry import Action, Registry
from omivoidlib.search import search_actions


def make_registry() -> Registry:
    actions = [
        Action(
            id="app.terminal.open",
            name="Open Terminal",
            description="Open the configured primary terminal.",
            category="Applications",
            risk="low",
            confirmation="none",
            keywords=["terminal", "console", "shell", "command"],
            keys=["Super+Enter"],
            primary_key="Super+Enter",
            adapter="app.launch",
            arguments={"role": "terminal"},
            contexts=["desktop"],
            platforms=["all"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="window.close",
            name="Close Window",
            description="Close the focused window.",
            category="Windows",
            risk="low",
            confirmation="none",
            keywords=["close", "quit", "kill"],
            keys=["Super+Q"],
            primary_key="Super+Q",
            adapter="niri.native",
            arguments={"action": "close-window"},
            contexts=["window"],
            platforms=["niri"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="window.focus.left",
            name="Focus Left",
            description="Focus the window to the left.",
            category="Navigation",
            risk="low",
            confirmation="none",
            keywords=["focus", "left", "column"],
            keys=["Super+Left"],
            primary_key="Super+Left",
            adapter="niri.native",
            arguments={"action": "focus-column-left"},
            contexts=["window"],
            platforms=["niri"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="network.bluetooth.open",
            name="Open Bluetooth Controls",
            description="Open the Bluetooth settings.",
            category="Network",
            risk="low",
            confirmation="none",
            keywords=["bluetooth", "wireless"],
            keys=["Super+Ctrl+B"],
            primary_key="Super+Ctrl+B",
            adapter="app.launch",
            arguments={"role": "bluetooth"},
            contexts=["desktop"],
            platforms=["all"],
            discoverable=True,
            palette=True,
            ai_accessible=True,
            voice_accessible=False,
            source_file="test",
        ),
        Action(
            id="internal.debug",
            name="Debug",
            description="Internal debugging action.",
            category="Developer",
            risk="high",
            confirmation="always",
            keywords=["debug"],
            keys=[],
            primary_key=None,
            adapter="command",
            arguments={},
            contexts=["desktop"],
            platforms=["all"],
            discoverable=False,
            palette=False,
            ai_accessible=False,
            voice_accessible=False,
            source_file="test",
        ),
    ]
    return Registry(actions={a.id: a for a in actions})


def test_search_by_name():
    results = search_actions(make_registry(), "terminal")
    assert [r["id"] for r in results] == ["app.terminal.open"]


def test_search_by_keyword():
    results = search_actions(make_registry(), "bluetooth")
    assert [r["id"] for r in results] == ["network.bluetooth.open"]


def test_search_by_category():
    results = search_actions(make_registry(), "network")
    assert [r["id"] for r in results] == ["network.bluetooth.open"]


def test_search_multi_term_and():
    results = search_actions(make_registry(), "focus left")
    assert [r["id"] for r in results] == ["window.focus.left"]
    # AND semantics: no action matches both terms.
    assert search_actions(make_registry(), "move window") == []


def test_search_ranking():
    # "close" matches window.close (name+keyword) and app.terminal.open
    # (keyword "command" → no; keyword "close"? no). window.close should rank first.
    results = search_actions(make_registry(), "close")
    assert results[0]["id"] == "window.close"


def test_search_palette_only_excludes_non_palette():
    results = search_actions(make_registry(), "debug", palette_only=True)
    assert results == []
    results = search_actions(make_registry(), "debug")
    assert results == []  # discoverable=false also excluded by default


def test_search_empty_query():
    assert search_actions(make_registry(), "") == []
    assert search_actions(make_registry(), "   ") == []


def test_search_no_match():
    assert search_actions(make_registry(), "nonexistent") == []


def test_search_result_shape():
    results = search_actions(make_registry(), "window")
    for entry in results:
        assert set(entry) == {
            "id", "name", "description", "category", "binding", "keywords"
        }


def test_search_application_actions():
    # app.* namespace actions are searchable (docs/10 §16).
    results = search_actions(make_registry(), "app")
    assert "app.terminal.open" in [r["id"] for r in results]