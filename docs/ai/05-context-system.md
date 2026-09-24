# Omivoid AI Context System Specification

**Project:** `omivoid-lmde`
**Subsystem:** AI
**Document:** 05
**Status:** Phase 1 Specification

---

# 1. Purpose

This document defines how Omivoid identifies, collects, packages and supplies contextual information to AI providers.

Context is one of the key differences between:

```text
generic AI chat
```

and:

```text
AI integrated into the user's working environment
```

The objective is:

> **Give AI the minimum accurate context required to assist effectively, while keeping context visible, controlled and provider-independent.**

---

# 2. Architectural Position

```text
Desktop / Project
       │
       ▼
Context Collectors
       │
       ▼
Context Normalisation
       │
       ▼
Omivoid Context Object
       │
       ├── policy
       ├── size controls
       └── privacy controls
              │
              ▼
       Provider Adapter
              │
              ▼
             AI
```

---

# 3. Context Is Not Prompt Text

Omivoid should treat context as structured information.

It should not merely concatenate arbitrary desktop data into a giant provider-specific prompt.

Preferred:

```text
context object
     ↓
provider adapter
     ↓
provider representation
```

---

# 4. Initial Context Types

Canonical context types should initially include:

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

More may be added later.

---

# 5. Context Object

Conceptual structure:

```json
{
  "type": "file",
  "content": "...",
  "source": {
    "path": "/project/src/example.php"
  },
  "metadata": {
    "language": "php"
  }
}
```

Exact schema may evolve.

---

# 6. Context Collection Principle

Context must come from a known source.

Do not silently infer context from unrelated state.

Example:

```text
Current clipboard
```

must not automatically be treated as:

```text
Current selection
```

unless the acquisition mechanism explicitly establishes this relationship.

---

# 7. Accuracy Over Convenience

If reliable context cannot be obtained:

```text
CONTEXT_UNAVAILABLE
```

is preferable to stale or guessed data.

This is particularly important for:

* selected text;
* active browser content;
* active editor file.

---

# 8. Context Provenance

Every context object should know where it came from.

Examples:

```text
selection
clipboard
filesystem
editor integration
browser integration
project definition
```

This improves debugging and trust.

---

# 9. Context Visibility

Where practical, the user should be able to see which context is being supplied.

Example:

```text
Ask AI

Context:
  Project: omivoid-lmde
  File: docs/ai/05-context-system.md
```

---

# 10. Context Scope

Context should be classified conceptually by scope:

```text
explicit
active
project
ambient
```

---

# 11. Explicit Context

Explicit context is deliberately chosen by the user.

Examples:

* selected file;
* selected text;
* pasted content;
* file passed through CLI.

This is the strongest context signal.

---

# 12. Active Context

Active context comes from the currently active work surface.

Examples:

* current editor file;
* current browser page;
* current terminal directory.

It should only be used when acquisition is reliable.

---

# 13. Project Context

Project context describes the currently active project.

Examples:

```text
project root
AGENTS.md
README
documentation
Git metadata
project configuration
```

Project context is specified further in `06-project-context.md`.

---

# 14. Ambient Context

Ambient context might include:

* date;
* active workspace;
* machine role;
* desktop state.

Use sparingly.

AI should not receive large amounts of ambient information simply because it is available.

---

# 15. Context Priority

When multiple contexts are available, use precedence such as:

```text
explicit
   ↓
active
   ↓
project
   ↓
ambient
```

Explicit user choice should normally override implicit context.

---

# 16. Selection Context

Selection context should represent text or another selection explicitly made by the user.

Desired flow:

```text
User selects text
       ↓
Super+A,E
       ↓
selection collector
       ↓
context object
```

---

# 17. Wayland Selection Challenge

Selection retrieval under Wayland may be application-dependent.

Phase 1 MUST investigate the actual environment before declaring selection context reliable.

Potential mechanisms should be evaluated rather than assumed.

---

# 18. Clipboard Is Separate

Clipboard context is its own context type:

```text
clipboard
```

Do not relabel it as:

```text
selection
```

This distinction prevents accidental use of stale clipboard data.

---

# 19. Clipboard Context

Clipboard context may support explicit commands such as:

```text
Explain Clipboard
Summarise Clipboard
Ask About Clipboard
```

This may provide a useful fallback when direct selection capture is unavailable.

---

# 20. File Context

File context should represent a specific file.

Metadata may include:

```text
path
filename
extension
language
size
project
modified state
```

