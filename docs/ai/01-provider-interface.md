# Ominty AI Provider Interface

**Project:** `ominty-core`
**Subsystem:** AI
**Document:** 01
**Status:** Phase 1 Specification

---

# 1. Purpose

This document defines the contract between Ominty and AI providers.

The interface allows Ominty to use Pi initially while retaining the ability to support other AI providers later.

The central rule is:

> **Ominty interacts with AI capabilities through a provider contract rather than directly coupling user interactions to Pi-specific commands.**

---

# 2. Architectural Position

```text
Ominty Interaction
       │
       ▼
Ominty AI Layer
       │
       ▼
Provider Interface
       │
 ┌─────┼─────────────┐
 ▼     ▼             ▼
Pi   Future Local   Future Remote
```

---

# 3. Provider vs Model

A provider and a model are different concepts.

Example:

```text
Provider: Pi
Model:    configured model used by Pi
```

Ominty should not assume that choosing Pi implies one particular model.

Likewise, model selection should not require changing the Ominty provider architecture.

---

# 4. Provider Responsibilities

An AI provider may be responsible for:

* conversation;
* prompt execution;
* model interaction;
* tool use;
* session management;
* streaming;
* provider-specific configuration;
* provider-specific history.

Ominty remains responsible for:

* desktop interaction;
* context packaging;
* Action Registry capabilities;
* action policy;
* provider selection;
* high-level routing.

---

# 5. Minimum Provider Contract

A Phase 1 provider should conceptually support:

```text
available()
ask()
open()
capabilities()
```

Not every provider must implement every operation.

---

# 6. `available()`

Purpose:

Determine whether the provider can currently be used.

Conceptual result:

```json
{
  "available": true,
  "provider": "pi"
}
```

Failure/unavailable example:

```json
{
  "available": false,
  "provider": "pi",
  "reason": "executable-not-found"
}
```

---

# 7. `ask()`

Purpose:

Submit an AI request.

Conceptual input:

```json
{
  "prompt": "Explain this function.",
  "context": {},
  "capabilities": [],
  "options": {}
}
```

Conceptual output:

```json
{
  "success": true,
  "provider": "pi",
  "response": "..."
}
```

Streaming may use a different transport while retaining equivalent semantics.

---

# 8. `open()`

Purpose:

Open the provider's interactive interface.

Example:

```text
ai.pi.open
```

may invoke Pi interactively in the configured terminal or presentation environment.

This is provider-specific behaviour exposed through an Ominty action.

---

# 9. `capabilities()`

Purpose:

Describe provider features relevant to Ominty.

Possible capabilities include:

```text
chat
streaming
tools
sessions
files
project-context
model-selection
```

This allows Ominty to avoid assuming every provider behaves identically.

---

# 10. Provider Identifier

Each provider must have a stable identifier.

Examples:

```text
pi
herdr
local
remote
```

Provider IDs should be lowercase and stable.

---

# 11. Default Provider

Ominty should support a configured default AI provider.

Example:

```toml
[ai]
default_provider = "pi"
```

Therefore:

```text
ai.ask
```

resolves to:

```text
configured default provider
```

rather than Pi directly.

---

# 12. Explicit Provider Actions

Provider-specific actions may still exist.

Example:

```text
ai.pi.open
ai.herdr.open
```

These are valid because the user explicitly intends to interact with that provider/system.

This does not change the generic meaning of:

```text
ai.ask
```

---

# 13. Provider Configuration

Ominty should store only provider integration settings required by Ominty.

Example:

```toml
[ai]
default_provider = "pi"

[ai.providers.pi]
enabled = true
```

Provider-native configuration should remain owned by the provider.

---

# 14. Do Not Duplicate Provider Configuration

If Pi already manages:

* models;
* API endpoints;
* authentication;
* prompts;
* sessions;
* tools;

Ominty should not duplicate those settings unless integration requires it.

Preferred:

```text
Ominty
  → "Use Pi"

Pi
  → determines provider/model configuration
```

---

# 15. Invocation Interface

The implementation should initially prefer the simplest stable interface Pi provides.

Possible mechanisms include:

```text
CLI
structured subprocess
IPC
API
```

Do not introduce an Ominty daemon merely to wrap a functioning provider CLI.

---

# 16. Structured Invocation

Where possible, avoid parsing human-oriented terminal output.

Prefer provider interfaces that can return structured data.

If Pi only exposes suitable CLI output, isolate parsing inside the Pi provider adapter.

Do not leak parsing assumptions into the wider Ominty AI layer.

---

# 17. Streaming

Streaming responses are desirable for interactive AI.

The provider interface should therefore permit:

```text
request
  ↓
stream events
  ↓
completion
```

without requiring all providers to implement streaming immediately.

---

# 18. Conceptual Stream Events

Possible events:

```text
start
text
tool_call
tool_result
error
complete
```

Exact transport is an implementation decision.

---

# 19. Context Contract

Ominty context should be packaged independently of provider-specific prompts.

Conceptual structure:

```json
{
  "type": "selection",
  "content": "...",
  "source": {
    "application": "...",
    "file": null
  }
}
```

The provider adapter converts this into whatever Pi requires.

---

# 20. Context Types

Initial context vocabulary:

```text
none
selection
clipboard
file
directory
project
browser
editor
terminal
```

The context specification will define these in more detail.

---

# 21. Capability Contract

