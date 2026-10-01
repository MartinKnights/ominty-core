# ADR-006 — DMS Plugin-First Integration

**Status:** Accepted
**Project:** `ominty-core`
**Phase:** Phase 1
**Decision scope:** Desktop UI, shell extensions and DMS integration

---

# 1. Context

Ominty uses Niri as its compositor and Quickshell as part of its desktop architecture.

DankMaterialShell (DMS) has been selected as the preferred Phase 1 shell layer, subject to practical validation.

Further examination of the DMS ecosystem has established that DMS provides substantially more than the basic desktop shell capabilities originally considered.

In addition to core functionality, DMS provides a plugin architecture capable of extending the desktop through components including:

* bar widgets;
* launcher providers;
* desktop widgets;
* background services/daemons;
* control-centre functionality;
* composite plugins;
* integrations with external applications and services.

The DMS plugin ecosystem also already contains implementations of capabilities relevant to Ominty.

Examples include:

* keyboard shortcut discovery;
* system-event hooks;
* command execution;
* Tailscale integration;
* task management;
* phone integration;
* AI interfaces;
* research/read-later integration.

This changes the cost/benefit calculation for developing custom Ominty shell components.

---

# 2. Decision

> **Ominty will follow a DMS plugin-first strategy for desktop-facing functionality.**

Before implementing a new graphical shell component, the project MUST determine whether the requirement can reasonably be satisfied through:

1. DMS core functionality;
2. an existing DMS plugin;
3. extension or configuration of an existing DMS plugin;
4. a dedicated Ominty DMS plugin;
5. a standalone Ominty component.

A standalone implementation is therefore the final option rather than the default.

---

# 3. Integration Hierarchy

The preferred decision path is:

```text
Requirement
    │
    ▼
Does DMS core provide it?
    │
 ┌──┴──┐
Yes    No
 │      │
 ▼      ▼
Use    Does an existing
DMS    plugin provide it?
          │
       ┌──┴──┐
      Yes    No
       │      │
       ▼      ▼
     Use /   Can it be implemented
     extend  cleanly as an
     plugin  Ominty DMS plugin?
                │
             ┌──┴──┐
            Yes    No
             │      │
             ▼      ▼
          Ominty  Standalone
          plugin   component
```

The shorthand rule is:

```text
DMS Core
   ↓
Existing Plugin
   ↓
Extend Plugin
   ↓
Ominty Plugin
   ↓
Standalone Component
```

---

# 4. Purpose

The plugin-first strategy exists to prevent Ominty from unnecessarily rebuilding mature desktop functionality.

Ominty development effort should primarily be invested in the capabilities that differentiate Ominty:

* canonical actions;
* interaction semantics;
* keyboard workflow;
* discoverability;
* AI integration;
* project workflows;
* system abstraction;
* orchestration;
* portability.

Generic shell infrastructure should be reused wherever practical.

---

# 5. DMS Does Not Define Ominty

This decision does NOT make DMS the architectural source of truth.

The intended relationship remains:

```text
              OMINTY
                 │
     ┌───────────┼───────────┐
     │           │           │
 Interaction   Actions      AI/Workflow
     │           │           │
     └───────────┼───────────┘
                 │
          Integration Layer
                 │
                 ▼
                DMS
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
       Core    Plugins  Ominty
                        Plugins
```

DMS provides presentation and integration capabilities.

Ominty retains ownership of Ominty semantics.

---

# 6. Architectural Ownership

The following remain authoritative Ominty responsibilities:

* Action Registry;
* canonical action IDs;
* keyboard grammar;
* action metadata;
* application roles;
* AI capability policy;
* action risk classification;
* confirmation policy;
* project/workflow semantics;
* platform abstraction;
* adapter architecture;
* Ominty configuration precedence.

A DMS plugin may expose these capabilities but must not silently redefine them.

---

# 7. DMS Responsibilities

DMS and its plugins may provide:

* graphical presentation;
* status widgets;
* launch/search interfaces;
* notifications;
* system controls;
* shell overlays;
* desktop widgets;
* event sources;
* service integrations;
* user interaction surfaces.

Where DMS already provides a good implementation, Ominty SHOULD consume or integrate with it rather than duplicate it.

---

# 8. Action Registry Relationship

DMS plugins that invoke Ominty capabilities SHOULD use canonical actions.

Preferred:

```text
DMS Plugin
    │
    ▼
app.browser.open
    │
    ▼
Ominty Action Resolver
    │
    ▼
Application Adapter
```

Avoid:

```text
DMS Plugin
    │
    ▼
firefox
```

when the semantic intent is simply "open the configured browser."

This preserves application roles and implementation independence.

