# ADR-003 — Action Registry as the Source of Truth

**Status:** Accepted
**Project:** `ominty-core`
**Phase:** Phase 1

---

# 1. Context

Ominty exposes desktop capabilities through several interaction surfaces:

* keyboard;
* GUI;
* command palette;
* CLI;
* AI;
* future voice;
* future automation.

Without a canonical capability definition, each interface could develop its own representation of the same operation.

For example:

```text
Super+Shift+B
browser button
ominty app browser
AI "open browser"
```

could become four independently maintained implementations.

This would create configuration drift and inconsistent behaviour.

---

# 2. Decision

> **The Ominty Action Registry is the canonical source of truth for meaningful Ominty actions and their interaction metadata.**

Canonical action IDs form a stable internal API.

Example:

```text
app.browser.open
```

represents the user intent independently of how or where it is invoked.

---

# 3. Registry Authority

The Action Registry is authoritative for:

* action identity;
* name;
* description;
* category;
* discovery keywords;
* keybinding metadata;
* context requirements;
* risk;
* confirmation policy;
* platform applicability;
* AI accessibility;
* voice accessibility;
* adapter/backend identity.

---

# 4. Registry Is Not the Execution Backend

The registry defines intent.

It does not need to implement the action itself.

Example:

```text
window.close
```

is defined by the registry.

Execution may occur directly inside Niri.

Likewise:

```text
theme.wallpaper.select
```

may execute through DMS.

---

# 5. Generated Consumers

Where practical, registry data should generate or supply:

```text
Action Registry
      │
      ├── Niri bindings
      ├── Super+K
      ├── command palette
      ├── CLI
      ├── AI tools
      └── documentation metadata
```

This reduces duplication.

---

# 6. Single Definition Principle

An action should not need separate authoritative definitions for:

```text
keyboard
help
CLI
AI
palette
```

Each interface may require presentation-specific data, but action identity and semantics come from the registry.

---

# 7. Stable Action IDs

Action IDs should be treated as API identifiers.

Once an action is used publicly:

```text
app.browser.open
```

should not be renamed simply because:

* an executable changes;
* a DMS API changes;
* the distro changes;
* implementation is refactored.

Implementation changes occur behind the action contract.

---

# 8. Human-Readable TOML

The registry source will initially use TOML.

Reasons include:

* readability;
* easy manual editing;
* clear structure;
* Git-friendly diffs;
* straightforward parsing;
* suitability for declarative metadata.

Generated runtime formats may differ.

---

# 9. Generated Runtime State

The implementation may compile TOML into a runtime representation such as JSON.

Example:

```text
~/.cache/ominty/registry.json
```

This is generated state.

It must not become the authoritative source.

---

# 10. User Extensions

Users may define:

```text
custom.*
```

actions.

Example:

```text
custom.notes.daily
```

These participate in discovery and execution while remaining distinguishable from canonical Ominty actions.

---

# 11. Overrides

Users should be able to modify metadata such as:

* binding;
* visibility;
* application role;
* preference.

without copying the complete core action definition.

Canonical action identity remains stable.

---

# 12. Validation

Because the registry is authoritative, it must be validated.

At minimum detect:

* malformed TOML;
* duplicate IDs;
* invalid IDs;
* missing required metadata;
* binding conflicts;
* invalid risk levels;
* unknown adapters;
* unsupported schema versions.

An invalid registry should fail explicitly.

---

# 13. Native Niri Exception

Native Niri bindings do not invalidate this ADR.

For example:

```text
Action Registry
    window.focus.left
           │
           ▼
generated Niri binding
           │
           ▼
native execution
```

The registry still defines the interaction.

Niri executes it efficiently.

---

# 14. DMS Exception

DMS may provide graphical controls that were not generated directly from the registry.

This is acceptable.

However, when an operation is exposed as an Ominty action, its canonical identity should remain the same.

---

# 15. Consequences

## Positive

The registry provides:

* consistent semantics;
* self-documenting interaction;
* AI capability control;
* easier portability;
* reduced duplication;
* searchable functionality;
* predictable CLI;
* future automation support.

## Negative

The registry introduces an additional architectural layer.

Validation and generation tooling must be maintained.

Poor schema design could become restrictive.

These costs are accepted because the registry is central to Ominty's interaction goals.

---

# 16. Rejected Alternative — Niri Config as Source of Truth

Niri configuration cannot describe all Ominty actions because many actions are not compositor operations.

It also cannot naturally provide:

* AI permissions;
* context;
* risk;
* platform information;
* CLI semantics.

Rejected.

---

# 17. Rejected Alternative — DMS as Source of Truth

DMS is a presentation/shell implementation.

Making it authoritative would couple Ominty's action model to one shell.

Rejected.

---

# 18. Rejected Alternative — Separate Config Per Interface

Maintaining independent keyboard, CLI, help and AI definitions would inevitably create drift.

Rejected.

---

# 19. Revisit Conditions

The registry architecture should only be reconsidered if implementation demonstrates that:

* it creates substantial unavoidable latency;
* action semantics cannot be represented cleanly;
* another mechanism provides equivalent central authority more simply.

Changes to the registry schema do not invalidate this decision.

---

# 20. Result

The architectural flow is:

```text
                ACTION REGISTRY
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Keyboard        GUI          CLI
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
                      AI
```

The Action Registry is one of the defining architectural components of Ominty.
