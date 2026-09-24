# Omivoid AI Security Policy

**Project:** `omivoid-lmde`
**Subsystem:** AI
**Document:** 09
**Status:** Phase 1 Security Specification

---

# 1. Purpose

This document defines security principles governing AI interaction with Omivoid.

AI introduces a new trust boundary because model-generated decisions may result in:

* commands;
* file access;
* system state changes;
* network activity;
* data transmission;
* remote delegation.

The objective is:

> **Give AI useful capabilities without making the AI provider an unrestricted authority over the desktop.**

---

# 2. Core Security Model

Preferred:

```text
AI
 │
 ▼
Declared Capability
 │
 ▼
Policy
 │
 ▼
Validated Arguments
 │
 ▼
Action Runner
 │
 ▼
Adapter
 │
 ▼
System
```

Avoid using:

```text
AI
 │
 ▼
unrestricted privileged shell
 │
 ▼
system
```

as the normal desktop control architecture.

---

# 3. AI Is Not a Trusted Authority

AI output is untrusted input.

This applies even when:

* the model runs locally;
* Pi runs locally;
* the provider is trusted;
* the user initiated the conversation.

AI-generated arguments and actions must still be validated.

---

# 4. Local Does Not Mean Trusted

A local model may:

* misunderstand;
* hallucinate;
* misinterpret context;
* follow malicious content;
* invoke an unintended tool.

Local execution improves some privacy properties but does not remove the need for capability controls.

---

# 5. Principle of Least Capability

AI should receive only capabilities necessary for useful interaction.

Do not expose the entire Action Registry merely because the provider supports tools.

---

# 6. Capability Eligibility

An action should only be exposed when:

```text
ai_accessible = true
```

and runtime policy allows it.

---

# 7. Risk Classes

Use the canonical registry risk vocabulary.

Conceptually:

```text
read
routine
state-change
privileged
destructive
critical
```

Risk should influence both exposure and confirmation.

---

# 8. Initial Policy

Phase 1 should favour:

```text
read
routine
```

capabilities.

Avoid privileged and destructive actions during the initial AI proof.

---

# 9. Confirmation

Actions may use:

```text
never
interactive
ai-only
always
```

AI invocation must respect these policies.

---

# 10. Confirmation Boundary

Confirmation is performed by Omivoid.

The AI provider cannot approve its own action.

---

# 11. Clear Confirmation

The user should know:

```text
who requested
what action
what arguments
what effect
```

before approving a significant operation.

---

# 12. Shell Access

Pi may legitimately require shell access for open-ended development work.

Shell access and Omivoid capability access are separate security surfaces.

Do not pretend the Action Registry alone creates a complete sandbox around Pi.

---

# 13. Privilege Escalation

AI should not automatically provide passwords or respond to privilege prompts on behalf of the user.

Privileged operations require explicit design and user involvement.

---

# 14. Root

AI should not routinely run as root.

Omivoid desktop AI integration must operate as the normal user unless a specifically authorised action requires elevation.

---

# 15. Destructive Operations

Destructive operations should require explicit user intent.

Examples:

* deletion;
* destructive Git operations;
* filesystem formatting;
* account removal;
* irreversible configuration changes.

---

# 16. File Access

Project AI should normally operate within the project boundary.

Broader filesystem access should arise from explicit user intent or appropriate general agent tooling.

---

# 17. Secret Files

General AI context must not automatically ingest:

```text
private keys
password databases
credential files
API tokens
.env secrets
secret stores
```

---

# 18. Prompt Injection

External content may contain instructions intended to manipulate AI.

Examples:

* websites;
* documentation;
* downloaded files;
* emails;
* research sources.

Such content is data, not automatically trusted instructions.

---

# 19. Instruction Hierarchy

Conceptually:

```text
Omivoid security policy
        ↓
provider/tool policy
        ↓
project instructions
        ↓
user task
        ↓
external content
```

External content must not override higher-level policy.

---

# 20. Project Instructions

Files such as `AGENTS.md` may legitimately contain project instructions.

Their authority is limited to the project/workflow and cannot override Omivoid security controls.

---

# 21. Context Transparency

The user should be able to understand what significant context is being sent.

Particularly important for remote providers.

---

# 22. Local vs Remote Processing

The system should distinguish:

```text
agent process location
```

from:

```text
model processing location
```

Pi running locally does not guarantee the model is local.

---

