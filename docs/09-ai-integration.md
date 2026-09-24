# Omivoid LMDE — AI Integration Specification

**Project:** `omivoid-lmde`
**Phase:** Phase 1
**Primary concepts:** Pi, Herdr, Omivoid Actions

---

# 1. Purpose

This document defines how AI integrates into Omivoid.

AI is a first-class interaction surface.

It is not intended to be merely another desktop application.

The central principle is:

> **AI should interact with the Omivoid capability model wherever practical rather than directly manipulating implementation-specific system commands.**

---

# 2. Architectural Position

The intended model is:

```text
User
 │
 ├── Keyboard
 ├── Command palette
 ├── AI palette
 └── Voice later
        │
        ▼
   AI Interaction Layer
        │
        ├── Pi
        ├── Herdr
        └── Future agents
        │
        ▼
 Omivoid Action Registry
        │
        ▼
 Controlled Capabilities
```

AI is both:

* something the user invokes;
* an authorised consumer of Omivoid actions.

---

# 3. Laptop Role

The Omivoid laptop is primarily a thinking and creation environment.

Primary workloads include:

* planning;
* research;
* writing;
* project ideation;
* web development;
* light coding;
* documentation;
* interacting with AI;
* handing larger workloads to other systems.

It is not expected to host every heavy AI workload locally.

---

# 4. Distributed AI Direction

The wider architecture may eventually operate as:

```text
Omivoid Laptop
      │
      ├── Pi
      │
      ├── Herdr
      │
      └── Remote task delegation
               │
            Tailscale
               │
        ┌──────┴──────┐
        │             │
 Desktop PC      IBIS Server
 heavy compute      Agno
```

Remote execution is not required for the initial Phase 1 implementation.

The interaction architecture should nevertheless avoid assumptions that every AI task executes locally.

---

# 5. Pi Role

Pi is intended as a lightweight, flexible AI interface suitable for the laptop.

Potential responsibilities include:

* conversational assistance;
* writing;
* research support;
* code assistance;
* local project context;
* invoking authorised Omivoid actions.

Pi should remain replaceable.

Omivoid should integrate with Pi through an adapter or defined interface rather than embedding Pi-specific assumptions throughout the desktop.

---

# 6. Herdr Role

Herdr is intended to support orchestration and delegation.

Potential future responsibilities include:

* dispatching work;
* selecting appropriate agents;
* handing tasks to remote machines;
* tracking delegated work;
* interacting with broader IBIS infrastructure.

Phase 1 may initially provide:

```text
ai.herdr.open
```

without implementing full delegation.

---

# 7. AI Namespace

`Super+A` is reserved for AI interaction.

Initial conceptual namespace:

```text
Super+A,A   Ask AI
Super+A,P   Pi
Super+A,H   Herdr
Super+A,E   Explain selection
Super+A,S   Summarise selection
Super+A,R   Research
Super+A,W   Writing
Super+A,C   Code
```

The prefix should display available continuation actions where practical.

---

# 8. AI Palette

Pressing:

```text
Super+A
```

should eventually expose an AI-specific palette.

Potential content:

```text
Ask
Explain selection
Summarise selection
Research
Writing
Code
Pi
Herdr
```

The UI may be implemented through:

* DMS extension;
* custom Quickshell component;
* command palette mode.

The action definitions remain independent of presentation.

---

# 9. AI Actions

Initial registry actions include:

```text
ai.open
ai.ask
ai.pi.open
ai.herdr.open
ai.selection.explain
ai.selection.summarise
```

Potential later actions:

```text
ai.selection.rewrite
ai.selection.translate
ai.selection.research

ai.file.summarise
ai.file.explain

ai.project.ask
ai.project.plan
ai.project.delegate

ai.remote.delegate
```

Do not implement speculative actions until context handling is reliable.

---

# 10. AI Should Use Registered Actions

Preferred:

```text
User:
"Open Bluetooth settings"

AI:
network.bluetooth.open
```

