Ominty AI Architecture

Project: "ominty-core"
Subsystem: AI
Document: 00
Status: Phase 1 Specification

---

1. Purpose

This document defines the overall AI architecture for Ominty.

AI is not treated as a separate chatbot application added to the desktop.

It is a first-class Ominty interaction surface capable of understanding context, assisting the user and invoking controlled Ominty capabilities.

The architectural objective is:

«AI should participate in Ominty through the same stable action and context architecture used by the rest of the desktop.»

---

2. Design Objectives

The Ominty AI subsystem should be:

- local-first;
- lightweight on laptops;
- provider-independent;
- context-aware;
- project-aware;
- action-aware;
- permission-controlled;
- scriptable;
- replaceable;
- capable of future delegation;
- capable of future remote execution.

It should not require the laptop to become the primary heavy-compute system.

---

3. Laptop Role

The Ominty laptop is primarily intended for:

- planning;
- research;
- writing;
- book development;
- web development;
- coding;
- documentation;
- project ideation;
- AI-assisted thinking;
- project preparation;
- task delegation.

Heavy workloads may later be delegated to other infrastructure.

Therefore the laptop AI architecture should optimise for:

interaction
context
coordination
delegation

rather than maximum local model capacity.

---

4. High-Level Architecture

                     USER
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Keyboard       DMS          CLI
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
               Ominty AI Layer
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
         Context Layer      Capability Layer
             │                   │
             │                   ▼
             │             Action Registry
             │                   │
             └─────────┬─────────┘
                       │
                       ▼
                 AI Provider
                       │
                 Phase 1: Pi
                       │
                       ▼
                 AI / Models

Future expansion:

                 Ominty AI Layer
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
            Pi                   Herdr
      local interaction       orchestration
                                   │
                               Tailscale
                                   │
                       ┌───────────┴───────────┐
                       ▼                       ▼
                 Main Desktop             IBIS Server
                                               │
                                              Agno

Remote delegation is not required for the initial AI implementation.

---

5. Architectural Layers

The AI subsystem is divided into:

Interaction Layer
Provider Layer
Context Layer
Capability Layer
Policy Layer
Delegation Layer

Each has a separate responsibility.

---

6. Interaction Layer

The interaction layer provides ways for the user to invoke AI.

Initial interfaces include:

Super+A
DMS launcher
Ominty CLI
contextual actions

Future interfaces may include:

- voice;
- editor integrations;
- browser integrations;
- project interfaces;
- remote devices.

The interaction layer must not depend directly on a specific AI provider.

---

7. Provider Layer

The provider layer connects Ominty to an AI implementation.

Initial provider:

Pi

Potential future providers include:

local model runner
remote API
Herdr
specialist agent
IBIS-hosted service

Ominty actions should therefore express intent such as:

ai.ask

rather than:

pi.ask

unless Pi itself is explicitly the intended target.

---

8. Context Layer

The context layer determines what information accompanies an AI request.

Potential contexts include:

selection
clipboard
file
directory
project
browser
editor
terminal
workspace

The context layer must distinguish between:

known context

and:

assumed context

Ominty MUST NOT silently provide guessed context.

---

9. Capability Layer

The capability layer exposes controlled Ominty actions to AI.

Example:

app.browser.open
app.editor.open
project.open
theme.wallpaper.select

AI should discover these capabilities from the Action Registry.

It should not require knowledge of implementation commands.

---

10. Policy Layer

The policy layer determines whether AI may invoke a capability.

Relevant registry metadata includes:

ai_accessible
risk
confirmation
contexts
platforms
requires

Example:

ai_accessible = true
risk = "routine"
confirmation = "never"

The policy layer exists between AI intent and action execution.

---

11. Delegation Layer

The delegation layer determines whether work should remain local or be handed to another system.

This is primarily a later-stage capability.

Expected architecture:

User
 ↓
Pi
 ↓
task analysis
 ↓
local or delegate?
      │
  ┌───┴────┐
  ▼        ▼
Local     Herdr
            │
         Tailscale
            │
      remote system

Pi should not itself become the distributed orchestration framework.

---

12. Pi's Architectural Role

Pi is the preferred Phase 1 AI provider for the Ominty laptop.

Its role is:

«lightweight local AI interaction and agent execution close to the user's working context.»

Pi may:

- conduct conversations;
- use project context;
- call tools;
- invoke Ominty actions;
- work with files;
- assist coding;
- assist research;
- assist writing;
- eventually request delegation.

Pi does not own Ominty's action architecture.

---

13. Herdr's Architectural Role

Herdr is intended to provide higher-level task delegation and orchestration.

Conceptually:

Pi
  = immediate interactive agent

Herdr
  = delegation/orchestration layer

A future request might flow:

User
 ↓
Pi
 ↓
"This task needs heavier resources"
 ↓
Herdr
 ↓
appropriate remote worker

Full Herdr implementation is outside the first AI milestone.

---

14. Agno's Architectural Role

Agno is expected to operate primarily on IBIS server infrastructure rather than on the laptop desktop.

It may host:

- business agents;
- specialist agents;
- persistent workflows;
- service agents;
- larger coordinated agent systems.

Ominty should not couple directly to Agno-specific implementation unless necessary.

Expected future path:

Ominty
   ↓
Herdr
   ↓
IBIS infrastructure
   ↓
Agno

---

15. Local-First Principle

AI interactions should remain local where practical.

Local-first means:

- local context collection;
- local policy enforcement;
- local action execution;
- local provider use where appropriate;
- explicit remote delegation.

It does not mean every model must run locally.

---

16. Model Independence

The Ominty AI architecture must not assume a particular model.

A provider may use:

- local LLM;
- remote LLM;
- coding model;
- reasoning model;
- specialist model.

Model selection belongs below the Ominty interaction contract.

---

17. Action Independence

AI should request:

app.browser.open

rather than know:

brave-browser

Likewise:

network.bluetooth.open

rather than know a DMS IPC command.

This keeps AI capabilities portable.

---

18. AI Action Namespace

Initial canonical actions include:

ai.open
ai.ask
ai.pi.open
ai.herdr.open
ai.selection.explain
ai.selection.summarise

Potential future actions include:

ai.research
ai.write
ai.code
ai.delegate
ai.model.select
ai.agent.select

New actions should only be added when their semantics are sufficiently stable.

---

19. "Super+A"

"Super+A" is the primary keyboard namespace for AI.

Conceptual map:

Super+A
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

The UI should expose only implemented/available functionality appropriately.

---

20. DMS Integration

DMS should provide AI presentation where practical.

Possible implementations include:

- launcher provider;
- AI panel;
- contextual menu;
- chord overlay;
- Ominty DMS plugin.

DMS does not own AI policy or provider selection.

---

21. AI Interaction Flow

Example:

Super+A,A
    │
    ▼
Ominty ai.ask
    │
    ▼
AI provider resolver
    │
    ▼
Pi
    │
    ▼
response
    │
    ▼
DMS presentation

---

22. Capability Invocation Flow

Example:

User:
"Open my browser"

        │
        ▼
       Pi
        │
        ▼
Capability discovery
        │
        ▼
app.browser.open
        │
        ▼
AI policy check
        │
        ▼
Action runner
        │
        ▼
app.launch adapter
        │
        ▼
configured browser

This is a required Phase 1 architecture proof.

---

23. Contextual AI Flow

Future example:

Selected text
      │
      ▼
Context collector
      │
      ▼
ai.selection.explain
      │
      ▼
Pi
      │
      ▼
Explanation

If selection cannot be reliably obtained:

CONTEXT_UNAVAILABLE

must be returned.

---

24. Project-Aware AI

Project context will eventually allow AI to understand:

- project root;
- documentation;
- source files;
- Git state;
- notes;
- project metadata;
- relevant tasks.

This enables:

Super+P,A

or equivalent project-aware AI interaction.

Project context is specified separately.

---

25. AI Should Not Own Desktop State

AI may query or change desktop state through controlled capabilities.

It should not maintain an independent competing representation of:

- applications;
- theme;
- networking;
- workspace;
- system configuration.

The relevant system remains authoritative.

---

26. Capability Discovery

AI should receive only capabilities appropriate to the current environment.

Filtering should consider:

ai_accessible
platform
dependencies
context
risk
policy
availability

This prevents AI from being presented with unusable or prohibited actions.

---

27. AI Security Boundary

The preferred model is:

AI
 │
 ▼
declared capability
 │
 ▼
policy
 │
 ▼
adapter
 │
 ▼
system

rather than:

AI
 │
 ▼
unrestricted shell
 │
 ▼
system

This does not prohibit shell use for legitimate development or novel tasks.

It establishes the preferred path for routine desktop capabilities.

---

28. AI and Shell Access

Pi may require shell capabilities for:

- coding;
- development;
- file operations;
- project tasks;
- investigation.

The Action Registry is not intended to replace every possible shell operation.

The distinction is:

known desktop capability
    → Ominty action

open-ended technical work
    → agent tools / shell where appropriate

---

29. Structured Results

Where practical, AI-facing action execution should return structured results.

Example:

{
  "success": true,
  "action": "app.browser.open"
}

Failure:

{
  "success": false,
  "error": {
    "code": "DEPENDENCY_MISSING",
    "message": "Configured browser is unavailable."
  }
}

This makes tool use more reliable.

---

30. Session Model

AI conversation/session state belongs primarily to the provider.

Ominty should not duplicate Pi's session management unless Ominty-specific cross-provider session behaviour later requires it.

---

31. Provider State

Provider-specific state should remain isolated.

Example:

Pi configuration
    → Pi

Ominty provider selection
    → Ominty

Avoid copying entire Pi configuration into Ominty.

---

32. Failure Isolation

AI failure must not break core desktop functionality.

If Pi fails:

- Niri continues;
- DMS continues;
- Action Registry continues;
- CLI continues;
- normal shortcuts continue.

AI is an integrated capability, not a dependency for basic desktop operation.

---

33. Offline Behaviour

The architecture should tolerate unavailable remote AI services.

Where possible:

- local actions remain available;
- local providers remain usable;
- unavailable providers are reported explicitly.

---

34. Observability

AI action invocation should be inspectable.

At minimum, debugging should be able to determine:

request
provider selected
context supplied
capability requested
policy decision
action result

Sensitive prompt/context data should not be logged indiscriminately.

---

35. Phase 1 Scope

Phase 1 AI should prove:

1. provider abstraction;
2. Pi integration;
3. "ai.ask";
4. "Super+A";
5. capability discovery;
6. AI → Ominty action execution;
7. basic context experiment;
8. policy enforcement.

---

36. Phase 1 Non-Goals

Do not initially build:

- distributed agent network;
- autonomous background agent;
- long-running Ominty AI daemon;
- full Herdr orchestration;
- Agno integration;
- voice;
- automatic remote workload routing;
- autonomous system administration;
- large memory framework;
- custom model server.

---

37. Success Criterion

The AI architecture is proven when a user can naturally interact with Pi through Ominty and Pi can safely consume Ominty context and invoke selected Ominty capabilities without needing implementation-specific desktop knowledge.

The defining principle is:

«Ominty gives AI context and capabilities; AI does not need to understand the machinery underneath them.»
