"""Registry tests — docs/11-testing-and-validation.md §4–6.

Covers:
- valid TOML loading
- malformed TOML
- duplicate action IDs
- missing required fields
- invalid registry version
- invalid action ID format
- schema enum validation (risk, confirmation, contexts, platforms)
- keybinding conflict detection
- override merging
"""

from __future__ import annotations

import pytest

from omivoidlib.registry import (
    Registry,
    has_errors,
    load_registry,
    validate_registry,
)


def write_toml(tmp_path, name: str, content: str):
    p = tmp_path / name
    p.write_text(content)
    return p


def load(tmp_path, *files):
    """Write files into tmp_path/actions and load the registry from there."""
    actions_dir = tmp_path / "actions"
    actions_dir.mkdir(exist_ok=True)
    for name, content in files:
        write_toml(actions_dir, name, content)
    return load_registry(core_dir=actions_dir, user_actions_dir=tmp_path / "no-user", overrides_dir=tmp_path / "no-overrides")


VALID_ACTION = """
registry_version = 1

[action."app.browser.open"]
name = "Open Browser"
description = "Open the default web browser."
category = "Applications"
risk = "routine"
"""


# ── Loading ───────────────────────────────────────────────────────────────

def test_valid_toml_loads(tmp_path):
    registry = load(tmp_path, ("apps.toml", VALID_ACTION))
    assert "app.browser.open" in registry.actions
    a = registry.actions["app.browser.open"]
    assert a.name == "Open Browser"
    assert a.category == "Applications"
    assert a.risk == "routine"
    assert a.confirmation == "never"  # default
    assert a.contexts == ["global"]  # default
    assert a.platforms == ["common"]  # default


def test_malformed_toml_raises(tmp_path):
    with pytest.raises(Exception):
        load(tmp_path, ("bad.toml", "registry_version = 1\n[action.\"x\"]\nname = \n"))


def test_unsupported_registry_version(tmp_path):
    registry = load(tmp_path, ("future.toml", 'registry_version = 99\n[action."x.y"]\nname = "X"\n'))
    issues = validate_registry(registry)
    assert any(i.code == "UNSUPPORTED_REGISTRY_VERSION" and i.level == "ERROR" for i in issues)
    assert "x.y" not in registry.actions  # file skipped


def test_duplicate_action_id_in_layer(tmp_path):
    registry = load(
        tmp_path,
        ("a.toml", VALID_ACTION),
        ("b.toml", VALID_ACTION),
    )
    issues = validate_registry(registry)
    assert any(i.code == "DUPLICATE_ACTION_ID" and i.level == "ERROR" for i in issues)


def test_missing_required_fields(tmp_path):
    registry = load(
        tmp_path,
        ("bad.toml", 'registry_version = 1\n[action."app.x.open"]\nname = "X"\n'),
    )
    issues = validate_registry(registry)
    codes = {i.code for i in issues}
    assert "MISSING_REQUIRED_FIELD" in codes
    # description, category, risk all missing
    missing = [i for i in issues if i.code == "MISSING_REQUIRED_FIELD"]
    assert len(missing) >= 3


def test_invalid_action_id_format(tmp_path):
    registry = load(
        tmp_path,
        ("bad.toml", 'registry_version = 1\n[action."UPPER.Case"]\nname = "X"\ndescription = "d"\ncategory = "c"\nrisk = "routine"\n'),
    )
    issues = validate_registry(registry)
    assert any(i.code == "INVALID_ACTION_ID" and i.level == "ERROR" for i in issues)


def test_two_segment_action_id_valid(tmp_path):
    # window.close and workspace.next are canonical two-segment IDs (docs/03 §3).
    registry = load(
        tmp_path,
        ("w.toml", 'registry_version = 1\n[action."window.close"]\nname = "Close"\ndescription = "d"\ncategory = "c"\nrisk = "routine"\n'),
    )
    issues = validate_registry(registry)
    assert not any(i.code == "INVALID_ACTION_ID" for i in issues)


# ── Schema enums ──────────────────────────────────────────────────────────

def test_invalid_risk(tmp_path):
    registry = load(
        tmp_path,
        ("bad.toml", 'registry_version = 1\n[action."app.x.open"]\nname = "X"\ndescription = "d"\ncategory = "c"\nrisk = "explosive"\n'),
    )
    issues = validate_registry(registry)
    assert any(i.code == "INVALID_RISK" and i.level == "ERROR" for i in issues)


def test_invalid_confirmation(tmp_path):
    registry = load(
        tmp_path,
        ("bad.toml", 'registry_version = 1\n[action."app.x.open"]\nname = "X"\ndescription = "d"\ncategory = "c"\nrisk = "routine"\nconfirmation = "sometimes"\n'),
    )
    issues = validate_registry(registry)
    assert any(i.code == "INVALID_CONFIRMATION" and i.level == "ERROR" for i in issues)


def test_unknown_context_warns(tmp_path):
    registry = load(
        tmp_path,
        ("bad.toml", 'registry_version = 1\n[action."app.x.open"]\nname = "X"\ndescription = "d"\ncategory = "c"\nrisk = "routine"\ncontexts = ["mars"]\n'),
    )
    issues = validate_registry(registry)
    assert any(i.code == "UNKNOWN_CONTEXT" and i.level == "WARNING" for i in issues)


def test_unknown_platform_warns(tmp_path):
    registry = load(
        tmp_path,
        ("bad.toml", 'registry_version = 1\n[action."app.x.open"]\nname = "X"\ndescription = "d"\ncategory = "c"\nrisk = "routine"\nplatforms = ["windows"]\n'),
    )
    issues = validate_registry(registry)
    assert any(i.code == "UNKNOWN_PLATFORM" and i.level == "WARNING" for i in issues)


