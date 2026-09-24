# DMS Plugin Inventory

**Status:** Initial audit (ADR-006 §18)
**Date:** 2026-09-11
**DMS version:** 1.6.1
**Registry size:** 352 plugins (at time of audit)

---

# 1. Purpose

This document records the evaluation of DMS core capabilities and DMS
plugins against Omivoid requirements, per ADR-006 (DMS Plugin-First
Integration).

The decision path for every desktop-facing requirement is:

```text
DMS Core
   ↓
Existing Plugin
   ↓
Extend Plugin
   ↓
Omivoid Plugin
   ↓
Standalone Component
```

Each evaluated plugin is classified:

```text
ADOPT
ADOPT WITH CONFIGURATION
EXTEND
REFERENCE ONLY
DEFER
REJECT
```

---

# 2. DMS Core Capabilities (no plugin required)

DMS 1.6.1 ships the following built-in modules (verified in
`/usr/share/quickshell/dms/Modules/`):

| Module | Purpose | Omivoid Relevance |
| ------ | ------- | ----------------- |
| DankBar | Top bar | Shell presentation (USE DMS) |
| DankDash | Dashboard overlay | Wallpaper browsing (`Mod+Y`) |
| DankIsland | Island/notifications popup | Notifications |
| AppDrawer | Application drawer | App launching |
| Dock | Dock | App launching |
| ControlCenter | Control centre | Wi-Fi/Bluetooth/audio controls |
| Network | Network module | Network UI |
| Notifications | Notification centre | Notifications |
| OSD | On-screen display | Volume/brightness feedback |
| PowerMenu | Power menu | Session controls (`Super+X`) |
| ProcessList | Task manager | Process management (`Mod+M`) |
| Settings | Settings UI | DMS configuration |
| Lock | Lock screen | Session lock (`Mod+Alt+L`) |
| Notepad | Notes | Notes (`Mod+Shift+N`) |
| Greetd | Greeter | Session switching |
| ColorPicker | Colour picker | Utility |
| WallpaperBackground | Wallpaper rendering | Theme foundation |
| WorkspaceOverlays | Workspace indicators | Workspace navigation |
| KeybindsModal | Keybinding viewer/editor | **Super+K candidate** |
| DankLauncherV2 | Spotlight launcher | **Super+Space candidate** |

**Classification:** DMS core provides the shell presentation layer. Omivoid
consumes it via `dms ipc call` and the generated Niri fragment.

---

# 3. Installed Plugins

## 3.1 dankKDEConnect (Phone Connect)

| Field | Value |
| ----- | ----- |
| ID | `dankKDEConnect` |
| Version | 3.0.0 |
| Author | Avenge Media (first-party) |
| Capabilities | `dankbar-widget`, `control-center` |
| Dependencies | kdeconnect, valent |
| Purpose | Control connected devices via KDE Connect/Valent |

**Classification:** ADOPT WITH CONFIGURATION (user-installed; phone
integration is a personal convenience, not core Omivoid).

**Omivoid role:** None directly. May later surface as a `phone.*` action
namespace if Omivoid exposes device actions.

## 3.2 quickCapture (Quick Capture)

| Field | Value |
| ----- | ----- |
| ID | `quickCapture` |
| Version | 5.4.2 |
| Author | Loc Huynh |
| Capabilities | `daemon`, `control-center`, `dankbar-widget` |
| Dependencies | none listed |
| Purpose | Screenshot annotation and screen recording |

**Classification:** ADOPT WITH CONFIGURATION (user-installed).

**Omivoid role:** DMS already binds `Print`/`Ctrl+Print`/`Alt+Print` to
`dms screenshot`. quickCapture extends this with annotation/recording.
`capture.screenshot.*` actions in the registry map to `dms screenshot`
(adapter `dms.ipc`), which quickCapture may enhance.

## 3.3 wallpaperCarousel (Wallpaper Carousel)

| Field | Value |
| ----- | ----- |
| ID | `wallpaperCarousel` |
| Version | 0.8.4 |
| Author | yngwe |
| Capabilities | `wallpaper` |
| Dependencies | quickshell |
| Purpose | Browse and pick wallpapers with a fullscreen carousel overlay |

