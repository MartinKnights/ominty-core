# Omivoid LMDE — Interaction Specification

## 1. Purpose

This document defines how users interact with Omivoid.

It defines interaction semantics rather than implementation details.

The same conceptual interaction model should remain applicable when Omivoid later moves from LMDE to Void.

---

# 2. Core Interaction Model

Every important Omivoid capability should, where practical, be available through:

```text
Keyboard
GUI
CLI
AI
Voice
```

These are interaction surfaces over the same underlying action model.

```text
Keyboard ─────┐
GUI ──────────┤
CLI ──────────┼──► Omivoid Action
AI ───────────┤
Voice ────────┘
```

No interaction surface should unnecessarily implement separate semantics.

---

# 3. Keyboard-First Requirement

Frequently used operations MUST have an efficient keyboard path.

Keyboard-first means:

* no pointer is required for routine operation;
* common actions use short bindings;
* less common actions remain accessible through searchable interfaces;
* users are not expected to memorise every binding.

Mouse, touchpad and graphical controls remain fully valid interaction methods.

---

# 4. The Omivoid Modifier

`Super` is the primary Omivoid desktop modifier.

The keyboard grammar should be built around predictable combinations of `Super`.

Initial conceptual grammar:

| Pattern               | Responsibility                          |
| --------------------- | --------------------------------------- |
| `Super + key`         | Navigation and frequent desktop actions |
| `Super + Shift + key` | Applications                            |
| `Super + Ctrl + key`  | System controls                         |
| `Super + Alt + key`   | Advanced window/display operations      |
| `Super + A`           | AI namespace                            |
| `Super + K`           | Help and discovery                      |
| `Super + P`           | Projects                                |
| `Super + Space`       | Universal command/action palette        |

These rules are conventions rather than immutable restrictions.

---

# 5. Immediate Actions

Highly frequent operations should use direct bindings rather than chords.

Initial baseline:

| Binding            | Action                   |
| ------------------ | ------------------------ |
| `Super+Enter`      | Open terminal            |
| `Super+Space`      | Universal palette        |
| `Super+K`          | Interaction explorer     |
| `Super+Shift+S`    | Keybindings cheat sheet  |
| `Super+A`          | AI palette               |
| `Super+P`          | Project palette          |
| `Super+Q`          | Close focused window     |
| `Super+F`          | Toggle fullscreen        |
| `Super+Arrow`      | Navigate Niri layout     |
| `Super+1..9`       | Switch workspace         |
| `Super+Shift+1..9` | Move window to workspace |

Exact bindings remain subject to validation against existing Niri configuration.

The implementation agent MUST inspect existing bindings before applying these defaults.

---

# 6. Application Bindings

Applications should be launched by role.

Initial convention:

| Binding         | Role     |
| --------------- | -------- |
| `Super+Shift+B` | Browser  |
| `Super+Shift+F` | Files    |
| `Super+Shift+E` | Editor   |
| `Super+Shift+N` | Notes    |
| `Super+Shift+M` | Mail     |
| `Super+Shift+T` | Terminal |

The action is not tied to an executable.

For example:

```text
Super+Shift+B
       ↓
app.browser.open
       ↓
configured browser role
```

---

# 7. Niri Navigation

Niri's native scrolling model is part of Omivoid's interaction design.

The implementation should favour native Niri semantics rather than attempting to reproduce Hyprland behaviour.

Canonical actions should include concepts such as:

```text
window.focus.left
window.focus.right
window.focus.up
window.focus.down

window.move.left
window.move.right

workspace.next
workspace.previous
workspace.switch
workspace.window.move
```

Where Niri provides an appropriate native binding, the generated configuration should use it directly.

---

# 8. Universal Palette

`Super+Space` opens the Omivoid universal command/action palette.

It is not merely an application launcher.

It should ultimately be capable of discovering:

* applications;
* Omivoid actions;
* system functions;
* settings;
* projects;
* AI actions;
* recent actions where useful.

Example searches:

```text
browser
bluetooth
wallpaper
volume
research
terminal
project
screenshot
lock
```

Search results should derive from the Action Registry wherever applicable.

---

