# Ominty AI Phase 1 Implementation Plan

**Project:** `ominty-core`
**Subsystem:** AI
**Document:** 10
**Status:** Implementation Plan

---

# 1. Purpose

This document defines the implementation sequence for the first Ominty AI milestone.

The objective is to prove the architecture with the smallest useful implementation before introducing distributed orchestration or advanced AI workflows.

---

# 2. Implementation Principle

The implementation order is:

```text
audit
 ↓
provider
 ↓
Pi
 ↓
context
 ↓
capabilities
 ↓
AI-to-action
 ↓
Super+A
 ↓
project context
 ↓
security validation
 ↓
Herdr readiness
```

Do not begin with remote orchestration.

---

# 3. Required Reading

Before implementation, read:

```text
docs/09-ai-integration.md

docs/ai/00-ai-architecture.md
docs/ai/01-provider-interface.md
docs/ai/02-pi-integration.md
docs/ai/03-super-a-interaction.md
docs/ai/04-ai-action-capabilities.md
docs/ai/05-context-system.md
docs/ai/06-project-context.md
docs/ai/07-herdr-integration.md
docs/ai/08-remote-delegation.md
docs/ai/09-ai-security-policy.md

docs/03-action-registry-spec.md
docs/04-phase-1-action-catalogue.md
docs/07-dms-integration.md

docs/decisions/ADR-003-action-registry-source-of-truth.md
docs/decisions/ADR-004-intent-adapter-separation.md
docs/decisions/ADR-006-dms-plugin-first-integration.md
```

`AGENTS.md` remains authoritative for implementation-agent behaviour.

---

# 4. Stage AI-0 — Environment Audit

Do not modify AI configuration yet.

Inspect:

```text
Pi installed?
Pi version
Pi executable
Pi configuration
Pi extension mechanism
Pi tool mechanism
Pi session behaviour
Pi structured invocation options
Pi streaming support
configured models/providers
DMS AI-related plugins
existing AI shortcuts
existing project AI configuration
```

Create:

```text
docs/implementation/ai-environment-audit.md
```

---

# 5. Audit Rule

The implementation must be based on the actual installed/current Pi interface.

Do not implement from assumptions in these specifications where Pi's real capabilities differ.

Document the discrepancy first.

---

# 6. Stage AI-1 — Provider Structure

Create the minimum provider abstraction.

Suggested logical structure:

```text
ai/
├── providers/
│   └── pi/
├── context/
├── capabilities/
└── policy/
```

Adapt to the actual repository language/layout.

---

# 7. Stage AI-2 — Provider Status

Implement provider availability detection.

Target conceptual behaviour:

```bash
ominty ai provider status pi
```

It should distinguish:

```text
available
unavailable
misconfigured
```

where practical.

---

# 8. Stage AI-3 — Pi Interactive Open

Implement:

```text
ai.pi.open
```

through the Action Registry.

Expected:

```text
Ominty
 ↓
configured terminal
 ↓
Pi
```

Do not bypass the registry with a standalone unrelated shortcut.

---

# 9. Stage AI-4 — Generic Ask

Implement generic:

```text
ai.ask
```

with provider resolution.

Configuration:

```toml
[ai]
default_provider = "pi"
```

The generic action must not hard-code Pi semantics.

---

# 10. Stage AI-5 — CLI Ask Proof

Prove:

```bash
ominty ai ask "..."
```

before implementing the full graphical AI interaction.

Success requires:

```text
CLI
 ↓
provider resolver
 ↓
Pi adapter
 ↓
Pi
 ↓
response
```

---

# 11. Stage AI-6 — Provider Error Handling

Implement stable provider errors required by the actual integration.

At minimum consider:

```text
PROVIDER_NOT_FOUND
PROVIDER_UNAVAILABLE
PROVIDER_FAILED
PROVIDER_TIMEOUT
```

Do not create unused error complexity.

---

# 12. Stage AI-7 — Explicit Text Context

Implement the simplest context case:

```text
explicit user text
```

This establishes the context envelope/provider conversion architecture.

---

# 13. Stage AI-8 — File Context

Implement bounded file context.

Prove a request equivalent to:

```bash
ominty ai ask --file docs/00-project-overview.md \
  "Summarise the architectural goals."
```

Exact syntax may differ.

---

# 14. File Safety

Before sending file context:

* confirm file exists;
* identify obvious binary content;
* enforce basic size limits;
* avoid known secret material in automatic collection.

---

# 15. Stage AI-9 — Capability Catalogue

Generate an AI capability view from Action Registry metadata.

Initial filtering:

```text
ai_accessible
platform
availability
risk
```

Machine-readable output is required for provider integration.

---

# 16. Stage AI-10 — Initial Capabilities

Expose only a small set.

Recommended:

```text
app.browser.open
app.terminal.open
app.editor.open
help.keys.open
help.actions.search
```

Adjust to actual registry IDs if the implemented catalogue differs.

Do not invent duplicate actions.

---

# 17. Stage AI-11 — Pi Tool Bridge

Map the filtered Ominty capabilities into Pi's actual tool/extension mechanism.

Keep Pi-specific translation inside the Pi adapter/integration.

---

# 18. Stage AI-12 — First AI-to-Action Proof

Required architecture proof:

```text
User:
"Open my browser."

        ↓
Pi
        ↓
app.browser.open
        ↓
Ominty policy
        ↓
Action runner
        ↓
application role
        ↓
browser
```

Pi must not require knowledge of the configured browser executable.

---

# 19. Stage AI-13 — Action Result Return

Return structured action success/failure to Pi.

Test:

```text
success
unavailable
unknown
denied
invalid argument
```

---

# 20. Stage AI-14 — Policy Enforcement

Implement the minimum AI policy needed for the exposed capability set.

Respect:

```text
ai_accessible
risk
confirmation
```

Do not expose privileged/destructive actions merely to test policy.

---

# 21. Stage AI-15 — Confirmation Proof

Select one harmless state-changing test action where appropriate.

Prove:

```text
Pi requests action
       ↓
confirmation required
       ↓
user approves/denies
       ↓
correct result
```

Do not use a destructive action for this proof.

---

# 22. Stage AI-16 — Recursive Action Protection

Ensure AI cannot accidentally invoke recursive AI actions such as:

```text
ai.ask
```

unless explicitly designed.

---

# 23. Stage AI-17 — DMS AI Evaluation

Before building custom AI UI, inspect:

```text
DMS core
installed DMS plugins
AI Assistant plugin if relevant
launcher provider capabilities
plugin API
```

Classify according to ADR-006:

```text
ADOPT
ADOPT WITH CONFIGURATION
EXTEND
REFERENCE ONLY
DEFER
REJECT
```

Record the decision.

---

# 24. Stage AI-18 — `Super+A`

Implement the AI prefix through the chosen DMS/Niri mechanism.

Minimum target:

```text
Super+A
```

opens discoverable AI actions.

---

# 25. Stage AI-19 — `Super+A,A`

Connect:

```text
Super+A,A
```

to:

```text
ai.ask
```

through the same provider architecture proven by CLI.

Do not create a second AI invocation path.

---

# 26. Stage AI-20 — `Super+A,P`

Connect:

```text
Super+A,P
```

to:

```text
ai.pi.open
```

---

# 27. Stage AI-21 — Context Indicator

The DMS AI presentation should show significant supplied context.

Minimum useful examples:

```text
File: ...
Project: ...
Clipboard
Selection
```

only for context types actually implemented.

---

# 28. Stage AI-22 — Clipboard Context

If useful, implement explicit clipboard context.

Do not confuse it with selection.

---

# 29. Stage AI-23 — Selection Investigation

Investigate reliable selection acquisition in the actual:

```text
LMDE
Niri
Wayland
DMS
```

environment.

Create implementation notes documenting tested mechanisms.

---

# 30. Stage AI-24 — Selection Decision

Classify selection support:

```text
IMPLEMENT
IMPLEMENT WITH LIMITATIONS
CLIPBOARD FALLBACK
DEFER
```

Do not fake successful selection acquisition.

---

# 31. Stage AI-25 — Explain/Summarise

If reliable context exists, implement:

```text
Super+A,E
Super+A,S
```

using:

```text
ai.selection.explain
ai.selection.summarise
```

or accurately named clipboard alternatives where necessary.

---

# 32. Stage AI-26 — Project Discovery

Implement minimum project identification.

Prefer simple existing signals:

```text
explicit root
Git root
AGENTS.md
```

Avoid building a project database at this stage.

---

# 33. Stage AI-27 — Project Context

Implement:

```text
project identity
project root
AGENTS.md discovery
bounded structure
```

Prove one project-aware Pi request.

---

# 34. Stage AI-28 — Project Security

Ensure project context does not automatically ingest:

```text
private keys
credentials
obvious secret files
```

Test boundary behaviour.

---

# 35. Stage AI-29 — Security Validation

Run the tests from:

```text
09-ai-security-policy.md
```

including:

```text
allowed action
denied action
unknown action
invalid argument
confirmation
secret exclusion
provider unavailable
```

---

# 36. Stage AI-30 — Failure Isolation

Test Pi failure.

Verify:

```text
Niri works
DMS works
Super+K works
Super+Space works
non-AI Ominty actions work
```

---

# 37. Stage AI-31 — Restart Validation

Test:

```text
logout/login
clean session startup
reboot where appropriate
```

Ensure AI integration does not introduce fragile startup dependencies.

---

