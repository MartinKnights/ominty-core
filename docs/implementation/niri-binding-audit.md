# Niri Binding Audit — omivoid-lmde

**Date:** 2026-09-10
**Stage:** 8 (docs/10-phase-1-implementation-plan.md §12)
**Status:** Complete

Compares the existing Niri configuration (`~/.config/niri/config.kdl`, 249 lines)
against the proposed Omivoid bindings (docs/02-interaction-spec.md §5–6,
docs/04-phase-1-action-catalogue.md).

**Note:** In Niri, `Mod` defaults to `Super`. `Mod+X` ≡ `Super+X` throughout.

---

## 1. Classification Legend

| Status | Meaning |
|---|---|
| `ACCEPT` | Proposed binding is free, or already bound to the same action |
| `COMPATIBLE` | Coexists with an existing binding without conflict |
| `CONFLICT` | Proposed binding collides with an existing binding for a different action |
| `CHANGE` | Proposed binding adjusted to avoid a conflict |
| `MIGRATE` | Existing binding moved/freed to make room for a core Omivoid action |
| `DEFER` | No binding applied in Phase 1 |

---

## 2. Immediate Actions (docs/02 §5)

| Proposed binding | Omivoid action | Existing binding | Status | Resolution |
|---|---|---|---|---|
| `Super+Enter` | app.terminal.open | — (free) | **ACCEPT** | New binding. Existing `Mod+T` → alacritty remains (COMPATIBLE). |
| `Super+Space` | help.actions.search | — (free) | **ACCEPT** | New binding. Existing `Mod+D` → fuzzel remains (COMPATIBLE; may be superseded by the palette in Stage 11–12). |
| `Super+K` | help.keys.open | `Mod+K` → focus-window-up | **MIGRATE** | **Core action.** focus-window-up has a redundant binding (`Mod+Up`); free `Mod+K` for `Super+K`. |
| `Super+A` | ai.open | — (free) | **ACCEPT** | New binding. All `Super+A,*` chords inherit the free prefix. |
| `Super+P` | project.* (reserved) | — (free) | **ACCEPT** | Reserved; no Phase 1 action yet. |
| `Super+Q` | window.close | `Mod+Q` → close-window | **ACCEPT** | Same action, already bound natively. |
| `Super+F` | window.fullscreen.toggle | `Mod+F` → maximize-column | **CHANGE** | `Mod+F` (maximize-column) is preserved (Contract 6). Bind fullscreen to the existing `Mod+Shift+F` → fullscreen-window instead. |
| `Super+Arrow` | window.focus.* | `Mod+Left/Right/Up/Down` → focus-column-left/right, focus-window-up/down | **ACCEPT** | Same actions, already bound natively. |
| `Super+1..9` | workspace.switch | `Mod+1..9` → focus-workspace N | **ACCEPT** | Same action, already bound natively. |
| `Super+Shift+1..9` | workspace.window.move | — (free; existing uses `Mod+Ctrl+1..9` → move-column-to-workspace) | **ACCEPT** | New binding. Existing `Mod+Ctrl+1..9` remains (COMPATIBLE). |

## 3. Application Bindings (docs/02 §6)

| Proposed binding | Role | Existing binding | Status | Resolution |
|---|---|---|---|---|
| `Super+Shift+B` | browser | — (free) | **ACCEPT** | New binding. |
| `Super+Shift+F` | files | `Mod+Shift+F` → fullscreen-window | **CONFLICT** | fullscreen-window keeps `Mod+Shift+F` (see §2 Super+F). **CHANGE** files to `Super+Shift+D` (Documents), or DEFER the direct binding (files remains reachable via palette/CLI/AI). |
| `Super+Shift+E` | editor | `Mod+Shift+E` → quit | **MIGRATE** | quit has a redundant binding (`Ctrl+Alt+Delete`); free `Mod+Shift+E` for the editor role. |
| `Super+Shift+N` | notes | — (free) | **ACCEPT** | New binding. |
| `Super+Shift+M` | mail | — (free) | **ACCEPT** | New binding. |
| `Super+Shift+T` | terminal (secondary) | — (free) | **ACCEPT** | Secondary binding for app.terminal.open (`keys = ["Super+Enter", "Super+Shift+T"]`). |

## 4. Window Actions (docs/04 §4)

| Proposed binding | Action | Existing binding | Status | Resolution |
|---|---|---|---|---|
| `Super+Q` | window.close | `Mod+Q` → close-window | **ACCEPT** | Native. |
| `Super+F` | window.fullscreen.toggle | `Mod+F` → maximize-column | **CHANGE** | Use existing `Mod+Shift+F` → fullscreen-window. |
| `Super+Left/Right/Up/Down` | window.focus.* | `Mod+Left/Right/Up/Down` | **ACCEPT** | Native. |
| (after audit) | window.move.left/right | `Mod+Ctrl+Left/Right` → move-column-left/right | **ACCEPT** | Map to existing movement conventions. |

