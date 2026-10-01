# DMS Evaluation — ominty-core

**Date:** 2026-09-11
**Stage:** 13 (docs/10-phase-1-implementation-plan.md §17)
**Status:** Complete (research-based; practical validation deferred to Stage 14)

This document evaluates DankMaterialShell (DMS) against the Phase 1 shell capability checklist (docs/07-dms-integration.md §27) and classifies each capability per AGENTS.md §13 and docs/07 §28. It is part of the implementation record (AGENTS.md §28).

---

## 1. Baseline Status

| Field | Value |
|---|---|
| DMS installed | **NO** (environment-audit.md §4) |
| Matugen installed | **NO** (environment-audit.md §5) |
| Quickshell | **0.3.0** installed (required dependency, already present) |
| Compositor | Niri 26.04 |
| Evaluation basis | Upstream documentation (v1.6 "Marble Tabby", 2026-09-05) + IPC reference |

**Implication:** This evaluation is research-based. Practical validation (install, run, observe) is a Stage 14 task per docs/10 §18. The classification below is provisional pending live validation.

---

## 2. DMS Facts (v1.6 "Marble Tabby")

| Field | Value |
|---|---|
| Upstream | `AvengeMedia/DankMaterialShell` |
| License | MIT |
| Stack | Quickshell (QML UI) + Go backend (`dms` binary, embedded UI) |
| Compositor support | niri (optimized), Hyprland, Sway, MangoWC, labwc, MiracleWM |
| Replaces | waybar, swaylock, swayidle, mako, fuzzel, polkit, etc. |
| Debian packaging | OBS repos for Debian 13 (Trixie), Testing, Sid (`distro/debian/dms`, `dms-git`) |
| LMDE 7 compatibility | LMDE 7 (gigi) is Debian 13-based → **Debian 13 OBS packages apply** |
| Install method | `sudo apt install dms` (OBS repo) or source build (`sudo make install`, Go 1.26+) |
| Runtime | `dms run` (foreground) or systemd user service (`systemctl --user enable dms`) |
| Config location | `~/.config/DankMaterialShell/` |
| Niri fragments | `~/.config/niri/dms/{colors,layout,alttab,binds}.kdl` + `windowrules.kdl` |

### 2.1 Key interfaces

- **IPC:** `dms ipc call <target> <function> [params...]` — the primary external control surface. Targets include: `audio`, `mic`, `brightness`, `night`, `mpris`, `lock`, `sessions`, `inhibit`, `powerprofile`, `wallpaper`, `profile`, `theme`, `bar`, `island`, `dock`, `widget`, `spotlight`, `spotlight-bar`, `clipboard`, `notifications`, `processlist`, `powermenu`, `control-center`, `notepad`, `settings`, `dash`, `file`, `color-picker`, `welcome`, `niri` (screenshot), `keybinds`, `window-rules`, `workspace-rename`, `outputs`, `plugins`, `systemupdater`, `defaultApp`, `desktopWidget`, `toast`.
- **CLI:** `dms run`, `dms setup`, `dms doctor`, `dms ipc list`, `dms keybinds`, `dms plugins search/lock/restore`, `dms color pick`, `dms switch-user`, etc.
- **Plugins:** registry at plugins.danklinux.com; `dms plugins search/lock/restore`; hot-reload via `dms ipc call plugins reload <id>`.
- **Cheatsheets:** custom JSON keybind cheatsheets in `~/.config/DankMaterialShell/cheatsheets/` (consumed by the `keybinds` modal).

### 2.2 Niri integration specifics

DMS integrates with niri via generated KDL fragments included at the end of `~/.config/niri/config.kdl`:

```kdl
include "dms/colors.kdl"
include "dms/layout.kdl"
include "dms/alttab.kdl"
include "dms/binds.kdl"
```

Plus a managed window-rules fragment (`~/.config/niri/dms/windowrules.kdl`, app-id `com.danklinux.dms` → open-floating). DMS startup is `spawn-at-startup "dms" "run"` or systemd (`systemctl --user add-wants niri.service dms`).

**Coexistence with the Ominty generated fragment** (`~/.config/ominty/generated/niri/bindings.kdl`) is the key integration concern — see §4.

