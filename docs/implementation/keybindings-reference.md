# Keybindings Reference — ominty-core

**Status:** generated reference (read-only).
**Source of truth:** the Action Registry plus the live Niri/DMS configuration.
This page is produced from `ominty keybinds --json` — **do not edit by hand**;
regenerate with the commands below.

## 1. How this is produced

| Command | Purpose |
|---|---|
| `ominty keybinds --json` | merge registry + Niri + DMS, tag each row with its GKS domain |
| `ominty registry build` | regenerate the Niri bindings fragment from the registry |
| `ominty registry validate` | validate the registry before generating |

## 2. Configuration files

| Path | Role | Managed by |
|---|---|---|
| `~/.config/niri/config.kdl` | Niri compositor config; includes the DMS + Ominty fragments | user / Ominty |
| `~/.config/niri/dms/binds.kdl` | DMS shell bindings (launcher, media, window management) | DMS |
| `~/.config/ominty/generated/niri/bindings.kdl` | Ominty-generated Niri fragment | **generated** — never hand-edit |
| `<repo>/actions/*.toml` | Action Registry — the source of actions and their keys | Ominty |
| `<repo>/cli/omintylib/generator.py` | Registry → Niri fragment generator | Ominty |
| `<repo>/cli/omintylib/keybinds.py` | Cheat-sheet data aggregation + plain-English labels | Ominty |
| `~/.config/DankMaterialShell/plugins/omintyKeybinds/` | GKS cheat-sheet DMS plugin (mirror of `<repo>/shell/dms/ominty-keybinds/`) | Ominty |

## 3. The cheat sheet

| Item | Value |
|---|---|
| Opens with | `Super+Shift+S` (Niri `Mod+Shift+S`) |
| IPC | `dms ipc call omintyKeybinds toggle` |
| Registry action | `help.keybinds.open` |
| Plugin | `omintyKeybinds` (DMS `PluginComponent`, tabbed by domain) |
| Data | `ominty keybinds --json` |
| Nature | read-only; one tab per GKS domain; labels rendered in plain English |

> The interaction explorer (`Super+K`) and the cheat sheet (`Super+Shift+S`) are
> distinct surfaces: the explorer runs actions, the cheat sheet documents keys.

## 4. Full keybinding list

Tab labels are shown in parentheses with their underlying GKS domain. Media keys
on the Surface Book F-row are shown as `F1`–`F12`. Rows marked `(shadowed)` are
defined but lose to a higher-priority layer for the same key. Keys with no
physical equivalent on the target keyboard (`XF86AudioPrev`, `XF86AudioNext`,
`XF86AudioMicMute`, `XF86Launch1`) are omitted.

### Apps (`Application`) — 16

| Key | Action | Raw key | Source |
|---|---|---|---|
| Ctrl + A | Select all | `Ctrl+A` | Universal |
| Ctrl + C | Copy | `Ctrl+C` | Universal |
| Ctrl + F | Find | `Ctrl+F` | Universal |
| Ctrl + N | New | `Ctrl+N` | Universal |
| Ctrl + O | Open | `Ctrl+O` | Universal |
| Ctrl + P | Print | `Ctrl+P` | Universal |
| Ctrl + Q | Quit | `Ctrl+Q` | Universal |
| Ctrl + S | Save | `Ctrl+S` | Universal |
| Ctrl + Shift + R | Rename Workspace | `Ctrl+Shift+R` | DMS |
| Ctrl + Shift + Z | Redo | `Ctrl+Shift+Z` | Universal |
| Ctrl + V | Paste | `Ctrl+V` | Universal |
| Ctrl + W | Close document/tab | `Ctrl+W` | Universal |
| Ctrl + X | Cut | `Ctrl+X` | Universal |
| Ctrl + F5 | Media Volume Down | `Ctrl+XF86AudioLowerVolume` | DMS |
| Ctrl + F6 | Media Volume Up | `Ctrl+XF86AudioRaiseVolume` | DMS |
| Ctrl + Z | Undo | `Ctrl+Z` | Universal |

### Navigate (`Navigation`) — 5

| Key | Action | Raw key | Source |
|---|---|---|---|
| Alt + Shift + Tab | Previous Window | `Alt+Shift+Tab` | Niri |
| Alt + Shift + ` | Previous Window (Same App) | `Alt+Shift+grave` | Niri |
| Alt + Space | Spotlight Bar | `Alt+Space` | DMS |
| Alt + Tab | Next Window | `Alt+Tab` | Niri |
| Alt + ` | Next Window (Same App) | `Alt+grave` | Niri |

