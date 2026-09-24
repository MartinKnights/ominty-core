# Omivoid LMDE — Phase 1 Action Catalogue

**Status:** Initial implementation catalogue
**Registry schema:** v1

---

# 1. Purpose

This document defines the initial set of actions that should be considered for implementation during Phase 1.

It is the bridge between the Action Registry specification and implementation.

The catalogue is intentionally small.

Its purpose is to prove:

* canonical action identity;
* registry loading;
* native Niri generation;
* adapter execution;
* application roles;
* action discovery;
* command palette integration;
* AI namespace;
* theme integration.

Not every conceptual Omivoid capability belongs in Phase 1.

---

# 2. Binding Status

Bindings in this document are **proposed defaults**.

They are not permission to overwrite the existing Niri configuration.

Because Niri is already installed and configured, the implementation agent must audit current bindings first.

Each proposed binding should therefore receive one of:

```text
ACCEPT
CONFLICT
MIGRATE
CHANGE
DEFER
```

before being applied.

---

# 3. Application Actions

## `app.terminal.open`

**Name:** Open Terminal
**Category:** Applications
**Proposed binding:** `Super+Enter`
**Risk:** `routine`
**Context:** `global`
**Implementation:** application role `terminal`

Purpose:

Open the configured primary terminal.

---

## `app.browser.open`

**Name:** Open Browser
**Category:** Applications
**Proposed binding:** `Super+Shift+B`
**Risk:** `routine`
**Context:** `global`
**Implementation:** application role `browser`

---

## `app.files.open`

**Name:** Open Files
**Category:** Applications
**Proposed binding:** `Super+Shift+F`
**Risk:** `routine`
**Context:** `global`
**Implementation:** application role `files`

---

## `app.editor.open`

**Name:** Open Editor
**Category:** Applications
**Proposed binding:** `Super+Shift+E`
**Risk:** `routine`
**Context:** `global`
**Implementation:** application role `editor`

---

## `app.notes.open`

**Name:** Open Notes
**Category:** Applications
**Proposed binding:** `Super+Shift+N`
**Risk:** `routine`
**Context:** `global`
**Implementation:** application role `notes`

---

## `app.mail.open`

**Name:** Open Mail
**Category:** Applications
**Proposed binding:** `Super+Shift+M`
**Risk:** `routine`
**Context:** `global`
**Implementation:** application role `mail`

---

# 4. Window Actions

These should use native Niri operations wherever appropriate.

## `window.close`

**Name:** Close Window
**Category:** Windows
**Proposed binding:** `Super+Q`
**Risk:** `routine`
**Context:** `window`
**Backend:** native Niri

---

## `window.fullscreen.toggle`

**Name:** Toggle Fullscreen
**Category:** Windows
**Proposed binding:** `Super+F`
**Risk:** `routine`
**Context:** `window`
**Backend:** native Niri

---

## `window.focus.left`

**Name:** Focus Left
**Category:** Navigation
**Proposed binding:** `Super+Left`
**Risk:** `routine`
**Context:** `window`
**Backend:** native Niri

---

## `window.focus.right`

**Name:** Focus Right
**Category:** Navigation
**Proposed binding:** `Super+Right`
**Risk:** `routine`
**Context:** `window`
**Backend:** native Niri

---

## `window.focus.up`

**Name:** Focus Up
**Category:** Navigation
**Proposed binding:** `Super+Up`
**Risk:** `routine`
**Context:** `window`
**Backend:** native Niri

---

## `window.focus.down`

**Name:** Focus Down
**Category:** Navigation
**Proposed binding:** `Super+Down`
**Risk:** `routine`
**Context:** `window`
**Backend:** native Niri

---

## `window.move.left`

**Name:** Move Window Left
**Category:** Windows
**Risk:** `routine`
**Context:** `window`
**Backend:** native Niri

Binding should be selected after inspecting existing Niri movement conventions.

---

## `window.move.right`

**Name:** Move Window Right
**Category:** Windows
**Risk:** `routine`
**Context:** `window`
**Backend:** native Niri

Binding should be selected after inspecting existing Niri movement conventions.

---

# 5. Workspace Actions

## `workspace.next`

**Name:** Next Workspace
**Category:** Workspaces
**Risk:** `routine`
**Context:** `global`
**Backend:** native Niri

---

## `workspace.previous`

**Name:** Previous Workspace
**Category:** Workspaces
**Risk:** `routine`
**Context:** `global`
**Backend:** native Niri

---

## `workspace.switch`

**Name:** Switch Workspace
**Category:** Workspaces
**Proposed bindings:** `Super+1` through `Super+9`
**Risk:** `routine`
**Context:** `global`
**Backend:** native Niri

Parameter:

```text
workspace: integer
```

The implementation should respect Niri's actual workspace semantics rather than assuming another compositor's model.

---

## `workspace.window.move`

**Name:** Move Window to Workspace
**Category:** Workspaces
**Proposed bindings:** `Super+Shift+1` through `Super+Shift+9`
**Risk:** `routine`
**Context:** `window`
**Backend:** native Niri

Parameter:

```text
workspace: integer
```

---

# 6. Session Actions

