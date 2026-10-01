"""Tests for the Super+K help data (docs/10 §15, docs/02 §10–12)."""

from omintylib.helpdata import (
    build_help_data,
    format_help_text,
    search_help_data,
)
from omintylib.registry import Action, Registry


def make_registry() -> Registry:
    actions = [
        Action(
            id="app.terminal.open",
            name="Open Terminal",
            description="Open the terminal.",
            category="Applications",
            risk="low",
            confirmation="none",
            keywords=["terminal", "console"],
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
            id="ai.ask",
            name="Ask AI",
            description="Ask the AI assistant.",
            category="AI",
            risk="low",
            confirmation="none",
            keywords=["ask", "assistant"],
            keys=["Super+A,A"],
            primary_key="Super+A,A",
            adapter="ai.ask",
            arguments={},
            contexts=["desktop"],
            platforms=["all"],
            discoverable=True,
            palette=True,
            ai_accessible=False,
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


def test_help_data_exposes_required_fields():
    data = build_help_data(make_registry())
    entries = [e for c in data["categories"] for e in c["actions"]]
    assert len(entries) == 4  # discoverable=false excluded
    for entry in entries:
        assert "name" in entry
        assert "description" in entry
        assert "binding" in entry
        assert "id" in entry


def test_help_data_grouped_by_category():
    data = build_help_data(make_registry())
    names = [c["name"] for c in data["categories"]]
    assert names == sorted(names)
    by_name = {c["name"]: c for c in data["categories"]}
    assert "Applications" in by_name
    assert "Navigation" in by_name
    assert "Network" in by_name
    assert "AI" in by_name


def test_help_data_primary_binding():
    data = build_help_data(make_registry())
    entries = {e["id"]: e for c in data["categories"] for e in c["actions"]}
    assert entries["app.terminal.open"]["binding"] == "Super+Enter"
    assert entries["ai.ask"]["binding"] == "Super+A,A"


def test_help_data_excludes_non_discoverable():
    data = build_help_data(make_registry())
    entries = [e for c in data["categories"] for e in c["actions"]]
    assert all(e["id"] != "internal.debug" for e in entries)


def test_search_by_keyword():
    data = build_help_data(make_registry())
    results = search_help_data(data, "bluetooth")
    assert len(results) == 1
    assert results[0]["id"] == "network.bluetooth.open"


def test_search_by_name():
    data = build_help_data(make_registry())
    results = search_help_data(data, "terminal")
    assert len(results) == 1
    assert results[0]["id"] == "app.terminal.open"


def test_search_multi_term():
    data = build_help_data(make_registry())
    results = search_help_data(data, "move window")
    # No action matches both terms → empty (AND semantics).
    assert results == []
    results = search_help_data(data, "focus left")
    assert len(results) == 1
    assert results[0]["id"] == "window.focus.left"


def test_search_by_category():
    data = build_help_data(make_registry())
    results = search_help_data(data, "network")
    assert len(results) == 1
    assert results[0]["id"] == "network.bluetooth.open"


def test_search_no_match():
    data = build_help_data(make_registry())
    assert search_help_data(data, "nonexistent") == []
    assert search_help_data(data, "") == []


def test_format_help_text():
    data = build_help_data(make_registry())
    text = format_help_text(data)
    assert "Open Terminal" in text
    assert "Super+Enter" in text
    assert "Navigation" in text