# ── Keybinding conflicts ──────────────────────────────────────────────────

def test_duplicate_keybinding(tmp_path):
    registry = load(
        tmp_path,
        ("a.toml", 'registry_version = 1\n[action."app.a.open"]\nname = "A"\ndescription = "d"\ncategory = "c"\nrisk = "routine"\nkeys = ["Super+X"]\n'),
        ("b.toml", 'registry_version = 1\n[action."app.b.open"]\nname = "B"\ndescription = "d"\ncategory = "c"\nrisk = "routine"\nkeys = ["Super+X"]\n'),
    )
    issues = validate_registry(registry)
    assert any(i.code == "DUPLICATE_KEYBINDING" and i.level == "ERROR" for i in issues)


def test_chord_prefix_conflict_warns(tmp_path):
    registry = load(
        tmp_path,
        ("a.toml", 'registry_version = 1\n[action."ai.open"]\nname = "AI"\ndescription = "d"\ncategory = "c"\nrisk = "routine"\nkeys = ["Super+A"]\n'),
        ("b.toml", 'registry_version = 1\n[action."ai.ask"]\nname = "Ask"\ndescription = "d"\ncategory = "c"\nrisk = "routine"\nkeys = ["Super+A,A"]\n'),
    )
    issues = validate_registry(registry)
    assert any(i.code == "CHORD_PREFIX_CONFLICT" and i.level == "WARNING" for i in issues)


def test_primary_key_must_be_in_keys(tmp_path):
    registry = load(
        tmp_path,
        ("a.toml", 'registry_version = 1\n[action."app.a.open"]\nname = "A"\ndescription = "d"\ncategory = "c"\nrisk = "routine"\nkeys = ["Super+X"]\nprimary_key = "Super+Y"\n'),
    )
    issues = validate_registry(registry)
    assert any(i.code == "PRIMARY_KEY_NOT_IN_KEYS" and i.level == "WARNING" for i in issues)


# ── Overrides / merging ───────────────────────────────────────────────────

def test_user_layer_overrides_core(tmp_path):
    core = tmp_path / "core"
    core.mkdir()
    write_toml(core, "apps.toml", VALID_ACTION)
    user = tmp_path / "user"
    user.mkdir()
    write_toml(user, "apps.toml", 'registry_version = 1\n[action."app.browser.open"]\nname = "My Browser"\ndescription = "d"\ncategory = "c"\nrisk = "routine"\n')
    registry = load_registry(core_dir=core, user_actions_dir=user, overrides_dir=tmp_path / "no-overrides")
    assert registry.actions["app.browser.open"].name == "My Browser"
    issues = validate_registry(registry)
    assert any(i.code == "ACTION_OVERRIDDEN" and i.level == "INFO" for i in issues)


def test_override_partial_merge(tmp_path):
    core = tmp_path / "core"
    core.mkdir()
    write_toml(core, "apps.toml", VALID_ACTION)
    overrides = tmp_path / "overrides"
    overrides.mkdir()
    write_toml(overrides, "o.toml", 'registry_version = 1\n[override."app.browser.open"]\nkeys = ["Super+B"]\n')
    registry = load_registry(core_dir=core, user_actions_dir=tmp_path / "no-user", overrides_dir=overrides)
    a = registry.actions["app.browser.open"]
    assert a.keys == ["Super+B"]
    assert a.name == "Open Browser"  # untouched by partial override


def test_override_unknown_action_warns(tmp_path):
    core = tmp_path / "core"
    core.mkdir()
    write_toml(core, "apps.toml", VALID_ACTION)
    overrides = tmp_path / "overrides"
    overrides.mkdir()
    write_toml(overrides, "o.toml", 'registry_version = 1\n[override."app.ghost.open"]\nkeys = ["Super+G"]\n')
    registry = load_registry(core_dir=core, user_actions_dir=tmp_path / "no-user", overrides_dir=overrides)
    issues = validate_registry(registry)
    assert any(i.code == "OVERRIDE_UNKNOWN_ACTION" and i.level == "WARNING" for i in issues)


# ── Groups ────────────────────────────────────────────────────────────────

def test_groups_loaded(tmp_path):
    registry = load(
        tmp_path,
        ("help.toml", 'registry_version = 1\n[group.help]\nname = "Help"\nprefix = "Super+K"\ndescription = "Help"\n'),
    )
    assert "help" in registry.groups
    assert registry.groups["help"].prefix == "Super+K"


# ── has_errors ────────────────────────────────────────────────────────────

def test_has_errors():
    registry = Registry()
    assert not has_errors(validate_registry(registry))
    registry.issues.append(type("I", (), {"level": "ERROR", "code": "X", "message": "m", "source": ""})())
    assert has_errors(validate_registry(registry))

# ── Real registry integration (ADR-006) ─────────────────────────────────────

def test_real_registry_help_actions_use_dms():
    """Super+K and Super+Space resolve through DMS (ADR-006 §12–13)."""
    from pathlib import Path

    registry = load_registry(
        user_actions_dir=Path("/nonexistent"),
        overrides_dir=Path("/nonexistent"),
    )

    explorer = registry.actions["help.keys.open"]
    assert explorer.adapter == "shell.explorer"
    assert explorer.arguments["command"] == [
        "dms", "ipc", "call", "spotlight", "openQuery", "!!",
    ]

    search = registry.actions["help.actions.search"]
    assert search.command == ["dms", "ipc", "call", "spotlight", "toggle"]
