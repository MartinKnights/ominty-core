# Omivoid Remote Delegation Specification

**Project:** `omivoid-lmde`
**Subsystem:** AI
**Document:** 08
**Status:** Future Architecture / Post-Core Phase 1

---

# 1. Purpose

This document defines the architectural requirements for delegating work from an Omivoid laptop to other computing resources.

The objective is to allow the laptop to remain lightweight while using more capable infrastructure when appropriate.

---

# 2. Principle

> **The laptop should coordinate heavy work rather than being required to perform all heavy work itself.**

---

# 3. Intended Topology

```text
                  Omivoid Laptop
                        │
                       Pi
                        │
                      Herdr
                        │
                    Tailscale
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
        Main Desktop           IBIS Server
             │                     │
       Heavy Compute              Agno
```

Additional workers may be added later.

---

# 4. Layer Separation

Remote delegation consists of separate concerns:

```text
User Intent
    ↓
Delegation
    ↓
Routing
    ↓
Transport
    ↓
Remote Worker
    ↓
Execution
```

These layers must not be collapsed into a collection of SSH scripts.

---

# 5. Delegation

Delegation describes:

```text
what should be done
```

not:

```text
which shell command to run on which IP address
```

---

# 6. Routing

Routing determines which worker is appropriate.

Possible factors:

```text
capability
availability
project
compute
GPU
privacy
location
cost
```

Automatic intelligent routing is not required initially.

---

# 7. Transport

Tailscale may provide secure connectivity.

Other transport mechanisms may exist underneath specific workers.

Transport should remain below the delegation API.

---

# 8. Worker

A worker performs delegated work.

A worker may be:

* desktop machine;
* server;
* VM;
* container;
* agent runtime;
* Agno agent;
* future specialised system.

---

# 9. Worker Identity

Workers should eventually have stable logical identities.

Example:

```text
desktop-primary
ibis-office
```

Avoid making IP addresses canonical worker identities.

---

# 10. Worker Capabilities

Workers should advertise or be configured with capabilities.

Example:

```toml
[worker.desktop-primary]
capabilities = [
    "gpu",
    "coding",
    "large-model",
    "build"
]
```

Exact configuration belongs to later implementation.

---

# 11. Machine Role

A machine role is more meaningful than a hostname alone.

Examples:

```text
interactive-laptop
heavy-desktop
agent-server
```

Routing may use these roles.

---

# 12. Task Package

A remote task should conceptually contain:

```text
task
project identity
context
requirements
constraints
expected output
```

---

# 13. Project Identity

Do not assume identical paths across machines.

Bad:

```text
/home/martin/projects/foo
```

as universal project identity.

Preferred:

```text
project = foo
```

with environment-specific path resolution.

---

# 14. Context Transfer

Only required context should move.

Possible methods:

```text
repository
selected files
artifact package
shared storage
structured task context
```

The mechanism should match the task.

---

# 15. Source Control

Git may become an important mechanism for development delegation.

Example future flow:

```text
local project
    ↓
known revision
    ↓
remote worker
    ↓
changes
    ↓
patch/branch
```

Do not require this for every type of project.

---

# 16. Non-Code Projects

Writing and research projects may use:

* selected documents;
* structured project context;
* notes;
* source bundles.

Remote delegation must not assume everything is source code.

---

# 17. Result Contract

Results should ideally be structured.

Example:

```json
{
  "status": "completed",
  "summary": "Tests completed successfully.",
  "artifacts": [],
  "changes": []
}
```

---

# 18. Artifacts

Remote work may produce:

* documents;
* patches;
* reports;
* datasets;
* generated files.

Artifacts should return through a controlled mechanism.

---

# 19. Do Not Automatically Apply Changes

Remote code changes should not automatically overwrite the user's working tree unless the workflow explicitly permits it.

Prefer:

```text
result
 ↓
review
 ↓
apply
```

---

# 20. Remote Execution Risk

Remote delegation expands the security boundary.

Risk includes:

* data leaving laptop;
* remote command execution;
* compromised worker;
* stale project state;
* conflicting modifications;
* credential exposure.

Security policy must govern delegation.

---

# 21. Authentication

Authentication belongs to the transport/orchestration infrastructure.

AI prompts must never contain credentials merely to allow remote execution.

---

# 22. Tailscale Role

Tailscale provides network connectivity and identity capabilities.

It should not become:

* task queue;
* project registry;
* AI provider;
* worker scheduler.

---

# 23. Offline Worker

If a requested worker is offline, delegation should return a clear state.

Do not silently reroute sensitive work without policy.

---

# 24. Explicit Routing

Initial implementation may use explicit worker selection.

Example:

```text
Delegate to:
  Main Desktop
  IBIS Server
```

Automatic routing can come later.

---

# 25. Future Automatic Routing

Future Herdr routing may choose based on:

```text
task → requirements → worker capability → policy → availability
```

This is not required for this phase.

---

# 26. Long-Running Tasks

Remote delegation is particularly useful for:

* model inference;
* builds;
* test suites;
* research;
* indexing;
* data processing;
* agent workflows.

These tasks may continue after the initiating UI closes.

---

# 27. Task Persistence

Persistent remote tasks should be owned by the orchestration layer rather than DMS.

DMS may display their status.

---

# 28. Notification

When a delegated task completes, Omivoid may use DMS notification:

```text
Omivoid
Research task completed.
```

---

# 29. Result Re-entry

Results should return into the user's current workflow.

Examples:

```text
open report
review patch
continue Pi conversation
attach result to project
```

---

# 30. Cancellation

Where Herdr/worker support exists, the user should be able to request cancellation.

Cancellation must not be falsely reported as successful if the remote worker cannot guarantee it.

---

# 31. Network Failure

Network failure should distinguish:

```text
task submission failed
task status unknown
worker unavailable
result retrieval failed
```

These are not equivalent.

---

# 32. Observability

The user should eventually be able to inspect:

```text
task
worker
submitted time
state
result
```

without inspecting transport logs.

---

# 33. Logging

Remote delegation logs should avoid unnecessary task content.

Operational metadata may include:

```text
task ID
worker
state
timestamps
error
```

---

# 34. Phase Scope

This document defines the future boundary.

The current AI phase does NOT require production remote delegation.

Implementation should occur only after:

```text
Pi
 ↓
local context
 ↓
local capabilities
```

is stable.

---

# 35. First Future Proof

A suitable first remote proof would be deliberately simple:

```text
Laptop:
"Run project tests on the desktop."

       ↓

Pi
       ↓
Herdr
       ↓
desktop worker
       ↓
tests
       ↓
structured result
       ↓
Laptop
```

No automatic file modification should be required.

---

# 36. Guiding Principle

> **Remote compute should feel like an Omivoid capability, not like manually administering another computer.**

The orchestration layer hides topology while preserving user control.
