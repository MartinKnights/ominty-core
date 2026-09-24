# Omivoid Action Registry Specification

**Project:** `omivoid-lmde`
**Specification version:** 0.1
**Registry schema version:** 1
**Phase:** Phase 1

---

# 1. Status

The Omivoid Action Registry is the canonical definition of meaningful actions exposed by the Omivoid desktop.

The fundamental architectural contract is:

> **The Action Registry defines what an action means. Adapters define how that action is performed.**

Action identifiers form a stable internal API between:

* keyboard interaction;
* Niri;
* graphical shell components;
* command palette;
* CLI;
* AI;
* future voice interaction;
* automation.

---

# 2. Phase 1 Scope

Phase 1 implements only the minimum registry functionality required to prove the architecture.

Required:

```text
TOML action definitions
        ↓
registry loading
        ↓
validation
        ↓
action resolution
        ↓
action execution
        ↓
Niri binding generation
        ↓
Super+K metadata
        ↓
command palette metadata
```

Explicitly deferred:

* persistent registry daemon;
* event bus;
* remote action routing;
* complex permissions engine;
* action marketplace;
* plugin sandbox;
* DBus API;
* machine-learning ranking;
* graphical registry editor.

---

# 3. Action Identity

Canonical action identifiers use:

```text
namespace.subject.action
```

Examples:

```text
app.browser.open
app.terminal.open

window.focus.left
window.move.right
window.close

workspace.next
workspace.switch

audio.volume.increase
audio.mute.toggle

network.wifi.toggle

theme.wallpaper.select
theme.palette.regenerate

ai.ask
ai.selection.explain

project.open
project.delegate

help.keys.open
```

Canonical identifiers should be treated as API identifiers.

Once published, they should not be renamed casually.

---

# 4. Initial Namespaces

Phase 1 recognises the following namespaces:

```text
app
window
workspace
display
input
audio
media
network
power
session
clipboard
capture
theme
notification
file
project
ai
developer
help
system
```

Namespace growth should be conservative.

Prefer:

```text
network.bluetooth.open
```

over unnecessarily deep names such as:

```text
wireless.bluetooth.device.manager.open
```

---

# 5. Registry Layout

Core actions should be stored under:

```text
actions/
├── applications.toml
├── windows.toml
├── workspaces.toml
├── display.toml
├── input.toml
├── audio.toml
├── network.toml
├── power.toml
├── session.toml
├── clipboard.toml
├── capture.toml
├── themes.toml
├── notifications.toml
├── files.toml
├── projects.toml
├── ai.toml
├── developer.toml
└── help.toml
```

Not every file must contain Phase 1 actions.

Empty categories do not need placeholder actions.

---

# 6. Schema Version

Every registry file should declare:

```toml
registry_version = 1
```

The loader must reject unsupported future schema versions rather than silently misinterpreting them.

---

# 7. Phase 1 Action Schema

The canonical Phase 1 schema is:

```toml
[action."action.id"]

name = ""
description = ""
category = ""

keywords = []

keys = []

adapter = ""

cli = []

risk = "routine"
confirmation = "never"

contexts = ["global"]

platforms = ["common"]
requires = []

discoverable = true
palette = true
ai_accessible = false
voice_accessible = false
```

Optional fields may include:

```toml
short_name = ""
subcategory = ""
primary_key = ""
scope = ""
priority = 50
icon = ""
```

Do not implement optional fields merely because they exist unless Phase 1 requires them.

---

# 8. Required Fields

Every Phase 1 action MUST contain:

```text
action ID
name
description
category
risk
```

Actions intended for execution MUST additionally resolve to an implementation through an adapter or supported native backend.

---

# 9. Human-Facing Metadata

## Name

Use:

```text
Verb + Object
```

Examples:

```text
Open Browser
Close Window
Increase Volume
Select Wallpaper
Explain Selection
```

## Description

Describe intent, not implementation.

Correct:

```toml
description = "Open the default web browser."
```

Incorrect:

```toml
description = "Executes Firefox."
```

Implementation details belong to adapters/configuration.

---

# 10. Keywords

Keywords support human discovery.

Example:

```toml
keywords = [
    "wifi",
    "wireless",
    "internet",
    "network"
]
```

The command palette and `Super+K` search should use these.

---

# 11. Keybindings

Bindings are metadata attached to actions.

Example:

```toml
keys = ["Super+Shift+B"]
```

Multiple bindings are allowed:

