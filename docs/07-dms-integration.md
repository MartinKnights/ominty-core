# Omivoid LMDE — DankMaterialShell Integration Specification

**Project:** `omivoid-lmde`
**Phase:** Phase 1
**Shell framework:** Quickshell
**Shell candidate:** DankMaterialShell (DMS)

---

# 1. Purpose

This document defines how Omivoid should evaluate and integrate DankMaterialShell.

DMS is considered a strong candidate for providing much of the graphical desktop shell required by Omivoid.

The purpose of the integration is to reuse mature shell functionality while preserving Omivoid's independent interaction architecture.

---

# 2. Current Baseline

Quickshell is already installed on the Phase 1 machine.

DMS should therefore be evaluated as a shell implementation that builds on the existing Quickshell environment.

The implementation agent MUST NOT assume DMS is already configured correctly.

It should inspect:

* whether DMS is installed;
* installed version;
* configuration state;
* existing Quickshell configuration;
* existing shell startup behaviour.

---

# 3. Architectural Position

The intended relationship is:

```text
Omivoid Interaction Architecture
          │
          ├── Action Registry
          ├── Keyboard Grammar
          ├── AI Integration
          └── Theme Semantics
                  │
                  ▼
                DMS
                  │
                  ▼
             Quickshell
```

DMS is a provider of shell functionality.

It is not the definition of Omivoid.

---

# 4. DMS Responsibilities

Where appropriate, DMS should provide:

* bar;
* workspace display;
* active-window information;
* system tray;
* clock;
* battery status;
* media controls;
* audio UI;
* network UI;
* Bluetooth UI;
* notifications;
* notification history;
* OSD;
* quick settings;
* power menu;
* wallpaper selection;
* shell-level theme presentation.

Exact features should be confirmed against the installed version during implementation.

---

# 5. Integration Before Duplication

If DMS provides a capability adequately, Omivoid should not rebuild it.

For example:

```text
Bluetooth panel
```

should preferably map:

```text
network.bluetooth.open
       ↓
DMS Bluetooth interface
```

rather than creating a separate Omivoid Bluetooth UI.

The same applies to audio, Wi-Fi and wallpaper controls where appropriate.

---

# 6. Omivoid Responsibilities

Omivoid remains responsible for:

* action IDs;
* action metadata;
* keybinding grammar;
* application roles;
* `Super+K`;
* command/action semantics;
* AI namespace;
* project namespace;
* platform abstraction;
* cross-component theme policy;
* future remote task integration.

DMS may render these capabilities, but it does not define their meaning.

---

# 7. DMS Adapter

DMS-specific actions should be implemented through a DMS adapter.

Suggested location:

```text
adapters/dms/
```

Example conceptual mappings:

```text
network.bluetooth.open
    → DMS Bluetooth panel

network.wifi.open
    → DMS network panel

theme.wallpaper.select
    → DMS wallpaper chooser

audio.controls.open
    → DMS audio panel
```

The precise IPC or invocation mechanism should be discovered and documented during implementation.

---

# 8. Prefer Public Interfaces

Integration should prefer stable public DMS interfaces such as:

* documented IPC;
* documented CLI;
* supported configuration;
* supported settings APIs.

Avoid depending unnecessarily on:

* private QML object names;
* undocumented internal file structures;
* implementation details likely to change.

---

# 9. Do Not Fork DMS Prematurely

Phase 1 should not fork DMS unless a specific requirement cannot be achieved through:

* configuration;
* supported extension mechanisms;
* IPC;
* small external integration.

A fork would significantly increase maintenance burden.

---

# 10. Custom Quickshell Components

Custom Omivoid Quickshell components are acceptable where DMS does not provide the required interaction.

Likely candidates include:

* `Super+K` Interaction Explorer;
* chord continuation overlay;
* Omivoid-specific AI palette;
* project palette.

Before implementing each component, confirm that DMS does not already provide an adequate extension point or equivalent UI.

---

# 11. `Super+K`

The Omivoid Interaction Explorer is a core Omivoid feature.

Preferred order of implementation:

1. determine whether DMS provides a suitable searchable custom command interface;
2. determine whether DMS plugin/extension mechanisms can host the UI;
3. implement a separate Quickshell component only if necessary.

Regardless of UI implementation, its data should come from the Omivoid Action Registry.

---

# 12. `Super+Space`

DMS may already provide launcher functionality.

If that launcher can expose arbitrary Omivoid actions cleanly, extend or integrate with it.

If it is application-only and cannot satisfy the Omivoid command/action model, then Omivoid may require a dedicated palette.

Do not create two visually competing launchers without a clear reason.

---

