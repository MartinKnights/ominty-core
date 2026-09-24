"""Omivoid action registry: loading, merging, and validation.

Implements docs/03-action-registry-spec.md (schema version 1).

The registry is the canonical definition of meaningful actions.
Adapters define how each action is performed.
"""

from __future__ import annotations

import os
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

# Registry schema version supported by this implementation.
SCHEMA_VERSION = 1

# Action ID: namespace.subject.action — at least two dot-separated
# lowercase segments; digits, hyphens and underscores allowed within
# segments (e.g. custom.obsidian.daily-note, media.play_pause). The spec
# uses both three-segment (app.browser.open) and two-segment
# (window.close, workspace.next) IDs.
ACTION_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*(\.[a-z][a-z0-9_-]*){1,}$")

# Recognised namespaces (docs/03 §4, plus custom for user actions).
NAMESPACES = {
    "app", "window", "workspace", "display", "input", "audio", "media",
    "network", "power", "session", "clipboard", "capture", "theme",
    "notification", "file", "project", "ai", "developer", "help", "system",
    "custom",
}

VALID_RISKS = {
    "read", "routine", "state-change", "privileged", "destructive", "critical",
}

VALID_CONFIRMATIONS = {"never", "interactive", "ai-only", "always"}

VALID_CONTEXTS = {
    "global", "window", "workspace", "selection", "text-selection",
    "file", "directory", "browser", "terminal", "editor", "project",
    "clipboard",
}

VALID_PLATFORMS = {"common", "debian", "void"}

# Known Phase 1 adapters (docs/03 §21–22). Unknown adapter names warn
# during validation; known-but-unimplemented adapters report unavailable
# at execution time (docs/04 §17 — do not fake availability).
KNOWN_ADAPTERS = {
    "app.launch",
    "command",
    "niri.native",
    "shell.explorer",
    "shell.palette",
    "dms.ipc",
    "ai.pi.open",
    "ai.ask",
    "ai.clipboard.explain",
    "ai.clipboard.summarise",
}

REQUIRED_FIELDS = ("name", "description", "category", "risk")

# Reserved error codes (docs/03 §32). Provider errors (docs/ai/10 §11)
# are returned through the same structured error envelope.
ERROR_CODES = {
    "ACTION_NOT_FOUND", "ACTION_UNAVAILABLE", "DEPENDENCY_MISSING",
    "INVALID_ARGUMENT", "PERMISSION_DENIED", "CONFIRMATION_REQUIRED",
    "ADAPTER_FAILED", "CONTEXT_UNAVAILABLE", "PLATFORM_UNSUPPORTED",
    "PROVIDER_NOT_FOUND", "PROVIDER_UNAVAILABLE", "PROVIDER_FAILED",
    "PROVIDER_TIMEOUT",
}


class RegistryError(Exception):
    """Raised when the registry cannot be loaded or validated."""


@dataclass
class Issue:
    """A validation or loading issue."""

    level: str  # ERROR | WARNING | INFO
    code: str
    message: str
    source: str = ""

    def __str__(self) -> str:
        return f"{self.level}: {self.code}: {self.message}"


@dataclass
class Action:
    """A single registry action definition."""

    id: str
    name: str
    description: str
    category: str
    risk: str
    confirmation: str = "never"
    keywords: list[str] = field(default_factory=list)
    keys: list[str] = field(default_factory=list)
    primary_key: str | None = None
    adapter: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    command: list[str] | None = None
    cli: list[str] = field(default_factory=list)
    contexts: list[str] = field(default_factory=lambda: ["global"])
    platforms: list[str] = field(default_factory=lambda: ["common"])
    requires: list[str] = field(default_factory=list)
    discoverable: bool = True
    palette: bool = True
    ai_accessible: bool = False
    voice_accessible: bool = False
    short_name: str | None = None
    subcategory: str | None = None
    scope: str | None = None
    priority: int = 50
    icon: str | None = None
    source_file: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict (for JSON output)."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "risk": self.risk,
            "confirmation": self.confirmation,
            "keywords": list(self.keywords),
            "keys": list(self.keys),
            "primary_key": self.primary_key,
            "adapter": self.adapter,
            "arguments": dict(self.arguments),
            "command": list(self.command) if self.command else None,
            "cli": list(self.cli),
            "contexts": list(self.contexts),
            "platforms": list(self.platforms),
            "requires": list(self.requires),
            "discoverable": self.discoverable,
            "palette": self.palette,
            "ai_accessible": self.ai_accessible,
            "voice_accessible": self.voice_accessible,
            "source_file": self.source_file,
        }