**Classification:** ADOPT WITH CONFIGURATION (user-installed).

**Omivoid role:** `theme.wallpaper.select` / `theme.wallpaper.next` may
integrate with this plugin's IPC (`noctalia msg plugin
yngwe/wallpaperCarousel:service all <event>`) or with DMS core wallpaper
handling. Evaluation pending at the theme stage.

---

# 4. Registry Plugin Evaluation

## 4.1 dankLauncherKeys — Shortcut Discovery

| Field | Value |
| ----- | ----- |
| ID | `dankLauncherKeys` |
| Author | Avenge Media (first-party) |
| Capabilities | `launcher` |
| Compositors | any |
| Purpose | Search and browse keyboard shortcuts from compositor and applications |
| Status | reviewed |
| Installed for evaluation | yes (trigger `\`) |

**Omivoid role:** **`Super+K` candidate** (ADR-006 §12).

**Evaluation result (2026-09-11):**

- Source of data: `dms keybinds show <provider>` (`DankLauncherKeys.qml`
  `Process.command`), the same parser used by the DMS keybinds modal.
- **The parser does not resolve the Omivoid Niri include.** Verified:
  `dms keybinds show niri` reports `Mod+K → focus-window-up`
  (`source=dms-default`) and does not list `Mod+Return`, `Mod+Shift+B` or
  the Omivoid override of `Mod+K`.
- The plugin has no extension surface for injecting external registry data;
  it consumes only the DMS keybinds parser output.
- It cannot surface Omivoid action names, descriptions, categories or
  keywords.

**Conclusion:** dankLauncherKeys cannot satisfy the ADR-006 §12 requirement
that the `Super+K` interface consume Omivoid registry data. It remains
useful as a general compositor/DMS keybind search.

**Classification:** REFERENCE ONLY (for `Super+K`). Not adopted as the
Omivoid interaction explorer.

## 4.2 dankHooks — Event Integration

| Field | Value |
| ----- | ----- |
| ID | `dankHooks` |
| Author | Avenge Media (first-party) |
| Capabilities | `watch-events` |
| Compositors | any |
| Purpose | Trigger scripts based on various system events |
| Status | reviewed |

**Omivoid role:** **Event bridge candidate** (ADR-006 §27).

Potential model:

```text
DMS event (wallpaper changed, etc.)
   ↓
dankHooks
   ↓
