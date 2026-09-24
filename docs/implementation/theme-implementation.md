# Theme Implementation — Wallpaper Carousel + Palette Regeneration

**Date:** 2026-09-19
**Stage:** Phase 1 close-out (docs/13 §14, §15)
**Status:** Complete

Implements the Appearance actions against the DMS Wallpaper Carousel plugin
and the DMS matugen pipeline, and records the theme → external-application
evidence required by DoD §14.

---

## 1. Summary

| Item | Outcome |
|---|---|
| `theme.wallpaper.select` | Opens/closes the carousel — `Super+Ctrl+P` (was broken) |
| `theme.wallpaper.next` / `.previous` | Carousel highlight next/previous |
| `theme.palette.regenerate` | Re-runs matugen from the current wallpaper (new) |
| `theme.mode.toggle` | DMS light/dark toggle (new) |
| Wallpaper folder | `~/Wallpapers` (29 images) |
| Theme → external app (§14) | Already provided by DMS — recorded in §6 |

Registry: **29 actions, 0 warnings**. Tests: **160 passing** (11 new).

---

## 2. Mechanism

```text
theme.wallpaper.select    → dms ipc call wallpaperCarousel toggle   (Super+Ctrl+P)
theme.wallpaper.next      → dms ipc call wallpaperCarousel cycleNext
theme.wallpaper.previous  → dms ipc call wallpaperCarousel cyclePrevious
theme.mode.toggle         → dms ipc call theme toggle
theme.palette.regenerate  → dms.theme adapter → dms matugen generate
```

`theme.wallpaper.select` is bound to **`Super+Ctrl+P`** (toggle — press to
open, press again to close). `Super+Ctrl+C` was the first choice but DMS
already binds it to `center-visible-columns` (`~/.config/niri/dms/binds.kdl`),
and niri rejects duplicate keybinds. The catalogue proposed
`Super+Ctrl+Space`; `Super+Ctrl+P` was selected instead.

The generator now emits niri binds for `dms.ipc` actions:

```kdl
// theme.wallpaper.select
Mod+Ctrl+P {
    spawn "dms" "ipc" "call" "wallpaperCarousel" "toggle"
}
```

Previously only `niri.native`, `app.launch`, and `command` actions produced
binds, so a `dms.ipc` action with `keys` silently generated nothing. Binding
directly to `dms ipc call` avoids a CLI process hop for a UI action
(AGENTS.md §10).

`dms.theme` (`adapters/dms/theme.py`) reads the current wallpaper
(`dms ipc call wallpaper get`) and mode (`… theme getMode`), then runs:

```text
dms matugen generate --value <wallpaper> --kind image|hex --mode <mode>
    --state-dir  ~/.local/state/DankMaterialShell
    --shell-dir  /usr/share/quickshell/dms
    --config-dir ~/.config/DankMaterialShell
```

DMS's `theme` IPC target exposes only `dark`/`light`/`getMode`/`toggle`,
so regeneration is the `dms matugen generate` subcommand, not an IPC call.

---

## 3. Bug found and fixed: `theme.wallpaper.select`

The pre-existing action called `dms ipc call wallpaper select`:

```text
$ dms ipc call wallpaper select
Function not found.
```

`wallpaper` exposes only `clear, get, getFor, next, nextFor, prev, prevFor,
set, setFor` — there is no `select`. The action was repointed to the
carousel's `toggle`, which is the actual browse-and-pick surface.

---

## 4. Carousel semantics (verified)

The carousel's cycle commands **open the overlay and move the highlight**;
they do not apply a wallpaper. Applying happens on Enter
(`pickWallpaper()` → `wallpaperPicked` → `SessionData.setWallpaper`).
This is documented in the plugin README and confirmed in `Carousel.qml`:

```text
cycleNext → root.cycle(+1) → incrementCurrentIndex()   # highlight only
Enter     → currentItem.pickWallpaper()                # applies
```

Action descriptions state this explicitly so the name is not misleading.

**Contrast:** DMS's own `wallpaper next`/`prev` *do* apply immediately
(verified live). They cycle the current wallpaper's directory.

---

## 5. Wallpaper folder and the carousel override

