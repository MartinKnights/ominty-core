# dankHooks Evaluation (ADR-006 §27–28)

**Date:** 2026-09-24 (activated 2026-09-27)
**Stage:** Phase 1 close-out
**Status:** Installed and wired
**Sources:** `~/.config/DankMaterialShell/plugins/.repos/.../DankHooks/` (v1.0.9),
`docs/implementation/dms-plugin-inventory.md` §4.2

ADR-006 §27–28 ask whether a DMS plugin can provide the event integration the
Ominty roadmap needs (e.g. wallpaper changed → regenerate theme) **without an
Ominty daemon**. `dankHooks` was the candidate.

---

## 1. What the plugin is

| Field | Value |
|---|---|
| ID | `dankHooks` |
| Author | Avenge Media (first-party) |
| Type | `daemon` |
| Permissions | `settings_read`, `settings_write` |
| Version reviewed | 1.0.9 |

It watches DMS/session state and executes a **user-configured script per event**.
The script receives two arguments: the hook name and the event value.

`executeHook(scriptPath, hookName, hookValue)` spawns the configured script (no
shell) with those two arguments. There is no built-in action vocabulary — the
behaviour lives entirely in the script the user points each hook at.

## 2. Relevant hooks

| Hook | Value | Possible Ominty use |
|---|---|---|
| `onWallpaperChanged` | wallpaper path | (re)generate theme output |
| `onMatugenCompleted` | `<mode>:<result>` | react to DMS palette generation |
| `onThemeChanged` | theme name | react to theme switch |
| `onLightModeChanged` | `light`/`dark` | react to mode switch |
| `onSessionLocked` / `onSessionUnlocked` | `locked`/`unlocked` | session state |
| `onWifiConnectedChanged`, `onBatteryLevelChanged`, … | varied | future AI/context signals |

(The full list is in the plugin `README.md`.)

## 3. Fit against the requirement

`dankHooks` **matches** the ADR-006 §27 requirement: it is a first-party DMS
daemon that can trigger an Ominty action on a DMS event without a new Ominty
process. The intended wiring is:

```text
DMS event (e.g. wallpaper changed)
   ↓
dankHooks  →  script
   ↓
ominty action run <id>
```

**However, Phase 1 has no mandatory event→action hook to wire.** DMS already
owns the theme pipeline and regenerates via matugen on wallpaper change (the
`onMatugenCompleted` hook exists precisely because DMS drives it). Ominty's
`theme.palette.regenerate` is a *manual* regeneration action, not something that
must fire on the event. So the bridge is valuable as **architecture**, not as a
current need.

## 4. Recommendation

**ADOPTED AND ACTIVATED (2026-09-27).**

- Record `dankHooks` as the designated event bridge (satisfies ADR-006 §27,
  avoids an Ominty daemon).
- The original evaluation recommended **not activating** it yet: there was no
  mandatory Phase 1 event→action need, and AGENTS.md §35 favours not adding a
  daemon speculatively. On 2026-09-27 the project decided the Ominty-owned
  regeneration reaction **is** a real need and activated the bridge (§6). The
  recipe below documents the intended wiring, now carried out.

### Activation recipe (for when it is needed)

1. Install:
   ```text
   dms plugins install dankHooks
   ```
2. Add a thin dispatcher the hook can call, e.g. `cli/ominty-hook` (or a small
   shell script) that maps a hook name to an action:
   ```sh
   #!/bin/sh
   # args: <hookName> <value>
   case "$1" in
     onWallpaperChanged) exec ominty action run theme.palette.regenerate ;;
     # add mappings as Ominty-owned reactions are introduced
     *) : ;;
   esac
   ```
3. Point the relevant hooks in DankHooks settings at that dispatcher
   (`wallpaperPath`, `matugenCompleted`, …).

### Caveats

- The plugin runs **user-provided scripts as the user**; hook scripts are trusted
  configuration, not sandboxed. Keep the dispatcher minimal and reviewable.
- Each fired hook spawns a process; keep mappings low-frequency.
- `dankHooks` is a DMS dependency; if DMS is replaced on Void, the event bridge
  must be revisited with it (tracked in the Void phase).

---

## 5. Outcome

Evaluation **complete**; the decision was **activated on 2026-09-27** (§6). The
`onWallpaperChanged` → `theme.palette.regenerate` bridge is wired and verified up
to the action boundary; the remaining step is a real-event desktop test.

## 6. Activation (2026-09-27)

Wired the event→action bridge for wallpaper changes.

| Piece | Detail |
|---|---|
| Plugin | `dankHooks` v1.0.9 — `dms plugins install dankHooks` (`plugins.lock.json` updated) |
| Dispatcher | `cli/ominty-hook` (repo; symlinked to `~/.local/bin/ominty-hook`): `onWallpaperChanged` → `ominty action run theme.palette.regenerate` |
| Hook config | `plugin_settings.json` → `dankHooks.enabled = true`, `dankHooks.wallpaperPath = ~/.local/bin/ominty-hook` (backup saved: `plugin_settings.json.bak-ominty-hook-*`) |
| Audit trail | mapped hooks append `ISO8601 onWallpaperChanged <path>` to `$XDG_STATE_HOME/ominty/hook.log` (`~/.local/state/ominty/hook.log`) |

Rationale for the specific mapping: `theme.palette.regenerate` re-runs the
matugen pipeline from the current wallpaper (docs/08 §27). DMS already
regenerates on a wallpaper change, so the hook-triggered run is usually a
no-change no-op ("No color changes detected" → success); the value is the
working event bridge + audit trail for future `theme.*`/`ai.*` reactions,
not a second generation pass.

**Verified 2026-09-27:**

- Dispatcher chain: `ominty-hook onWallpaperChanged <current-wallpaper>` →
  `OK: theme.palette.regenerate` (rc 0) + `hook.log` line.
- `dms restart` reloads the plugin cleanly; `dms plugins list` shows `Dank Hooks`.

**Manual desktop test (open):** trigger a real wallpaper change (e.g. next in the
wallpaper carousel) and confirm a `hook.log` line appears and the palette
regenerates. Restore the wallpaper afterwards. (No `dms ipc` wallpaper setter
exists, so a UI trigger is required.)

Caveats from §4 still apply: hook scripts run as the user; keep mappings
low-frequency.
