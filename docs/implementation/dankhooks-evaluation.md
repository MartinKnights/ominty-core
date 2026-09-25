# dankHooks Evaluation (ADR-006 §27–28)

**Date:** 2026-09-24
**Stage:** Phase 1 close-out
**Status:** Complete
**Sources:** `~/.config/DankMaterialShell/plugins/.repos/.../DankHooks/` (v1.0.9),
`docs/implementation/dms-plugin-inventory.md` §4.2

ADR-006 §27–28 ask whether a DMS plugin can provide the event integration the
Omivoid roadmap needs (e.g. wallpaper changed → regenerate theme) **without an
Omivoid daemon**. `dankHooks` was the candidate.

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

| Hook | Value | Possible Omivoid use |
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
daemon that can trigger an Omivoid action on a DMS event without a new Omivoid
process. The intended wiring is:

```text
DMS event (e.g. wallpaper changed)
   ↓
dankHooks  →  script
   ↓
omivoid action run <id>
```

**However, Phase 1 has no mandatory event→action hook to wire.** DMS already
owns the theme pipeline and regenerates via matugen on wallpaper change (the
`onMatugenCompleted` hook exists precisely because DMS drives it). Omivoid's
`theme.palette.regenerate` is a *manual* regeneration action, not something that
must fire on the event. So the bridge is valuable as **architecture**, not as a
current need.

## 4. Recommendation

**ADOPT WITH CONFIGURATION — path chosen, not activated.**

- Record `dankHooks` as the designated event bridge (satisfies ADR-006 §27,
  avoids an Omivoid daemon).
- **Do not install or wire it yet**: there is no concrete Phase 1 event→action
  need, and AGENTS.md §35 favours not adding a daemon speculatively.
- When a real need appears (e.g. a future `theme.*`/`ai.*` reaction, or
  Omivoid-owned regeneration), install and configure it as below.

### Activation recipe (for when it is needed)

1. Install:
   ```text
   dms plugins install dankHooks
   ```
2. Add a thin dispatcher the hook can call, e.g. `cli/omivoid-hook` (or a small
   shell script) that maps a hook name to an action:
   ```sh
   #!/bin/sh
   # args: <hookName> <value>
   case "$1" in
     onWallpaperChanged) exec omivoid action run theme.palette.regenerate ;;
     # add mappings as Omivoid-owned reactions are introduced
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

Evaluation **complete**: `dankHooks` is the correct event-integration mechanism
(ADOPT WITH CONFIGURATION) and requires no Phase 1 work beyond recording the
decision and the activation recipe. `dms-plugin-inventory.md` §4.2 updated to
match.
