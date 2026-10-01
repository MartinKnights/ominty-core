# Ominty Pi Integration Specification

**Project:** `ominty-core`
**Subsystem:** AI
**Document:** 02
**Status:** Phase 1 Specification

---

# 1. Purpose

This document defines how Pi integrates with Ominty.

Pi is the preferred initial AI provider for Ominty laptops.

The objective is not to transform Pi into a large orchestration framework.

The objective is to use Pi as a lightweight, extensible AI agent operating close to the user's desktop, files, projects and Ominty capabilities.

---

# 2. Architectural Role

Pi occupies this position:

```text
User
 │
 ▼
Ominty
 │
 ▼
AI Provider Interface
 │
 ▼
Pi
 │
 ├── conversation
 ├── reasoning
 ├── coding
 ├── file work
 ├── research assistance
 ├── tools
 └── Ominty capabilities
```

Pi remains replaceable.

---

# 3. Why Pi

Pi is attractive for Ominty because the laptop does not require a heavyweight orchestration system for everyday AI interaction.

The desired characteristics are:

* lightweight;
* fast to invoke;
* terminal-friendly;
* customisable;
* tool-capable;
* project-friendly;
* suitable for coding;
* suitable for writing;
* suitable for research;
* capable of integrating with external systems.

These characteristics align with the Ominty laptop role.

---

# 4. Pi Is Not Ominty

Pi must not become the location where Ominty architecture is defined.

Pi may consume:

```text
Ominty actions
Ominty context
Ominty project metadata
```

but canonical definitions remain in Ominty.

---

# 5. Pi Is Not Herdr

Pi and Herdr have different intended responsibilities.

```text
Pi
 = interactive local agent

Herdr
 = orchestration/delegation
```

Do not expand Pi into a distributed orchestration system simply because it can execute tools.

---

# 6. Pi Is Not Agno

Agno belongs primarily in the broader IBIS server/agent architecture.

Pi should not reproduce business-agent infrastructure intended for Agno.

Expected future relationship:

```text
Pi
 ↓
Herdr
 ↓
IBIS server
 ↓
Agno
```

---

# 7. Phase 1 Integration Objectives

Pi integration should prove:

1. Pi can be detected;
2. Pi can be launched;
3. Ominty can submit a request;
4. context can be supplied;
5. Ominty actions can be exposed;
6. Pi can request an allowed action;
7. Ominty policy can approve/deny it;
8. result can be returned to Pi.

---

# 8. Environment Audit

Before implementation, inspect the actual Pi installation or intended installation method.

Record:

```text
Pi version
executable location
configuration location
supported invocation modes
tool mechanism
extension mechanism
session mechanism
model configuration
structured output capability
streaming capability
project behaviour
```

Do not implement against assumptions about Pi's interface.

---

# 9. Pi Installation

Pi installation should be treated separately from Pi integration.

If Pi is not installed, the implementation agent should identify the appropriate installation method and document it before changing the system.

Installation logic should not be embedded deeply inside the AI provider adapter.

---

# 10. Provider Adapter

Pi should be implemented as:

```text
ai/providers/pi/
```

Conceptually:

```text
Ominty AI request
       │
       ▼
Pi provider adapter
       │
       ▼
Pi interface
```

All Pi-specific invocation details belong inside this adapter.

---

# 11. Availability

The adapter must determine whether Pi is usable.

Conceptual command:

```text
ominty ai provider status pi
```

Potential result:

```text
Provider: pi
Available: yes
```

Exact CLI syntax may follow existing Ominty conventions.

---

# 12. Interactive Pi

Canonical action:

```text
ai.pi.open
```

should open Pi in the configured Ominty terminal workflow.

This action explicitly targets Pi and is therefore allowed to be provider-specific.

---

# 13. Generic Ask

Canonical:

```text
ai.ask
```

should resolve through the default provider.

If:

```toml
default_provider = "pi"
```

then:

```text
ai.ask
 ↓
Pi provider
```

Pi must not be hard-coded into the generic action.

---

# 14. CLI Proof

Before implementing DMS AI UI, prove Pi through CLI.

Example conceptual interface:

```bash
ominty ai ask "Explain this project structure"
```

Expected flow:

```text
CLI
 ↓
Ominty AI layer
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

# 15. Pi Configuration Ownership

Pi-native configuration remains owned by Pi.

Ominty should not duplicate settings such as:

* model provider;
* API keys;
* model names;
* native Pi preferences;
* session history;

unless required for Ominty integration.

---

# 16. Ominty Pi Configuration

Ominty may maintain integration-specific settings.

Example:

```toml
[ai.providers.pi]
enabled = true
```

Potential future settings:

```toml
terminal_mode = "interactive"
allow_actions = true
```

Only add settings when needed.

---

# 17. Pi Tools and Ominty Actions

The key integration point is exposing selected Ominty actions as Pi tools/capabilities.

Example:

```text
Pi tool:
open_browser

maps to:

app.browser.open
```

However, the canonical identity remains:

```text
app.browser.open
```

where Pi's tool mechanism permits it.

---

# 18. Capability Generation

Pi tool definitions SHOULD be generated from Action Registry metadata where practical.

Input:

```toml
[action."app.browser.open"]
name = "Open Browser"
description = "Open the configured web browser."
ai_accessible = true
risk = "routine"
confirmation = "never"
```

Derived Pi capability:

```text
ID:
app.browser.open

Description:
Open the configured web browser.
```

Avoid maintaining an independent hand-written catalogue of Pi desktop tools.

---

# 19. Capability Execution

Pi must not execute implementation commands directly for registered capabilities.

Preferred:

```text
Pi
 ↓
app.browser.open
 ↓
Ominty
 ↓
policy
 ↓
action runner
```

Not:

```text
Pi
 ↓
brave-browser
```

for the routine semantic action.

---

# 20. Shell Tools Remain Valid

Pi may still have shell access where appropriate.

Examples:

* inspect source code;
* run tests;
* Git operations;
* search files;
* development commands;
* one-off technical investigation.

Ominty actions are not intended to replace Pi's general development capabilities.

---

# 21. Capability Boundary

Use this rule:

```text
Stable known Ominty operation?
       │
      yes
       │
       ▼
Ominty Action Registry

Open-ended technical task?
       │
      yes
       │
       ▼
Pi tools / shell
```

---

# 22. Initial Pi Capability Set

Do not expose the entire registry immediately.

Start with a small test set.

Recommended:

```text
app.browser.open
app.terminal.open
app.editor.open
help.keys.open
help.actions.search
```

Add capabilities after policy behaviour is validated.

---

# 23. Capability Discovery

Pi should receive capabilities dynamically where practical.

This means newly enabled actions can become available without editing Pi-specific prompt files manually.

Desired flow:

```text
Action Registry
      │
      ▼
AI capability filter
      │
      ▼
Pi capability adapter
      │
      ▼
Pi
```

---

# 24. Risk Filtering

Initial Pi capability exposure should favour:

```text
read
routine
```

actions.

State-changing actions may be added once confirmation behaviour is tested.

Privileged/destructive actions should not be part of the initial proof.

---

# 25. Context Input

Pi should be able to receive structured Ominty context.

Initial experiments should consider:

```text
selection
file
directory
project
```

The context layer is responsible for collection.

Pi is responsible for interpreting supplied context.

---

# 26. Context Packaging

Avoid constructing one enormous provider-specific prompt in every calling component.

Preferred:

```text
Context object
    ↓
Pi adapter
    ↓
Pi-compatible representation
```

This keeps future providers possible.

---

# 27. Selected Text

A desired workflow is:

```text
select text
    ↓
Super+A,E
    ↓
ai.selection.explain
    ↓
selection context
    ↓
Pi
```

However, reliable Wayland selection acquisition must first be established.

Do not implement clipboard guessing as though it were reliable selection context.

---

# 28. File Context

File context should eventually allow:

```text
Explain this file
Summarise this file
Review this file
Refactor this file
```

Context should include where useful:

```text
path
content
type
project
```

Subject to privacy and size controls.

---

# 29. Project Context

Pi is particularly valuable when aware of the project currently being developed.

Potential project information:

```text
project name
root
README
AGENTS.md
documentation
Git status
relevant source files
task metadata
```

Project context is specified in a later document.

---

# 30. AGENTS.md Awareness

Where Pi supports project instructions, Ominty projects should be able to expose their local `AGENTS.md`.

This is especially important because Ominty itself uses `AGENTS.md` to constrain implementation agents.

Pi should respect project-local agent instructions where its architecture supports this.

---

# 31. Skills and Extensions

Pi's extensibility should be used selectively.

Useful extension categories may include:

```text
Ominty action access
project context
research workflow
writing workflow
development workflow
delegation
```

Do not install large extension bundles simply because they are available.

---

# 32. OMP and Similar Projects

Projects that extend/configure Pi may be studied for useful ideas.

Potentially useful concepts include:

* improved session handling;
* project awareness;
* prompt organisation;
* tool management;
* reusable skills;
* model switching;
* workflow shortcuts;
* contextual commands.

However:

> **Ominty should adopt useful capabilities, not inherit another project's entire opinionated Pi environment.**

Each borrowed capability must solve an Ominty requirement.

---

# 33. Ominty Pi Extension

If Pi's extension system supports it cleanly, prefer one focused Ominty integration package.

Conceptually:

```text
pi-ominty
│
├── actions
├── context
├── projects
└── delegation
```

Exact implementation depends on Pi's supported extension architecture.

---

# 34. Avoid Extension Fragmentation

Do not create separate Pi extensions for every trivial Ominty action.

Prefer one coherent integration boundary where practical.

---

# 35. Session Behaviour

Interactive Pi sessions should use Pi's native session management.

Ominty should not implement a competing session database during Phase 1.

---

# 36. Project Sessions

Future enhancement:

```text
project
  ↓
