# ADR-005 — LMDE as the Phase 1 Validation Platform

**Status:** Accepted
**Project:** `omivoid-lmde`
**Phase:** Phase 1

---

# 1. Context

The long-term Omivoid target is Void Linux.

However, the current development machine is already running LMDE with:

* Niri installed;
* Quickshell installed;
* an operational Linux environment suitable for development and experimentation.

Moving immediately to Void would combine two major tasks:

1. designing the Omivoid desktop architecture;
2. establishing a new Void Linux platform.

This would make failures harder to diagnose and increase implementation complexity.

---

# 2. Decision

> **LMDE is the Phase 1 Omivoid validation and reference implementation platform.**

The initial Omivoid interaction architecture will be developed and proven on LMDE before the full Void implementation.

---

# 3. Purpose of Phase 1

Phase 1 is intended to answer architectural questions such as:

* Does the Action Registry work?
* Is the keyboard grammar effective?
* Does `Super+K` provide useful discoverability?
* Can the command palette consume registry actions?
* Does DMS provide an appropriate shell foundation?
* Can wallpaper-driven theming provide visual coherence?
* Can Pi participate naturally in the desktop?
* Can AI safely invoke Omivoid capabilities?
* Are the abstraction boundaries sufficient for Void?

These questions do not require Void Linux to answer.

---

# 4. LMDE Is Not a Throwaway Prototype

Although LMDE precedes the Void implementation, `omivoid-lmde` should be built as a usable implementation.

It may later become:

* a maintained Omivoid variant;
* a Debian-family reference implementation;
* a public GitHub project;
* a useful desktop configuration for other users.

Therefore quality and portability still matter.

---

# 5. Architecture Must Not Become Debian-Specific

LMDE provides the current operating environment.

It does not define Omivoid.

Core components should avoid unnecessary assumptions about:

* APT;
* systemd;
* Debian paths;
* LMDE package names.

Such details belong in the Debian platform adapter.

---

# 6. Existing Installation

The current machine already contains:

```text
LMDE
  │
  ├── Niri
  └── Quickshell
```

These should be treated as the Phase 1 starting point.

The implementation should not begin with:

* LMDE installation;
* Niri installation;
* Quickshell installation.

Instead it begins with:

```text
inspect
   ↓
document
   ↓
backup
   ↓
integrate
   ↓
validate
```

---

# 7. Incremental Development

Phase 1 should be developed incrementally.

Preferred sequence:

```text
existing working desktop
        ↓
small Omivoid integration
        ↓
test
        ↓
next capability
        ↓
test
```

Avoid large configuration replacements followed by debugging many failures simultaneously.

---

# 8. Void Migration

Once the interaction architecture is proven:

```text
Omivoid Core
       │
       ├── Action Registry
       ├── Interaction
       ├── Niri
       ├── DMS
       ├── Theme
       └── AI
              │
              ▼
       replace platform adapter
              │
              ▼
            Void
```

The Void implementation will additionally need to address:

* XBPS;
* runit;
* Void package availability;
* hardware setup;
* boot configuration;
* hardening;
* installation/reproducibility.

Those concerns should not block Phase 1 UX development.

---

# 9. Phase Boundary

The following belong primarily to Phase 1:

* action architecture;
* keyboard interaction;
* Niri integration;
* DMS evaluation;
* command palette;
* `Super+K`;
* application roles;
* basic AI namespace;
* dynamic theming;
* Debian adapter proof.

The following are principally later Void work:

* Void installation automation;
* XBPS-specific implementation;
* runit-specific implementation;
* Void boot configuration;
* Void kernel selection;
* final kernel hardening;
* production Void machine profiles.

Security-conscious design should still be maintained during Phase 1.

---

# 10. Platform Portability Test

Throughout Phase 1, implementation should periodically ask:

> What in this component would change on Void?

The answer should ideally be limited to:

* package installation;
* service management;
* platform-specific dependencies;
* machine-specific configuration.

If interaction semantics would need to change, the abstraction should be reviewed.

---

# 11. LMDE-Specific Features

An LMDE-specific feature may be implemented when useful.

It must be clearly identified as platform-specific.

Example structure:

```text
adapters/debian/
```

Do not disguise LMDE-specific behaviour as portable Omivoid core functionality.

---

# 12. Documentation Value

Using LMDE first also allows the project to document the distinction between:

```text
Omivoid core
```

and:

```text
Omivoid platform implementation
```

before the second platform exists.

This is useful because portability becomes a deliberate design requirement rather than a later refactoring exercise.

---

# 13. Consequences

## Positive

LMDE provides a working environment in which Omivoid concepts can be tested quickly.

It reduces the number of simultaneously changing variables.

Existing Niri and Quickshell installations accelerate experimentation.

The resulting project may also remain independently useful.

## Negative

Some Phase 1 implementation choices may prove Debian-specific despite attempts at abstraction.

The future Void port will test whether the abstraction boundaries were correct.

Some work may need refactoring.

This is accepted.

---

# 14. Rejected Alternative — Move to Void Immediately

Moving immediately to Void would combine:

* OS migration;
* compositor setup;
* shell setup;
* hardware configuration;
* security configuration;
* Omivoid architecture development.

This would make it difficult to distinguish platform failures from Omivoid design failures.

Rejected for Phase 1.

---

# 15. Rejected Alternative — Treat LMDE as Disposable

A disposable prototype encourages:

* hard-coded paths;
* undocumented dependencies;
* Debian leakage;
* temporary scripts becoming permanent.

That would weaken the value of Phase 1.

Rejected.

---

# 16. Exit Criteria

Phase 1 is ready to inform the Void implementation when the following have been demonstrated:

* Action Registry is operational;
* keybinding grammar is usable;
* Niri integration is stable;
* `Super+K` is functional;
* universal action search is functional;
* application roles work;
* DMS suitability is understood;
* wallpaper/theme integration works;
* AI namespace works;
* at least one AI→Omivoid capability path is proven;
* platform-specific behaviour is reasonably isolated;
* implementation and architecture are documented.

---

# 17. Result

LMDE is both:

> **the Phase 1 development platform**

and:

> **the first reference implementation of Omivoid.**

Void remains the eventual primary target, but the move to Void should happen after Omivoid's interaction architecture has been proven rather than while it is still being invented.
