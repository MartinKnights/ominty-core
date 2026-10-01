# Ominty Actions — DMS launcher plugin

Bridges the Ominty Action Registry into the DMS launcher / spotlight.

**Status:** Phase 1 prototype (ADR-006)
**Plugin API:** DMS >= 1.2.0, `type: launcher`
**Activation:** always-active (palette merge) by default; `!!` opens the
interaction explorer

---

## Purpose

Expose Ominty canonical actions as searchable, executable items inside the
DMS launcher. This is the first graphical bridge between the Ominty
architecture and the DMS presentation layer (ADR-006 §10).

```text
Ominty Action Registry          (authoritative)
        │  ominty action list --json
        ▼
OmintyActions.qml               (presentation)
        │  launcher items (name · binding · description)
        ▼
DMS launcher / spotlight
        │  executeItem()
        ▼
ominty action run <id>          (execution)
```

## Why Ominty uses it

ADR-006 establishes a **DMS plugin-first** strategy: before building any
desktop-facing UI, Ominty must use DMS core, an existing plugin, an
extension, or a dedicated Ominty plugin. The Action Registry needs a
graphical search/invocation surface; an Ominty DMS launcher plugin is the
preferred implementation (ADR-006 §11–13).

The registry remains authoritative. The plugin only presents and invokes
actions; it never redefines action semantics (ADR-006 §5–6).

## Dependencies

- DMS (DankMaterialShell) with launcher plugin support.
- The Ominty CLI (`cli/ominty`), invoked with `action list` and
  `action run`.

No third-party plugin dependencies.

## Configuration

Settings are stored by DMS (`PluginSettings`) and read by the launcher
component via `pluginService.loadPluginData`. On first run the plugin
defaults to **always-active** so Ominty actions merge into the universal
palette (ADR-006 §13); `Super+K` instead opens the interaction explorer via
the `!!` sentinel (ADR-006 §12).

| Key | Default | Purpose |
| --- | ------- | ------- |
| `noTrigger` | `true` | Actions appear alongside normal search results (palette merge) |
| `trigger` | `""` | Optional prefix that activates the provider; empty = always-active |
| `cliPath` | `$OMINTY_CLI` or `ominty` (PATH) | Ominty CLI executable |
| `filterMode` | `all` | `all` / `discoverable` / `palette` |

### Query semantics

| Query | Result |
| ----- | ------ |
| `""` (trigger mode) | All actions (DMS strips the trigger) |
| `""` (always-active) | Nothing — keeps the palette default view clean |
| `!!` | All actions — the `Super+K` interaction explorer |
| `!!term` | Actions matching `term` |
| `term` | Actions matching `term`, merged with other palette results |

Two `!` characters are required because the DMS launcher ignores
single-character queries in its plugin phase.

### Data contract

`getItems()` filters `ominty action list --json` on name, description,
category, id, keywords and keybindings. Each item shows:

```text
<Action name>
<binding>  ·  <description>
```

`executeItem()` runs `ominty action run <id>` via `Quickshell.execDetached`.

## Canonical actions exposed

All registry actions are surfaced, including (non-exhaustive):

- `app.browser.open`, `app.terminal.open`
- `help.keys.open`, `help.actions.search`
- `window.*`, `workspace.*`, `audio.*`, `display.*`, `media.*`
- `session.lock`, `theme.wallpaper.*`

Action availability is always determined by the registry, not the plugin.

## Platform limitations

- Tested on LMDE (Niri + DMS).
- The launcher plugin API is DMS-specific; this component is not portable
  to other shells. The Ominty CLI it calls is portable.
- `Quickshell.execDetached` is used for execution; `ominty action run`
  handles adapter resolution and platform behaviour.

## Known issues

- The default `cliPath` points at the in-repository entry point. Once
  Ominty installs an `ominty` binary, update the setting.
- Bindings shown are the canonical registry bindings (e.g. `Super+Enter`),
  which may differ cosmetically from the generated Niri KEYS
  (`Mod+Return`).
- The interaction-explorer view currently lists actions with their
  bindings; a dedicated keybinding-first ordering is a future refinement.

## Removal / rollback

The plugin is a symlink into the repo during development:

```text
~/.config/DankMaterialShell/plugins/omintyActions
    → <repo>/shell/dms/ominty-actions
```

To disable: `dms ipc call plugins disable omintyActions`.
To remove: delete the symlink. No Ominty core configuration is affected.

## Verification (Phase 1)

| Check | Result |
| ----- | ------ |
| Manifest valid against `plugin-schema.json` | pass |
| Plugin discovered (`dms ipc call plugins list`) | pass |
| Plugin loads (`dms ipc call plugins status`) | pass |
| Registry read (`Loaded 21 actions from registry`) | pass |
| Action execution (`ominty action run <id>`) | pass |
| Always-active mode (`Activation mode: always-active`) | pass |
| `Super+K` explorer (`openQuery "!!"` → 21 actions) | pass |
| `Super+Space` merge (`getItems("browser")` → 1) | pass |
| No QML load errors | pass |
| Visual UI confirmation | pending user check |

## Related

- `Super+K` binding: `actions/help.toml` (`help.keys.open`, adapter
  `shell.explorer` → `dms ipc call spotlight openQuery "!!"`).
- `Super+Space`: DMS spotlight on `Mod+Space` (`help.actions.search`).
- Adapter: `adapters/dms/explorer.py`.