---

# 9. DMS as an Interaction Surface

DMS should be considered one of several Ominty interaction surfaces.

```text
                 Action Registry
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
    Keyboard          DMS             CLI
                       │
                       ▼
                      AI
```

DMS is therefore a consumer of Ominty actions rather than their owner.

---

# 10. Ominty DMS Plugin

Phase 1 SHOULD investigate creating a dedicated:

```text
Ominty Actions
```

DMS plugin.

This plugin may become the primary graphical bridge between DMS and the Ominty architecture.

The plugin should remain focused on integration rather than duplicating DMS core functionality.

---

# 11. Candidate Ominty Plugin Capabilities

A future Ominty DMS plugin may provide:

```text
Ominty Actions
│
├── Launcher Provider
│   └── Action Registry search
│
├── Interaction Explorer
│   └── Super+K
│
├── AI Provider
│   └── Super+A
│
├── Project Provider
│   └── Super+P
│
├── Context Actions
│
├── Action Status
│
└── Event Integration
```

These capabilities may initially be implemented incrementally rather than as one large plugin.

---

# 12. `Super+K`

The existing plan calls for an Ominty Interaction Explorer available through:

```text
Super+K
```

Before implementing a custom interface, Phase 1 MUST evaluate existing DMS keyboard-shortcut discovery functionality.

If an existing plugin can consume or be extended to consume Ominty registry data, it SHOULD be preferred.

The desired architecture is:

```text
Ominty Action Registry
          │
          ├── binding metadata
          ├── categories
          ├── descriptions
          └── keywords
                  │
                  ▼
          DMS help interface
                  │
                  ▼
               Super+K
```

The registry remains authoritative.

DMS provides presentation.

---

# 13. `Super+Space`

The universal command palette requirement should similarly be implemented through DMS where practical.

The Ominty requirement extends beyond application launching.

The palette should eventually search:

* applications;
* Ominty actions;
* settings;
* project actions;
* AI actions;
* potentially recent items and contextual actions.

A DMS launcher provider is therefore preferred over building a separate launcher if DMS provides sufficient extension capability.

---

# 14. `Super+A`

The AI namespace should also prefer DMS integration for presentation.

Potential architecture:

```text
Super+A
   │
   ▼
DMS / Ominty AI interface
   │
   ▼
Ominty AI Layer
   │
 ┌─┴──────────────┐
 ▼                ▼
Pi               Herdr
                   │
             remote delegation
```

DMS may provide the interface.

Ominty defines:

* available AI actions;
* provider routing;
* context;
* permissions;
* action access.

---

# 15. `Super+P`

Project workflow should follow the same principle.

A future DMS launcher provider may expose:

```text
Open Project
Recent Projects
Project Terminal
Project Editor
Project AI
Project Context
Delegate Project Task
```

These should resolve to canonical:

```text
project.*
```

actions rather than being hard-coded into DMS configuration.

---

# 16. Existing Plugin Evaluation

When a requirement appears to match an existing plugin, the implementation agent MUST evaluate that plugin before creating a replacement.

Evaluation should consider:

* functionality;
* Niri compatibility;
* LMDE compatibility;
* Void portability;
* maintenance status;
* dependencies;
* configuration;
* security implications;
* Action Registry integration;
* extensibility;
* performance;
* upstream activity.

---

# 17. Plugin Classification

Each evaluated plugin should be classified:

```text
ADOPT
ADOPT WITH CONFIGURATION
EXTEND
REFERENCE ONLY
DEFER
REJECT
```

The decision and rationale should be recorded.

---

# 18. Plugin Inventory

Phase 1 SHOULD maintain:

```text
docs/implementation/dms-plugin-inventory.md
```

Suggested structure:

| Plugin            | Purpose            | Decision           | Ominty Role        | Notes                              |
| ----------------- | ------------------ | ------------------ | ------------------- | ---------------------------------- |
| Launcher Keys     | Shortcut discovery | Evaluate           | `Super+K`           | Registry integration required      |
| Hooks             | Event integration  | Evaluate           | Action/event bridge | May avoid daemon                   |
| Tailscale Manager | Mesh networking    | Adopt candidate    | Network UI          | Relevant to IBIS infrastructure    |
| Command Runner    | Command execution  | Evaluate           | Expert interface    | Prefer Ominty actions             |
| Taskwarrior       | Tasks              | Defer/Evaluate     | Project workflow    | Strong local-first fit             |
| AI Assistant      | AI UI              | Reference/Evaluate | AI presentation     | Must not replace Ominty AI policy |

The inventory should evolve as the DMS ecosystem changes.

---

# 19. Plugin Installation Is Not Architecture