@dataclass
class Group:
    """A prefix namespace group (docs/03 §13)."""

    name: str
    prefix: str
    description: str = ""
    source_file: str = ""


@dataclass
class Registry:
    """A loaded and merged action registry."""

    actions: dict[str, Action] = field(default_factory=dict)
    groups: dict[str, Group] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)


# ── Path helpers ──────────────────────────────────────────────────────────

def xdg_config_home() -> Path:
    """Return $XDG_CONFIG_HOME with the standard fallback (docs/11 §24)."""
    env = os.environ.get("XDG_CONFIG_HOME")
    return Path(env) if env else Path.home() / ".config"


def user_config_dir() -> Path:
    """Return the user Omivoid config directory (~/.config/omivoid)."""
    return xdg_config_home() / "omivoid"


def repo_root() -> Path:
    """Return the omivoid-lmde repository root (parent of cli/)."""
    return Path(__file__).resolve().parents[2]


# ── Loading ───────────────────────────────────────────────────────────────

def discover_action_files(dirs: Iterable[Path]) -> list[Path]:
    """Discover *.toml files in the given directories (non-recursive)."""
    files: list[Path] = []
    for d in dirs:
        if d.is_dir():
            files.extend(sorted(d.glob("*.toml")))
    return files


def load_toml(path: Path) -> dict[str, Any]:
    """Load a TOML file, raising RegistryError on malformed content."""
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise RegistryError(f"malformed TOML in {path}: {e}") from e
    except OSError as e:
        raise RegistryError(f"cannot read {path}: {e}") from e


def _parse_action(id_: str, data: dict[str, Any], source: str) -> Action:
    """Build an Action from a raw [action."id"] table."""
    return Action(
        id=id_,
        name=str(data.get("name", "")),
        description=str(data.get("description", "")),
        category=str(data.get("category", "")),
        risk=str(data.get("risk", "")),
        confirmation=str(data.get("confirmation", "never")),
        keywords=[str(k) for k in data.get("keywords", [])],
        keys=[str(k) for k in data.get("keys", [])],
        primary_key=(
            str(data["primary_key"]) if data.get("primary_key") is not None else None
        ),
        adapter=str(data["adapter"]) if data.get("adapter") else None,
        arguments=dict(data.get("arguments", {})),
        command=(
            [str(c) for c in data["command"]] if data.get("command") is not None else None
        ),
        cli=[str(c) for c in data.get("cli", [])],
        contexts=[str(c) for c in data.get("contexts", ["global"])],
        platforms=[str(p) for p in data.get("platforms", ["common"])],
        requires=[str(r) for r in data.get("requires", [])],
        discoverable=bool(data.get("discoverable", True)),
        palette=bool(data.get("palette", True)),
        ai_accessible=bool(data.get("ai_accessible", False)),
        voice_accessible=bool(data.get("voice_accessible", False)),
        short_name=(
            str(data["short_name"]) if data.get("short_name") is not None else None
        ),
        subcategory=(
            str(data["subcategory"]) if data.get("subcategory") is not None else None
        ),
        scope=str(data["scope"]) if data.get("scope") else None,
        priority=int(data.get("priority", 50)),
        icon=str(data["icon"]) if data.get("icon") else None,
        source_file=source,
    )


def _load_action_file(
    path: Path, registry: Registry, layer: str, seen_in_layer: set[str]
) -> None:
    """Load one action file into the registry (core/user layer)."""
    data = load_toml(path)

    version = data.get("registry_version", SCHEMA_VERSION)
    if version != SCHEMA_VERSION:
        registry.issues.append(
            Issue(
                "ERROR",
                "UNSUPPORTED_REGISTRY_VERSION",
                f"registry_version {version} in {path} is not supported "
                f"(expected {SCHEMA_VERSION}); file skipped",
                str(path),
            )
        )
        return

    for gid, gdata in data.get("group", {}).items():
        registry.groups[gid] = Group(
            name=str(gdata.get("name", gid)),
            prefix=str(gdata.get("prefix", "")),
            description=str(gdata.get("description", "")),
            source_file=str(path),
        )

    for aid, adata in data.get("action", {}).items():
        if aid in seen_in_layer:
            registry.issues.append(
                Issue(
                    "ERROR",
                    "DUPLICATE_ACTION_ID",
                    f"duplicate action ID '{aid}' in layer '{layer}'",
                    str(path),
                )
            )
            continue
        seen_in_layer.add(aid)
        registry.actions[aid] = _parse_action(aid, adata, str(path))