Content inclusion should depend on size and policy.

---

# 21. File Size Limits

Do not automatically pass extremely large files into AI.

Possible strategy:

```text
small file
   → full content

large file
   → metadata + explicit approval / chunking
```

Exact limits should be configurable later.

---

# 22. Binary Files

Binary files should not be inserted as raw prompt data.

Instead:

* identify file type;
* use an appropriate extractor if supported;
* or report unsupported context.

---

# 23. Directory Context

Directory context should primarily supply structure.

Example:

```text
src/
├── Controllers/
├── Models/
└── Views/
```

Do not automatically load every file in a directory.

---

# 24. Directory Expansion

An AI provider may request additional files through tools when permitted.

This is preferable to dumping the entire directory into initial context.

---

# 25. Current Working Directory

Terminal context may include:

```text
cwd
```

This can be useful for coding and project work.

Do not assume the terminal's working directory is the same as the active project unless verified.

---

# 26. Editor Context

Editor context may include:

```text
current file
cursor location
selection
language
project root
```

This requires editor-specific integration.

Phase 1 may begin with file-path/context integration rather than deep editor protocol support.

---

# 27. Browser Context

Browser context may eventually include:

```text
URL
title
selected text
page content
```

Browser page extraction requires explicit browser integration and should not be assumed from the active window title.

---

# 28. Terminal Context

Terminal context may include:

```text
cwd
command
selected text
recent output
```

Recent terminal output may contain secrets.

It must not be collected automatically without careful design.

---

# 29. Project Context

Project context should be compositional rather than one enormous blob.

Conceptually:

```text
Project Context
├── identity
├── instructions
├── structure
├── documentation
├── Git state
└── task state
```

The provider should receive only relevant pieces.

---

# 30. Context Request

An AI action should declare required/preferred context.

Example:

```toml
contexts = ["selection"]
```

or conceptually:

```text
required: selection
```

Another action may accept:

```text
selection
file
clipboard
```

---

# 31. Required vs Optional Context

The context system should distinguish:

```text
required
optional
preferred
```

Example:

```text
ai.selection.explain
```

requires selection.

Generic:

```text
ai.ask
```

does not.

---

# 32. Context Resolver

A context resolver may determine which available context satisfies an action.

Conceptual:

```text
action requests context
       │
       ▼
context resolver
       │
       ├── explicit context?
       ├── active context?
       └── project context?
              │
              ▼
         selected context
```

---

# 33. No Silent Context Substitution

If an action specifically requires:

```text
selection
```

the resolver should not silently substitute:

```text
clipboard
```

unless the action explicitly permits it.

---

# 34. Context Combination

Some requests may benefit from multiple contexts.

Example:

```text
current file
+
project instructions
```

Context combination should be deliberate.

---

# 35. Context Envelope

Conceptual combined request:

```json
{
  "contexts": [
    {
      "type": "file",
      "content": "..."
    },
    {
      "type": "project",
      "metadata": {
        "name": "omivoid-lmde"
      }
    }
  ]
}
```

---

# 36. Context Size Budget

Providers have finite context capacity and cost.

Omivoid should eventually support a context budget.

Conceptually:

```text
high priority:
    explicit user selection

medium priority:
    current file

lower priority:
    general project documentation
```

Phase 1 can implement simple limits.

---

# 37. Relevance

More context is not automatically better.

The desired model is:

```text
minimum sufficient context
```

rather than:

```text
everything Omivoid can collect
```

---

# 38. Provider Conversion

Provider adapters are responsible for converting Omivoid context into provider-specific form.

Pi adapter example:

```text
Omivoid context
    ↓
Pi-compatible files/prompts/tools
```

Other providers may use different mechanisms.

---

# 39. Context Locality

Omivoid should distinguish context collection from model processing location.

A context may be collected locally but sent to a remote model.

The UI should not conflate these concepts.

---

# 40. Privacy Classification

Future context policy may classify context such as:

```text
public
personal
project
sensitive
secret
```

Phase 1 does not require a full data classification engine.

However, secrets must never be intentionally supplied as normal AI context.

---

# 41. Secret Avoidance

Collectors should avoid known high-risk sources such as:

```text
.env
private keys
credential stores
tokens
password files
```

unless the user explicitly performs an appropriate authorised task.

General project context should exclude obvious secrets by default.

---

# 42. Git-Ignored Files

Being Git-ignored does not automatically mean a file is secret.