# 38. Stage AI-32 — Performance Review

Check:

```text
Super+A opening latency
provider startup latency
action-tool latency
DMS responsiveness
memory overhead
```

Do not introduce persistent processes without justification.

---

# 39. Stage AI-33 — Herdr Readiness Audit

Do not implement full Herdr orchestration yet.

Instead inspect/document the actual Herdr integration surface.

Create:

```text
docs/implementation/herdr-readiness-review.md
```

Cover:

```text
interface
task model
workers
authentication
transport
results
lifecycle
```

---

# 40. Stage AI-34 — Remote Delegation Readiness

Document how the current infrastructure could support later delegation.

Include:

```text
logical worker roles
Tailscale availability
project identity concerns
security concerns
```

Do not hard-code network addresses into Pi.

---

# 41. Stage AI-35 — Documentation Reconciliation

Update specifications where actual implementation revealed incorrect assumptions.

Architecture changes require explicit documentation rather than silent divergence.

---

# 42. Required Implementation Records

By completion, the implementation directory should include:

```text
docs/implementation/
├── ai-environment-audit.md
├── ai-dms-evaluation.md
├── ai-context-evaluation.md
├── ai-security-validation.md
├── herdr-readiness-review.md
└── ai-phase-1-validation.md
```

Names may be adjusted consistently if existing implementation documentation conventions differ.

---

# 43. Phase 1 Required Features

The AI phase requires:

```text
provider abstraction
Pi availability
Pi interactive open
generic ai.ask
CLI AI invocation
explicit/file context
registry-derived capability catalogue
Pi capability bridge
one AI-to-action proof
AI policy enforcement
Super+A
project context proof
security validation
```

---

# 44. Desirable But Non-Blocking

Desirable:

```text
streaming DMS responses
selection context
clipboard context
context chips
additional routine capabilities
```

These should not block completion if the underlying platform makes them disproportionately complex.

---

# 45. Explicitly Deferred

Do not implement during this milestone:

```text
full Herdr orchestration
remote execution
Agno integration
automatic worker routing
voice
autonomous background agents
AI daemon
provider marketplace
model router
large memory framework
unattended privileged actions
unattended destructive actions
```

---

# 46. Implementation Order Summary

```text
AI-0   Audit
AI-1   Provider abstraction
AI-2   Provider status
AI-3   Pi open
AI-4   Generic ask
AI-5   CLI proof
AI-6   Errors
AI-7   Text context
AI-8   File context
AI-9   Capability catalogue
AI-10  Initial capabilities
AI-11  Pi tool bridge
AI-12  AI → Action proof
AI-13  Results
AI-14  Policy
AI-15  Confirmation
AI-16  Recursion protection
AI-17  DMS evaluation
AI-18  Super+A
AI-19  Ask
AI-20  Pi
AI-21  Context indicators
AI-22  Clipboard
AI-23  Selection investigation
AI-24  Selection decision
AI-25  Explain/Summarise
AI-26  Project discovery
AI-27  Project context
AI-28  Project security
AI-29  Security validation
AI-30  Failure isolation
AI-31  Restart
AI-32  Performance
AI-33  Herdr readiness
AI-34  Remote readiness
AI-35  Reconcile documentation
```

---

# 47. Stop Conditions

The implementation agent should stop and report rather than improvise architecture if:

* Pi's actual integration model fundamentally conflicts with the provider specification;
* DMS cannot support the expected AI interaction without significant architectural changes;
* Action Registry changes would break existing contracts;
* safe capability invocation cannot be achieved;
* project context requires broad uncontrolled filesystem access;
* implementation appears to require a persistent daemon contrary to current design;
* Herdr's actual architecture materially differs from assumptions in this specification.

---

# 48. Definition of Done

The first Ominty AI milestone is complete when:

```text
Super+A
   ↓
Ominty AI layer
   ↓
Pi
```

works as a normal user interaction;

and:

```text
Pi
 ↓
Ominty capability
 ↓
policy
 ↓
Action Registry
 ↓
desktop action
```

works safely;

and:

```text
Project
 ↓
bounded context
 ↓
Pi
```

has been demonstrated.

---

# 49. Architecture Review

Before proceeding to Herdr implementation, review whether the completed system still preserves:

```text
Pi
    = interactive intelligence

Ominty
    = context + capabilities + policy

DMS
    = presentation

Action Registry
    = canonical desktop intent

Herdr
    = future delegation

Tailscale
    = transport

Agno
    = larger server-side agent systems
```

If these boundaries have blurred significantly, resolve the architecture before adding distributed functionality.

---

# 50. Final Principle

> **First make AI genuinely native to one Ominty laptop. Then make Ominty capable of delegating beyond that laptop.**

Distributed complexity must follow a proven local architecture, not compensate for the absence of one.