---

## 3. Capability Classification

Classification per docs/07 §28:

```text
USE DMS            — adopt DMS capability as-is, wire via IPC
EXTEND DMS         — use DMS capability, extend via plugin/cheatsheet/config
OMINTY COMPONENT  — build in Ominty (registry/runner/generator/search)
DEFER              — not needed for Phase 1
```

### 3.1 Checklist classification (docs/07 §27)

| # | Capability | Classification | Evidence / Notes |
|---|---|---|---|
| 1 | **Bar quality** | USE DMS | Full bar: workspaces, tray, clock, battery, media, widgets; per-bar IPC (`bar` target); auto-hide, position control. Replaces the minimal Quickshell bar. |
| 2 | **Niri integration** | USE DMS | Native niri fragments (colors/layout/alttab/binds), niri screenshot IPC (niri 25.11+), window-rules editor, workspace-rename dialog, output profiles. |
| 3 | **Workspace presentation** | USE DMS | Workspaces widget + niri-native workspace switching; `workspace-rename` IPC. Niri remains authoritative for compositor state (docs/07 §29). |
| 4 | **Launcher capability** | USE DMS + EXTEND | Spotlight launcher (`spotlight`/`spotlight-bar` IPC) with modes all/apps/files/plugins and `openQuery`. Ominty search can feed it via a plugin or `openQuery` (see §3.2). |
| 5 | **Custom action support** | EXTEND DMS | DMS launcher is plugin-extensible; Ominty actions can be exposed as a launcher plugin. Until then, `ominty action run <id>` remains the canonical execution path. |
| 6 | **Notification support** | USE DMS | Notification center + popups + Do-Not-Disturb (`notifications` IPC). Replaces the mako gap. |
| 7 | **OSD** | USE DMS | Built-in OSD for volume/mic/brightness/power-profile changes. |
| 8 | **Wi-Fi interface** | USE DMS | Control center (`control-center` IPC) covers network. NetworkManager remains the provider. |
| 9 | **Bluetooth interface** | USE DMS | Control center covers Bluetooth. Blueman remains installed (existing user config preserved). |
| 10 | **Audio interface** | USE DMS | `audio`/`mic` IPC (setvolume, increment, mute, cycleoutput, OSD). Replaces `wpctl` binds. |
| 11 | **Power controls** | USE DMS | `powermenu` IPC, `powerprofile` IPC (needs power-profiles-daemon/tuned-ppd/tlp-pd), `inhibit` IPC, `lock lockAndOutputsOff`. |
| 12 | **Wallpaper workflow** | USE DMS + EXTEND | `wallpaper` IPC (global + per-monitor, next/prev/clear). Matugen theming boundary per docs/07 §18 — evaluate DMS's bundled pipeline before installing Matugen separately (AGENTS.md §15). |
| 13 | **Matugen integration** | EXTEND DMS | DMS ships dynamic theming (matugen + dank16). Theme adapters remain an Ominty concern (docs/08); DMS is the palette provider. |
| 14 | **IPC/CLI support** | USE DMS | `dms ipc call` is the stable, documented external interface — the natural adapter boundary for `adapters/dms/` (AGENTS.md §20). |
| 15 | **Extension/plugin options** | EXTEND DMS | Plugin registry + hot-reload (`plugins` IPC). Ominty launcher plugin is the planned extension point. |
| 16 | **Configuration stability** | USE DMS | Settings modal with `get`/`set` IPC; managed fragments; `dms doctor` diagnostics; systemd service. |

### 3.2 Additional classifications