Ominty may expose selected Action Registry capabilities to a provider.

Conceptual capability:

```json
{
  "id": "app.browser.open",
  "name": "Open Browser",
  "description": "Open the configured web browser.",
  "risk": "routine",
  "confirmation": "never"
}
```

Provider-specific tool definitions should be generated from this representation.

---

# 22. Provider Must Not Decide Action Policy

Pi may decide that it wants to call:

```text
app.browser.open
```

but Ominty decides whether the call is allowed.

Flow:

```text
Pi
 ↓
tool request
 ↓
Ominty policy
 ↓
allowed?
 ↓
action runner
```

The provider must not bypass this step.

---

# 23. Capability Filtering

Before exposing actions, Ominty should filter them by:

```text
ai_accessible
platform
dependencies
availability
context
policy
```

Do not expose every registry action automatically.

---

# 24. Risk and Confirmation

The provider interface must preserve action risk information.

Example:

```text
read
routine
state-change
privileged
destructive
critical
```

The provider itself should not be trusted to enforce final confirmation policy.

Ominty remains the enforcement boundary.

---

# 25. Tool Result Contract

Tool execution should return structured results to the provider.

Success:

```json
{
  "success": true,
  "action": "app.browser.open"
}
```

Failure:

```json
{
  "success": false,
  "action": "app.browser.open",
  "error": {
    "code": "ACTION_UNAVAILABLE",
    "message": "Browser role is not configured."
  }
}
```

---

# 26. Provider Errors

Provider-level errors should be distinguishable from Ominty action errors.

Possible provider errors:

```text
PROVIDER_NOT_FOUND
PROVIDER_UNAVAILABLE
PROVIDER_FAILED
PROVIDER_TIMEOUT
PROVIDER_AUTH_REQUIRED
PROVIDER_UNSUPPORTED_OPERATION
```

---

# 27. Provider Discovery

Phase 1 may use static configuration.

Example:

```text
providers/
└── pi
```

A dynamic plugin framework is not required.

---

# 28. Provider Adapter Location

Recommended structure:

```text
ai/
├── providers/
│   └── pi/
├── context/
├── capabilities/
└── policy/
```

Exact implementation language may adjust this structure.

---

# 29. Provider Selection

Initial selection logic:

```text
explicit provider requested?
        │
    ┌───┴───┐
   yes      no
    │        │
    ▼        ▼
requested  default
provider   provider
```

Future routing may consider:

* task type;
* cost;
* privacy;
* local/remote;
* model capability;
* compute requirements.

That is deferred.

---

# 30. Provider Fallback

Automatic provider fallback is NOT required in the initial implementation.

If Pi is unavailable:

```text
PROVIDER_UNAVAILABLE
```

is preferable to silently sending a request to a remote provider.

Future fallback must respect privacy and routing policy.

---

# 31. Privacy Boundary

Provider invocation must make it possible to know whether data is:

```text
local
```

or:

```text
remote
```

before sensitive context is transmitted.

This becomes particularly important for:

* project source;
* documents;
* selected text;
* business information;
* credentials.

---

# 32. Secret Handling

Provider credentials must not be stored in:

* Action Registry;
* committed Ominty config;
* documentation;
* generated capability files.

Use provider-native or appropriate secret mechanisms.

---

# 33. Session Ownership

Pi should own Pi sessions.

Ominty may store:

```text
current provider
current project
current context source
```

but should not duplicate entire provider histories.

---

# 34. Stateless Invocation

The provider interface should permit stateless requests.

Example:

```text
ai.selection.explain
```

should not necessarily require an existing conversational session.

---

# 35. Interactive Invocation

It should also permit interactive sessions.

Example:

```text
ai.pi.open
```

opens a normal Pi interaction environment.

---

# 36. DMS Independence

The provider interface must not depend on DMS.

Correct:

```text
DMS
 ↓
Ominty AI
 ↓
Provider
```

CLI should be able to invoke the same provider without DMS.

---

# 37. CLI Proof

Phase 1 should provide an equivalent of:

```bash
ominty ai ask "Explain Niri's scrolling layout"
```

before requiring the full `Super+A` graphical experience.

This proves the provider architecture independently of UI.

---

# 38. Testing

Provider tests should include:

* provider installed;
* provider missing;
* provider starts;
* simple prompt;
* provider failure;
* context request;
* capability exposure;
* tool call;
* tool failure;
* unavailable action;
* policy denial.

---

# 39. Phase 1 Provider Requirements

The Pi provider implementation should prove:

```text
availability
basic ask
interactive open
context input
Ominty capability exposure
tool result handling
```

Streaming is desirable but not a blocker if Pi integration initially requires non-streaming invocation.

---

# 40. Future Providers

The interface should be capable of supporting future providers without redesigning:

```text
Super+A
Action Registry
context system
AI policy
```

This is the primary reason the provider boundary exists.

---

# 41. Non-Goals

Do not build during this stage:

* provider marketplace;
* automatic model benchmarking;
* intelligent model router;
* automatic cost optimisation;
* provider load balancing;
* distributed inference scheduler;
* universal AI API compatibility layer.

---

# 42. Success Criterion

The provider interface is successful when:

```text
ominty ai ask ...
```

can use Pi while the rest of Ominty does not need to understand Pi's internal implementation.

The defining contract is:

> **Ominty defines the AI interaction; the provider defines how the intelligence is supplied.**