```toml
keys = [
    "Super+Enter",
    "Super+Shift+T"
]
```

If necessary:

```toml
primary_key = "Super+Enter"
```

identifies the binding presented most prominently to the user.

---

# 12. Chords

Chord notation uses a comma:

```toml
keys = ["Super+A,E"]
```

meaning:

```text
Super+A
then E
```

This MUST remain distinct from:

```text
Super+A+E
```

which represents a simultaneous key combination.

---

# 13. Groups

Prefix namespaces are declared separately.

Example:

```toml
[group.ai]
name = "AI"
prefix = "Super+A"
description = "AI and agent operations"

[group.help]
name = "Help"
prefix = "Super+K"
description = "Help and interaction discovery"

[group.project]
name = "Projects"
prefix = "Super+P"
description = "Project operations"
```

The shell may use these definitions to construct visible prefix overlays.

---

# 14. Categories

Initial presentation categories include:

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
Help
```

Categories are user-facing.

Do not use implementation components such as `Niri` or `DMS` as presentation categories.

---

# 15. Contexts

Actions may declare valid contexts.

Initial recognised values include:

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

Example:

```toml
contexts = ["text-selection"]
```

An action requiring unavailable context should not be offered as immediately executable.

---

# 16. Risk Classification

Phase 1 uses:

| Risk           | Meaning                                         |
| -------------- | ----------------------------------------------- |
| `read`         | No meaningful state change                      |
| `routine`      | Normal low-risk operation                       |
| `state-change` | Changes configuration or system state           |
| `privileged`   | Requires elevated authority                     |
| `destructive`  | Could lose data/work or terminate state         |
| `critical`     | Security-sensitive or major system modification |

Risk describes the operation.

It does not independently determine whether confirmation is required.

---

# 17. Confirmation Policy

Allowed values:

```text
never
interactive
ai-only
always
```

Example:

```toml
risk = "destructive"
confirmation = "ai-only"
```

allows different treatment of trusted direct interaction and AI invocation.

---

# 18. AI Accessibility

Actions explicitly declare AI exposure:

```toml
ai_accessible = true
```

or:

```toml
ai_accessible = false
```

AI MUST NOT infer permission merely because an action exists.

Actions that invoke AI itself should normally not be exposed back to AI unless there is a clear reason.

This avoids recursive agent behaviour.

---

# 19. Voice Accessibility

Voice exposure uses:

```toml
voice_accessible = true
```

Voice implementation is not required in the initial Phase 1 milestone.

The metadata exists to avoid redesigning the registry later.

---

# 20. CLI Mapping

Public actions should support a CLI mapping where practical.

Example:

```toml
cli = ["network", "wifi", "toggle"]
```

maps to:

```text
omivoid network wifi toggle
```

The generic form is:

```text
omivoid action run network.wifi.toggle
```

The canonical action ID remains authoritative.

---

# 21. Adapter Rule

Core actions should not normally contain raw implementation commands.

Avoid:

```toml
command = ["nmcli", "radio", "wifi", "off"]
```

Prefer:

```toml
adapter = "network.wifi.toggle"
```

Adapters own implementation.

---

# 22. Adapter Resolution

Initial resolution precedence:

```text
machine-specific adapter
        ↓
platform adapter
        ↓
common adapter
```

The first valid implementation wins.

Platform-specific adapters should be introduced only where common implementation is unsuitable.

---

# 23. Niri Native Actions

Niri operations are a special case.

Latency-sensitive compositor actions may compile directly to native Niri bindings.

Example canonical action:

```text
window.close
```

may generate:

```kdl
Mod+Q {
    close-window
}
```

rather than:

```text
Niri
→ spawn Omivoid
→ invoke Niri IPC
```

The registry remains authoritative for:

* action identity;
* binding;
* description;
* discovery;
* metadata.

Niri remains authoritative for execution.

---

# 24. Requirements

Actions may declare dependencies:

```toml
requires = [
    "dms",
    "matugen"
]
```

Phase 1 may use direct component names.

Future versions may migrate toward abstract capabilities.

Missing requirements must produce an explicit unavailable state rather than silent failure.

---

# 25. Platforms

Most actions should use:

```toml
platforms = ["common"]
```

Platform-specific actions may use:

```toml
platforms = ["debian"]
```

or:

```toml
platforms = ["void"]
```

A high number of platform-specific actions should be treated as an architectural warning.

---

# 26. Application Roles

Application actions resolve roles rather than hard-coded executables.

Example:

```toml
[action."app.browser.open"]