Installing a plugin does not automatically make it part of canonical Ominty.

There is a distinction between:

```text
User-installed DMS plugin
```

and:

```text
Ominty-supported DMS integration
```

Ominty-supported plugins should be deliberately selected, documented and tested.

Users remain free to install additional DMS plugins.

---

# 20. Default Plugin Set

Ominty MAY eventually define a recommended/default plugin set.

It should remain deliberately small.

A plugin belongs in the default set only if it contributes directly to the intended Ominty experience.

Avoid turning Ominty into a large bundle of unrelated DMS plugins.

---

# 21. Optional Plugin Profiles

Future Ominty releases MAY provide optional plugin profiles.

For example:

```text
ominty-core
ominty-development
ominty-research
ominty-infrastructure
ominty-writing
```

Possible mapping:

```text
Core
├── interaction discovery
├── hooks
└── Ominty Actions

Development
├── development-service monitoring
└── project tools

Infrastructure
├── Tailscale
└── SSH monitoring

Research
├── read-later
└── AI research tools

Writing
├── task/project integration
└── AI writing actions
```

Profiles are not required for Phase 1.

---

# 22. Plugin Dependencies

Dependencies introduced by plugins must be reviewed.

A plugin SHOULD NOT be adopted automatically if it requires substantial unrelated infrastructure.

Particular attention should be paid to:

* Arch-specific assumptions;
* Hyprland-specific commands;
* systemd-only behaviour;
* package names;
* hard-coded paths.

These matter because Ominty Phase 1 runs on LMDE and the eventual target includes Void Linux.

---

# 23. Portability

A useful DMS plugin that is currently distribution-specific MAY still be considered.

However, classify it appropriately.

Example:

```text
Useful concept
    │
    ▼
Plugin is Arch-specific
    │
    ├── easy portability fix
    │       ↓
    │    EXTEND
    │
    └── tightly coupled
            ↓
       REFERENCE ONLY
```

Do not contaminate Ominty core with distro-specific workarounds merely to support one plugin.

---

# 24. Compositor Compatibility

Similarly, a Hyprland-specific plugin must not be assumed suitable for Ominty.

Since Ominty uses Niri, compositor-specific dependencies must be evaluated.

Where the plugin concept is valuable but implementation is Hyprland-specific, consider:

1. upstream Niri support;
2. a clean portable contribution;
3. an Ominty/Niri plugin;
4. reference only.

---

# 25. Upstream-First Modification

When an existing DMS plugin is almost suitable, prefer:

```text
configuration
    ↓
extension
    ↓
upstream contribution
```

before maintaining a permanent private fork.

A private fork should require a clear technical justification.

---

# 26. Fork Policy

Forking a DMS plugin is acceptable when:

* the functionality is strategically important;
* required changes cannot reasonably be upstreamed;
* upstream architecture prevents required integration;
* maintenance cost is understood.

Forking is NOT justified merely to:

* rename UI elements;
* change minor styling;
* avoid learning configuration;
* make trivial convenience modifications.

---

# 27. Event Integration

DMS plugins capable of responding to desktop events should be evaluated before Ominty introduces a persistent daemon.

Potential model:

```text
DMS event
   │
   ▼
Hook / plugin
   │
   ▼
Ominty Action
```

Examples may include:

```text
wallpaper changed
    → theme.palette.regenerate

desktop event
    → registered Ominty action
```

This may satisfy Phase 1 requirements without introducing:

```text
omintyd
```

---

# 28. Daemon Deferral

ADR-006 strengthens the existing Phase 1 decision to defer an Ominty daemon.

Before proposing a daemon, implementation MUST determine whether the requirement can be satisfied through:

* Niri IPC;
* DMS IPC;
* DMS plugin;
* DMS event hook;
* one-shot Ominty action;
* existing system service.

Only introduce a persistent Ominty process when persistent Ominty-owned state or event handling genuinely requires it.

---

# 29. Command Execution

DMS command-execution plugins may be useful as expert interfaces.

However:

```text
arbitrary shell execution
```

must not replace:

```text
canonical Ominty actions
```

for normal supported workflows.

Preferred:

```text
DMS
  ↓
ominty action run app.browser.open
```

rather than embedding:

```text
firefox
```

throughout DMS configuration.

---

# 30. Security

Plugins expand the trusted desktop surface.

Before adopting a plugin that:

* executes commands;
* accesses credentials;
* controls network state;
* communicates externally;
* accesses files;
* invokes AI;

review its behaviour and permissions.

Plugin convenience does not override Ominty's security model.

---

# 31. AI Plugins

Existing DMS AI plugins should be evaluated primarily as:

* presentation layers;
* UX references;
* integration examples.