### Desktop (`Desktop`) — 88

| Key | Action | Raw key | Source |
|---|---|---|---|
| Super + 1 | Switch to Workspace 1 | `Mod+1` | DMS |
| Super + 2 | Switch to Workspace 2 | `Mod+2` | DMS |
| Super + 3 | Switch to Workspace 3 | `Mod+3` | DMS |
| Super + 4 | Switch to Workspace 4 | `Mod+4` | DMS |
| Super + 5 | Switch to Workspace 5 | `Mod+5` | DMS |
| Super + 6 | Switch to Workspace 6 | `Mod+6` | DMS |
| Super + 7 | Switch to Workspace 7 | `Mod+7` | DMS |
| Super + 8 | Switch to Workspace 8 | `Mod+8` | DMS |
| Super + 9 | Switch to Workspace 9 | `Mod+9` | DMS |
| Super + Alt + L | Lock Screen | `Mod+Alt+L` | DMS |
| Super + [ | Consume/Expel Window Left | `Mod+BracketLeft` | DMS |
| Super + ] | Consume/Expel Window Right | `Mod+BracketRight` | DMS |
| Super + C | Center Column | `Mod+C` | DMS |
| Super + , | Settings | `Mod+Comma` | DMS |
| Super + Down | Focus Window Down | `Mod+Down` | DMS |
| Super + F9 | Focus Last Column | `Mod+End` | DMS |
| Super + = | Grow Column Width | `Mod+Equal` | DMS |
| Super + Esc | Inhibit Shortcuts | `Mod+Escape` | DMS |
| Super + F | Maximize Column | `Mod+F` | DMS |
| Super + H | Focus Column Left | `Mod+H` | DMS |
| Super + F8 | Focus First Column | `Mod+Home` | DMS |
| Super + I | Focus Workspace Up | `Mod+I` | DMS |
| Super + J | Focus Window Down | `Mod+J` | DMS |
| Super + K | Focus Window Up | `Mod+K` | DMS (shadowed) |
| Super + K | Interaction Explorer | `Mod+K` | Ominty |
| Super + L | Focus Column Right | `Mod+L` | DMS |
| Super + Left | Focus Column Left | `Mod+Left` | DMS |
| Super + M | Task Manager | `Mod+M` | DMS |
| Super + - | Shrink Column Width | `Mod+Minus` | DMS |
| Super + N | Notifications | `Mod+N` | DMS |
| Super + O | Overview | `Mod+O` | DMS |
| Super + P | Cycle Display Profile | `Mod+P` | DMS |
| Super + F11 | Focus Workspace Down | `Mod+Page_Down` | DMS |
| Super + F10 | Focus Workspace Up | `Mod+Page_Up` | DMS |
| Super + . | Expel Window from Column | `Mod+Period` | DMS |
| Super + Q | Close Window | `Mod+Q` | DMS |
| Super + R | Cycle Column Width | `Mod+R` | DMS |
| Super + Enter | Open Terminal | `Mod+Return` | Ominty |
| Super + Right | Focus Column Right | `Mod+Right` | DMS |
| Super + Shift + 1 | Move Column to Workspace 1 | `Mod+Shift+1` | DMS |
| Super + Shift + 2 | Move Column to Workspace 2 | `Mod+Shift+2` | DMS |
| Super + Shift + 3 | Move Column to Workspace 3 | `Mod+Shift+3` | DMS |
| Super + Shift + 4 | Move Column to Workspace 4 | `Mod+Shift+4` | DMS |
| Super + Shift + 5 | Move Column to Workspace 5 | `Mod+Shift+5` | DMS |
| Super + Shift + 6 | Move Column to Workspace 6 | `Mod+Shift+6` | DMS |
| Super + Shift + 7 | Move Column to Workspace 7 | `Mod+Shift+7` | DMS |
| Super + Shift + 8 | Move Column to Workspace 8 | `Mod+Shift+8` | DMS |
| Super + Shift + 9 | Move Column to Workspace 9 | `Mod+Shift+9` | DMS |
| Super + Shift + B | Open Browser | `Mod+Shift+B` | Ominty |
| Super + Shift + Down | Move Window Down | `Mod+Shift+Down` | DMS |
| Super + Shift + E | Quit | `Mod+Shift+E` | DMS |
| Super + Shift + = | Grow Window Height | `Mod+Shift+Equal` | DMS |
| Super + Shift + F | Toggle Fullscreen | `Mod+Shift+F` | DMS |
| Super + Shift + H | Move Column Left | `Mod+Shift+H` | DMS |
| Super + Shift + I | Move Workspace Up | `Mod+Shift+I` | DMS |
| Super + Shift + J | Move Window Down | `Mod+Shift+J` | DMS |
| Super + Shift + K | Move Window Up | `Mod+Shift+K` | DMS |
| Super + Shift + L | Move Column Right | `Mod+Shift+L` | DMS |
| Super + Shift + Left | Move Column Left | `Mod+Shift+Left` | DMS |
| Super + Shift + - | Shrink Window Height | `Mod+Shift+Minus` | DMS |
| Super + Shift + N | Notepad | `Mod+Shift+N` | DMS |
| Super + Shift + P | Power Off Monitors | `Mod+Shift+P` | DMS |
| Super + Shift + F11 | Move Workspace Down | `Mod+Shift+Page_Down` | DMS |
| Super + Shift + F10 | Move Workspace Up | `Mod+Shift+Page_Up` | DMS |
| Super + Shift + R | Cycle Window Height | `Mod+Shift+R` | DMS |
| Super + Shift + Right | Move Column Right | `Mod+Shift+Right` | DMS |
| Super + Shift + S | Keybindings Cheat Sheet | `Mod+Shift+S` | Ominty |
| Super + Shift + Slash | Show Hotkeys | `Mod+Shift+Slash` | DMS |
| Super + Shift + T | Toggle Floating | `Mod+Shift+T` | DMS |
| Super + Shift + U | Move Workspace Down | `Mod+Shift+U` | DMS |
| Super + Shift + Up | Move Window Up | `Mod+Shift+Up` | DMS |
| Super + Shift + V | Switch Floating/Tiling | `Mod+Shift+V` | DMS |
| Super + Shift + W | Window Rules | `Mod+Shift+W` | DMS |
| Super + Shift + Scroll Down | Focus Column Right | `Mod+Shift+WheelScrollDown` | DMS |
| Super + Shift + Scroll Up | Focus Column Left | `Mod+Shift+WheelScrollUp` | DMS |
| Super + Space | App Launcher | `Mod+Space` | DMS |
| Super + T | Terminal | `Mod+T` | DMS |
| Super + Tab | Overview | `Mod+Tab` | DMS |
| Super + U | Focus Workspace Down | `Mod+U` | DMS |
| Super + Up | Focus Window Up | `Mod+Up` | DMS |
| Super + V | Clipboard | `Mod+V` | DMS |
| Super + W | Toggle Tabbed Display | `Mod+W` | DMS |
| Super + Scroll Down | Focus Workspace Down | `Mod+WheelScrollDown` | DMS |
| Super + Scroll Left | Focus Column Left | `Mod+WheelScrollLeft` | DMS |
| Super + Scroll Right | Focus Column Right | `Mod+WheelScrollRight` | DMS |
| Super + Scroll Up | Focus Workspace Up | `Mod+WheelScrollUp` | DMS |
| Super + X | Power Menu | `Mod+X` | DMS |
| Super + Y | Wallpapers | `Mod+Y` | DMS |