def _load_override_file(path: Path, registry: Registry) -> None:
    """Load one override file ([override."id"] partial tables)."""
    data = load_toml(path)

    version = data.get("registry_version", SCHEMA_VERSION)
    if version != SCHEMA_VERSION:
        registry.issues.append(
            Issue(
                "ERROR",
                "UNSUPPORTED_REGISTRY_VERSION",
                f"registry_version {version} in {path} is not supported "
                f"(expected {SCHEMA_VERSION}); file skipped",
                str(path),
            )
        )
        return

    for aid, odata in data.get("override", {}).items():
        action = registry.actions.get(aid)
        if action is None:
            registry.issues.append(
                Issue(
                    "WARNING",
                    "OVERRIDE_UNKNOWN_ACTION",
                    f"override for unknown action '{aid}'",
                    str(path),
                )
            )
            continue
        _apply_override(action, odata, str(path))


def _apply_override(action: Action, odata: dict[str, Any], source: str) -> None:
    """Apply a partial override table onto an existing action."""
    if "name" in odata:
        action.name = str(odata["name"])
    if "description" in odata:
        action.description = str(odata["description"])
    if "category" in odata:
        action.category = str(odata["category"])
    if "risk" in odata:
        action.risk = str(odata["risk"])
    if "confirmation" in odata:
        action.confirmation = str(odata["confirmation"])
    if "keywords" in odata:
        action.keywords = [str(k) for k in odata["keywords"]]
    if "keys" in odata:
        action.keys = [str(k) for k in odata["keys"]]
    if "primary_key" in odata:
        action.primary_key = str(odata["primary_key"])
    if "adapter" in odata:
        action.adapter = str(odata["adapter"])
    if "arguments" in odata:
        action.arguments = dict(odata["arguments"])
    if "command" in odata:
        action.command = [str(c) for c in odata["command"]]
    if "cli" in odata:
        action.cli = [str(c) for c in odata["cli"]]
    if "contexts" in odata:
        action.contexts = [str(c) for c in odata["contexts"]]
    if "platforms" in odata:
        action.platforms = [str(p) for p in odata["platforms"]]
    if "requires" in odata:
        action.requires = [str(r) for r in odata["requires"]]
    if "discoverable" in odata:
        action.discoverable = bool(odata["discoverable"])
    if "palette" in odata:
        action.palette = bool(odata["palette"])
    if "ai_accessible" in odata:
        action.ai_accessible = bool(odata["ai_accessible"])
    if "voice_accessible" in odata:
        action.voice_accessible = bool(odata["voice_accessible"])
    action.source_file = source


def load_registry(
    core_dir: Path | None = None,
    user_actions_dir: Path | None = None,
    overrides_dir: Path | None = None,
) -> Registry:
    """Load and merge the action registry.

    Precedence (docs/03 §28): core < platform < machine < user < local.
    Phase 1 implements core + user actions + user overrides.
    """
    registry = Registry()

    core_dir = core_dir or (repo_root() / "actions")
    user_actions_dir = user_actions_dir or (user_config_dir() / "actions")
    overrides_dir = overrides_dir or (user_config_dir() / "overrides")

    # Core layer.
    seen_core: set[str] = set()
    for path in discover_action_files([core_dir]):
        _load_action_file(path, registry, "core", seen_core)

    # User layer (later definitions override earlier ones).
    seen_user: set[str] = set()
    for path in discover_action_files([user_actions_dir]):
        _load_action_file(path, registry, "user", seen_user)
    for aid in seen_user:
        registry.issues.append(
            Issue(
                "INFO",
                "ACTION_OVERRIDDEN",
                f"action '{aid}' overridden by user layer",
                aid,
            )
        )

    # Override layer (partial merges).
    for path in discover_action_files([overrides_dir]):
        _load_override_file(path, registry)

    return registry


# ── Validation ────────────────────────────────────────────────────────────