Avoid:

```text
AI decides to inspect distro
AI searches for Bluetooth command
AI invokes arbitrary shell command
```

when a registered action already exists.

This improves:

* consistency;
* portability;
* security;
* auditability;
* error handling.

---

# 11. Shell Access Is Not Forbidden

The Action Registry is not intended to eliminate shell access.

AI may still require shell execution for:

* development;
* diagnostics;
* novel tasks;
* implementation work;
* operations not yet represented by actions.

However, routine desktop operations should prefer registered capabilities.

---

# 12. AI Permission Metadata

Each action declares:

```toml
ai_accessible = true
```

or:

```toml
ai_accessible = false
```

AI must respect this field.

An action not exposed to AI should not be invoked indirectly merely because the agent can construct the underlying shell command.

This is an important policy boundary.

---

# 13. Risk Metadata

AI should consider action risk.

Initial risk levels:

```text
read
routine
state-change
privileged
destructive
critical
```

Examples:

```text
app.browser.open
routine

network.wifi.toggle
state-change

session.shutdown
destructive

security.firewall.modify
critical
```

---

# 14. Confirmation

Actions also declare confirmation policy:

```text
never
interactive
ai-only
always
```

Example:

```toml
risk = "destructive"
confirmation = "ai-only"
```

An AI request to shut down may therefore require explicit confirmation even if a direct user hotkey does not.

---

# 15. Context

AI actions should use context deliberately.

Possible contexts include:

```text
text-selection
file
directory
browser
editor
project
```

Example:

```text
ai.selection.explain
```

should only be offered when Omivoid can actually acquire relevant selected text.

---

# 16. Do Not Fake Context

If reliable selected-text capture is unavailable, return:

```text
CONTEXT_UNAVAILABLE
```

Do not silently:

* read the clipboard without clear semantics;
* use stale selection;
* infer content from unrelated windows.

Context correctness matters more than appearing intelligent.

---

# 17. Selection Workflow

A future text-selection workflow may be:

```text
User selects text
       ↓
Super+A,E
       ↓
Omivoid obtains selection
       ↓
context packaged
       ↓
configured AI provider
       ↓
response presented
```

The exact selection mechanism should be established experimentally in Phase 1.

---

# 18. Context Packaging

AI providers should receive structured context where practical.

Conceptually:

```json
{
  "action": "ai.selection.explain",
  "context": {
    "type": "text-selection",
    "text": "..."
  }
}
```

Avoid forcing every AI integration to rediscover context independently.

---

# 19. Project Context

Project-aware AI is strategically important.

Potential future project context includes:

* project root;
* documentation;
* active files;
* Git state;
* notes;
* task metadata.

This could support:

```text
ai.project.ask
```

and:

```text
project.delegate
```

Full project-context management is outside the minimum Phase 1 implementation.

---

# 20. AI Provider Abstraction

Omivoid should not bind the entire AI subsystem to Pi.

Conceptually:

```text
ai.ask
   ↓
AI adapter
   ↓
configured provider
```

Potential providers:

```text
Pi
Herdr
local model
remote model
specialist agent
```

The provider model may evolve later.

---

# 21. Agent Recursion

Actions that invoke AI should generally use:

```toml
ai_accessible = false
```

Examples:

```text
ai.ask
ai.pi.open
ai.selection.explain
```

This prevents one AI from repeatedly invoking another AI action without explicit orchestration.

---

# 22. AI and CLI

AI-facing actions should be callable through the same runtime used by CLI where appropriate.

Example:

```text
omivoid action run theme.wallpaper.select
```

and an AI tool call to:

```text
theme.wallpaper.select
```

should resolve the same capability.

---

# 23. Action Discovery for AI

AI should eventually be able to query available actions.

Conceptual request:

```text
list available AI-accessible actions
```

The result should be filtered by:

* `ai_accessible`;
* current context;
* platform availability;
* dependencies;
* user policy.

---

# 24. Do Not Expose the Entire Registry Blindly