## `session.lock`

**Name:** Lock Session
**Category:** System
**Risk:** `state-change`
**Context:** `global`

Prefer integration with the selected shell/session mechanism.

---

## `session.logout`

**Name:** Log Out
**Category:** System
**Risk:** `destructive`
**Confirmation:** `ai-only` minimum
**Context:** `global`

---

## `session.reboot`

**Name:** Restart Computer
**Category:** System
**Risk:** `destructive`
**Confirmation:** `ai-only` minimum
**Context:** `global`

---

## `session.shutdown`

**Name:** Shut Down
**Category:** System
**Risk:** `destructive`
**Confirmation:** `ai-only` minimum
**Context:** `global`

---

# 7. Audio Actions

These should integrate with the existing PipeWire/WirePlumber environment or the shell's existing controls rather than creating a parallel audio stack.

## `audio.volume.increase`

**Name:** Increase Volume
**Category:** Audio
**Risk:** `state-change`
**Context:** `global`

Media-key integration should be considered.

---

## `audio.volume.decrease`

**Name:** Decrease Volume
**Category:** Audio
**Risk:** `state-change`
**Context:** `global`

---

## `audio.mute.toggle`

**Name:** Toggle Audio Mute
**Category:** Audio
**Risk:** `state-change`
**Context:** `global`

---

## `audio.microphone.toggle`

**Name:** Toggle Microphone
**Category:** Audio
**Risk:** `state-change`
**Context:** `global`

---

# 8. Display Actions

## `display.brightness.increase`

**Name:** Increase Brightness
**Category:** Displays
**Risk:** `state-change`
**Context:** `global`

Brightness control integrates with the shell's existing controls (DMS `brightness` IPC) rather than creating a parallel brightness stack.

---

## `display.brightness.decrease`

**Name:** Decrease Brightness
**Category:** Displays
**Risk:** `state-change`
**Context:** `global`

---

# 9. Media Actions

## `media.play_pause`

**Name:** Play/Pause Media
**Category:** Media
**Risk:** `routine`
**Context:** `global`

Media control integrates with the shell's existing controls (DMS `mpris` IPC) rather than a parallel playerctl stack.

---

## `media.next`

**Name:** Next Track
**Category:** Media
**Risk:** `routine`
**Context:** `global`

---

## `media.previous`

**Name:** Previous Track
**Category:** Media
**Risk:** `routine`
**Context:** `global`

---

# 10. Network Actions

## `network.wifi.open`

**Name:** Open Wi-Fi Controls
**Category:** Network
**Proposed binding:** `Super+Ctrl+W`
**Risk:** `routine`
**Context:** `global`

If DMS provides an appropriate Wi-Fi panel, use it.

Do not create a second Wi-Fi UI merely to satisfy the action.

---

## `network.bluetooth.open`

**Name:** Open Bluetooth Controls
**Category:** Network
**Proposed binding:** `Super+Ctrl+B`
**Risk:** `routine`
**Context:** `global`

Prefer DMS or the existing configured Bluetooth interface.

---

# 11. Theme Actions

## `theme.wallpaper.select`

**Name:** Select Wallpaper
**Category:** Appearance
**Proposed binding:** `Super+Ctrl+Space`
**Risk:** `state-change`
**Context:** `global`

**Implementation (2026-09-19):** bound to **`Super+Ctrl+P`** — opens/toggles
the DMS Wallpaper Carousel (`dms ipc call wallpaperCarousel toggle`).
`Super+Ctrl+C` was rejected (DMS owns it), and the proposal was revised to
`Super+Ctrl+P`. See `docs/implementation/theme-implementation.md`.

This action should eventually initiate the complete wallpaper/theme workflow.

Expected conceptual flow:

```text
Select Wallpaper
       ↓
Apply Wallpaper
       ↓
Generate Palette
       ↓
Apply Omivoid Theme
```

DMS/Matugen should be evaluated as the primary implementation.

---

## `theme.wallpaper.next`

**Name:** Next Wallpaper
**Category:** Appearance
**Risk:** `state-change`
**Context:** `global`

Implementation depends on the selected wallpaper provider.

This action may be deferred if the provider does not expose a clean mechanism.

---

## `theme.palette.regenerate`

**Name:** Regenerate Colour Palette
**Category:** Appearance
**Risk:** `state-change`
**Context:** `global`

Regenerate the theme palette from the current wallpaper.

---

## `theme.mode.toggle`

**Name:** Toggle Light/Dark Mode
**Category:** Appearance
**Risk:** `state-change`
**Context:** `global`

Implementation should align with DMS/theme-provider capabilities.

---

# 12. Capture Actions

## `capture.screenshot.full`

**Name:** Capture Screenshot
**Category:** Capture
**Proposed binding:** `Print`
**Risk:** `routine`
**Context:** `global`

The capture backend should be selected according to the existing Wayland environment.

---

## `capture.screenshot.region`

**Name:** Capture Region
**Category:** Capture
**Proposed binding:** `Shift+Print`
**Risk:** `routine`
**Context:** `global`

---

# 13. AI Actions

The AI namespace is structurally important even where some capabilities initially launch tools rather than provide deep desktop integration.