They must not silently replace the Ominty AI architecture.

Ominty intends to support a controlled AI layer involving Pi, Herdr and potentially additional providers.

AI capability access remains governed by the Action Registry.

---

# 32. Plugin Locking and Reproducibility

Where DMS supports reproducible plugin configuration or locking, Ominty SHOULD use it for officially supported plugins.

The project should be able to determine:

* which plugins are expected;
* which versions/revisions are active where supported;
* which plugins are optional;
* which configuration belongs to Ominty.

This supports reproducible LMDE and future Void installations.

---

# 33. Failure Isolation

A failed optional plugin should not prevent the core desktop from functioning.

Where practical:

```text
Niri
  ↓
core desktop interaction
```

must remain available independently of optional DMS plugins.

Similarly, failure of an Ominty plugin should not prevent basic DMS functionality.

---

# 34. Testing

Official Ominty plugin integrations must be included in Phase 1 testing.

Test at minimum:

* plugin loads;
* intended UI appears;
* Niri compatibility;
* action invocation;
* failure behaviour;
* configuration persistence;
* clean session startup;
* interaction with DMS updates where practical.

---

# 35. Documentation

For every officially adopted plugin, document:

```text
Purpose
Why Ominty uses it
Dependencies
Configuration
Canonical actions exposed
Platform limitations
Known issues
Removal/rollback
```

Do not rely solely on external plugin documentation for Ominty-specific integration behaviour.

---

# 36. Impact on Phase 1 Implementation

Before implementing the custom UI portions of:

```text
Super+K
Super+Space
Super+A
Super+P
```

the implementation agent MUST evaluate whether they can be provided through DMS core or DMS plugins.

Therefore the DMS evaluation stage should occur before substantial custom Quickshell UI development.

---

# 37. Revised Phase 1 UI Sequence

The preferred sequence becomes:

```text
Action Registry
      ↓
Action Runner
      ↓
Niri Integration
      ↓
DMS Plugin Audit
      ↓
DMS Integration
      ↓
Ominty DMS Plugin Prototype
      ↓
Super+K / Super+Space
      ↓
AI Integration
      ↓
Project Integration
```

This replaces any assumption that Ominty should first build independent interfaces for each capability.

---

# 38. Consequences

## Positive

This approach:

* reduces duplicate implementation;
* reduces maintenance;
* accelerates Phase 1;
* benefits from existing DMS UX;
* keeps Ominty visually coherent;
* provides a natural extension mechanism;
* reduces pressure to create an Ominty daemon;
* lets development focus on Ominty-specific capabilities;
* creates opportunities to contribute improvements upstream.

## Negative

Ominty becomes more dependent on the DMS ecosystem.

Plugin APIs may change.

Third-party plugin quality may vary.

Some useful plugins may be distribution- or compositor-specific.

Additional dependency review is required.

These costs are accepted because the dependency remains behind defined architectural boundaries.

---

# 39. Rejected Alternative — Build Ominty UI First

Building custom:

* bar widgets;
* launcher;
* keybinding explorer;
* AI panel;
* system controls;

before evaluating DMS would duplicate functionality unnecessarily.

Rejected.

---

# 40. Rejected Alternative — Adopt Every Useful Plugin

Installing every attractive plugin would create:

* dependency growth;
* inconsistent UX;
* maintenance burden;
* larger attack surface;
* unclear project scope.

Rejected.

Ominty should remain curated.

---

# 41. Rejected Alternative — Make Plugins Authoritative

Allowing plugins to independently define Ominty semantics would fragment the architecture.

Rejected.

Plugins provide implementation and presentation.

The Action Registry and Ominty specifications remain authoritative.

---

# 42. Revisit Conditions

This decision should be reconsidered if:

* DMS plugin APIs prove unstable;
* plugins cannot access the capabilities required by Ominty;
* plugin integration creates excessive coupling;
* DMS performance becomes problematic;
* maintaining DMS compatibility becomes more expensive than maintaining focused Ominty components;
* the project later replaces DMS.

Individual plugin decisions may change without invalidating this ADR.

---

# 43. Result

The new Ominty development rule is:

> **Before building a desktop-facing capability, determine whether DMS already provides the capability, whether an existing plugin provides it, or whether it can be implemented cleanly as an Ominty DMS plugin. Build a standalone component only when those approaches are inadequate.**

This keeps the architectural distinction clear:

```text
DMS
    = desktop presentation and shell ecosystem

Ominty
    = interaction, actions, AI, workflow and system abstraction
```

The goal is not to build another desktop shell on top of DMS.

The goal is to make DMS an effective presentation and extension platform for the Ominty operating experience.
