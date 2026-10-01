# Ominty `Super+A` Interaction Specification

**Project:** `ominty-core`
**Subsystem:** AI
**Document:** 03
**Status:** Phase 1 Specification

---

# 1. Purpose

This document defines the primary human interaction model for AI within Ominty.

The canonical keyboard entry point is:

```text
Super+A
```

`Super+A` is not intended to be a single chatbot shortcut.

It is the root of the Ominty AI interaction namespace.

The objective is:

> **Make AI as predictable and discoverable as any other Ominty desktop capability.**

---

# 2. Design Principles

The `Super+A` interaction model should be:

* keyboard-first;
* discoverable;
* consistent;
* low-latency;
* context-aware;
* provider-independent;
* extensible;
* DMS-integrated;
* usable without memorising every binding.

---

# 3. Interaction Model

`Super+A` acts as an AI prefix.

Conceptually:

```text
Super+A
   │
   ▼
AI mode / palette
   │
   ├── A  Ask
   ├── P  Pi
   ├── H  Herdr
   ├── E  Explain
   ├── S  Summarise
   ├── R  Research
   ├── W  Writing
   ├── C  Coding
   ├── T  Delegate
   └── M  Models / Agents
```

Not every action needs to be implemented in the first milestone.

The namespace should remain stable even as implementation grows.

---

# 4. Canonical Initial Mapping

Recommended mapping:

| Binding     | Action                   | Purpose                             |
| ----------- | ------------------------ | ----------------------------------- |
| `Super+A`   | `ai.open`                | Open AI interface                   |
| `Super+A,A` | `ai.ask`                 | Ask default provider                |
| `Super+A,P` | `ai.pi.open`             | Open Pi directly                    |
| `Super+A,H` | `ai.herdr.open`          | Open Herdr interface                |
| `Super+A,E` | `ai.selection.explain`   | Explain current context/selection   |
| `Super+A,S` | `ai.selection.summarise` | Summarise current context/selection |
| `Super+A,R` | `ai.research`            | Start research workflow             |
| `Super+A,W` | `ai.write`               | Start writing workflow              |
| `Super+A,C` | `ai.code`                | Start coding workflow               |
| `Super+A,T` | `ai.delegate`            | Delegate task                       |
| `Super+A,M` | `ai.model.select`        | Models/providers/agents             |

Actions not yet implemented should either:

* be visibly unavailable;
* be omitted from the active UI;
* or be marked as future capability.

Do not silently map them to unrelated behaviour.

---

# 5. `ai.open`

`ai.open` is the generic AI entry point.

It should not necessarily launch Pi directly.

Preferred behaviour:

```text
Super+A
   ↓
DMS / Ominty AI interface
   ↓
AI options
```

Possible presentation:

```text
AI
───────────────────────
Ask
Explain
Summarise
Research
Write
Code
Pi
Herdr
Models / Agents
```

---

# 6. Prefix Overlay

When `Super+A` is pressed, Ominty should display the available next keys where practical.

Example:

```text
A  Ask
P  Pi
E  Explain
S  Summarise
R  Research
W  Writing
C  Code
T  Delegate
M  Models
Esc Cancel
```

This preserves the keyboard-first approach without requiring memorisation.

---

# 7. DMS-First Presentation

Per ADR-006, the preferred implementation order is:

```text
DMS core
   ↓
existing plugin
   ↓
extend existing plugin
   ↓
Ominty DMS plugin
   ↓
standalone UI
```

Before creating a dedicated Quickshell component, determine whether DMS can provide:

* launcher mode;
* chord overlay;
* prompt interface;
* AI result panel;
* action feedback.

---

# 8. Keyboard Independence From UI

The action semantics must not depend on the graphical implementation.

For example:

```text
Super+A,A
```

must invoke:

```text
ai.ask
```

whether the UI is implemented using:

* DMS launcher;
* DMS plugin;
* custom Quickshell;
* terminal fallback.

