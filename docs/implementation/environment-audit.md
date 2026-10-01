# Environment Audit — ominty-core

**Date:** 2026-09-10
**Stage:** 0 (docs/10-phase-1-implementation-plan.md §4)
**Status:** Complete

This document records the state of the target machine before Phase 1 implementation begins. It is part of the implementation record (AGENTS.md §28).

---

## 1. Operating System

| Field | Value |
|---|---|
| Distribution | LMDE 7 (gigi) — Linux Mint Debian Edition |
| ID | linuxmint |
| Base | Debian (bookworm-derived, LMDE 7) |
| Kernel | (not captured — not required for Phase 1) |

LMDE is the Phase 1 validation platform (ADR-005). The eventual target is Void Linux; nothing in this audit should be assumed to transfer to Void without re-validation.

## 2. Niri

| Field | Value |
|---|---|
| Version | **26.04** (v26.04) |
| Config location | `~/.config/niri/config.kdl` (249 lines) |
| Config style | Clean, portable, commented "Portable: survives the move to Void Linux unchanged" |

### 2.1 Niri config structure (existing)

- **Input:** xkb layout from `org.freedesktop.locale1` (localectl), numlock on, touchpad tap + natural-scroll.
- **Output:** `eDP-1` at scale 2 (Surface Book 1, 3000x2000 @ 60Hz, 200% HiDPI).
- **Layout:** gaps 16, center-focused-column never, preset widths 1/3–1/2–2/3, default 1/2, focus-ring width 4 (active `#7fc8ff`, inactive `#505050`), border off.
- **Workspaces:** 9 dynamic workspaces by index, "matching Cinnamon's default (Super+1..9)". No named workspaces.
- **Window rules:** WezTerm initial-configure workaround; Firefox PiP floating.
- **Startup:** `spawn-at-startup "quickshell" "-c" "ominty"` (Ominty shell, Stage 7 comment). xwayland-satellite auto-spawned by niri.
- **Screenshots:** `screenshot-path "~/Pictures/Screenshots/Screenshot from %Y-%m-%d %H-%M-%S.png"`.
- **Key bindings:** full inventory in §8 below.

### 2.2 Niri 26.04 behavioural notes (from prior Stage 10 work)

- `niri msg event-stream` vocabulary: `Workspaces changed:`, `Workspace focused:`, `Window focus changed:`, `Window opened or changed:`, `Keyboard layouts changed:` (trigger-only, Rust-style).
- `focus-workspace N` works by **index/position**, not id; clamps beyond range; **no auto-create in 26.04**.
- `niri msg -j keyboard-layouts` → `{"names":["English (UK)"],"current_idx":0}`.
- `switch-layout <name>` for layout switching.
- No temperature/gamma action; `xkbcli` missing.

## 3. Quickshell

| Field | Value |
|---|---|
| Version | **0.3.0** (revision , distributed by Debian) |
| Config location | `~/.config/quickshell/ominty/shell.qml` (2257 bytes) |
| Status | Running (pid visible in PipeWire client list) |

Quickshell is already installed and running the minimal Ominty shell. Do not reinstall (AGENTS.md §3, §12).

## 4. DMS (DankMaterialShell)

| Field | Value |
|---|---|
| Installed | **NO** |
| Upstream | `AvengeMedia/DankMaterialShell` (github.com/AvengeMedia/DankMaterialShell) |
| Latest release | **v1.6 "Marble Tabby"** (2026-09-05) — unified versioning across DMS/dsearch/dgop/dcal/dgreeter |
| License | MIT |
| Stack | Quickshell (QML) + Go backend |
| Compositor support | niri, Hyprland, Sway, MangoWC, labwc, Scroll, MiracleWM (full features on niri) |
| Distribution | GitHub releases (`dms-full-amd64.tar.gz`), Arch package `dms-shell-niri`, NixOS flake, Debian packaging under `distro/` |
| Replaces | waybar, swaylock, swayidle, mako, fuzzel, polkit, etc. |

**Implication:** DMS adoption is provisionally accepted (ADR-002) but requires practical validation. Stage 13 (DMS evaluation) must install and evaluate DMS before integration. This audit records DMS as **absent** — installation is a Stage 13 task, not a Stage 0 task.

## 5. Matugen

| Field | Value |
|---|---|
| Installed | **NO** |
| Role | Wallpaper → palette generation (docs/08-theme-system.md) |

**Implication:** Theme system (Stage 15–16) requires Matugen or an evaluated alternative. DMS may bundle its own wallpaper/palette pipeline — evaluate DMS's existing capability first (AGENTS.md §15, docs/08 §4) before installing Matugen separately.

## 6. Network Provider

| Field | Value |
|---|---|
| Service | **NetworkManager** (systemd: active, nmcli: running) |

## 7. Audio Stack

| Field | Value |
|---|---|
| Server | **PipeWire 1.4.2** (`pipewire-0`) with WirePlumber |
| PulseAudio compat | Yes (PulseAudio on PipeWire 1.4.2) |
| Default sink | `alsa_output.pci-0000_00_1f.3.analog-stereo` (ALC298, Surface Book 1) |
| Active clients | WirePlumber, KDE Connect, Blueman, xdg-desktop-portal, LibreWolf, quickshell |

