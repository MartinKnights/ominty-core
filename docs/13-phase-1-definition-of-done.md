# Omivoid LMDE — Phase 1 Definition of Done

**Project:** `omivoid-lmde`
**Phase:** Phase 1

---

# 1. Purpose

This document defines when Phase 1 is complete.

Phase 1 is not complete simply because the desktop looks finished.

It is complete when the core Omivoid architecture has been proven, documented and validated.

---

# 2. Primary Outcome

At completion, `omivoid-lmde` should demonstrate:

> **A keyboard-first, discoverable, dynamically themed, AI-aware Niri desktop driven by a canonical action model.**

---

# 3. Existing System Preserved

The project MUST leave the machine with:

* working LMDE;
* working Niri;
* working Quickshell;
* recoverable configuration;
* no unnecessary loss of existing user configuration.

---

# 4. Action Registry Complete

The Phase 1 registry must:

* load from TOML;
* validate successfully;
* contain approximately 30–40 useful actions;
* use stable canonical IDs;
* expose required metadata;
* support action lookup;
* support action execution where applicable.

---

# 5. Registry Validation Complete

The project must provide:

```text
omivoid registry validate
```

and validation must cover the core schema and key conflicts.

A clean Phase 1 registry must pass.

---

# 6. Action Runner Complete

The project must provide:

```text
omivoid action run <id>
```

for actions that require Omivoid runtime execution.

Errors must be understandable.

---

# 7. Application Roles Complete

At minimum, roles should exist for:

```text
terminal
browser
files
editor
notes
mail
```

Configured roles should launch correctly or report unavailable status.

---

# 8. Niri Integration Complete

Niri integration must demonstrate:

* native window actions;
* native focus actions;
* workspace actions;
* Omivoid application bindings;
* no major regression of existing Niri functionality.

Frequent compositor actions must remain responsive.

---

# 9. Binding Audit Complete

A documented Niri binding audit must exist.

No known unresolved binding conflict should be silently active.

---

# 10. `Super+K` Complete

`Super+K` must provide an interaction discovery interface driven from registry data.

It must expose at minimum:

* name;
* keybinding;
* category;
* description.

Search is expected unless a documented technical limitation prevents it.

---

# 11. `Super+Space` Complete

The universal palette must expose Omivoid actions rather than function solely as a traditional app launcher.

At minimum it should find:

* applications;
* actions;
* system functions represented in the registry.

---

# 12. DMS Decision Complete

DMS must have been evaluated.

For major shell responsibilities, the project should know whether the implementation is:

```text
USE DMS
EXTEND DMS
OMIVOID COMPONENT
DEFER
```

The decision must be documented.

---

# 13. Shell Experience Complete

The desktop should have one coherent shell experience.

There must not be competing:

* notification daemons;
* OSD systems;
* bars;
* power interfaces;

without a documented reason.

---

# 14. Theme Flow Complete

Phase 1 must demonstrate:

```text
wallpaper
   ↓
palette
   ↓
shell
   ↓
at least one external application
```

This proves cross-application theme architecture.

---

# 15. Theme Regeneration Complete

The project should support regeneration of theme output from the current source without requiring a new wallpaper selection.

---

# 16. AI Namespace Complete

`Super+A` must exist as a coherent AI entry point.

At minimum, it should expose implemented AI capabilities and reserved conceptual actions.

---

# 17. Pi Integration Complete

Pi should be launchable or invokable through the Omivoid AI layer.

If Pi itself is unavailable, the reason must be documented and the action marked unavailable.

---

# 18. Herdr Position Defined

Full Herdr orchestration is not required.

However:

```text
ai.herdr.open
```

or its equivalent architectural position must be defined.

The future relationship between Omivoid and Herdr should remain clear.

---

# 19. AI-to-Action Proof Complete

At least one controlled non-AI Omivoid action must be callable through the AI capability path.

Recommended:

```text
app.browser.open
```

The AI should resolve and invoke the registered action rather than directly hard-coding the application command.

---

# 20. Context Experiment Complete

Selection-context behaviour must be investigated.

Outcome may be:

```text
IMPLEMENTED
```

or:

```text
DEFERRED — reliable selection acquisition not established
```

Either is acceptable if documented.

---

# 21. Platform Abstraction Complete

Portable code must not contain unnecessary Debian-specific implementation.

Platform-specific behaviour must be isolated where practical.

---

# 22. Void Portability Review Complete

A written portability review must exist.

It should identify:

* portable components;
* Debian-specific components;
* expected Void replacements;
* unresolved portability questions.

---

# 23. Configuration Layout Complete

User configuration, generated state and project source must follow the defined configuration layout or a documented approved revision.

---

# 24. Backups and Rollback Complete

The project must demonstrate that relevant configuration can be restored.

At least one rollback test should have been performed successfully.

---

# 25. Test Suite Passes

Automated tests relevant to the implemented features must pass.

Manual desktop interaction tests must also be completed.

---

# 26. Startup Validation Complete

The system must survive a clean session restart or reboot.

After startup:

* Niri works;
* shell works;
* Omivoid bindings work;
* registry is valid;
* no required manual startup commands remain undocumented.

---

# 27. Documentation Complete

The following architecture documents must reflect the implementation:

```text
00-project-overview.md
01-design-principles.md
02-interaction-spec.md
03-action-registry-spec.md
04-phase-1-action-catalogue.md
05-platform-abstraction.md
06-niri-integration.md
07-dms-integration.md
08-theme-system.md
09-ai-integration.md
10-phase-1-implementation-plan.md
11-testing-and-validation.md
12-configuration-layout.md
13-phase-1-definition-of-done.md
```

Relevant ADRs must remain current.

---

# 28. Implementation Records Complete

At minimum expect:

```text
docs/implementation/
├── environment-audit.md
├── niri-binding-audit.md
├── dms-evaluation.md
└── void-portability-review.md
```

Additional implementation notes may be added as needed.

---

# 29. No Known Critical Architecture Violations

There must be no known unresolved cases where:

* core actions bypass the registry without reason;
* platform implementation leaks widely into portable core;
* user config is overwritten destructively;
* AI bypasses declared policy for routine actions;
* duplicate shell components conflict;
* generated config cannot be rolled back.

---

# 30. Deferred Work Is Explicit

Deferred work must be recorded rather than silently abandoned.

Examples:

* selection capture;
* remote Herdr delegation;
* voice;
* additional theme adapters;
* daemon/event architecture.

---

# 31. Code Quality

Implementation should be:

* readable;
* documented where non-obvious;
* structured around defined boundaries;
* free of dead experimental code;
* suitable for Git version control;
* understandable by another developer or agent.

---

# 32. Public-Project Readiness

The repository should be close to a state where it could be shown publicly without exposing:

* personal credentials;
* private paths;
* undocumented local assumptions.

A polished public release is not required.

---

# 33. Phase 1 Exit Decision

Phase 1 should not automatically transition into Void implementation.

At completion, perform an architectural review.

Ask:

1. What worked?
2. What felt awkward?
3. Which abstraction was unnecessary?
4. Which abstraction is missing?
5. Is DMS the correct long-term shell?
6. Is the Action Registry schema sufficient?
7. Is the keyboard grammar comfortable?
8. Is AI integration useful rather than decorative?
9. What must change before Void?
10. What should remain exactly the same?

---

# 34. Completion Statement

Phase 1 is done when the architecture has moved from:

```text
documented idea
```

to:

```text
tested working reference implementation
```

and when that implementation provides enough evidence to design the Void phase with confidence.