### Workspaces (`Workspace topology`) — 30

| Key | Action | Raw key | Source |
|---|---|---|---|
| Ctrl + Super + C | Center Visible Columns | `Ctrl+Mod+C` | DMS |
| Ctrl + Super + Down | Move Column to Workspace Down | `Ctrl+Mod+Down` | DMS |
| Ctrl + Super + F9 | Move Column to Last | `Ctrl+Mod+End` | DMS |
| Ctrl + Super + F | Expand Column | `Ctrl+Mod+F` | DMS |
| Ctrl + Super + H | Focus Monitor Left | `Ctrl+Mod+H` | DMS |
| Ctrl + Super + F8 | Move Column to First | `Ctrl+Mod+Home` | DMS |
| Ctrl + Super + I | Move Column to Workspace Up | `Ctrl+Mod+I` | DMS |
| Ctrl + Super + J | Focus Monitor Down | `Ctrl+Mod+J` | DMS |
| Ctrl + Super + K | Focus Monitor Up | `Ctrl+Mod+K` | DMS |
| Ctrl + Super + L | Focus Monitor Right | `Ctrl+Mod+L` | DMS |
| Ctrl + Super + Left | Focus Monitor Left | `Ctrl+Mod+Left` | DMS |
| Ctrl + Super + P | Wallpaper Carousel | `Ctrl+Mod+P` | Ominty |
| Ctrl + Super + R | Reset Window Height | `Ctrl+Mod+R` | DMS |
| Ctrl + Super + Right | Focus Monitor Right | `Ctrl+Mod+Right` | DMS |
| Ctrl + Super + Shift + Down | Move Column to Monitor Down | `Ctrl+Mod+Shift+Down` | DMS |
| Ctrl + Super + Shift + H | Move Column to Monitor Left | `Ctrl+Mod+Shift+H` | DMS |
| Ctrl + Super + Shift + J | Move Column to Monitor Down | `Ctrl+Mod+Shift+J` | DMS |
| Ctrl + Super + Shift + K | Move Column to Monitor Up | `Ctrl+Mod+Shift+K` | DMS |
| Ctrl + Super + Shift + L | Move Column to Monitor Right | `Ctrl+Mod+Shift+L` | DMS |
| Ctrl + Super + Shift + Left | Move Column to Monitor Left | `Ctrl+Mod+Shift+Left` | DMS |
| Ctrl + Super + Shift + Right | Move Column to Monitor Right | `Ctrl+Mod+Shift+Right` | DMS |
| Ctrl + Super + Shift + Up | Move Column to Monitor Up | `Ctrl+Mod+Shift+Up` | DMS |
| Ctrl + Super + Shift + Scroll Down | Move Column Right | `Ctrl+Mod+Shift+WheelScrollDown` | DMS |
| Ctrl + Super + Shift + Scroll Up | Move Column Left | `Ctrl+Mod+Shift+WheelScrollUp` | DMS |
| Ctrl + Super + U | Move Column to Workspace Down | `Ctrl+Mod+U` | DMS |
| Ctrl + Super + Up | Move Column to Workspace Up | `Ctrl+Mod+Up` | DMS |
| Ctrl + Super + Scroll Down | Move Column to Workspace Down | `Ctrl+Mod+WheelScrollDown` | DMS |
| Ctrl + Super + Scroll Left | Move Column Left | `Ctrl+Mod+WheelScrollLeft` | DMS |
| Ctrl + Super + Scroll Right | Move Column Right | `Ctrl+Mod+WheelScrollRight` | DMS |
| Ctrl + Super + Scroll Up | Move Column to Workspace Up | `Ctrl+Mod+WheelScrollUp` | DMS |