Volume control via `wpctl` (used in existing Niri binds).

## 8. Existing Keybindings (Niri config.kdl)

### 8.1 Programs / system

| Binding | Action |
|---|---|
| `Mod+Shift+Slash` | show-hotkey-overlay |
| `Mod+T` | spawn alacritty |
| `Mod+D` | spawn fuzzel |
| `Super+Alt+L` | spawn swaylock ⚠️ **swaylock not installed** |

### 8.2 Media / brightness (all `allow-when-locked=true`)

| Binding | Action |
|---|---|
| `XF86AudioRaiseVolume` | wpctl set-volume +0.1 |
| `XF86AudioLowerVolume` | wpctl set-volume -0.1 |
| `XF86AudioMute` | wpctl set-mute toggle |
| `XF86AudioMicMute` | wpctl set-mute source toggle |
| `XF86AudioPlay/Stop/Prev/Next` | playerctl ⚠️ **playerctl not installed** |
| `XF86MonBrightnessUp/Down` | brightnessctl ⚠️ **brightnessctl not installed** |

### 8.3 Window / layout operations

| Binding | Action |
|---|---|
| `Mod+O` | toggle-overview |
| `Mod+Q` | close-window |
| `Mod+Left/Down/Up/Right` + `Mod+H/J/K/L` | focus-column-left / focus-window-down / focus-window-up / focus-column-right |
| `Mod+Ctrl+Left/Down/Up/Right` + `Mod+Ctrl+H/J/K/L` | move-column-left / move-window-down / move-window-up / move-column-right |
| `Mod+Home/End` | focus-column-first / focus-column-last |
| `Mod+Ctrl+Home/End` | move-column-to-first / move-column-to-last |
| `Mod+Shift+Left/Down/Up/Right` + `Mod+Shift+H/J/K/L` | focus-monitor-* |
| `Mod+Shift+Ctrl+Left/Down/Up/Right` + `Mod+Shift+Ctrl+H/J/K/L` | move-column-to-monitor-* |
| `Mod+BracketLeft/Right` | consume-or-expel-window-left/right |
| `Mod+Comma/Period` | consume-window-into-column / expel-window-from-column |
| `Mod+R` / `Mod+Shift+R` | switch-preset-column-width / back |
| `Mod+Ctrl+Shift+R` / `Mod+Ctrl+R` | switch-preset-window-height / reset-window-height |
| `Mod+Minus/Equal` | set-column-width -10%/+10% |
| `Mod+Shift+Minus/Equal` | set-window-height -10%/+10% |
| `Mod+F` / `Mod+Shift+F` | maximize-column / fullscreen-window |
| `Mod+M` / `Mod+Ctrl+F` | maximize-window-to-edges / expand-column-to-available-width |
| `Mod+C` / `Mod+Ctrl+C` | center-column / center-visible-columns |
| `Mod+V` / `Mod+Shift+V` | toggle-window-floating / switch-focus-between-floating-and-tiling |
| `Mod+W` | toggle-column-tabbed-display |

### 8.4 Workspace operations

| Binding | Action |
|---|---|
| `Mod+Page_Down/Up` + `Mod+U/I` | focus-workspace-down / focus-workspace-up |
| `Mod+Ctrl+Page_Down/Up` + `Mod+Ctrl+U/I` | move-column-to-workspace-down/up |
| `Mod+Shift+Page_Down/Up` + `Mod+Shift+U/I` | move-workspace-down/up |
| `Mod+WheelScrollDown/Up` | focus-workspace-down/up (cooldown 150ms) |
| `Mod+Ctrl+WheelScrollDown/Up` | move-column-to-workspace-down/up |
| `Mod+WheelScrollRight/Left` | focus-column-right/left |
| `Mod+Ctrl+WheelScrollRight/Left` | move-column-right/left |
| `Mod+Shift+WheelScrollDown/Up` | focus-column-right/left |
| `Mod+Ctrl+Shift+WheelScrollDown/Up` | move-column-right/left |
| `Mod+1..9` | focus-workspace 1..9 (by index) |
| `Mod+Ctrl+1..9` | move-column-to-workspace 1..9 |

### 8.5 Screenshots / misc

| Binding | Action |
|---|---|
| `Print` | screenshot |
| `Ctrl+Print` | screenshot-screen |
| `Alt+Print` | screenshot-window |
| `Mod+Escape` | toggle-keyboard-shortcuts-inhibit |
| `Mod+Shift+E` / `Ctrl+Alt+Delete` | quit |
| `Mod+Shift+P` | power-off-monitors |

### 8.6 Binding audit implications (preliminary)

- **Modifier:** `Mod` = Super (per Niri default). Ominty grammar uses `Super+key` navigation, `Super+Shift+key` apps, `Super+Ctrl+key` system.
- **Conflicts to resolve in Stage 8 (niri-binding-audit.md):**
  - `Mod+D` currently = fuzzel launcher. Ominty palette (`Super+Space`) and Super+K explorer will need to replace or coexist with this.
  - `Mod+T` currently = alacritty. Ominty `app.terminal.open` (Super+Enter per docs/04) will conflict.
  - `Mod+Shift+E` = quit; `Mod+Shift+P` = power-off-monitors — system namespace candidates.
  - `Mod+1..9` workspace-by-index matches docs/04 workspace navigation intent.
  - `Mod+Q` close-window, `Mod+F` maximize, `Mod+V` floating — native actions that should stay native (Contract 4).