# 23. Remote Provider Disclosure

Where practical, the UI should indicate when project or document context may be sent to a remote model.

---

# 24. Remote Delegation

Remote delegation requires additional policy because both:

```text
task
```

and:

```text
context
```

may leave the laptop.

---

# 25. Delegation Confirmation

Sensitive or significant remote tasks should require confirmation identifying:

* destination;
* task;
* data/context being transferred.

---

# 26. No Credentials in Delegation Payloads

Remote authentication must use authorised infrastructure mechanisms.

Do not package passwords or private keys inside AI task prompts.

---

# 27. Worker Trust

A remote worker is another security boundary.

Worker capability should not imply unlimited access to all projects.

Future infrastructure may need worker-specific permissions.

---

# 28. Tailscale

Tailscale connectivity does not itself authorise an AI action.

Network reachability and application permission are separate concepts.

---

# 29. DMS Plugins

AI-related DMS plugins should be treated as executable desktop components.

Review plugins that:

* execute commands;
* access context;
* call remote APIs;
* store credentials;
* interact with AI providers.

---

# 30. Third-Party Pi Extensions

Pi extensions similarly expand the trusted computing base.

Do not install large extension bundles without understanding their behaviour.

---

# 31. OMP-Derived Features

When borrowing ideas from Pi extension ecosystems, prefer reimplementing or adopting only the required capability.

Do not inherit permissions merely because an extension bundle assumes them.

---

# 32. Capability Arguments

AI-generated arguments must be validated.

Particularly sensitive:

```text
paths
URLs
commands
worker IDs
project IDs
network targets
```

---

# 33. Command Injection

Do not construct shell commands through unsafe string concatenation from AI arguments.

Prefer:

* argument arrays;
* validated enums;
* structured APIs;
* safe subprocess invocation.

---

# 34. URLs

AI-provided URLs should be treated as untrusted input.

Opening a URL may be routine, but URLs must not become shell fragments.

---

# 35. Logging

Do not log by default:

* complete prompts;
* file contents;
* clipboard contents;
* selected text;
* credentials;
* full model responses.

Operational logging should favour metadata.

---

# 36. Auditability

For AI-triggered Omivoid actions, useful audit data includes:

```text
timestamp
provider
action
risk
confirmation
result
```

---

# 37. Failure Must Be Safe

If policy evaluation fails:

```text
deny
```

is preferable to guessing.

---

# 38. Unknown Action

Unknown actions must return:

```text
ACTION_NOT_FOUND
```

and never be interpreted as arbitrary shell commands.

---

# 39. Unavailable Capability

Unavailable actions must fail explicitly.

Do not substitute another operation that the AI considers equivalent.

---

# 40. Provider Failure

AI provider failure must not affect normal desktop controls.

---

# 41. Network Failure

Network failure must not trigger insecure fallback.

Example:

```text
remote provider unavailable
```

must not automatically cause sensitive data to be sent to another provider.

---

# 42. Provider Fallback

Automatic provider fallback is disabled for the initial phase.

Future fallback requires explicit privacy/routing policy.

---

# 43. Context Size

Extremely large context should be rejected or deliberately reduced.

This reduces:

* accidental disclosure;
* cost;
* poor model performance;
* resource consumption.

---

# 44. Context Provenance

AI should know the distinction between:

```text
user instruction
project instruction
external source
```

where provider/tooling architecture permits.

---

# 45. AI-Generated Code

Generated code should follow normal development controls:

```text
inspect
test
review
commit
```

AI generation does not bypass project quality controls.

---

# 46. Autonomous Changes

Continuous autonomous desktop modification is outside Phase 1.

AI actions are user-initiated interactions.

---

# 47. Background Agents

Do not introduce persistent autonomous agents as part of the initial desktop AI integration.

---

# 48. Security Tests

Phase 1 should test at least:

```text
AI requests allowed action
AI requests denied action
AI requests unknown action
AI requests confirmation action
AI supplies invalid argument
AI supplies hostile shell-like argument
context unavailable
secret file excluded
provider unavailable
```

---

# 49. Security Review Trigger

A new review is required before adding:

* privileged AI actions;
* destructive AI actions;
* unattended remote delegation;
* autonomous background agents;
* credential-access capabilities;
* automatic provider fallback.

---

# 50. Guiding Principle

> **AI can propose and request. Omivoid remains the authority that decides what the desktop actually does.**
