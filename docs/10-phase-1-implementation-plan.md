# Omivoid LMDE — Phase 1 Implementation Plan

**Project:** `omivoid-lmde`
**Phase:** Phase 1
**Platform:** LMDE
**Existing baseline:** Niri and Quickshell already installed

---

# 1. Purpose

This document defines the implementation sequence for Phase 1.

The objective is to move from architecture to a working Omivoid LMDE reference implementation without introducing unnecessary complexity.

The implementation strategy is incremental:

```text
inspect
  ↓
baseline
  ↓
introduce one capability
  ↓
validate
  ↓
integrate
  ↓
expand
```

The project must remain usable throughout development.

---

# 2. Phase 1 Objective

Phase 1 must prove that the Omivoid architecture works in practice.

It must demonstrate:

* the Action Registry;
* action validation;
* application roles;
* Niri integration;
* registry-driven help;
* registry-driven action search;
* DMS suitability;
* dynamic theming;
* AI namespace;
* at least one controlled AI-to-action workflow;
* platform abstraction suitable for later Void migration.

---

# 3. Existing Environment

The implementation MUST assume the following already exist:

* LMDE;
* Niri;
* Quickshell.

The agent must not reinstall or replace these by default.

Before making changes:

1. inspect existing configuration;
2. record relevant versions;
3. locate active config files;
4. identify currently active bindings;
5. identify shell startup;
6. create appropriate backups;
7. establish a recoverable baseline.

---

# 4. Stage 0 — Environment Audit

Before implementation, produce an environment audit.

The audit should capture:

```text
Operating system
Niri version
Quickshell version
DMS status
Matugen status
Network provider
Audio stack
Terminal
Browser
File manager
Editor
Notes application
Mail application
Screenshot tooling
Existing Niri config location
Existing Quickshell config location
Existing keybindings
```

Output should be saved under:

```text
docs/implementation/
environment-audit.md
```

This document becomes part of the implementation record.

---

# 5. Stage 1 — Establish Repository Runtime Structure

Create only the directories required for Phase 1.

Recommended:

```text
omivoid-lmde/
├── actions/
├── adapters/
│   ├── common/
│   ├── niri/
│   ├── dms/
│   └── debian/
├── cli/
├── config/
├── niri/
│   ├── templates/
│   └── generated/
├── shell/
├── themes/
├── ai/
├── tests/
└── docs/
```

Do not create empty architecture for deferred subsystems unless needed.

---

# 6. Stage 2 — Implement Registry Loader

Implement the smallest functional registry loader.

It must:

* discover action TOML files;
* parse schema version;
* load action definitions;
* merge definitions;
* detect duplicate IDs;
* expose loaded actions to CLI tooling.

Initial target:

```text
omivoid action list
```

No execution is required at this stage.

---

# 7. Stage 3 — Implement Registry Validation

Implement:

```text
omivoid registry validate
```

Validation must initially detect:

* malformed TOML;
* unsupported registry version;
* duplicate action IDs;
* invalid action IDs;
* missing required fields;
* invalid risk values;
* invalid confirmation values;
* duplicate keybindings;
* unknown adapters where detectable.

Validation output must clearly separate:

```text
ERROR
WARNING
INFO
```

Do not continue to generated configuration if validation fails.

---

# 8. Stage 4 — Implement Initial Action Files

Create the Phase 1 registry files based on:

```text
docs/04-phase-1-action-catalogue.md
```

Start with a small Priority A subset.

Recommended first actions:

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

Validate these before expanding the catalogue.

---

# 9. Stage 5 — Application Roles

Implement:

```text
config/apps.toml
```

Application actions must resolve roles.

Example:

```toml
[apps]
terminal = ""
browser = ""
files = ""
editor = ""
notes = ""
mail = ""
```

Actual values should be based on the environment audit.

Do not assume example application names from documentation are installed.

---

# 10. Stage 6 — Action Runner

Implement:

```text
omivoid action run <action-id>
```

Initial requirements:

* locate action;
* check platform;
* resolve adapter;
* validate required parameters;
* execute action;
* return useful success or error output.

Support machine-readable output where practical.

---

# 11. Stage 7 — Common Application Adapter

Implement:

```text
app.launch
```

The adapter should:

1. receive a role;
2. resolve the configured application;
3. validate availability where practical;
4. launch it;
5. report failure clearly.

This is the first proof of:

```text
intent
→ registry
→ adapter
→ implementation
```

---

# 12. Stage 8 — Niri Binding Audit

Before generating Niri configuration:

* parse or inspect current bindings;
* compare against proposed Omivoid bindings;
* produce a conflict report.

Save the result under:

```text
docs/implementation/niri-binding-audit.md
```

Classify bindings as:

```text
ACCEPT
COMPATIBLE
CONFLICT
CHANGE
DEFER
```

No conflicting binding should be silently overwritten.

---

# 13. Stage 9 — Niri Native Mapping

Implement native mappings for the first Niri actions.

Priority:

```text
window.close
window.focus.left
window.focus.right
window.focus.up
window.focus.down
workspace.next
workspace.previous
```

Where practical, generate native Niri configuration.

Do not route frequent navigation through the Omivoid runner.

---

# 14. Stage 10 — Generated Niri Fragment

Generate an Omivoid-owned Niri configuration fragment.

Requirements:

* generated file clearly marked;
* source action IDs documented;
* existing user config preserved;
* only Omivoid-managed bindings included;
* invalid output must not replace working config.

If the installed Niri version supports clean includes, prefer an include-based structure.

If not, document the safest available integration approach.

---

# 15. Stage 11 — `Super+K` Data