---

# 9. `ai.ask`

`ai.ask` means:

> Submit a general request to the configured default AI provider.

It must not mean:

> Open Pi.

If Pi is the default provider:

```text
ai.ask
   ↓
provider resolver
   ↓
pi
```

This preserves provider independence.

---

# 10. Prompt Entry

`ai.ask` should support fast prompt entry.

Possible UI:

```text
┌─────────────────────────────────────────┐
│ Ask Ominty AI...                       │
└─────────────────────────────────────────┘
```

The prompt interface should display relevant context indicators when context is attached.

Example:

```text
[Project: ominty-core] [File: provider.py]
```

---

# 11. Context Indicators

The user should be able to see what context is being sent.

Examples:

```text
Selection
Current File
Project
Clipboard
Browser Page
```

Avoid invisible context injection where practical.

---

# 12. Context Confirmation

Routine context such as current project metadata may be implicitly included according to configuration.

Sensitive or large context should be explicit.

The context system specification defines these rules.

---

# 13. `ai.pi.open`

`ai.pi.open` explicitly launches Pi.

This should generally open the normal interactive Pi environment.

Expected path:

```text
Super+A,P
   ↓
ai.pi.open
   ↓
configured terminal
   ↓
Pi
```

Pi's native experience should remain available even if DMS provides a graphical AI panel.

---

# 14. `ai.herdr.open`

This action reserves the Herdr interaction location.

Initially it may:

* open an available Herdr interface;
* report unavailable;
* or remain disabled.

It must not be faked.

---

# 15. Explain Workflow

Desired:

```text
Select text
   ↓
Super+A,E
   ↓
ai.selection.explain
   ↓
context collection
   ↓
provider
   ↓
explanation
```

If no reliable selection exists:

```text
CONTEXT_UNAVAILABLE
```

should be returned.

---

# 16. Summarise Workflow

Desired:

```text
Context
   ↓
Super+A,S
   ↓
ai.selection.summarise
   ↓
provider
   ↓
summary
```

The same action may later work with:

* selection;
* current document;
* browser page;
* file.

The context type should be explicit.

---

# 17. Research Mode

`Super+A,R` should eventually start a research-oriented workflow.

Potential behaviour:

```text
Research
  │
  ├── question
  ├── current project context
  ├── selected source
  └── research tools
```

This should not simply be a different prompt string hard-coded into the UI.

Prefer a reusable workflow or skill definition.

---

# 18. Writing Mode

`Super+A,W` may expose workflows such as:

```text
Draft
Rewrite
Critique
Expand
Condense
Structure
Compare
```

Writing functionality should be implemented above the generic provider interface.

---

# 19. Coding Mode

`Super+A,C` may expose:

```text
Explain code
Review file
Review diff
Fix issue
Plan implementation
Run tests
```

Pi's native coding capabilities should remain available.

The Ominty UI primarily provides faster context-aware entry.

---

# 20. Delegation

`Super+A,T` is reserved for controlled task delegation.

Future flow:

```text
task
 ↓
ai.delegate
 ↓
Herdr
 ↓
target selection
 ↓
remote execution
```

Delegation must not be implemented merely as arbitrary SSH execution.

---

# 21. Model / Agent Selection

`Super+A,M` is intended as a future interface for:

* provider;
* model;
* agent;
* workflow.

This distinction matters.

For example:

```text
Provider: Pi
Model:    Claude / local model / other
Agent:    coding
Workflow: research
```

Do not collapse all of these concepts into a single "model" selector.

---

# 22. Esc Behaviour

`Esc` should cancel or close transient AI interfaces.

If a request is already executing, the UI may distinguish:

```text
Esc
    close UI

Ctrl+C / cancel action
    terminate request
```

depending on implementation.

---

# 23. Navigation

AI menus should follow Ominty interaction conventions:

```text
Arrow keys    navigate
Enter         execute
Esc           cancel
Tab           next region
Shift+Tab     previous region
```

Search results should also support keyboard navigation.

---

# 24. Direct Actions vs Palette

Common AI actions may have direct chords.

Less common AI actions should be discoverable through the AI palette rather than consuming many global bindings.

Preferred:

```text
few stable shortcuts
+
searchable AI action list
```

---

# 25. Action Registry Source

The `Super+A` interface should be derived from Action Registry metadata where practical.

Example:

```toml
[action."ai.selection.explain"]
name = "Explain Selection"
category = "AI"
keys = ["Super+A,E"]
discoverable = true
```

This prevents UI/keybinding drift.

---

# 26. Availability

The UI should reflect provider/action availability.

Example:

```text
Ask                available
Pi                 available
Herdr              unavailable
Explain Selection  unavailable — no context
```

Do not make unavailable functions appear operational.

---

# 27. Capability Awareness

The AI UI may eventually display what Ominty actions are available to AI.

For example:

```text
Capabilities: 21
Restricted:    6
Unavailable:   3
```

Not required for initial implementation.

---

# 28. AI Status

A lightweight status indicator may eventually show:

```text
provider
model
local/remote
project
context
```

Example:

```text
Pi · local interface · Project: ominty-core
```

Avoid clutter.

---

# 29. Locality Indicator

Where feasible, indicate whether the active model request is expected to remain local or use a remote service.

Example:

```text
LOCAL
REMOTE
```

This should be derived from provider/model configuration rather than guessed.

---

# 30. Terminal Fallback

If the graphical AI interface is unavailable, Ominty should retain CLI/terminal access.

Examples:

```text
ominty ai ask "..."
ominty action run ai.pi.open
```

DMS failure must not make AI entirely inaccessible.

---

# 31. DMS Failure Behaviour

If DMS cannot present the AI UI:

```text
Super+A,P
```

may still launch Pi through the terminal where possible.

Other graphical workflows may return an explicit unavailable state.

---

# 32. AI UI State

The graphical interface may hold transient state such as:

* current prompt;
* displayed response;
* selected AI action.

It should not become the canonical owner of:

* provider sessions;
* project context;
* action policy.

---

# 33. Session Behaviour

Opening `ai.pi.open` should preserve Pi's own session behaviour.

The DMS prompt interface may initially use stateless requests.

Persistent graphical chat sessions can be added later if they provide real value.

---

# 34. Notifications

Longer AI actions may use DMS notifications for completion.

Example:

```text
Research summary ready
```

This should be used sparingly for interactive requests.

---

# 35. Streaming

Where provider support exists, AI responses should stream into the UI.

Streaming should not block:

* cancellation;
* navigation;
* error reporting.

---

# 36. Errors

Examples:

```text
No AI provider configured.
Pi is unavailable.
Current selection could not be obtained.
This action requires confirmation.
The requested action is not AI-accessible.
```

Avoid exposing raw stack traces in normal UI.

---

# 37. Initial Implementation Scope

Phase 1 should initially implement:

```text
Super+A
Super+A,A
Super+A,P
Super+A,E
Super+A,S
```

only where corresponding backend functionality exists.

Other entries may be reserved.

---

# 38. Minimum Usable Experience

A successful initial interaction should support:

```text
Super+A,A
    ↓
enter question
    ↓
Pi receives request
    ↓
response displayed
```

and:

```text
Super+A,P
    ↓
interactive Pi
```

---

# 39. Integration Test

Required test:

1. press `Super+A`;
2. AI options appear;
3. choose Ask;
4. enter prompt;
5. configured provider receives request;
6. response returns;
7. `Esc` closes interface;
8. normal desktop interaction remains functional.

---

# 40. Guiding Principle

`Super+A` should become to AI what `Super+Space` is to general Ominty actions:

> **A predictable, discoverable gateway into a larger capability system rather than a shortcut to one particular application.**