## `ai.open`

**Name:** Open AI Palette
**Category:** AI
**Proposed binding:** `Super+A`
**Risk:** `routine`
**Context:** `global`
**AI accessible:** `false`

This opens the AI namespace/interaction surface.

---

## `ai.ask`

**Name:** Ask AI
**Category:** AI
**Proposed chord:** `Super+A,A`
**Risk:** `routine`
**Context:** `global`
**AI accessible:** `false`

---

## `ai.pi.open`

**Name:** Open Pi
**Category:** AI
**Proposed chord:** `Super+A,P`
**Risk:** `routine`
**Context:** `global`
**AI accessible:** `false`

Phase 1 may initially launch Pi in the configured environment.

---

## `ai.herdr.open`

**Name:** Open Herdr
**Category:** AI
**Proposed chord:** `Super+A,H`
**Risk:** `routine`
**Context:** `global`
**AI accessible:** `false`

If Herdr is not yet installed/configured, the action should be marked unavailable rather than removed from the conceptual namespace.

---

## `ai.selection.explain`

**Name:** Explain Selection
**Category:** AI
**Proposed chord:** `Super+A,E`
**Risk:** `read`
**Context:** `text-selection`
**AI accessible:** `false`

This may be deferred until reliable selection acquisition is established.

---

## `ai.selection.summarise`

**Name:** Summarise Selection
**Category:** AI
**Proposed chord:** `Super+A,S`
**Risk:** `read`
**Context:** `text-selection`
**AI accessible:** `false`

---

# 14. Help Actions

## `help.keys.open`

**Name:** Open Interaction Explorer
**Category:** Help
**Proposed binding:** `Super+K`
**Risk:** `routine`
**Context:** `global`

This is a core Phase 1 action.

Its content should be generated from registry metadata.

---

## `help.actions.search`

**Name:** Search Actions
**Category:** Help
**Proposed binding:** `Super+Space`
**Risk:** `routine`
**Context:** `global`

This is the basis of the universal action palette.

---

# 15. Project Namespace Reservation

Project workflow is important to the wider Omivoid architecture, but a complete project system is not required to prove Phase 1.

Reserve:

```text
Super+P
```

and canonical namespace:

```text
project.*
```

Potential later actions include:

```text
project.open
project.create
project.recent
project.terminal.open
project.editor.open
project.ai.open
project.delegate
```

Only implement these in Phase 1 if doing so supports an actual tested workflow.

---

# 16. Initial Catalogue Summary

The initial catalogue therefore covers approximately:

```text
Applications       6
Windows            8
Workspaces         4
Session            4
Audio              4
Display            2
Media              3
Network            2
Appearance         4
Capture            2
AI                 6
Help               2
                  ──
Total             47
```

The exact count is not a target.

Actions may be deferred where implementation would be speculative.

The goal is approximately 30–40 working actions by the end of Phase 1.

**Phase 1 implementation (2026-09-19):** **40 actions** implemented and
validating (0 errors, 0 warnings). By category: Applications 6, Windows 4,
Navigation 4, Workspaces 2, System 1, Audio 4, Displays 2, Media 3,
Appearance 5, Capture 2, AI 5, Help 2.

Deferred (documented, not implemented): `session.*` (logout/reboot/
shutdown — destructive, needs a confirmation design), `network.*`
(DMS control-center integration), and the remaining window/workspace
navigation and `window.move` binding conventions.

---

# 17. Implementation Priority

## Priority A — Architecture proof

Implement first:

```text
app.terminal.open
app.browser.open

window.close
window.focus.left
window.focus.right

workspace.next
workspace.previous

help.keys.open
help.actions.search
```

These prove:

* registry;
* application role;
* native Niri mapping;
* discovery;
* action search.

## Priority B — Desktop experience

Then implement:

```text
remaining app roles
remaining Niri navigation
audio.*
display.*
media.*
network.*.open
capture.*
session.*
```

## Priority C — Omivoid differentiators

Then implement:

```text
theme.*
ai.*
```

These establish the visual and AI-native characteristics of Omivoid.

---

# 18. Catalogue Acceptance Rule

An action is not considered complete merely because a shortcut works.

A completed Phase 1 action should have, where applicable:

* canonical action ID;
* registry entry;
* description;
* category;
* keywords;
* risk;
* context;
* adapter/native backend;
* validated binding;
* discoverability through `Super+K`;
* command-palette visibility where appropriate;
* CLI invocation where required;
* understandable failure behaviour.

---

# 19. Do Not Fake Availability

If an action is defined but its implementation is unavailable, report it as unavailable.

For example:

```text
ai.herdr.open
Status: unavailable
Reason: Herdr provider is not configured
```

Do not create placeholder scripts that report success without performing the operation.

---

# 20. Phase 1 Completion

The catalogue is complete enough when it demonstrates that:

```text
one action definition
       │
       ├── drives keyboard behaviour
       ├── appears in help
       ├── appears in search
       ├── can resolve an implementation
       └── can be safely exposed to other interfaces
```

At that point the Action Registry has proven its architectural value and can be expanded incrementally.
