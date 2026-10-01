# ADR-002 — DankMaterialShell as the Preferred Shell Layer

**Status:** Provisionally Accepted — Validate During Phase 1
**Project:** `ominty-core`
**Phase:** Phase 1

---

# 1. Context

Ominty requires graphical desktop-shell functionality including:

* bar;
* system status;
* notifications;
* OSD;
* system tray;
* quick settings;
* audio controls;
* network controls;
* Bluetooth controls;
* wallpaper management;
* theme presentation;
* launch/search interfaces.

Quickshell is already installed on the Phase 1 LMDE machine.

DankMaterialShell (DMS) is a Quickshell-based desktop shell with explicit Niri support and provides many of the capabilities Ominty requires.

Building all of these components independently would create significant implementation and maintenance work without necessarily improving the Ominty interaction architecture.

---

# 2. Decision

> **DankMaterialShell is the preferred Phase 1 graphical shell implementation, subject to practical validation.**

Ominty should use DMS for shell capabilities that DMS already provides adequately.

Ominty should build custom Quickshell components only where an Ominty-specific requirement cannot reasonably be satisfied through DMS.

---

# 3. Status Qualification

This ADR is intentionally marked:

```text
Provisionally Accepted
```

rather than permanently accepted.

Phase 1 must validate DMS against actual Ominty requirements.

The project must not become architecturally dependent on DMS before that validation is complete.

---

# 4. Expected DMS Responsibilities

Subject to validation, DMS should provide or participate in:

* bar;
* workspace display;
* active-window display;
* clock;
* battery;
* media;
* tray;
* notifications;
* notification history;
* OSD;
* Wi-Fi UI;
* Bluetooth UI;
* audio UI;
* quick settings;
* power UI;
* wallpaper UI;
* dynamic theme presentation.

---

# 5. Ominty Responsibilities

DMS does not own:

* canonical actions;
* action IDs;
* action metadata;
* keyboard grammar;
* application roles;
* AI policy;
* project workflow;
* platform abstraction;
* risk classification;
* interaction semantics.

Those remain Ominty responsibilities.

---

# 6. Architectural Relationship

The intended relationship is:

```text
Ominty
   │
   ├── Interaction Model
   ├── Action Registry
   ├── AI Layer
   ├── Theme Contract
   └── Platform Abstraction
             │
             ▼
            DMS
             │
             ▼
         Quickshell
```

Not:

```text
Ominty
   =
DMS configuration
```

---

# 7. Integration Strategy

For every shell requirement, classify it as:

```text
USE DMS
EXTEND DMS
BUILD OMINTY COMPONENT
DEFER
```

`USE DMS` should be the default when DMS already provides a suitable implementation.

---

# 8. Preferred Interfaces

Ominty should integrate with DMS through supported interfaces wherever possible.

Preference order:

1. documented IPC/API;
2. documented CLI;
3. supported configuration;
4. supported plugin/extension mechanism;
5. external integration;
6. internal modification only as a last resort.

---

# 9. Fork Policy

DMS should not be forked during Phase 1 unless a critical Ominty requirement cannot otherwise be implemented.

A fork creates:

* maintenance burden;
* upstream divergence;
* upgrade complexity;
* unnecessary ownership of shell code.

A missing convenience feature is not sufficient justification.

---

# 10. Custom Ominty UI

Likely Ominty-specific interfaces include:

* `Super+K` Interaction Explorer;
* chord continuation overlays;
* AI namespace;
* project namespace;
* potentially universal action search.

These should first be evaluated against DMS extension capabilities.

A small separate Quickshell component is acceptable if necessary.

---

# 11. Command Palette Question

DMS launcher functionality must be evaluated against the Ominty requirement for:

```text
Super+Space
```

to search more than applications.

The Ominty palette should eventually be capable of searching:

* applications;
* actions;
* settings;
* AI functions;
* projects.

If DMS can provide this cleanly, use it.

If not, Ominty may provide its own action palette.

---

# 12. Theme Relationship

DMS's wallpaper and Matugen functionality should be used where practical.

However, Ominty requires a theme architecture capable of serving consumers outside DMS.

Therefore:

```text
DMS theme capability
       ↓
participates in
       ↓
Ominty theme architecture
```

rather than becoming the only source available to other Ominty components.

---

# 13. Failure Isolation

Core Ominty functionality should not disappear entirely if DMS fails.

In particular:

* native Niri bindings;
* CLI actions;
* registry inspection;
* basic application launching;

should remain recoverable where practical.

---

# 14. Consequences

## Positive

DMS may eliminate the need to independently maintain numerous desktop components.

This allows Ominty development to focus on its differentiators:

* interaction architecture;
* discoverability;
* action model;
* AI integration;
* workflows.

## Negative

Ominty becomes partially dependent on an external project for graphical shell behaviour.

DMS changes may require adapter maintenance.

Some Ominty UX requirements may not fit DMS directly.

These costs are acceptable if the dependency remains bounded.

---

# 15. Rejected Alternative — Build Entire Shell

Building an entire Quickshell shell from scratch during Phase 1 would duplicate mature functionality and substantially increase project scope.

It is rejected unless DMS proves unsuitable.

---

# 16. Rejected Alternative — Make DMS the Ominty Architecture

Using DMS configuration itself as the definition of Ominty would tightly couple:

* actions;
* keyboard behaviour;
* theming;
* AI;
* shell presentation.

This would make future replacement difficult.

It is rejected.

---

# 17. Validation Criteria

DMS should be retained as the preferred shell if it proves satisfactory for:

* Niri integration;
* stability;
* bar;
* notifications;
* OSD;
* system controls;
* wallpaper management;
* dynamic theming;
* action invocation;
* customisation/extensibility.

---

# 18. Revisit Conditions

Reconsider DMS if:

* required Niri integration is unreliable;
* extension mechanisms are insufficient;
* core Ominty interaction requires extensive patching;
* DMS introduces unacceptable performance or stability issues;
* maintaining compatibility becomes harder than maintaining a focused Ominty shell.

---

# 19. Result

Phase 1 begins with the assumption:

> **Use DMS for conventional shell infrastructure and reserve custom Ominty development for the interaction capabilities that make Ominty distinct.**