- **Missing binaries referenced by config:** `swaylock`, `playerctl`, `brightnessctl` are bound but **not installed**. These binds currently fail silently. DMS replaces swaylock; playerctl/brightnessctl may be needed or replaced by DMS equivalents.

## 9. Applications (for app roles, docs/04 + docs/12 config/apps.toml)

| Role | Application | Path | Notes |
|---|---|---|---|
| Terminal | **alacritty** | /usr/bin/alacritty | Primary; also gnome-terminal available |
| Browser | **librewolf** | /usr/bin/librewolf | Also firefox, firefox-esr |
| File manager | **nemo** | /usr/bin/nemo | Cinnamon file manager |
| Editor | **nvim** | /usr/local/bin/nvim | Primary; vim also available |
| Notes | **obsidian** | ~/.local/bin/obsidian | |
| Mail | **thunderbird** | /usr/bin/thunderbird | |
| Launcher | **fuzzel** | /usr/bin/fuzzel | Currently bound to Mod+D |

## 10. Screenshot Tooling

| Tool | Status |
|---|---|
| gnome-screenshot | /usr/bin/gnome-screenshot |
| grim / slurp | **not installed** |
| hyprshot / flameshot / spectacle / maim / scrot | not installed |

Niri has native `screenshot` / `screenshot-screen` / `screenshot-window` binds (Print keys) — these are the primary screenshot path. gnome-screenshot is a fallback for region capture.

## 11. AI Stack

| Component | Version | Path |
|---|---|---|
| Pi | 0.85.1 | ~/.nvm/versions/node/v22.22.3/bin/pi |
| Herdr | 0.9.0 | ~/.local/bin/herdr |

AI integration is Stage 18–20. This audit records presence only.

## 12. Runtime Environment

| Field | Value |
|---|---|
| XDG_CONFIG_HOME | unset (defaults to ~/.config) |
| XDG_CACHE_HOME | unset (defaults to ~/.cache) |
| XDG_DATA_HOME | unset (defaults to ~/.local/share) |
| Python | 3.13.5 |
| Node | v22.22.3 (via nvm) |
| Shell | bash |

## 13. Existing Ominty State

| Item | Status |
|---|---|
| `~/.config/ominty/` | **does not exist** — runtime config to be created per docs/12 |
| `~/.config/quickshell/ominty/shell.qml` | exists (2257 bytes, minimal shell) |
| `~/.config/niri/config.kdl` | exists (249 lines, audited above) |
| Ominty repo | `~/Projects/Ominty` (git, branch main) |
| ominty-core location | `~/Projects/Ominty/ominty-core/` — **currently untracked inside the Ominty repo** |

**Note:** `ominty-core/` currently lives inside the Ominty git repository as an untracked directory. The docs describe it as its own repository ("Repository: ominty-core"). Decision needed: keep as subdirectory of Ominty repo, or initialise as a separate repository. This does not block Stage 1–7.

## 14. Findings Summary

| # | Finding | Impact | Action |
|---|---|---|---|
| 1 | DMS not installed | ADR-002 provisional — must validate | Stage 13: install + evaluate DMS |
| 2 | Matugen not installed | Theme pipeline needs palette generator | Stage 15: evaluate DMS palette capability first, then Matugen if needed |
| 3 | `swaylock` bound but not installed | Lock bind fails silently | DMS replaces swaylock (docs/07); verify in Stage 13 |
| 4 | `playerctl` bound but not installed | Media keys fail silently | Install playerctl or use DMS media handling |
| 5 | `brightnessctl` bound but not installed | Brightness keys fail silently | Install brightnessctl or use DMS equivalent |
| 6 | No grim/slurp | Region capture limited to gnome-screenshot | Niri native screenshot binds are primary; evaluate in Stage 13 |
| 7 | `Mod+D` = fuzzel, `Mod+T` = alacritty | Conflicts with Ominty grammar (Super+Space palette, Super+Enter terminal) | Stage 8 binding audit |
| 8 | ominty-core inside Ominty repo (untracked) | Repo boundary unclear | Decide: separate repo vs subdirectory |
| 9 | XDG vars unset | Defaults apply | Use XDG defaults with fallbacks (AGENTS.md §22) |

## 15. Baseline

The recoverable baseline for Phase 1:

| Path | Purpose |
|---|---|
| `~/.config/niri/config.kdl` | Niri config (249 lines) — back up before any modification |
| `~/.config/quickshell/ominty/shell.qml` | Minimal Ominty shell — back up before modification |
| `~/.config/ominty/` | Will be created fresh (no existing data to preserve) |

Backup strategy: copy to `~/.config/ominty/backups/` or a timestamped directory before each significant change (AGENTS.md §30). At least one rollback path must be tested during Phase 1.