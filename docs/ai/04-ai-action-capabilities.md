# Omivoid AI Action Capability Specification

**Project:** `omivoid-lmde`
**Subsystem:** AI
**Document:** 04
**Status:** Phase 1 Specification

---

# 1. Purpose

This document defines how Omivoid exposes Action Registry capabilities to AI providers.

The Action Registry is the authoritative definition of supported Omivoid operations.

AI providers receive a filtered capability view.

The governing rule is:

> **AI may request capabilities; Omivoid decides whether and how those capabilities execute.**

---

# 2. Architectural Position

```text
Action Registry
      │
      ▼
Capability Filter
      │
      ▼
AI Capability Catalogue
      │
      ▼
Provider Adapter
      │
      ▼
AI Provider
      │
      ▼
Tool Request
      │
      ▼
Policy Enforcement
      │
      ▼
Action Runner
```

---

# 3. Capability Is Not Command

An AI capability represents user intent.

Example:

```text
app.browser.open
```

is a capability.

```text
brave-browser
```

is an implementation detail.

AI should normally receive the capability rather than the command.

---

# 4. Source of Truth

AI capabilities are derived from Action Registry actions.

Do not maintain an independent AI tool catalogue when the capability corresponds to an Omivoid action.

---

# 5. Eligibility

An action is potentially eligible for AI exposure when:

```toml
ai_accessible = true
```

This field is necessary but not sufficient.

Runtime filtering must also consider:

* platform;
* dependencies;
* availability;
* context;
* risk;
* confirmation policy;
* local policy.

---

# 6. Capability Filtering

Conceptual flow:

```text
All Actions
    │
    ▼
ai_accessible?
    │
    ▼
platform supported?
    │
    ▼
dependencies available?
    │
    ▼
required context available?
    │
    ▼
policy allows exposure?
    │
    ▼
AI Capability
```

---

# 7. Initial Capability Levels

For AI policy purposes, Phase 1 should distinguish:

```text
read
routine
state-change
privileged
destructive
critical
```

Exact registry terminology must remain consistent with the main Action Registry specification.

---

# 8. Read Capabilities

Read capabilities inspect state without modifying it.

Examples might include:

```text
help.actions.search
system.status.show
project.info
```

Read actions are generally suitable for AI access.

---

# 9. Routine Capabilities

Routine actions perform normal user operations with limited consequences.

Examples:

```text
app.browser.open
app.editor.open
help.keys.open
```

These are good initial AI capability candidates.

---

# 10. State-Changing Capabilities

State-changing actions alter desktop/system state.

Examples may include:

```text
theme.mode.toggle
network.wifi.toggle
audio.mute.toggle
```

These may require additional confirmation depending on policy.

---

# 11. Privileged Capabilities

Privileged capabilities require elevated system authority.

They should normally be excluded from the initial AI capability set.

---

# 12. Destructive Capabilities

Actions capable of data loss or significant disruption should not be exposed casually.

Examples could include:

* deleting data;
* destructive system operations;
* irreversible project modifications.

AI access requires explicit policy and confirmation.

---

# 13. Critical Capabilities

Critical/restricted capabilities may remain permanently unavailable to general AI providers.

Examples might include:

* security control changes;
* credential access;
* destructive infrastructure actions.

---

# 14. Confirmation Modes

Capability execution may use:

```text
never
interactive
ai-only
always
```

Example:

```toml
confirmation = "ai-only"
```

means a direct keyboard invocation may execute normally while AI invocation requires user confirmation.

---

# 15. `ai-only` Confirmation

This mode is especially useful for ordinary state changes.

Example:

```text
theme.wallpaper.select
```

may be safe interactively but should not necessarily execute because AI inferred the request incorrectly.

---

# 16. Confirmation Flow

```text
AI requests action
      │
      ▼
policy evaluates
      │
      ▼
confirmation required?
      │
   ┌──┴──┐
  yes    no
   │      │
   ▼      ▼
prompt   execute
   │
approved?
   │
   ▼
execute
```

---

# 17. Confirmation Content

A confirmation should identify:

* requesting AI/provider;
* action;
* relevant arguments;
* effect.

Example:

```text
Pi wants to:

Switch Wi-Fi off

Action:
network.wifi.toggle

Allow?
```

---

# 18. Provider Does Not Confirm Itself

The provider must not satisfy Omivoid confirmation requirements by claiming that the user approved something.

Confirmation belongs to Omivoid's interaction/policy layer.

---

# 19. Capability Representation

Conceptual capability metadata:

```json
{
  "id": "app.browser.open",
  "name": "Open Browser",
  "description": "Open the configured web browser.",
  "risk": "routine",
  "confirmation": "never",
  "arguments": {}
}
```

---

# 20. Capability Descriptions

Descriptions supplied to AI should be:

* concise;
* precise;
* semantic;
* implementation-neutral.

Good:

```text
Open the configured default web browser.
```

Poor:

```text
Runs brave-browser via shell.
```

---

# 21. Arguments

Parameterized actions should expose structured arguments.

Example:

```text
workspace.switch
```

might accept:

```json
{
  "workspace": 3
}
```

Do not require AI to construct shell fragments.

---

# 22. Argument Validation

Arguments must be validated after the provider requests the capability.

Provider-generated tool arguments are untrusted input.

Validate:

* type;
* range;
* enum;
* required values;
* path constraints where applicable.

---

# 23. Path Arguments

File/path actions require particular care.