# 9. Palette Behaviour

The universal palette should follow standard Omivoid navigation semantics:

```text
typing      Search
↑ / ↓       Navigate
Enter       Execute
Esc         Close
```

Search should use:

* action name;
* short name;
* description where useful;
* keywords.

Results should prefer commonly useful actions over obscure internal operations.

---

# 10. `Super+K` Interaction Explorer

`Super+K` opens the Omivoid Interaction Explorer.

This is the primary discoverability interface.

It should expose categories such as:

```text
Navigation
Applications
Windows
Workspaces
System
Audio
Network
Displays
Appearance
Clipboard
Capture
Notifications
Files
Projects
AI
Developer
```

Each entry should be capable of displaying:

* action name;
* primary keybinding;
* description;
* category.

---

# 11. Searchable Help

The Interaction Explorer should be searchable.

Example:

```text
Search: bluetooth
```

may return:

```text
Open Bluetooth Controls
Super+Ctrl+B
network.bluetooth.open
```

Searching:

```text
move window
```

should locate the relevant Niri window actions even if the user does not know the exact action name.

---

# 12. Self-Documenting Bindings

The Interaction Explorer MUST derive its binding information from the same source that defines Omivoid actions.

Do not maintain a separate manually authored keybinding cheat sheet as the authoritative source.

The intended flow is:

```text
Action Registry
      │
      ├──► Niri bindings
      │
      ├──► Super+K
      │
      └──► Command palette
```

Documentation may explain bindings, but it should not become a conflicting source of truth.

---

# 13. Chorded Interaction

Less frequent actions may use prefix chords.

A chord is represented as:

```text
Super+A,E
```

meaning:

```text
press Super+A
then E
```

This is distinct from:

```text
Super+A+E
```

which represents simultaneous modifiers/keys.

---

# 14. Visible Prefix Modes

When a prefix is entered, Omivoid should display available continuation keys where practical.

Example:

```text
Super+A
```

may display:

```text
AI
──────────────────
A  Ask
C  Code
E  Explain
H  Herdr
P  Pi
R  Research
S  Summarise
W  Writing
Esc Cancel
```

This behaviour makes chorded interaction discoverable while the user is learning it.

---

# 15. AI Namespace

`Super+A` is reserved for AI.

Initial conceptual actions include:

| Chord       | Action                  |
| ----------- | ----------------------- |
| `Super+A,A` | Ask AI                  |
| `Super+A,P` | Open Pi                 |
| `Super+A,H` | Open Herdr              |
| `Super+A,E` | Explain selected text   |
| `Super+A,S` | Summarise selected text |
| `Super+A,R` | Research                |
| `Super+A,W` | Writing assistance      |
| `Super+A,C` | Coding assistance       |

Not every conceptual action must be fully implemented in the first milestone.

The namespace should nevertheless be reserved consistently.

---

# 16. Project Namespace

`Super+P` is reserved for project-oriented workflow.

Potential actions include:

```text
Super+P,O    Open project
Super+P,N    New project
Super+P,R    Recent projects
Super+P,T    Project terminal
Super+P,E    Project editor
Super+P,A    Project AI
Super+P,S    Delegate/send task
```

The Phase 1 implementation may initially provide only the prefix structure and a small subset of these actions.

Remote delegation is not required for the initial Phase 1 milestone.

---

# 17. System Controls

Initial system interaction conventions may include:

| Binding            | Intent             |
| ------------------ | ------------------ |
| `Super+Ctrl+B`     | Bluetooth controls |
| `Super+Ctrl+W`     | Wi-Fi controls     |
| `Super+Ctrl+A`     | Audio controls     |
| `Super+Ctrl+Space` | Wallpaper selector |

The final implementation should account for functionality already exposed effectively by DMS.

Omivoid should not create redundant graphical controls solely to satisfy this specification.

---

# 18. Screenshot Interaction

Initial expected bindings:

```text
Print
    Full screenshot

Shift+Print
    Region screenshot
```

The exact capture backend is an implementation detail.

The canonical actions should remain stable.

---

# 19. Escape Semantics

For Omivoid-controlled transient interfaces:

> `Esc` means cancel, close or leave the current transient interaction.

This applies to:

* command palette;
* interaction explorer;
* chord overlays;
* AI palette;
* project palette;
* selectors.

A component that cannot follow this convention should be documented.

---

# 20. Common Navigation Semantics

Omivoid interfaces should use:

| Key         | Meaning               |
| ----------- | --------------------- |
| `Enter`     | Select / execute      |
| `Esc`       | Cancel / close        |
| `↑ ↓ ← →`   | Navigate              |
| `Tab`       | Next major region     |
| `Shift+Tab` | Previous major region |

Additional bindings are allowed.

Contradictory behaviour should be avoided.

---

# 21. Context-Aware Interaction

Actions may be offered only when their required context exists.

Potential contexts include:

```text
global
window
workspace
selection
text-selection
file
directory
browser
terminal
editor
project
```

For selected text, Omivoid may expose:

```text
Explain Selection
Summarise Selection
Rewrite Selection
Research Selection
```

When there is no text selection, those actions should not be presented as immediately executable.

---

# 22. Interaction Through CLI

Public actions should ideally have a corresponding CLI interface.

Examples:

```text
omivoid app browser
omivoid window close
omivoid theme wallpaper select
omivoid ai ask
```

A universal low-level form should also be possible:

```text
omivoid action run app.browser.open
```

The CLI and keyboard interaction should resolve the same canonical action.

---

# 23. Interaction Through AI

AI should interact with Omivoid through registered capabilities where practical.

Example:

```text
User:
"Change the wallpaper."

AI resolves:
theme.wallpaper.select
```

rather than the AI independently deciding how to modify wallpaper configuration.

This allows Omivoid to apply:

* context checks;
* permissions;
* risk classification;
* confirmation;
* platform abstraction.

---

# 24. Voice

Voice is considered a future interaction surface over the same action system.

Example:

```text
"Turn Bluetooth off."
        ↓
network.bluetooth.disable
```

Phase 1 should preserve this possibility but does not require full voice implementation.

---

# 25. Action Feedback

Where an action changes state and the result is not visually obvious, the user should receive concise feedback.

Examples:

```text
Wi-Fi disabled

Microphone muted

Theme applied
```

Feedback may be provided through DMS notifications/OSDs where appropriate.

Do not create redundant notification mechanisms if the shell already provides them.

---

# 26. Error Feedback

Failed interactions should produce understandable feedback.

Prefer:

```text
Bluetooth controls unavailable:
required service is not running.
```

over raw command output.

Technical detail should remain available for diagnostics.

---

# 27. Interaction Latency

Common keyboard operations must feel immediate.

Native compositor actions should not be routed through unnecessary processes.

Examples:

```text
window.focus.left
window.close
workspace.next
```

should normally compile to native Niri operations.

Actions requiring broader orchestration may go through the Omivoid action runner.

---

# 28. Interaction Precedence

Where multiple interaction methods exist, none should secretly implement different semantics.

For example:

```text
Keyboard
Super+Ctrl+Space

Palette
Select Wallpaper

CLI
omivoid theme wallpaper select

AI
"Choose a wallpaper"
```

should all resolve toward:

```text
theme.wallpaper.select
```

---

# 29. Existing Binding Conflicts

Because Niri is already installed and configured, the implementation agent MUST audit existing keybindings before generating Omivoid bindings.

For every conflict it should determine whether to:

* preserve existing binding;
* migrate it to the Omivoid equivalent;
* propose an alternative;
* request an architectural decision.

Existing bindings must not be silently overwritten.

---

# 30. Phase 1 Interaction Acceptance Criteria

The initial interaction implementation is successful when:

* keyboard navigation works naturally with Niri;
* application role bindings function;
* `Super+K` exposes registry-derived help;
* `Super+Space` exposes registry-derived actions;
* the AI namespace can be invoked;
* core system actions can be reached from the keyboard;
* wallpaper/theme interaction is available;
* no significant existing Niri functionality has been unintentionally lost;
* common interactions remain responsive.

The objective is not maximum feature count.

The objective is a small, coherent interaction language that can grow without becoming inconsistent.
