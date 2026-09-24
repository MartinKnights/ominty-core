# Omivoid Herdr Integration Specification

**Project:** `omivoid-lmde`
**Subsystem:** AI
**Document:** 07
**Status:** Architectural Specification / Post-Core Phase 1

---

# 1. Purpose

This document defines the intended relationship between Omivoid and Herdr.

Herdr is introduced as a delegation and orchestration layer.

It is not intended to replace Pi as the primary interactive laptop AI.

The core distinction is:

> **Pi works with the user. Herdr coordinates work beyond the immediate Pi session.**

---

# 2. Architectural Position

```text
User
  │
  ▼
Omivoid
  │
  ▼
Pi
  │
  ▼
Delegation Request
  │
  ▼
Herdr
  │
  ├── local worker
  ├── desktop worker
  └── IBIS worker
```

---

# 3. Separation of Responsibilities

```text
Pi
────────────────────
conversation
reasoning
coding
writing
research
local tools
desktop capabilities
project interaction


Herdr
────────────────────
delegation
task routing
worker selection
task lifecycle
remote coordination
result collection
```

The exact Herdr feature set must be validated against its actual implementation before coding integration.

---

# 4. Do Not Duplicate Pi

Herdr should not become another general chat interface merely because it can interact with models.

Normal user interaction remains:

```text
User → Pi
```

rather than requiring:

```text
User → Herdr → Pi
```

for ordinary tasks.

---

# 5. Do Not Turn Pi Into Herdr

Likewise, Pi should not accumulate:

* remote worker discovery;
* distributed scheduling;
* machine routing;
* persistent remote job management;

if those responsibilities belong to Herdr.

---

# 6. Delegation Boundary

The principal integration should be:

```text
Pi
 ↓
structured delegation request
 ↓
Herdr
```

Pi should express what needs to be done rather than how to connect to a remote machine.

---

# 7. Canonical Action

Potential canonical action:

```text
ai.delegate
```

or, where project-specific:

```text
project.delegate
```

The final action vocabulary should avoid duplicate semantics.

---

# 8. Delegation Request

A delegation request should eventually contain structured information such as:

```json
{
  "task": "Run the full test suite and investigate failures.",
  "project": "omivoid-lmde",
  "requirements": {
    "capabilities": ["development", "testing"]
  },
  "constraints": {},
  "context": []
}
```

Exact schema should be developed from actual Herdr capabilities.

---

# 9. Intent Over Destination

Preferred:

```text
"This task requires heavy local inference."
```

Herdr resolves an appropriate worker.

Avoid requiring Pi to say:

```text
"SSH to 100.x.x.x and execute..."
```

Machine routing belongs below the delegation boundary.

---

# 10. Worker Capabilities

Future Herdr integration may describe workers by capability.

Examples:

```text
coding
large-model
GPU
research
browser
business-agent
build
test
```

This allows task routing by capability rather than hostname.

---

# 11. Infrastructure Independence

Pi should not need to know whether the eventual worker is:

* laptop;
* desktop;
* office server;
* container;
* VM;
* Agno agent.

That is orchestration information.

---

# 12. Tailscale

Tailscale provides secure network connectivity between relevant systems.

Herdr may use connectivity available through Tailscale.

However:

> **Tailscale is transport infrastructure, not the Omivoid delegation API.**

Pi should not normally manipulate Tailscale addressing as part of delegation.

---

# 13. IBIS Server

The IBIS server may host persistent agent infrastructure.

Herdr may eventually route suitable work there.

Conceptually:

```text
Omivoid Laptop
      ↓
     Herdr
      ↓
   Tailscale
      ↓
 IBIS Server
      ↓
    Agno
```

---

# 14. Desktop PC

The main desktop may be an appropriate target for compute-intensive local tasks.

Conceptually:

```text
Laptop
   ↓
Herdr
   ↓
Desktop worker
   ↓
heavy compute
```

The laptop remains the interactive planning surface.

---

# 15. Agno

Agno may provide persistent or specialised agent systems on server infrastructure.

Herdr should provide the orchestration boundary where practical rather than coupling Pi directly to every Agno agent.

---

# 16. Task Lifecycle

Future delegation may use states such as:

```text
created
queued
assigned
running
waiting
completed
failed
cancelled
```

Do not implement a parallel Omivoid task engine if Herdr already provides suitable lifecycle management.

---

# 17. Result Return

Delegated results should return through the orchestration boundary.

```text
worker
  ↓
Herdr
  ↓
Omivoid/Pi
  ↓
User
```

Results may include:

* text;
* files;
* patch;
* report;
* status;
* structured output.

---

# 18. User Visibility

Delegation should not disappear into an invisible remote process.

The user should eventually be able to determine:

```text
what was delegated
where it is running
current state
result
```

---

# 19. Confirmation

Delegation may require confirmation depending on:

* destination;
* task;
* data being transferred;
* cost;
* capability;
* security classification.

The AI must not silently send sensitive project material remotely.

---

# 20. Context Transfer

Delegation should transfer only required context.

Preferred:

```text
task
+
required files
+
relevant instructions
```

not:

```text
entire home directory
```

---

# 21. Repository-Based Delegation

For software projects, a repository may eventually provide a cleaner remote context mechanism than copying arbitrary directories.

Possible future model:

```text
project identity
    ↓
repository/revision
    ↓
remote worker
```

This is outside the initial implementation.

---

# 22. Secrets

Secrets should not be included automatically in delegated context.

Remote workers requiring credentials should obtain them through authorised infrastructure-specific mechanisms.

---

# 23. Herdr Adapter

Omivoid should integrate Herdr behind a defined adapter.

Conceptually:

```text
ai/delegation/herdr/
```

Do not spread Herdr-specific commands throughout:

* DMS;
* Pi extensions;
* project actions.

---

# 24. Herdr Availability

Omivoid should be able to determine:

```text
Herdr available
Herdr unavailable
```

without making core AI dependent upon it.

---

# 25. Failure Isolation

If Herdr is unavailable:

```text
Pi local workflows
Omivoid actions
DMS
Niri
```

continue normally.

Only delegation is unavailable.

---

# 26. `Super+A,H`

`Super+A,H` may provide direct access to Herdr status/interface where useful.

This should not become the normal path for everyday AI conversation.

---

# 27. `Super+A,T`

The intended primary user-facing delegation command is:

```text
Super+A,T
```

which maps to the appropriate delegation action.

---

# 28. `Super+P,S`

A project-specific delegation shortcut may also be appropriate:

```text
Super+P,S
```

Both should resolve to shared delegation semantics rather than separate implementations.

---

# 29. DMS Presentation

DMS may eventually show:

```text
Delegated Tasks
───────────────
Build       running
Research    complete
Tests       failed
```

Do not build this until the underlying Herdr task model is understood.

---

# 30. Phase Boundary

Full Herdr integration is not required to prove the initial Pi AI architecture.

The initial requirement is to establish:

* architectural boundary;
* intended adapter location;
* delegation semantics;
* security boundary.

Implementation follows after local Pi integration is stable.

---

# 31. Validation Before Implementation

Before implementing Herdr integration, document:

```text
actual Herdr interface
task schema
worker model
transport requirements
authentication
result model
lifecycle
```

Do not design an adapter against assumptions.

---

# 32. Success Criterion

Herdr integration is successful when Omivoid can express:

> "Delegate this task"

without Pi needing to understand machine topology, transport details or remote execution commands.

---

# 33. Guiding Principle

```text
Pi understands the task.

Herdr understands where/how the task should run.

Omivoid understands the user's context and policy.
```

Keep these responsibilities separate.