# 13. Prefix Overlays

Chord namespaces such as:

```text
Super+A
Super+P
```

should ideally display an overlay showing continuation keys.

DMS should be evaluated as the host for this UI.

If unsuitable, a small standalone Quickshell overlay is acceptable.

The overlay should remain data-driven from the Action Registry.

---

# 14. Notifications

If DMS provides the notification daemon and history:

* use it;
* avoid starting an additional notification daemon;
* route Omivoid action feedback through standard notification interfaces where appropriate.

There must not be competing notification daemons.

---

# 15. OSD

Volume, brightness and similar feedback should use DMS OSD where available.

Do not introduce a second OSD stack.

---

# 16. Power Menu

If DMS provides a suitable power menu, Omivoid actions such as:

```text
session.lock
session.logout
session.reboot
session.shutdown
```

may be accessible from it.

The underlying action semantics remain governed by Omivoid.

---

# 17. Wallpaper Management

DMS is expected to play a central role in wallpaper selection.

The Omivoid action remains:

```text
theme.wallpaper.select
```

DMS may provide the implementation.

Wallpaper selection should integrate with the Omivoid theme system rather than remain an isolated shell preference.

---

# 18. DMS and Matugen

DMS may use Matugen for dynamic colour generation.

Omivoid should leverage this where appropriate.

However, Omivoid's architectural goal is:

```text
Wallpaper
   ↓
palette generation
   ↓
canonical theme colours
   ↓
multiple consumers
```

not:

```text
DMS-only colour state
```

The theme system specification defines this boundary in more detail.

---

# 19. System Tray

DMS should remain responsible for normal tray rendering if available.

Omivoid should not build an independent tray.

---

# 20. Workspace Display

DMS may render workspace state obtained from Niri.

This is presentation.

Niri remains authoritative for workspace behaviour.

Omivoid does not need to proxy basic workspace-state communication unless required for a specific feature.

---

# 21. Application Launcher

If DMS provides application launching, it may continue doing so.

However, Omivoid application role actions must remain available.

Example:

```text
app.browser.open
```

must still be callable even if the user normally launches Firefox via the DMS launcher.

---

# 22. Theme Consistency

DMS should consume or participate in the same colour source used by supported applications.

The shell should not drift visually from:

* GTK;
* Qt;
* terminal;
* editor;
* other supported applications.

---

# 23. DMS Configuration

DMS-specific configuration should remain separate from core Omivoid configuration.

Recommended logical split:

```text
config/
    Omivoid settings

dms/
    DMS-specific integration
```

User-owned DMS configuration should not be overwritten wholesale.

---

# 24. Upgrade Resilience

Integration should minimise dependence on internal DMS implementation details.

The agent should document:

* DMS version tested;
* interfaces used;
* assumptions made;
* configuration files touched.

This will make future upgrades easier to diagnose.

---

# 25. Failure Isolation

A DMS failure should not invalidate the entire Omivoid action model.

Where possible:

```text
CLI actions
native Niri actions
core configuration
```

should remain usable even if the shell UI fails.

This is another reason to keep DMS as an implementation layer rather than the architectural core.

---

# 26. Replacement Principle

If DMS is replaced in future, the following should remain largely unchanged:

```text
action IDs
keyboard grammar
CLI
AI tools
project workflows
platform adapters
Niri semantics
```

Only shell-specific adapters and presentation should require substantial changes.

---

# 27. Phase 1 DMS Evaluation Checklist

The implementation agent should explicitly evaluate:

* bar quality;
* Niri integration;
* workspace presentation;
* launcher capability;
* custom action support;
* notification support;
* OSD;
* Wi-Fi interface;
* Bluetooth interface;
* audio interface;
* power controls;
* wallpaper workflow;
* Matugen integration;
* IPC/CLI support;
* extension/plugin options;
* configuration stability.

---

# 28. DMS Adoption Decision

At the end of the initial evaluation, classify each needed shell capability as:

```text
USE DMS
EXTEND DMS
OMIVOID COMPONENT
DEFER
```

This should prevent accidental duplication.

---

# 29. Phase 1 Acceptance Criteria

DMS integration is successful when:

* it reduces rather than increases shell complexity;
* duplicated shell functionality is avoided;
* Omivoid actions can invoke relevant DMS capabilities;
* DMS remains replaceable;
* custom Omivoid UI exists only where justified;
* Niri remains authoritative for compositor state;
* theme integration remains coherent;
* the desktop feels like one environment rather than several overlapping shells.

The guiding rule is:

> **Use DMS as infrastructure where it is strong; build Omivoid where the interaction architecture requires something DMS does not provide.**