Create registry-derived help data.

The first implementation does not need elaborate graphics.

It must prove that:

```text
registry
   ↓
discoverability
```

works.

At minimum, `Super+K` should expose:

* action name;
* category;
* primary binding;
* description.

Search is strongly preferred.

---

# 16. Stage 12 — Universal Action Search

Implement the data/backend for:

```text
Super+Space
```

The initial action search should support:

* action names;
* keywords;
* category;
* application actions.

The UI may use DMS or a custom Quickshell component depending on the DMS evaluation.

The search backend should remain independent of the UI.

---

# 17. Stage 13 — DMS Evaluation

Evaluate DMS according to:

```text
docs/07-dms-integration.md
```

For each shell capability classify:

```text
USE DMS
EXTEND DMS
OMIVOID COMPONENT
DEFER
```

Save findings under:

```text
docs/implementation/dms-evaluation.md
```

Do not begin by modifying DMS internals.

---

# 18. Stage 14 — DMS Integration

Integrate only the DMS capabilities selected during evaluation.

Likely candidates:

* bar;
* notifications;
* audio;
* Wi-Fi;
* Bluetooth;
* wallpaper;
* power controls.

Map relevant Omivoid actions to stable DMS interfaces where possible.

---

# 19. Stage 15 — Theme Proof

Implement the minimum theme flow:

```text
wallpaper
   ↓
palette
   ↓
DMS
   ↓
one external application
```

Recommended first external application:

```text
terminal
```

because it is central to the Omivoid workflow.

Do not attempt full application coverage yet.

---

# 20. Stage 16 — Theme Regeneration

Implement:

```text
theme.palette.regenerate
```

This must allow palette/application theme regeneration without requiring a new wallpaper selection.

---

# 21. Stage 17 — Expand Action Catalogue

Once the architecture is stable, add Priority B actions:

* remaining application roles;
* additional Niri operations;
* audio actions;
* network panel actions;
* capture;
* session actions.

Validate after each category.

Do not add the entire catalogue in one untested batch.

---

# 22. Stage 18 — AI Namespace

Implement:

```text
Super+A
```

Provide a visible or searchable AI namespace.

Initial entries:

```text
Ask AI
Pi
Herdr
Explain Selection
Summarise Selection
```

Unavailable actions should appear as unavailable or be omitted according to UI design.

Do not fake implementation.

---

# 23. Stage 19 — Pi Integration

Implement:

```text
ai.pi.open
```

and, if practical:

```text
ai.ask
```

through the selected Pi integration.

The goal is not deep orchestration.

The goal is a clean Omivoid-to-AI provider boundary.

---

# 24. Stage 20 — AI Capability Proof

Expose one non-AI Omivoid action to the AI layer.

Recommended proof:

```text
app.browser.open
```

Demonstrate:

```text
user request
    ↓
AI
    ↓
registered action selection
    ↓
Omivoid action runner
    ↓
configured browser
```

This is a major Phase 1 milestone.

---

# 25. Stage 21 — Selection Context Experiment

Investigate reliable selected-text acquisition under the Wayland/Niri environment.

Do not assume clipboard state equals current selection.

If reliable context acquisition is achieved, implement one action:

```text
ai.selection.explain
```

If not, mark selection actions deferred.

This is acceptable for Phase 1.

---

# 26. Stage 22 — Complete Registry Catalogue

Expand toward approximately 30–40 stable actions.

Each action must satisfy the Phase 1 completeness criteria defined in:

```text
docs/04-phase-1-action-catalogue.md
```

Do not optimise for action count.

---

# 27. Stage 23 — Platform Boundary Review

Review all implementation code for Debian leakage.

Search specifically for:

```text
apt
apt-get
dpkg
systemctl
/etc/debian*
linuxmint
```

Determine whether each occurrence belongs in:

```text
adapters/debian/
```

or genuinely belongs elsewhere.

---

# 28. Stage 24 — Void Portability Review

Produce:

```text
docs/implementation/void-portability-review.md
```

For each subsystem classify:

```text
PORTABLE
COMMON ADAPTER
DEBIAN-SPECIFIC
MACHINE-SPECIFIC
UNKNOWN
```

The purpose is not to implement Void yet.

It is to expose abstraction weaknesses.

---

# 29. Stage 25 — Stabilisation

Before declaring Phase 1 complete:

* remove dead experiments;
* document dependencies;
* remove hard-coded personal paths;
* validate generated files;
* run all tests;
* update implementation notes;
* ensure rollback remains possible.

---

# 30. Explicitly Out of Scope

Do not implement during Phase 1 unless required to unblock core work:

* Omivoid daemon;
* event bus;
* remote action routing;
* full Herdr orchestration;
* Agno integration;
* voice system;
* plugin marketplace;
* complex permissions engine;
* AI autonomy framework;
* remote fleet management;
* full Void installer;
* kernel hardening implementation;
* comprehensive application theming;
* graphical registry editor.

---

# 31. Implementation Order Summary

```text
Environment audit
      ↓
Registry loader
      ↓
Registry validation
      ↓
Initial actions
      ↓
Application roles
      ↓
Action runner
      ↓
Niri audit/integration
      ↓
Super+K
      ↓
Super+Space
      ↓
DMS evaluation
      ↓
Theme proof
      ↓
Expanded actions
      ↓
AI namespace
      ↓
AI capability proof
      ↓
Portability review
      ↓
Stabilisation
```

---

# 32. Phase 1 Guiding Rule

At every stage:

> **Prove the smallest useful version of the architecture before expanding it.**

Phase 1 should end with a coherent working system, not a large collection of half-implemented subsystems.