Wallpapers moved from `~/Pictures/Backgrounds` to **`~/Wallpapers`** (29
images), and the active wallpaper was set into that folder so stock DMS
cycling also uses it.

The carousel supports a `wallpaperDirectory` override (otherwise it follows
the active wallpaper's folder). **DMS reads `plugin_settings.json` only at
startup** — it does not hot-reload external edits:

```text
$ dms ipc call settings get pluginSettings
… "wallpaperCarousel":{"enabled":true}                 # in-memory

$ cat plugin_settings.json
… "wallpaperDirectory":"~/Wallpapers"           # on disk
```

Neither atomic nor non-atomic external writes updated DMS's in-memory
settings; `plugins reload` re-instantiates the plugin but its `pluginData`
comes from those in-memory settings. The supported write path is the plugin
settings UI (which calls `SettingsData.setPluginSetting`). Applying the
override therefore required a DMS restart (`dms restart`), after which:

```text
$ dms ipc call settings get pluginSettings
… "wallpaperDirectory":"~/Wallpapers"           # in-memory ✓
# carousel cycles the full range (index 0–28 = 29 images) ✓
```

Proven with a 2-image control folder: with the override set to it, the
carousel was bounded to indices 0–1.

**Operational note:** changing the override via file edit requires
`dms restart`; via the DMS settings UI it applies immediately.

---

## 6. Theme → external application (§14 evidence)

DMS already themes external applications through matugen. `dms matugen check`
reports detected templates:

```text
detected: gtk, niri, qt5ct, qt6ct, firefox, ghostty, alacritty, nvim,
          dgop, kcolorscheme, zed
```

Observed outputs: `~/.config/alacritty/dank-theme.toml`,
`~/.config/qt6ct/colors/matugen.conf`, `~/.config/DankMaterialShell/firefox.css`.

So the DoD §14 flow is satisfied:

```text
wallpaper → palette (matugen/dank16) → shell (DMS) → external app
```

No Omivoid theme adapter is required for Phase 1; DMS is the palette
provider (AGENTS.md §15, dms-evaluation.md §4.2/§13).

---

## 7. Palette regeneration — DMS no-op quirk

`dms matugen generate` exits **2** with
`INFO go: No color changes detected, skipping refresh` when the palette is
already current. The adapter treats that message as a successful no-op
rather than a failure.

---

## 8. Files

| File | Change |
|---|---|
| `actions/theme.toml` | 5 Appearance actions (carousel + regenerate + mode) |
| `adapters/dms/theme.py` | `dms.theme` regeneration adapter (new) |
| `cli/omivoidlib/adapters.py` | register `dms.theme` |
| `cli/omivoidlib/registry.py` | known adapter `dms.theme` |
| `cli/omivoidlib/generator.py` | emit niri binds for `dms.ipc` actions |
| `tests/test_theme.py` | 10 tests (new) |
| `tests/test_generator.py` | `dms.ipc` bind test |
| `~/.config/DankMaterialShell/plugin_settings.json` | carousel `wallpaperDirectory` (backup taken) |
| `~/Wallpapers/` | 29 wallpapers (moved from `~/Pictures/Backgrounds`) |

---

## 9. Evidence

```text
$ omivoid registry validate
29 action(s), 0 error(s), 0 warning(s), 0 info

$ omivoid action run theme.palette.regenerate --json
{"success": true, "state": {"mode": "dark", "value": "~/Wallpapers/…"}}

$ omivoid action run theme.mode.toggle      → dark → light → dark (restored)

$ omivoid action run theme.wallpaper.next
→ dms ipc call wallpaperCarousel cycleNext   (opens + highlights)

$ dms ipc call wallpaper next
→ wallpaper applied: Loop-Z17Pro.jpg → prev → LibreWolf_wallpaper.png
```

---

## 10. Limitations

* Carousel cycle actions highlight rather than apply (by plugin design).
  If immediate apply is wanted, `theme.wallpaper.next`/`previous` could use
  DMS `wallpaper next`/`prev` instead — left as-is because the carousel was
  the requested browsing surface.
* Changing the carousel folder by file edit needs `dms restart` (see §5).
* Only `theme.wallpaper.select` has a Niri keybinding (`Super+Ctrl+P`);
  the other Appearance actions are palette/CLI/AI only.