def validate_registry(registry: Registry) -> list[Issue]:
    """Validate the loaded registry, returning all issues.

    Errors must be fixed before generated configuration is produced.
    """
    issues = list(registry.issues)

    seen_bindings: dict[str, str] = {}
    all_bindings: list[tuple[str, str]] = []  # (binding, action_id)

    for aid, action in registry.actions.items():
        # Action ID format.
        if not ACTION_ID_RE.match(aid):
            issues.append(
                Issue(
                    "ERROR",
                    "INVALID_ACTION_ID",
                    f"invalid action ID format '{aid}' "
                    "(expected namespace.subject.action)",
                    aid,
                )
            )
        namespace = aid.split(".")[0]
        if namespace not in NAMESPACES:
            issues.append(
                Issue(
                    "WARNING",
                    "UNKNOWN_NAMESPACE",
                    f"namespace '{namespace}' is not a recognised Phase 1 namespace",
                    aid,
                )
            )

        # Required fields.
        for f in REQUIRED_FIELDS:
            if not getattr(action, f):
                issues.append(
                    Issue(
                        "ERROR",
                        "MISSING_REQUIRED_FIELD",
                        f"missing required field '{f}'",
                        aid,
                    )
                )

        # Risk.
        if action.risk not in VALID_RISKS:
            issues.append(
                Issue(
                    "ERROR",
                    "INVALID_RISK",
                    f"invalid risk value '{action.risk}' "
                    f"(expected one of {sorted(VALID_RISKS)})",
                    aid,
                )
            )

        # Confirmation.
        if action.confirmation not in VALID_CONFIRMATIONS:
            issues.append(
                Issue(
                    "ERROR",
                    "INVALID_CONFIRMATION",
                    f"invalid confirmation value '{action.confirmation}' "
                    f"(expected one of {sorted(VALID_CONFIRMATIONS)})",
                    aid,
                )
            )

        # Contexts.
        for ctx in action.contexts:
            if ctx not in VALID_CONTEXTS:
                issues.append(
                    Issue(
                        "WARNING",
                        "UNKNOWN_CONTEXT",
                        f"unknown context '{ctx}'",
                        aid,
                    )
                )

        # Platforms.
        for plat in action.platforms:
            if plat not in VALID_PLATFORMS:
                issues.append(
                    Issue(
                        "WARNING",
                        "UNKNOWN_PLATFORM",
                        f"unknown platform '{plat}'",
                        aid,
                    )
                )

        # Adapter / command consistency.
        if action.adapter is None and action.command is None:
            issues.append(
                Issue(
                    "WARNING",
                    "NO_IMPLEMENTATION",
                    f"action has no adapter and no command; it cannot be executed",
                    aid,
                )
            )
        if action.adapter == "command" and not action.command:
            issues.append(
                Issue(
                    "ERROR",
                    "MISSING_COMMAND",
                    "adapter is 'command' but no command is defined",
                    aid,
                )
            )
        if action.adapter and action.adapter not in KNOWN_ADAPTERS:
            issues.append(
                Issue(
                    "WARNING",
                    "UNKNOWN_ADAPTER",
                    f"adapter '{action.adapter}' is not a known Phase 1 adapter",
                    aid,
                )
            )

        # Bindings.
        for key in action.keys:
            if key in seen_bindings:
                issues.append(
                    Issue(
                        "ERROR",
                        "DUPLICATE_KEYBINDING",
                        f"binding '{key}' is used by both "
                        f"'{seen_bindings[key]}' and '{aid}'",
                        aid,
                    )
                )
            else:
                seen_bindings[key] = aid
            all_bindings.append((key, aid))

        # Primary key must be among keys.
        if action.primary_key and action.primary_key not in action.keys:
            issues.append(
                Issue(
                    "WARNING",
                    "PRIMARY_KEY_NOT_IN_KEYS",
                    f"primary_key '{action.primary_key}' is not listed in keys",
                    aid,
                )
            )

    # Chord prefix conflicts (e.g. Super+A,E vs Super+A) — checked after all
    # bindings are collected so ordering does not matter. A declared group
    # prefix (docs/03 §13) intentionally prefixes its chords, so it is not a
    # conflict.
    group_prefixes = {g.prefix for g in registry.groups.values() if g.prefix}

    for key, aid in all_bindings:
        if "," in key:
            continue  # a chord is never a prefix of another binding
        if key in group_prefixes:
            continue  # intentional prefix namespace (docs/03 §13)
        for other, other_owner in all_bindings:
            if other is key:
                continue
            if other.startswith(key + ","):
                issues.append(
                    Issue(
                        "WARNING",
                        "CHORD_PREFIX_CONFLICT",
                        f"binding '{key}' ({aid}) is a prefix of chord "
                        f"'{other}' ({other_owner})",
                        aid,
                    )
                )

    return issues


def has_errors(issues: list[Issue]) -> bool:
    """Return True if any issue is an ERROR."""
    return any(i.level == "ERROR" for i in issues)