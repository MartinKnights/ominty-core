# ADR-004 — Separation of Intent and Implementation

**Status:** Accepted
**Project:** `omivoid-lmde`
**Phase:** Phase 1

---

# 1. Context

Omivoid is intended to operate first on LMDE and later on Void Linux.

The desktop also depends on replaceable components such as:

* Niri;
* DMS;
* NetworkManager;
* PipeWire;
* Matugen;
* AI providers.

If canonical desktop actions directly contain implementation commands, changes to the underlying system would propagate throughout:

* keybindings;
* scripts;
* AI tools;
* documentation;
* command palette;
* automation.

---

# 2. Decision

> **Omivoid separates user intent from implementation through adapters.**

The Action Registry defines what should happen.

Adapters define how it happens.

---

# 3. Example

Canonical intent:

```text
network.wifi.toggle
```

Possible implementation:

```text
NetworkManager
      ↓
nmcli
```

The action itself does not become:

```text
nmcli radio wifi ...
```

---

# 4. Architecture

```text
User Intent
    │
    ▼
Canonical Action
    │
    ▼
Action Resolver
    │
    ▼
Adapter
    │
    ▼
Implementation
```

Example:

```text
"Open Bluetooth controls"
          │
          ▼
network.bluetooth.open
          │
          ▼
DMS adapter
          │
          ▼
DMS Bluetooth panel
```

---

# 5. Adapter Categories

Initial adapter categories include:

```text
common
niri
dms
debian
void
ai
```

Potential future categories may include:

```text
machine
application
remote
```

New categories should be introduced only when they represent a meaningful implementation boundary.

---

# 6. Common Adapter

Portable implementations belong in:

```text
adapters/common/
```

This should be preferred when the same implementation works on LMDE and Void.

---

# 7. Platform Adapters

Distribution-specific behaviour belongs in:

```text
adapters/debian/
```

or:

```text
adapters/void/
```

Examples include:

* package management;
* init/service management;
* distribution-specific paths.

---

# 8. Component Adapters

Component-specific behaviour belongs with the component adapter.

Examples:

```text
window.close
    → Niri

theme.wallpaper.select
    → DMS

ai.ask
    → configured AI provider
```

---

# 9. Application Roles

Application roles are another form of intent separation.

Correct:

```text
app.browser.open
      ↓
role: browser
      ↓
configured application
```

Incorrect:

```text
app.firefox.open
```

for a generic browser action.

Specific application actions may exist when the application itself is the intended target, but generic user roles should remain generic.

---

# 10. Native Execution Exception

Intent/adapter separation does not mean every action must launch an adapter process.

For native Niri operations:

```text
window.focus.left
```

may compile directly into Niri configuration.

The generated binding itself is the implementation adapter.

The architectural separation remains intact because the Action Registry does not depend on Niri syntax as its canonical representation.

---

# 11. Why This Matters for Void

LMDE may implement:

```text
service.restart
```

using systemd.

Void may implement the same intent using runit.

The higher layers remain unchanged.

```text
service.restart
       │
   ┌───┴───┐
   ▼       ▼
systemd   runit
```

---

# 12. Why This Matters for AI

AI should reason about:

```text
session.lock
theme.wallpaper.select
app.browser.open
```

rather than:

```text
loginctl ...
matugen ...
firefox ...
```

This gives AI a smaller and more stable capability vocabulary.

---

# 13. Why This Matters for Security

Adapters create a control boundary.

An action can declare:

```text
risk
confirmation
AI accessibility
context
```

before implementation is invoked.

This is much harder to govern if agents simply construct arbitrary shell commands for routine system actions.

---

# 14. Why This Matters for Testing

Adapters allow intent to be tested independently from implementation.

For example:

```text
app.browser.open
```

can be tested for:

* correct registry metadata;
* correct role resolution;
* correct adapter selection;

without requiring every test to know which browser executable is configured.

---

# 15. Adapter Interface

Phase 1 should keep the adapter interface simple.

An adapter needs enough information to:

* identify the action;
* receive arguments;
* perform the operation;
* return success/failure;
* optionally return state.

Avoid designing a complex plugin protocol before practical requirements exist.

---

# 16. Adapter Result

Preferred conceptual result:

```json
{
  "success": true,
  "state": {}
}
```

Failure:

```json
{
  "success": false,
  "error": {
    "code": "ADAPTER_FAILED",
    "message": "..."
  }
}
```

Implementation language may vary.

---

# 17. Raw Commands

Core actions should avoid raw commands when a meaningful adapter exists.

User-defined:

```text
custom.*
```

actions may use a generic command adapter.

This preserves flexibility without weakening the canonical core.

---

# 18. No Adapter for Adapter's Sake

Do not wrap a stable standard interface merely to satisfy architectural aesthetics.

If an operation can safely use a common standard interface directly, a thin common adapter is sufficient.

The goal is replaceability and clarity, not maximum indirection.

---

# 19. Consequences

## Positive

This decision provides:

* LMDE/Void portability;
* provider replacement;
* cleaner AI capabilities;
* easier testing;
* clearer security boundaries;
* less duplicated implementation knowledge.

## Negative

Adapter resolution introduces additional code.

Debugging may occasionally require inspecting both action and adapter.

These costs are accepted.

---

# 20. Rejected Alternative — Commands in Registry

Example:

```toml
command = ["nmcli", "..."]
```

for every core action.

This is simple initially but couples the registry to current implementation details.

Rejected for core actions.

---

# 21. Rejected Alternative — Distribution-Specific Actions

Examples:

```text
debian.package.install
void.package.install
```

would expose platform differences to users and AI.

Rejected except where the platform itself is genuinely the subject of the action.

---

# 22. Revisit Conditions

This decision should only be reconsidered if adapter abstraction demonstrably causes more complexity than it removes across actual supported platforms.

Individual actions may bypass generic runtime adapters for performance reasons without invalidating the architectural separation.

---

# 23. Result

The defining rule is:

> **Stable intent above; replaceable implementation below.**

This is the primary mechanism by which Omivoid remains portable and maintainable.