AI should not automatically gain unrestricted filesystem access merely because an action accepts a path.

Policy may restrict paths to:

* current project;
* user-approved file;
* configured directories.

General development tools may have broader access separately.

---

# 24. Context-Constrained Capabilities

Some actions should only exist when relevant context exists.

Example:

```text
ai.selection.explain
```

requires selection context.

If absent:

```text
CONTEXT_UNAVAILABLE
```

The tool should not be exposed or should report unavailable.

---

# 25. Dynamic Availability

Capability exposure may change during a session.

Examples:

```text
file context acquired
    → file actions appear

project opened
    → project actions appear

selection disappears
    → selection actions unavailable
```

Phase 1 does not require continuous live capability updates if technically expensive.

---

# 26. Capability Discovery

The provider should be able to obtain an appropriate capability list.

Potential conceptual command:

```text
omivoid ai capabilities
```

Possible output:

```text
app.browser.open
app.editor.open
help.keys.open
```

A machine-readable form should be preferred for provider integration.

---

# 27. Capability Search

Future AI providers may search capabilities rather than receiving every tool definition.

This could matter once the registry becomes large.

Not required in Phase 1.

---

# 28. Initial Capability Set

Start deliberately small.

Recommended first set:

```text
app.browser.open
app.terminal.open
app.editor.open
help.keys.open
help.actions.search
```

Optional additional read-only capabilities may be added.

---

# 29. First Architecture Proof

User:

```text
Open my browser.
```

Pi:

```text
requests app.browser.open
```

Omivoid:

```text
checks policy
```

Runner:

```text
executes app.launch role=browser
```

Result:

```text
browser opened
```

---

# 30. Second Architecture Proof

User:

```text
Show me the Omivoid keybindings.
```

Pi requests:

```text
help.keys.open
```

The same interface used by the keyboard shortcut should open.

This proves AI and keyboard share capabilities.

---

# 31. Tool Result

Success should be structured.

Example:

```json
{
  "success": true,
  "action": "help.keys.open"
}
```

---

# 32. Tool Failure

Example:

```json
{
  "success": false,
  "action": "app.editor.open",
  "error": {
    "code": "ACTION_UNAVAILABLE",
    "message": "Editor role is not configured."
  }
}
```

The AI may explain the failure to the user.

---

# 33. Policy Denial

If policy blocks an action:

```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "This capability is not available to AI."
  }
}
```

Do not silently execute a different action.

---

# 34. Confirmation Required

Example:

```json
{
  "success": false,
  "error": {
    "code": "CONFIRMATION_REQUIRED"
  }
}
```

The interaction layer should then obtain confirmation.

---

# 35. Recursion Protection

Actions invoking AI should normally not themselves be exposed as AI tools.

Example:

```text
ai.ask
ai.pi.open
```

should generally use:

```toml
ai_accessible = false
```

This prevents loops such as:

```text
Pi
 ↓
ai.ask
 ↓
Pi
 ↓
ai.ask
```

---

# 36. AI Namespace Exception

Some AI actions may eventually need cross-agent invocation.

Examples:

```text
ai.delegate
```

Such exposure should be deliberate and governed separately.

---

# 37. Shell Escape Hatch

The capability system does not prohibit provider shell tools.

However:

```text
known Omivoid operation
```

should use:

```text
Omivoid capability
```

rather than arbitrary shell execution where practical.

---

# 38. Capability Audit

Phase 1 should be able to produce an audit showing:

```text
action
AI accessible?
risk
confirmation
available?
reason unavailable
```

This could later become part of developer diagnostics.

---

# 39. Logging

AI capability invocation should record operational metadata where appropriate:

```text
timestamp
provider
action
result
confirmation outcome
```

Avoid logging sensitive arguments/content unnecessarily.

---

# 40. Provider Identity

Policy should know which provider requested an action.

Example:

```text
provider = pi
```

Future policy may distinguish providers.

---

# 41. Provider-Specific Capability Restrictions

Future configuration may support:

```toml
[ai.providers.pi]
allow = ["app.*", "help.*"]

[ai.providers.remote-agent]
allow = ["help.*"]
```

Not required initially.

---

# 42. Project Policy

Future project configuration may restrict AI capabilities.

Example:

```toml
[ai]
allow_project_shell = false
```

This belongs to later project/context specifications.

---

# 43. Capability Versioning

Action IDs should remain stable.

If capability semantics materially change, normal Action Registry compatibility rules should apply.

Do not version Pi-specific tool names independently unless required.

---

# 44. DMS Role

DMS may display:

* confirmation;
* success;
* failure;
* action requested;
* capability status.

DMS does not decide whether an action is permitted.

---

# 45. Test Cases

Required initial tests:

```text
allowed routine action
non-AI-accessible action
missing dependency
invalid argument
confirmation-required action
unknown action
unavailable action
provider requests recursive AI action
```

---

# 46. Phase 1 Completion Criteria

The AI capability layer is complete for the initial milestone when:

* capabilities derive from registry metadata;
* filtering works;
* Pi receives allowed capabilities;
* Pi can request one;
* policy evaluates it;
* action runner executes it;
* structured result returns;
* denied actions remain denied;
* confirmation policy is enforceable.

---

# 47. Guiding Principle

The action capability system should make AI powerful without requiring AI to understand or control the desktop's implementation directly.

The desired boundary is:

```text
AI knows:
    what Omivoid can do

AI does not need to know:
    how Omivoid does it
```