### System (`System`) — 1

| Key | Action | Raw key | Source |
|---|---|---|---|
| Ctrl + Alt + Delete | Task Manager | `Ctrl+Alt+Delete` | DMS |

### AI (`AI`) — 5

| Key | Action | Raw key | Source |
|---|---|---|---|
| Super + A | AI Menu | `Mod+A` | Ominty |
| Super + A, A | Ask AI | `Mod+A,A` | Ominty |
| Super + A, E | Explain Clipboard | `Mod+A,E` | Ominty |
| Super + A, P | Open AI Prompt | `Mod+A,P` | Ominty |
| Super + A, S | Summarise Clipboard | `Mod+A,S` | Ominty |

### Projects (`Projects`) — reserved, no bindings yet

### Hardware (`Hardware`) — 9

| Key | Action | Raw key | Source |
|---|---|---|---|
| F1 | Brightness Down | `XF86MonBrightnessDown` | DMS |
| F2 | Brightness Up | `XF86MonBrightnessUp` | DMS |
| F3 | Play/Pause | `XF86AudioPause` | DMS |
| F4 | Mute | `XF86AudioMute` | DMS |
| F5 | Volume Down | `XF86AudioLowerVolume` | DMS |
| F6 | Volume Up | `XF86AudioRaiseVolume` | DMS |
| Alt + F7 | Screenshot: Window | `Alt+Print` | DMS |
| Ctrl + F7 | Screenshot: Full Screen | `Ctrl+Print` | DMS |
| F7 | Screenshot: Region | `Print` | DMS |

---

*Generated from `ominty keybinds --json`. 154 bindings; one tab per GKS domain.*