However, Git ignore state can be a useful signal in future context policy.

Do not use it as the sole security rule.

---

# 43. User Control

Users should eventually be able to:

```text
add context
remove context
inspect context
clear context
```

A graphical context chip model may work well in DMS.

Example:

```text
[Project: Omivoid] [File: ai.py] [×]
```

---

# 44. Context Persistence

Transient context should normally disappear when the interaction ends.

Project context may persist while the project remains active.

Do not persist arbitrary selected text indefinitely.

---

# 45. Session Context

Pi may maintain conversational context internally.

That is separate from Omivoid environment context.

The two should not be conflated.

---

# 46. Stale Context

Context should include enough identity to detect stale references where practical.

Example:

```text
file path
modification time
```

A long-running AI session should not assume a file is unchanged.

---

# 47. Current File Changes

If AI is working on a file that changes externally, the provider should re-read it through tools where appropriate rather than relying indefinitely on the original context.

---

# 48. Context Errors

Relevant stable errors include:

```text
CONTEXT_UNAVAILABLE
CONTEXT_UNSUPPORTED
CONTEXT_TOO_LARGE
CONTEXT_ACCESS_DENIED
CONTEXT_STALE
```

Only implement errors that are needed; preserve a coherent vocabulary.

---

# 49. Context Logging

Do not log context content by default.

Operational logs may record:

```text
context type
source
size
status
```

but not full sensitive contents.

---

# 50. Phase 1 Context Proofs

Phase 1 should attempt three progressively useful context cases.

## Proof 1 — Explicit text

```text
user supplies text
   ↓
ai.ask
```

## Proof 2 — File

```text
known file
   ↓
Pi
```

## Proof 3 — Selection

```text
desktop selection
   ↓
ai.selection.explain
```

The third may be deferred if reliable acquisition cannot be established.

---

# 51. File Context CLI Proof

Potential command:

```text
omivoid ai ask --file docs/00-project-overview.md \
  "Summarise the architectural goals."
```

Exact syntax is implementation-dependent.

The purpose is to prove context independently of DMS.

---

# 52. Selection Fallback

If direct selection capture is unreliable, Phase 1 may offer:

```text
copy selection
   ↓
Explain Clipboard
```

as an explicit fallback.

This must be labelled clipboard-based rather than pretending direct selection capture works.

---

# 53. Context and Capabilities

Context and capabilities are independent concepts.

Example:

```text
Context:
current file

Capabilities:
open editor
run tests
search project
```

The provider may use both to complete a task.

---

# 54. Context and Project Instructions

Project-local instructions such as:

```text
AGENTS.md
```

may be considered high-priority project context for development agents.

This should be handled by the project context layer rather than inserted globally into every AI interaction.

---

# 55. DMS Role

DMS may provide:

* context indicators;
* context picker;
* add/remove UI;
* active project indicator.

DMS should not become the canonical context store.

---

# 56. No Giant Context Daemon

Phase 1 does not require a persistent daemon continuously scraping desktop state.

Prefer on-demand collectors.

Example:

```text
AI action invoked
    ↓
collect required context
    ↓
submit request
```

---

# 57. Collector Architecture

Suggested:

```text
ai/context/
├── selection
├── clipboard
├── file
├── directory
├── project
├── editor
├── browser
└── terminal
```

Only implement required collectors.

---

# 58. Collector Contract

Conceptually:

```text
available()
collect()
describe()
```

A collector should return either:

```text
context object
```

or a clear failure.

---

# 59. Context Provider Independence

The selection collector should not know anything about Pi.

The Pi adapter should not know how desktop selection was acquired.

Correct:

```text
collector
   ↓
context object
   ↓
provider adapter
```

---

# 60. Test Cases

Initial tests should include:

```text
explicit text
empty text
existing file
missing file
oversized file
clipboard present
clipboard empty
selection unavailable
binary file
restricted file
multiple context items
```

---

# 61. Phase 1 Completion Criteria

The context system is complete for the first AI milestone when:

* context types are defined;
* explicit text works;
* file context works;
* provider adapter consumes structured context;
* unavailable context fails explicitly;
* sensitive content is not automatically harvested;
* selection acquisition has been investigated and either implemented or formally deferred;
* DMS can display context indicators for implemented context types.

---

# 62. Guiding Principle

The context system should make AI more useful without making it opaque.

The user should be able to answer:

> **What is the AI looking at right now?**

Omivoid should have a clear and accurate answer.