associated Pi session/context
```

This could allow the user to return to a project and continue AI work with appropriate context.

This is not required for initial integration.

---

# 37. Model Selection

Pi should remain responsible for its supported model configuration.

Ominty may later expose:

```text
Super+A,M
```

as a model/provider interface.

Do not implement a second model configuration system during Phase 1.

---

# 38. Research Workflow

Pi should eventually support research-oriented interactions such as:

```text
summarise source
extract claims
identify questions
compare sources
build notes
prepare project context
```

The browser/research integration should be designed later rather than bundled into the initial provider adapter.

---

# 39. Writing Workflow

Given the laptop's writing role, Pi should eventually support:

```text
outline
rewrite
critique
expand
condense
compare drafts
research supporting material
project-aware writing
```

These are workflows above the basic provider interface.

---

# 40. Development Workflow

Pi should support development tasks such as:

```text
inspect code
explain code
propose change
run tests
review diff
work from AGENTS.md
```

General development operations may legitimately use Pi's shell/tool environment.

---

# 41. Delegation Preparation

Pi should eventually be able to express:

```text
delegate this task
```

without needing to know remote machine implementation.

Desired future flow:

```text
Pi
 ↓
Ominty delegation request
 ↓
Herdr
 ↓
target selection
 ↓
remote worker
```

This is intentionally deferred until local integration works.

---

# 42. Tailscale

Pi should not directly encode knowledge of Tailscale addresses as part of normal AI behaviour.

Tailscale is transport infrastructure.

Future remote delegation should resolve destinations through the delegation layer.

---

# 43. DMS Presentation

Pi does not need to own graphical presentation.

Possible interaction:

```text
DMS
 ↓
Ominty AI
 ↓
Pi
```

DMS can present:

* prompt input;
* streaming response;
* history shortcuts;
* action feedback;
* context indicators.

---

# 44. Terminal Presentation

The normal Pi terminal interface remains important.

`ai.pi.open` should provide quick access to the full native Pi experience.

The DMS AI interface should complement rather than unnecessarily replace it.

---

# 45. Context Indicator

Future AI UI should clearly indicate when context is being supplied.

Examples:

```text
Context: Selected text
Context: project ominty-core
Context: current file
```

This helps prevent accidental transmission or misunderstanding.

---

# 46. Remote Data Awareness

If Pi's configured model uses a remote service, the user should not be misled into believing processing is local merely because Pi itself runs locally.

Provider/model locality should be distinguishable where practical.

---

# 47. Secrets

Pi credentials remain under Pi/provider-native secret handling.

Ominty must not extract or duplicate them unnecessarily.

---

# 48. Logging

Do not log full prompts, selected text, files or model responses by default merely for debugging.

Operational logs should focus on:

```text
provider
action
status
error
timing
```

Sensitive content logging should require explicit diagnostic intent.

---

# 49. Error Behaviour

Pi adapter errors should use stable provider errors.

Examples:

```text
PROVIDER_UNAVAILABLE
PROVIDER_FAILED
PROVIDER_TIMEOUT
```

Ominty action failures returned through Pi retain Action Registry error semantics.

---

# 50. Failure Isolation

If Pi fails:

```text
Super+A AI functions
```

may become unavailable.

But:

```text
Super+K
Super+Space
Niri
DMS
Ominty actions
```

must continue to function.

---

# 51. Testing Sequence

Recommended integration tests:

```text
1. detect Pi
2. open Pi interactively
3. send basic prompt
4. receive response
5. provide simple context
6. expose one Ominty capability
7. ask Pi to invoke capability
8. enforce policy
9. return result
10. test denied/unavailable capability
```

---

# 52. Primary Proof

The first complete Pi integration proof should be intentionally simple.

User request:

```text
Open my browser.
```

Expected:

```text
User
 ↓
Pi
 ↓
discovers app.browser.open
 ↓
requests action
 ↓
Ominty policy
 ↓
Action Registry
 ↓
app.launch
 ↓
configured browser
```

Pi should not need to know which browser is installed.

---

# 53. Second Proof

After the first proof works, test a read-only information capability or context workflow.

For example:

```text
"What are my available Ominty application actions?"
```

Pi should be able to reason from exposed capability metadata rather than a manually maintained prompt.

---

# 54. Do Not Overbuild Phase 1

Initial Pi integration does NOT require:

* custom memory system;
* distributed orchestration;
* remote workers;
* autonomous background operation;
* large skill marketplace;
* multi-agent teams;
* model router;
* custom inference server;
* graphical session manager;
* replacement of Pi's native UI.

---

# 55. Phase 1 Completion Criteria

Pi integration is complete for the first AI milestone when:

* Pi is detected;
* `ai.pi.open` works;
* generic `ai.ask` can resolve to Pi;
* Ominty can supply context;
* selected registry capabilities can be exposed;
* Pi can request an allowed action;
* Ominty executes it;
* failures are structured;
* policy remains authoritative;
* Pi-specific implementation is isolated inside its provider adapter.

---

# 56. Guiding Principle

Pi should remain small enough to preserve the reason it was selected.

The desired architecture is:

```text
Pi
    = intelligence close to the user

Ominty
    = desktop context + controlled capabilities

Herdr
    = delegation

Agno
    = larger persistent agent systems
```

The goal is not to make Pi do everything.

The goal is to make Pi exceptionally effective at the work being performed on the Ominty laptop.