omivoid action run theme.palette.regenerate
```

This may satisfy Phase 1 event requirements without introducing an Omivoid
daemon (ADR-006 §28).

**Classification:** EVALUATE → likely ADOPT WITH CONFIGURATION.

## 4.3 dms-command-runner — Command Execution

| Field | Value |
| ----- | ----- |
| ID | `dms-command-runner` |
| Author | devnullvoid |
| Capabilities | `launcher` |
| Compositors | any |
| Purpose | Execute shell commands from the launcher with history tracking |
| Status | reviewed |

**Omivoid role:** Expert interface (ADR-006 §29). Arbitrary shell execution
must NOT replace canonical Omivoid actions for normal workflows.

**Classification:** REFERENCE ONLY (or DEFER). Omivoid actions should be
invoked via `omivoid action run <id>`, not raw shell.

## 4.4 aiAssistant — AI Chat

| Field | Value |
| ----- | ----- |
| ID | `aiAssistant` |
| Author | devnullvoid |
| Capabilities | `slideout`, `ai` |
| Compositors | any |
| Dependencies | curl, wl-copy |
| Purpose | Integrated AI chat assistant with markdown, multiple providers, streaming |
| Status | reviewed |

**Omivoid role:** AI presentation layer candidate (ADR-006 §31). Must NOT
replace the Omivoid AI architecture (Pi, Herdr, Action Registry policy).

**Classification:** REFERENCE ONLY for Phase 1. Omivoid AI policy
(`ai_accessible`, `risk`, `confirmation`) governs AI capability access.

## 4.5 tailscale — Tailscale Manager

| Field | Value |
| ----- | ----- |
| ID | `tailscale` |
| Author | cglavin50 |
| Capabilities | `dankbar-widget` |
| Compositors | any |
| Dependencies | tailscale |
| Purpose | Tailscale-toggle plugin for DankBar |
| Status | **unmaintained, deprecated** |

**Omivoid role:** Network UI (ADR-006 §18 suggested "Adopt candidate").

**Classification:** REJECT (deprecated/unmaintained). If Tailscale UI is
needed, evaluate alternatives or defer.

## 4.6 taskwarrior — Taskwarrior Integration

| Field | Value |
| ----- | ----- |
| ID | `taskwarrior` |
| Author | Michał Wazgird |
| Capabilities | `dankbar-widget` |
| Compositors | any |
| Dependencies | taskwarrior |
| Purpose | See pending tasks in status bar, create tasks, check off |
| Status | reviewed |

**Omivoid role:** Project workflow candidate (ADR-006 §18: "Defer/Evaluate").
Strong local-first fit.

**Classification:** DEFER for Phase 1. Project workflow is reserved
(`project.*` namespace, `Super+P`) but not required to prove Phase 1.

## 4.7 todoLauncher — Todo List

| Field | Value |
| ----- | ----- |
| ID | `todoLauncher` |
| Author | Mohammed Skepr |
| Capabilities | `launcher` |
| Compositors | any |
| Purpose | Simple todo list from the launcher |
| Status | reviewed |

**Omivoid role:** Project workflow candidate.

**Classification:** DEFER for Phase 1 (same rationale as taskwarrior).

---

# 5. Omivoid Requirement Mapping

| Requirement | DMS Core | Existing Plugin | Omivoid Plugin | Standalone |
| ----------- | -------- | --------------- | -------------- | ---------- |
| `Super+K` interaction explorer | KeybindsModal (partial — no Omivoid data) | dankLauncherKeys (REFERENCE ONLY — cannot consume registry) | **Omivoid Actions launcher provider (wired: `openQuery "!!"`)** | Omivoid popup (retired) |
| `Super+Space` universal palette | DankLauncherV2 spotlight | — | **Omivoid Actions launcher provider (wired: always-active / merge)** | Custom launcher (rejected) |
| `Super+A` AI namespace | — | aiAssistant (reference only) | Future Omivoid AI provider | Future |
| `Super+P` project namespace | — | taskwarrior/todoLauncher (defer) | Future Omivoid project provider | Future |
| Event integration | — | dankHooks (evaluate) | Future | Omivoid daemon (deferred) |
| Wallpaper/theme | WallpaperBackground, DankDash | wallpaperCarousel (installed) | Future theme provider | Custom theme engine (rejected) |
| Screenshots | `dms screenshot` | quickCapture (installed) | — | — |
| Audio/brightness/media | `dms ipc call` | — | — | — |

---

# 6. Recommended Phase 1 Actions

Based on this audit:

1. ✅ **Install and evaluate `dankLauncherKeys`** for `Super+K` (ADR-006 §12).
   **Result:** cannot consume Omivoid registry data; classified REFERENCE
   ONLY.
2. ✅ **Prototype the "Omivoid Actions" DMS launcher plugin** (ADR-006 §10).
   **Result:** built at `shell/dms/omivoid-actions/`; loads 21 registry
   actions; invokes actions via `omivoid action run <id>`. See §6.1.
3. ⏳ **Evaluate `dankHooks`** for event integration (wallpaper → theme
   regenerate) to avoid an Omivoid daemon.
4. ✅ **Retire the Omivoid Quickshell popup.** `Super+K` now opens the DMS
   spotlight with `openQuery "!!"`; `Super+Space` merges Omivoid actions
   into the palette. See §6.2.
5. ⏳ **Defer** AI presentation, project workflow, and Tailscale UI to later
   stages.

## 6.1 Omivoid Actions plugin prototype

| Field | Value |
| ----- | ----- |
| Location | `shell/dms/omivoid-actions/` |
| Plugin ID | `omivoidActions` |
| Type | `launcher` (capabilities `launcher`, `action-registry`) |
| Activation | always-active (palette merge) by default; optional trigger |
| Explorer | `!!` query sentinel (Super+K) |
| Data source | `omivoid action list --json` |
| Execution | `omivoid action run <id>` |
| Install (dev) | symlink into `~/.config/DankMaterialShell/plugins/` |

Verified 2026-09-11:

```text
DMS: Plugin loaded: omivoidActions
DMS: [OmivoidActions] Activation mode: always-active (palette merge)
DMS: [OmivoidActions] Loaded 21 actions from registry
DMS: [OmivoidActions] Explorer requested: 21 actions
```

## 6.2 `Super+K` / `Super+Space` wiring

| Path | Binding | Mechanism |
| ---- | ------- | --------- |
| Interaction explorer | `Super+K` | `help.keys.open` → adapter `shell.explorer` → spawn `dms ipc call spotlight openQuery "!!"` |
| Keybindings cheat sheet | `Super+Shift+S` | `help.keybinds.open` → adapter `command` → spawn `dms ipc call omivoidKeybinds toggle` (own `omivoidKeybinds` DMS plugin, tabbed by GKS domain) |
| Universal palette | `Super+Space` (DMS `Mod+Space`) | plugin is always-active, so `getItems(query)` runs alongside app search (`help.actions.search` toggles the spotlight) |

Design notes:

- The plugin is registered **always-active** (`noTrigger = true`,
  `trigger = ""`) so Omivoid actions merge into every search (ADR-006 §13).
- The `Super+K` explorer uses the `!!` sentinel because the DMS launcher
  ignores single-character queries in its plugin phase; the plugin treats a
  leading run of `!` as an explicit explorer request.
- The `shell.explorer` adapter (`adapters/dms/explorer.py`) makes the action
  runnable from every surface (CLI, AI, palette), not only the Niri binding.
- The former Omivoid Quickshell popup is retired.

Verified live 2026-09-11:

```text
dms ipc call spotlight openQuery "!!"      → Explorer requested: 21 actions
dms ipc call spotlight openQuery "browser" → Palette query: 1 action
dms ipc call spotlight openQuery "volume"  → Palette query: 3 actions
```

---



# 7. Plugin Locking

DMS supports plugin locking via `plugins.lock.json`
(`~/.config/DankMaterialShell/plugins.lock.json`). Omivoid-supported
plugins should be recorded there for reproducible installations
(ADR-006 §32).

Current lockfile records:

```json
{
  "dankKDEConnect": "6fc7f25bfb24f93b6488fb8a36ed67b5f242abdb",
  "quickCapture": "045ce4f645363d421f1fdaf92388d6c65989cd00",
  "wallpaperCarousel": "761ecd1b7f347beee9f17909f8334d987c935a1a"
}
```

---

# 8. Open Questions

Resolved during this audit:

- ✅ Can `dankLauncherKeys` consume Omivoid registry data? **No** — it
  consumes only `dms keybinds show <provider>`, which does not resolve the
  Omivoid include.
- ✅ Does the DMS launcher plugin contract support dynamic item loading from
  an external process? **Yes** — `getItems()` + `Process` reading
  `omivoid action list --json` works (21 actions loaded).
- ✅ Should the Omivoid Actions plugin use a trigger prefix or
  always-visible mode? **Always-visible (palette merge) is the Phase 1
  default**; a trigger prefix remains available via settings.
- ✅ For `Super+Space`, should Omivoid actions merge into every search or
  stay behind a trigger? **Merge** (ADR-006 §13; user decision
  2026-09-11).
- ✅ Should `Super+K` open the launcher with a trigger or a dedicated
  explorer view? **Open the DMS spotlight via `openQuery "!!"`** (ADR-006
  §12; user decision 2026-09-11). A keybinding-first ordering remains a
  possible future refinement.

Still open:

- Does `dankHooks` support the specific events Omivoid needs (wallpaper
  changed, session events)?

---

# 9. Revisit Conditions

This inventory should be updated when:

- the DMS plugin registry changes materially;
- a plugin's maintenance status changes;
- a new Omivoid requirement maps to a plugin;
- a plugin is adopted, extended, or rejected.