| Capability | Classification | Notes |
|---|---|---|
| **Help / discoverability (Super+K)** | EXTEND DMS | `ominty help --json` can be emitted as a DMS custom cheatsheet (`~/.config/DankMaterialShell/cheatsheets/`), making Ominty actions visible in the DMS keybinds modal. |
| **App launch** | USE DMS | Spotlight resolves apps; `defaultApp` IPC launches MIME-type defaults (browser, fileManager, textEditor, etc.). |
| **Window management** | USE DMS (niri native) | `window.close`, `window.focus.*`, `workspace.*` stay native Niri (Contract 4, AGENTS.md §10). No change. |
| **Screenshot** | USE DMS | `niri screenshot` IPC (niri 25.11+) replaces gnome-screenshot gap. Requires swappy/satty editor. |
| **Lock screen** | USE DMS | `lock` IPC replaces swaylock gap (environment-audit finding). |
| **Brightness** | USE DMS | `brightness` IPC replaces brightnessctl gap (environment-audit finding). |
| **Media control** | USE DMS | `mpris` IPC replaces playerctl gap (environment-audit finding). |
| **Clipboard history** | USE DMS | `clipboard` IPC + `wl-paste --watch cliphist store` startup line. |
| **Process list / task manager** | USE DMS | `processlist` IPC. |
| **Session switching** | USE DMS | `sessions` IPC (logind wrapper). |
| **Night mode** | USE DMS | `night` IPC (gamma/color temperature). |
| **Keybinds cheatsheet** | EXTEND DMS | Custom JSON cheatsheets; Ominty help data feeds this. |
| **Greeter** | DEFER | Separate product (DankGreeter); not Phase 1. |
| **Weather / Calendar** | DEFER | Separate products (dcal); not Phase 1. |
| **Desktop widgets** | DEFER | Optional; not Phase 1 scope. |
| **Dank Island** | DEFER | v1.6 activity surface; evaluate after core integration. |

---

## 4. Niri Coexistence Analysis

### 4.1 Fragment layout after Stage 14

```text
~/.config/niri/config.kdl
  ├── (existing user config, preserved)
  ├── include optional=true "~/.config/ominty/generated/niri/bindings.kdl"   (Ominty)
  ├── include "dms/colors.kdl"                                                (DMS)
  ├── include "dms/layout.kdl"                                                (DMS)
  ├── include "dms/alttab.kdl"                                                (DMS)
  └── include "dms/binds.kdl"                                                 (DMS)
```

Positional precedence: later includes win on conflict. Order must be decided deliberately (see §4.3).

### 4.2 Binding overlap

| Key | Ominty (current) | DMS (default) | Resolution |
|---|---|---|---|
| `Mod+Space` | spawn ominty-popup | spotlight toggle | **DMS owns it** — remove from Ominty fragment; popup retired |
| `Mod+K` | spawn ominty-popup | focus-window-up | **DMS owns it** — help.keys.open moved to `Mod+Shift+Space` |
| `Mod+Return` | app.terminal.open | — | Ominty keeps |
| `Mod+Shift+B` | app.browser.open | — | Ominty keeps |
| `Mod+Q` | close-window | close-window | **DMS owns it** (native) — registry action remains for CLI/palette/AI |
| `Mod+Left/Right` | focus-column | focus-column | **DMS owns it** (native) |
| `Mod+Page_Down/Up` | focus-workspace | focus-workspace | **DMS owns it** (native) |
| `Mod+V` | — | clipboard toggle | DMS |
| `Mod+M` | — | processlist | DMS |
| `Mod+N` | — | notifications | DMS |
| `Mod+Alt+L` | — | lock | DMS |
| `XF86Audio*` | wpctl binds (existing) | DMS audio/mpris IPC | DMS |
| `XF86MonBrightness*` | brightnessctl binds (broken) | DMS brightness IPC | DMS |

### 4.3 Conflict strategy

1. **DMS owns shell-level keys** (launcher, clipboard, notifications, lock, media keys).
2. **Ominty owns action keys** (app launch, help/search). DMS owns native Niri navigation (close, focus, workspace, move, monitors) — the registry actions remain for CLI/palette/AI invocation.
3. **No double-binding**: the Ominty generator must exclude keys claimed by DMS. Add a `dms_claimed_keys` exclusion set to the generator (Stage 14 change).
4. **DMS binds fragment** may be customized via DMS Settings → Keybinds rather than hand-editing `dms/binds.kdl` (managed fragment — prefer settings over manual edits, AGENTS.md §23).

### 4.4 Startup