## 5. Workspace Actions (docs/04 §5)

| Proposed binding | Action | Existing binding | Status | Resolution |
|---|---|---|---|---|
| `Super+Page_Down` | workspace.next | `Mod+Page_Down` → focus-workspace-down | **ACCEPT** | Native. (`Mod+U` also bound — COMPATIBLE.) |
| `Super+Page_Up` | workspace.previous | `Mod+Page_Up` → focus-workspace-up | **ACCEPT** | Native. (`Mod+I` also bound — COMPATIBLE.) |
| `Super+1..9` | workspace.switch | `Mod+1..9` → focus-workspace N | **ACCEPT** | Native. |
| `Super+Shift+1..9` | workspace.window.move | — (free) | **ACCEPT** | New binding. |

## 6. System / Network / Theme / Capture / AI / Help

| Proposed binding | Action | Existing binding | Status | Resolution |
|---|---|---|---|---|
| `Super+Ctrl+W` | network.wifi.open | — (free) | **ACCEPT** | New binding. |
| `Super+Ctrl+B` | network.bluetooth.open | — (free) | **ACCEPT** | New binding. |
| `Super+Ctrl+Space` | theme.wallpaper.select | — (free) | **ACCEPT** | New binding. |
| `Print` | capture.screenshot.full | `Print` → screenshot | **ACCEPT** | Native. |
| `Shift+Print` | capture.screenshot.region | — (free; `Ctrl+Print` → screenshot-screen, `Alt+Print` → screenshot-window exist) | **ACCEPT** | New binding. |
| `Super+A` / `Super+A,*` | ai.* | — (free) | **ACCEPT** | New prefix + chords. |
| `Super+K` | help.keys.open | `Mod+K` → focus-window-up | **MIGRATE** | See §2. |
| `Super+Space` | help.actions.search | — (free) | **ACCEPT** | See §2. |
| — | session.lock | `Super+Alt+L` → swaylock (⚠️ not installed) | **DEFER** | DMS lock integration (Stage 13). |
| — | session.logout / reboot / shutdown | — | **DEFER** | Palette-only in Phase 1. |
| `Super+Ctrl+P` | theme.wallpaper.select (carousel toggle) | — (free) | **ACCEPT** | New binding. `Super+Ctrl+C` was taken by DMS (`center-visible-columns`). See theme-implementation.md. |
| — | theme.wallpaper.next / previous / palette.regenerate / mode.toggle | — | **IMPLEMENTED (no binding)** | Palette/CLI/AI only — realised via the DMS Wallpaper Carousel and `dms.theme` (theme-implementation.md). |
| — | audio.volume.* / mute / microphone | `XF86Audio*` → wpctl/playerctl | **ACCEPT** | Map to existing media-key binds. ⚠️ playerctl not installed (audit finding 4). |

## 7. Existing Bindings Preserved Unchanged

The following existing bindings have no Omivoid counterpart and remain untouched:

- `Mod+Shift+Slash` → show-hotkey-overlay (COMPATIBLE with Super+K explorer)
- `Mod+O` → toggle-overview
- `Mod+H/J/K/L` → focus (H/J/L remain; **K freed by MIGRATE**)
- `Mod+Ctrl+*` → move column/window
- `Mod+Home/End`, `Mod+Ctrl+Home/End` → first/last column
- `Mod+Shift+*` → monitor focus (except `Shift+E` freed, `Shift+F` kept)
- `Mod+Shift+Ctrl+*` → move column to monitor
- `Mod+Ctrl+Page_Down/Up`, `Mod+Ctrl+U/I` → move column to workspace
- `Mod+Shift+Page_Down/Up`, `Mod+Shift+U/I` → move workspace
- `Mod+WheelScroll*` → workspace/column scrolling
- `Mod+Ctrl+1..9` → move-column-to-workspace
- `Mod+BracketLeft/Right`, `Mod+Comma/Period` → consume/expel
- `Mod+R`, `Mod+Shift+R`, `Mod+Ctrl+Shift+R`, `Mod+Ctrl+R` → width/height
- `Mod+Minus/Equal`, `Mod+Shift+Minus/Equal` → width/height
- `Mod+F` → maximize-column (kept)
- `Mod+M` → maximize-window-to-edges
- `Mod+Ctrl+F` → expand-column-to-available-width
- `Mod+C`, `Mod+Ctrl+C` → center
- `Mod+V`, `Mod+Shift+V` → floating
- `Mod+W` → tabbed display
- `Ctrl+Print`, `Alt+Print` → screenshot-screen/window
- `Mod+Escape` → inhibit
- `Mod+Shift+E` → quit (**freed by MIGRATE**; `Ctrl+Alt+Delete` → quit remains)
- `Mod+Shift+P` → power-off-monitors
- `XF86Audio*`, `XF86MonBrightness*` → media/brightness

