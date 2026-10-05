# AGENTS.md — Ominty LMDE

## 1. Purpose

This file defines the operating instructions for any implementation agent working on the `ominty-core` project.

The agent is responsible for implementing the project.

The architecture is defined by the project documentation.

The agent MUST treat the documentation as the design authority rather than independently redesigning Ominty during implementation.

---

# 2. Project Objective

`ominty-core` is the Phase 1 reference implementation of Ominty.

Ominty is intended to be:

* keyboard-first;
* discoverable;
* action-driven;
* dynamically themed;
* AI-native;
* Niri-based;
* portable toward Void Linux.

LMDE is the Phase 1 validation platform.

This repository is **objective 1** of a twofold project: it is developed and
validated on a live machine. **Objective 2** turns what is validated here into a
reproducible install/**migration** process for the distribution repo
(`MartinKnights/Ominty`). Development here therefore feeds distribution — work
must stay generic and free of personal paths (§33) so it can be lifted into the
installer. The deployment entry point is that repo's `AGENTS.md`; the migration
record is its `docs/MIGRATION.md`.

---

# 3. Existing Environment

The target machine already has:

* LMDE installed;
* Niri installed;
* Quickshell installed.

Do NOT begin by reinstalling these components.

Do NOT assume a clean system.

Before modifying existing configuration:

1. inspect it;
2. identify the active files;
3. identify existing behaviour;
4. back up affected files;
5. preserve unrelated user configuration.

---

# 4. Read Documentation Before Implementation

Before making architectural or implementation decisions, read the relevant project documentation.

Core documents:

```text
docs/00-project-overview.md
docs/01-design-principles.md
docs/02-interaction-spec.md
docs/03-action-registry-spec.md
docs/04-phase-1-action-catalogue.md
docs/05-platform-abstraction.md
docs/06-niri-integration.md
docs/07-dms-integration.md
docs/08-theme-system.md
docs/09-ai-integration.md
docs/10-phase-1-implementation-plan.md
docs/11-testing-and-validation.md
docs/12-configuration-layout.md
docs/13-phase-1-definition-of-done.md
```

Architecture decisions:

```text
docs/decisions/
```

---

# 5. Documentation Precedence

When guidance conflicts, use this precedence:

```text
Accepted ADR
    ↓
core specification
    ↓
implementation plan
    ↓
implementation notes
    ↓
existing code
```

Existing code does not override documented architecture merely because it already exists.

However, do not rewrite working code/configuration without a concrete reason.

---

# 6. Do Not Change Architecture Silently

If implementation reveals that a documented architecture is impractical:

DO NOT silently work around it and establish a different design.

Instead:

1. identify the conflict;
2. document the technical reason;
3. propose a specific alternative;
4. record the decision before treating it as architectural policy.

Implementation discoveries are expected.

Undocumented architectural drift is not.

---

# 7. Core Architectural Contracts

The following rules are mandatory.

## Contract 1

> The Action Registry defines what an action means.

## Contract 2

> Adapters define how the action is performed.

## Contract 3

> No normal interaction surface should need to know implementation-specific commands where a canonical action exists.

## Contract 4

> Native Niri operations should remain native where this improves correctness or latency.

## Contract 5

> Platform-specific implementation must remain below the platform abstraction where practical.

## Contract 6

> Existing user configuration must be preserved unless replacement is explicitly justified and approved by the project design.

---

# 8. Action Registry Is Authoritative

Canonical action IDs must come from the registry.

Examples:

```text
app.browser.open
window.close
workspace.next
theme.wallpaper.select
ai.ask
```

Do not invent parallel identifiers casually.

If a new action is needed:

1. determine whether an existing action already represents the intent;
2. follow namespace conventions;
3. add registry metadata;
4. validate it;
5. implement through the appropriate backend.

---

# 9. Do Not Hard-Code Applications Into Generic Actions

Use application roles.

Correct:

```text
app.browser.open
    ↓
role = browser
```

Incorrect for a generic action:

```text
app.firefox.open
```

Specific application actions are allowed only when that application is genuinely the intended semantic target.

---

# 10. Niri Rules

Niri is the compositor.

Respect Niri's native scrolling model.

Do NOT attempt to reproduce Hyprland behaviour mechanically.

Native actions such as:

```text
window.focus.*
window.move.*
workspace.*
```

should use native Niri bindings where practical.

Avoid unnecessary:

```text
Niri
→ spawned script
→ Ominty
→ Niri IPC
```

for high-frequency compositor operations.

---

# 11. Existing Niri Configuration

Before changing Niri:

* locate active config;
* inspect existing bindings;
* create a binding audit;
* preserve unrelated config;
* create backup;
* validate generated changes.

Do not overwrite the entire configuration by default.

---

# 12. Quickshell Rules

Quickshell already exists.

Do not reinstall or replace it unnecessarily.

Custom Ominty Quickshell components should be focused and isolated.

Do not build a full shell from scratch unless DMS proves unsuitable.

---

# 13. DMS Rules

DankMaterialShell is the preferred Phase 1 shell candidate, but its adoption remains subject to practical validation.

For each capability classify:

```text
USE DMS
EXTEND DMS
OMINTY COMPONENT
DEFER
```

Prefer stable documented DMS interfaces.

Do not fork DMS merely for convenience.

---

# 14. Avoid Duplicate Desktop Components

Do not introduce competing:

* bars;
* notification daemons;
* OSD systems;
* launchers;
* power menus;
* wallpaper engines;

without a documented reason.

Integration is preferred to duplication.

---

# 15. Theme Rules

The intended theme model is:

```text
Wallpaper
   ↓
Palette
   ↓
Canonical Ominty colours
   ↓
Theme adapters
   ↓
Shell + applications
```

Prefer existing DMS/Matugen capability before writing a parallel theme engine.

Preserve application configuration.

Prefer generated theme fragments/includes over rewriting entire config files.

---

# 16. AI Rules

AI is a first-class interaction surface.

Initial namespace:

```text
Super+A
```

AI should use registered Ominty capabilities for routine desktop actions where practical.

Example:

```text
app.browser.open
```

is preferable to an agent independently launching an arbitrary browser command.

---

# 17. AI Must Respect Registry Policy

An AI-facing implementation MUST respect:

```text
ai_accessible
risk
confirmation
contexts
availability
```

Do not bypass these fields merely because the underlying shell command is known.

---

# 18. AI Recursion

Actions that invoke AI should normally use:

```text
ai_accessible = false
```

unless explicit orchestration requires otherwise.

Avoid accidental recursive tool invocation.

---

# 19. No Fake Context

For context-dependent actions:

```text
ai.selection.explain
```

do not provide stale or guessed context.

If reliable context is unavailable, return:

```text
CONTEXT_UNAVAILABLE
```

or mark the feature deferred.

---

# 20. Platform Rules

LMDE-specific implementation belongs under:

```text
adapters/debian/
```

where practical.

Portable implementations belong in:

```text
adapters/common/
```

Niri-specific implementation belongs in:

```text
adapters/niri/
```

DMS-specific implementation belongs in:

```text
adapters/dms/
```

Future Void implementation belongs in:

```text
adapters/void/
```

but Phase 1 does not need to implement it.

---

# 21. Avoid Distribution Leakage

Portable code should not casually invoke:

```text
apt
apt-get
dpkg
systemctl
```

If required, ensure the code belongs at the appropriate platform boundary.

Remember that the eventual Void system will use a different package manager and init/service system.

---

# 22. XDG Paths

Prefer:

```text
$XDG_CONFIG_HOME
$XDG_CACHE_HOME
$XDG_DATA_HOME
```

with sensible fallbacks.

Do not hard-code personal home paths in portable code.

---

# 23. Generated Files

Generated files must be clearly marked.

Do not manually edit generated files unless debugging.

Fix the source or generator instead.

Generated data must never become the undocumented source of truth.

---

# 24. User Overrides

Do not require users to modify core project action files for routine preferences.

Use override layers where defined.

User configuration must survive project upgrades.

---

# 25. Error Handling

Actions should fail explicitly.

Prefer stable errors such as:

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

Do not silently ignore failures.

---

# 26. Implementation Strategy

Follow the implementation plan in:

```text
docs/10-phase-1-implementation-plan.md
```

Do not attempt to implement the entire architecture simultaneously.

Prove one layer before expanding it.

---

# 27. Start With Audit, Not Code

The first implementation task is environment discovery.

Create:

```text
docs/implementation/environment-audit.md
```

before significant configuration modification.

---

# 28. Required Implementation Records

Maintain:

```text
docs/implementation/
├── environment-audit.md
├── niri-binding-audit.md
├── dms-evaluation.md
└── void-portability-review.md
```

Add additional implementation notes when useful.

---

# 29. Tests

Follow:

```text
docs/11-testing-and-validation.md
```

Do not activate invalid generated configuration.

Run automated tests where practical and document manual desktop tests.

---

# 30. Rollback

Before significant Niri, Quickshell or DMS configuration changes:

* create recoverable backup;
* know how to restore it;
* avoid destructive replacement.

At least one rollback path must be tested during Phase 1.

---

# 31. Git Discipline

Keep commits focused.

Prefer changes that represent one coherent step.

Examples:

```text
Add registry loader
Add registry validation
Add application role adapter
Add Niri native action generator
```

Avoid large mixed commits combining unrelated architecture, shell and theme changes.

---

# 32. Do Not Commit Secrets

Never commit:

* API keys;
* tokens;
* credentials;
* private certificates;
* personal secrets.

Use appropriate external secret handling.

---

# 33. Do Not Commit Personal Machine State

Avoid committing:

* personal absolute paths;
* transient caches;
* generated runtime state;
* irrelevant user data.

Machine profiles must remain reusable or clearly scoped.

---

# 34. Dependency Policy

Before adding a dependency, determine:

1. Is it already available in the current environment?
2. Does an existing dependency already provide the capability?
3. Is it portable to Void?
4. Is it maintained?
5. Does its benefit justify project complexity?

Do not add libraries for trivial functionality that can be implemented clearly without them.

---

# 35. Simplicity Rule

Do not build:

* daemon;
* event bus;
* DBus service;
* plugin marketplace;
* complex policy engine;
* distributed orchestrator;

during Phase 1 unless a current requirement cannot reasonably be met without it.

Architectural possibility is not implementation requirement.

---

# 36. Performance Rule

High-frequency desktop actions must remain responsive.

Do not add unnecessary process hops to:

* focus;
* move;
* close;
* workspace navigation.

Prefer native compositor execution.

---

# 37. Public-Project Mindset

Implement as though the project may later be published.

Code and configuration should therefore be:

* readable;
* documented;
* reproducible;
* configurable;
* free of unexplained local assumptions.

---

# 38. Definition of Done

Use:

```text
docs/13-phase-1-definition-of-done.md
```

as the authoritative completion checklist.

Do not declare Phase 1 complete based solely on visual appearance or partial functionality.

---

# 39. Deferred Features

The following are intentionally deferred unless required to unblock Phase 1:

```text
Ominty daemon
event bus
remote action routing
full Herdr orchestration
Agno integration
voice
complex permissions engine
remote fleet management
Void installer
kernel hardening implementation
full application theme coverage
graphical action editor
```

Do not implement them opportunistically.

---

# 40. When to Stop and Report

Stop the current implementation path and report the issue when:

* architecture and implementation materially conflict;
* existing user data/config risks being lost;
* a requested operation is destructive and undocumented;
* Niri cannot be validated safely;
* a dependency requires a major architectural change;
* DMS would require substantial forking;
* an AI capability would require bypassing declared policy;
* a platform abstraction clearly fails.

Provide:

1. problem;
2. evidence;
3. impact;
4. recommended options.

---

# 41. When You May Decide Independently

You may make normal engineering decisions that do not alter architecture.

Examples:

* function names;
* module layout within defined boundaries;
* test framework;
* parsing library;
* logging details;
* internal helper functions;
* formatting;
* safe implementation details.

Do not escalate trivial implementation choices.

---

# 42. Architectural Decision Test

Before making a substantial decision ask:

> Does this change what Ominty is, what owns a capability, how users interact with it, or a boundary between components?

If yes, it is probably an architectural decision and should be documented.

---

# 43. Final Guiding Principle

The project should evolve according to:

```text
Specifications
      ↓
small implementation
      ↓
validation
      ↓
evidence
      ↓
refinement
```

not:

```text
agent preference
      ↓
large implementation
      ↓
architecture after the fact
```

The implementation agent's job is to make the Ominty design concrete while protecting the architectural intent that makes the project coherent.