- DMS: `spawn-at-startup "dms" "run"` in niri config (or `systemctl --user add-wants niri.service dms`).
- Ominty shell: existing `spawn-at-startup "quickshell" "-c" "ominty"` — **retire** once DMS bar is validated (avoid two bars, AGENTS.md §14).
- Ominty popup: retired once DMS spotlight + cheatsheet path is validated.

---

## 5. Adapter Impact (Stage 14)

| Ominty action | Current adapter | After Stage 14 |
|---|---|---|
| `app.terminal.open` / `app.browser.open` | app_launch (spawn) | unchanged (spawn) |
| `window.close` / `window.focus.*` / `workspace.*` | niri.native | unchanged (native) |
| `audio.volume.*` | command (`wpctl`) | **dms** (`dms ipc call audio ...`) |
| `audio.mute` | command (`wpctl`) | **dms** |
| `display.brightness.*` | command (`brightnessctl`, broken) | **dms** (`dms ipc call brightness ...`) |
| `session.lock` | (missing) | **dms** (`dms ipc call lock lock`) |
| `media.*` | (missing) | **dms** (`dms ipc call mpris ...`) |
| `help.keys.open` / `help.actions.search` | command (quickshell popup) | **dms** spotlight / cheatsheet |
| `theme.wallpaper.*` | (missing) | **dms** (`dms ipc call wallpaper ...`) |

New adapter module: `adapters/dms/` (AGENTS.md §20). DMS IPC is a stable documented interface — no forking required (AGENTS.md §13).

---

## 6. Install Requirements (for Stage 14)

1. **sudo required** — DMS is system-wide (OBS repo or source build). No user-local install path exists. This is a deliberate exception to the no-sudo working rule and requires explicit user approval.
2. Debian 13 (Trixie) OBS repos: `home:AvengeMedia:danklinux` + `home:AvengeMedia:dms` (stable) or `dms-git` (dev).
3. Quickshell already installed (0.3.0) — no action.
4. Optional: matugen (theming), swappy/satty (screenshot editor), power-profiles-daemon (power profile IPC), cliphist (clipboard history).
5. Post-install: `dms setup` generates niri starter config; then reconcile with existing config (preserve user config, AGENTS.md §3).

---

## 7. Risks and Open Questions

| Risk / Question | Impact | Mitigation |
|---|---|---|
| DMS v1.6 is new (2026-09-05) | Rapid iteration; config churn | Pin stable release; document config state; `dms doctor` before/after changes |
| LMDE 7 = Debian 13 base assumed | If base is actually Bookworm, OBS packages won't apply | Verify `cat /etc/os-release` before install |
| `Mod+Space` handover | Popup retired before DMS validated = launcher gap | Keep popup until DMS spotlight confirmed working |
| Two bars (DMS + Ominty shell) | Visual duplication | Retire Ominty shell only after DMS bar validated |
| DMS binds fragment is managed | Hand edits may be overwritten | Use DMS Settings → Keybinds; document in PROGRESS.md |
| Matugen bundling | Theme boundary (docs/08) | Evaluate DMS palette pipeline before installing Matugen separately |
| systemd service vs spawn-at-startup | Double-start risk | Choose one path; document in Stage 14 |
| DMS replaces polkit/swaylock/etc. | Existing user config | Preserve; only replace what is validated |

---

## 8. Conclusion

DMS v1.6 is a strong fit for Phase 1 shell infrastructure:

- **USE DMS** for bar, notifications, OSD, control center (Wi-Fi/Bluetooth), audio, brightness, lock, screenshot, media, wallpaper, power, clipboard, process list, session switching, night mode, output profiles.
- **EXTEND DMS** for launcher (Ominty actions as plugin), help/discoverability (custom cheatsheet), theming (Matugen boundary).
- **OMINTY COMPONENT** remains: action registry, runner, adapters, Niri fragment generator, search backend.
- **DEFER**: greeter, weather, calendar, desktop widgets, Dank Island.

The guiding rule (docs/07 §29) holds:

> Use DMS as infrastructure where it is strong; build Ominty where the interaction architecture requires something DMS does not provide.

**Next step (Stage 14):** install DMS (requires sudo approval), validate live, reconcile niri fragments, migrate adapters to `dms ipc call`, retire the temporary popup and minimal bar.