## 8. Summary of Required Changes

| # | Change | Rationale |
|---|---|---|
| 1 | Free `Mod+K` (remove focus-window-up; `Mod+Up` covers it) → `Super+K` = help.keys.open | Core architectural action (interaction explorer); redundant binding exists |
| 2 | Free `Mod+Shift+E` (remove quit; `Ctrl+Alt+Delete` covers it) → `Super+Shift+E` = app.editor.open | Editor is a core app role; quit has a redundant binding |
| 3 | `window.fullscreen.toggle` binds to existing `Mod+Shift+F` (not `Super+F`) | `Mod+F` = maximize-column preserved (Contract 6); fullscreen already native |
| 4 | `app.files.open` → `Super+Shift+D` (or DEFER direct binding) | `Super+Shift+F` is taken by fullscreen-window |
| 5 | Add new bindings: `Super+Enter`, `Super+Space`, `Super+A`(+chords), `Super+Shift+B/N/M/T`, `Super+Shift+1..9`, `Super+Ctrl+W/B/Space`, `Shift+Print` | All free; no conflicts |

## 9. Unresolved Items

| Item | Status |
|---|---|
| `playerctl` not installed (media keys bound) | Install playerctl or use DMS media handling (Stage 13) |
| `brightnessctl` not installed (brightness keys bound) | Install brightnessctl or use DMS equivalent (Stage 13) |
| `swaylock` not installed (lock bound) | DMS lock integration (Stage 13) |
| `Mod+D` → fuzzel vs `Super+Space` palette | Coexist; fuzzel may be superseded by the Omivoid palette (Stage 11–12) |
| `Mod+T` → alacritty vs `Super+Enter` | Coexist; both launch the terminal role |

## 10. Application Plan

Changes are applied in Stage 9–10 via a **generated Niri fragment** (include file),
not by rewriting `config.kdl`. The existing config is preserved; the fragment
adds Omivoid bindings and the two MIGRATE changes are applied as a minimal,
documented edit to the existing config (removing the two redundant binds).

Backup: `~/.config/niri/config.kdl` is copied to a timestamped backup before
any edit (AGENTS.md §30).

## 11. Applied Status (Stage 9–10)

| # | Change | Status |
|---|---|---|
| 1 | Free `Mod+K` (removed `focus-window-up`; `Mod+Up` covers it) | **APPLIED** — `config.kdl` edited; backup `config.kdl.bak-omivoid-20260911` |
| 2 | Free `Mod+Shift+E` (removed `quit`; `Ctrl+Alt+Delete` covers it) | **APPLIED** — `config.kdl` edited |
| 3 | `window.fullscreen.toggle` → `Mod+Shift+F` | **ALREADY NATIVE** — no change needed |
| 4 | `app.files.open` → `Super+Shift+D` or DEFER | **PENDING** — decision deferred to Stage 11–12 (palette) |
| 5 | New bindings via generated fragment | **APPLIED** — `~/.config/omivoid/generated/niri/bindings.kdl` |

Generated fragment (`~/.config/omivoid/generated/niri/bindings.kdl`):

- `Mod+Return` → spawn omivoid `app.terminal.open` (registry → adapter)
- `Mod+Shift+B` → spawn omivoid `app.browser.open` (registry → adapter)
- `Mod+Q` → `close-window` (native)
- `Mod+Left` / `Mod+Right` → `focus-column-left` / `focus-column-right` (native)
- `Mod+Page_Down` / `Mod+Page_Up` → `focus-workspace-down` / `focus-workspace-up` (native)

Integration: `config.kdl` ends with
`include optional=true "~/.config/omivoid/generated/niri/bindings.kdl"`.
The include is positional (last), so Omivoid bindings take precedence on any
future conflict. `optional=true` means a missing generated file degrades to a
warning, never a config failure. `niri validate` passes on the full config.

Generator: `omivoid registry build` (validates registry → generates → validates
fragment with `niri validate` before writing; `--dry-run` prints without writing;
invalid output is removed, never left in place).

Chords (`Super+A,W`) and shell-handled adapters (`shell.explorer`, `shell.palette`)
are intentionally not generated into Niri — they belong to the shell (Stage 11–12).