AI does not necessarily need every action.

Expose only the subset relevant to:

* current context;
* current agent role;
* permissions;
* environment.

This reduces both risk and tool-selection ambiguity.

---

# 25. Structured Results

AI should receive machine-readable results.

Example:

```json
{
  "action": "network.wifi.toggle",
  "success": true,
  "state": {
    "enabled": false
  }
}
```

This is preferable to parsing arbitrary shell output.

---

# 26. Structured Errors

Example:

```json
{
  "action": "ai.selection.explain",
  "success": false,
  "error": {
    "code": "CONTEXT_UNAVAILABLE",
    "message": "No text selection is available."
  }
}
```

Agents should respond to error codes rather than guessing from stderr.

---

# 27. Local-First Behaviour

Where practical, core AI interaction should support local tooling.

The desktop should not require permanent cloud connectivity merely to expose the AI interaction layer.

However, Omivoid should remain capable of invoking remote providers where configured.

---

# 28. Privacy

Context should be sent only to the selected AI provider necessary for the requested operation.

The architecture should leave room for future provider policies such as:

```text
local-only
trusted-remote
any-provider
```

Full data-classification policy is outside Phase 1.

---

# 29. User Awareness

When a task will leave the local machine, the eventual system should make this clear where practical.

For example:

```text
Run locally
Send to desktop
Send to IBIS server
```

This becomes especially important for research documents, code and private project context.

---

# 30. Herdr Delegation

Future workflow:

```text
project.delegate
       ↓
Herdr
       ↓
available execution target
       ↓
remote/local agent
```

The user should not need to know machine-specific orchestration commands.

---

# 31. Tailscale

Remote Omivoid/IBIS communication may use the existing Tailscale network.

Tailscale is transport infrastructure.

It should not become part of canonical action naming.

Correct:

```text
project.delegate
```

Incorrect:

```text
tailscale.project.delegate
```

---

# 32. UI Presentation

AI responses may be presented through:

* terminal;
* overlay;
* dedicated panel;
* editor integration;
* project UI.

The appropriate presentation depends on action context.

Example:

```text
ai.selection.explain
```

may benefit from a transient overlay.

A coding task may be better opened in a terminal/editor.

---

# 33. Do Not Build a Giant AI Shell in Phase 1

Phase 1 should prove:

* namespace;
* provider invocation;
* registry exposure;
* context concept;
* permissions concept.

It should not attempt to solve:

* full orchestration;
* persistent agent memory;
* distributed execution;
* agent marketplace;
* large context manager;
* autonomous desktop management.

---

# 34. Phase 1 AI Priorities

Priority order:

1. implement `Super+A`;
2. provide visible AI namespace;
3. implement `ai.pi.open`;
4. implement `ai.ask` through the chosen provider;
5. implement `ai.herdr.open` if Herdr is available;
6. test selected-text acquisition;
7. implement one context action if reliable;
8. expose at least one non-AI Omivoid action safely to an AI provider as proof of concept.

---

# 35. Phase 1 Proof-of-Concept Capability

A strong Phase 1 demonstration would be:

```text
User:
"Open my browser."

       ↓
Pi
       ↓
Action discovery
       ↓
app.browser.open
       ↓
Omivoid action runner
       ↓
configured browser
```

This proves that AI is participating in the Omivoid action architecture rather than merely executing arbitrary shell commands.

---

# 36. Phase 1 Acceptance Criteria

AI integration is successful when:

* `Super+A` provides a coherent AI entry point;
* Pi can be invoked;
* Herdr has a defined integration position;
* AI actions exist in the registry;
* recursion is controlled;
* context actions fail safely when context is unavailable;
* at least one controlled Omivoid capability can be exposed to AI;
* heavy remote infrastructure is not required for normal laptop operation;
* future distributed execution can be added without redesigning the interaction model.

The Phase 1 goal is not maximum autonomy.

It is to establish AI as a **controlled, native participant in the Omivoid desktop architecture**.