adapter = "app.launch"
arguments = { role = "browser" }
```

Application configuration:

```toml
[apps]
browser = "firefox"
terminal = "alacritty"
files = "nemo"
editor = "nvim"
notes = "obsidian"
mail = "thunderbird"
```

The actual Phase 1 values must be established by inspecting the existing LMDE machine and user configuration.

Do not assume these example applications are installed.

---

# 27. User Actions

User-defined actions live under:

```text
~/.config/omivoid/actions/
```

They should use:

```text
custom.*
```

Example:

```text
custom.obsidian.daily-note
```

Raw commands MAY be permitted for user-defined actions:

```toml
adapter = "command"
command = [...]
```

Core Omivoid actions should prefer adapters.

---

# 28. Overrides

Users should be able to override metadata without copying complete core definitions.

Example:

```toml
[override."app.browser.open"]
keys = ["Super+B"]
```

Override precedence:

```text
core
  ↓
platform
  ↓
machine
  ↓
user
  ↓
local/session
```

Later definitions override earlier definitions.

Canonical action identity remains unchanged.

---

# 29. Validation

Phase 1 MUST provide:

```text
omivoid registry validate
```

Validation should detect at least:

* malformed TOML;
* unsupported schema version;
* invalid action IDs;
* missing required fields;
* duplicate action IDs;
* duplicate/conflicting bindings;
* unknown adapters;
* unavailable required dependencies where detectable;
* unsupported risk values;
* unsupported confirmation values.

Validation should distinguish errors from warnings.

---

# 30. Registry Inspection

The CLI should eventually support:

```text
omivoid action list
omivoid action show <id>
omivoid action search <query>
omivoid action run <id>

omivoid registry validate
omivoid registry build
```

The first Phase 1 milestone may implement these incrementally.

---

# 31. Action Results

Executable actions should move toward a predictable result model.

Successful result:

```json
{
  "action": "network.wifi.toggle",
  "success": true,
  "state": {
    "enabled": true
  }
}
```

Failure:

```json
{
  "action": "network.wifi.toggle",
  "success": false,
  "error": {
    "code": "DEPENDENCY_MISSING",
    "message": "Required network provider is unavailable."
  }
}
```

Human-readable CLI output may differ.

Machine-readable output should remain structured.

---

# 32. Error Vocabulary

Reserve the following error codes:

```text
ACTION_NOT_FOUND
ACTION_UNAVAILABLE
DEPENDENCY_MISSING
INVALID_ARGUMENT
PERMISSION_DENIED
CONFIRMATION_REQUIRED
ADAPTER_FAILED
CONTEXT_UNAVAILABLE
PLATFORM_UNSUPPORTED
```

The implementation may introduce additional documented codes when necessary.

---

# 33. Generated Registry

The human-maintained source is TOML.

A future or Phase 1 registry build may produce a runtime representation such as:

```text
~/.cache/omivoid/registry.json
```

The generated representation is disposable.

It MUST NOT become the authoritative configuration.

---

# 34. Existing Niri Configuration

Because Niri is already installed and configured, registry-generated bindings must not blindly overwrite the existing Niri configuration.

The implementation must:

1. inspect active configuration;
2. identify conflicts;
3. preserve unrelated bindings;
4. clearly separate generated Omivoid configuration where possible;
5. report unresolved conflicts.

---

# 35. Existing Quickshell Configuration

Quickshell is also already installed.

The registry implementation must not assume a clean or disposable Quickshell environment.

DMS integration and any custom Omivoid Quickshell components should be isolated where practical.

---

# 36. Phase 1 Registry Size

The initial registry should contain approximately 30–40 useful actions.

The goal is sufficient breadth to test:

* applications;
* Niri;
* workspaces;
* system actions;
* audio;
* networking;
* theming;
* capture;
* AI;
* help.

Do not inflate the registry with speculative actions merely to reach a number.

---

# 37. Architectural Contract

All implementations must preserve these three rules:

> **1. No Omivoid interaction surface should need to know how an action is implemented.**

> **2. The Action Registry is authoritative for intent and interaction metadata; adapters are authoritative for implementation.**

> **3. AI should receive controlled Omivoid capabilities instead of being forced to manipulate implementation-specific shell commands wherever practical.**

These contracts are more important than the exact Phase 1 implementation language or tooling.
