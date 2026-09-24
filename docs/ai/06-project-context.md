# Omivoid Project Context Specification

**Project:** `omivoid-lmde`
**Subsystem:** AI
**Document:** 06
**Status:** Phase 1 Specification

---

# 1. Purpose

This document defines how Omivoid represents and supplies project-specific context to AI.

Projects are a primary unit of work within Omivoid.

A project may represent:

* software development;
* research;
* writing;
* documentation;
* system design;
* infrastructure work;
* business planning;
* another structured body of work.

The objective is:

> **Allow AI to understand the project the user is currently working on without indiscriminately loading the entire project into context.**

---

# 2. Architectural Position

```text
Project
   │
   ▼
Project Discovery
   │
   ▼
Project Context Resolver
   │
   ├── identity
   ├── instructions
   ├── structure
   ├── documentation
   ├── Git
   └── task state
          │
          ▼
   Context Selection
          │
          ▼
      AI Provider
```

---

# 3. Project Is a Context Boundary

A project establishes a logical boundary around related work.

Example:

```text
~/Projects/omivoid-lmde/
```

may represent one project.

The project root should be identifiable without requiring AI to infer it repeatedly.

---

# 4. Project Context Is Compositional

Project context must not be treated as:

```text
read every file
     ↓
send everything to AI
```

Instead:

```text
Project Context
│
├── identity
├── instructions
├── structure
├── relevant documentation
├── relevant files
├── Git state
└── task/workflow state
```

Components should be supplied according to need.

---

# 5. Project Identity

Basic project context may include:

```text
name
root
type
description
repository
```

Example conceptual metadata:

```toml
[project]
name = "omivoid-lmde"
type = "software"
```

A formal Omivoid project manifest is not required for Phase 1.

---

# 6. Project Discovery

Phase 1 should support practical project discovery using existing signals.

Potential signals include:

```text
Git repository root
AGENTS.md
README
explicit project root
current working directory
```

Explicit user selection should take precedence over inference.

**Phase 1 implementation note (AI-35).** Implementation revealed that the
Git root and the instruction boundary can differ. In this repository the
Git root is the parent directory, while the project instructions
(`AGENTS.md`) live in `omivoid-lmde/`; using the Git root alone produced
the wrong project. Phase 1 therefore resolves:

```text
explicit root (--root / OMIVOID_PROJECT)
    → nearest AGENTS.md (walk-up, bounded by home)
    → Git root
    → current working directory
```

`AGENTS.md` outranks the Git root because it is the strongest
project-instruction boundary (docs/ai/06 §8–9). See
`docs/implementation/ai-phase-f.md` and
`cli/omivoidlib/ai/project/__init__.py`.

---

# 7. Project Root

Once established, the project root becomes the boundary for many project-scoped operations.

Example:

```text
project root
    │
    ├── source
    ├── docs
    ├── tests
    └── project instructions
```

This is particularly important for safe AI file access.

---

# 8. Project Instructions

Project-local instructions should have high priority.

Examples:

```text
AGENTS.md
CONTRIBUTING.md
project-specific AI instructions
```

For software projects, `AGENTS.md` should be recognised as an important instruction source where applicable.

---

# 9. `AGENTS.md`

When present, `AGENTS.md` may define:

* architectural constraints;
* coding standards;
* testing requirements;
* files not to modify;
* implementation workflow;
* project-specific rules.

AI working on the project should receive relevant instructions before proposing or making project changes.

---

# 10. Instruction Hierarchy

Project instructions should not override higher-level security or Omivoid policy.

Conceptually:

```text
Omivoid security/policy
        ↓
provider/tool policy
        ↓
project instructions
        ↓
task instructions
```

---

# 11. README

README files provide useful project orientation.

They should not automatically be treated as authoritative implementation instructions if more specific project documentation exists.

---

# 12. Project Structure

AI may receive a bounded project tree.

Example:

```text
omivoid-lmde/
├── AGENTS.md
├── actions/
├── adapters/
├── ai/
├── cli/
├── docs/
└── niri/
```

Avoid recursively supplying huge trees unnecessarily.

---

# 13. Relevant Files

Relevant files should be selected according to the current task.

Example:

```text
Task:
"Modify Pi provider handling"

Relevant:
ai/providers/pi/*
docs/ai/01-provider-interface.md
docs/ai/02-pi-integration.md
```

This is preferable to sending the entire repository.

---

# 14. Documentation Context

Project documentation may be particularly valuable for AI planning.

Omivoid should support discovering relevant documents without loading all documentation automatically.

---

# 15. Git Context

Useful Git context may include:

```text
branch
working-tree status
modified files
recent commits
diff
```

Only supply what the task requires.

---

# 16. Dirty Working Tree

AI must not assume a dirty working tree contains its own changes.

Existing modifications may belong to the user or another agent.

Before modifying files, tooling should distinguish existing changes where practical.

---

# 17. Git Is Not Required

Projects need not be Git repositories.

Project context should degrade gracefully when Git is absent.

---

# 18. Project Type

Future project types might include:

```text
software
research
writing
book
infrastructure
website
business
```

Project type may influence available workflows but should not create rigid silos.

---

# 19. Writing Projects

Writing context may prioritise:

```text
outline
current chapter
research notes
references
style instructions
previous chapters
```

Do not assume software-development context structures apply to writing projects.

---

# 20. Research Projects

Research context may prioritise:

```text
research question
sources
notes
claims
references
open questions
```

---

# 21. Development Projects

Development context may prioritise:

```text
AGENTS.md
architecture
source tree
current file
tests
Git state
```

---

# 22. Project Context Levels

A useful conceptual model is:

```text
Level 0 — identity
Level 1 — instructions
Level 2 — structure
Level 3 — relevant documents/files
Level 4 — task-specific deep context
```

Higher levels should be loaded only as required.

---

# 23. Active Project

Omivoid may maintain the concept of:

```text
current project
```

This can support:

```text
Super+P
Super+A
Pi
DMS
```

without repeatedly selecting the same root.

---

# 24. Project Selection

Project selection may eventually occur through:

```text
Super+P,O
```

or the DMS launcher.

Phase 1 may use explicit CLI/project-root selection first.

---

# 25. Project Switching

Switching projects should change project context without necessarily changing Pi provider configuration.

```text
Project A
   ↓
Pi

switch

Project B
   ↓
same Pi provider
   ↓
different project context
```

---

# 26. Project AI

A project-aware AI request should conceptually become:

```text
request
+
project identity
+
project instructions
+
task-relevant context
```

not:

```text
request
+
entire project
```

---

# 27. Context Budget

Project context must respect the context budget defined by the general context system.

Priority should normally be:

```text
task instructions
explicit files
project instructions
active file
relevant docs
general structure
background information
```

---

# 28. Project File Security

Project context should remain bounded to the project root by default.

Path traversal outside the project root should require explicit intent or broader tooling authority.

---

# 29. Secret Exclusion

General project context should exclude obvious credential material such as:

```text
.env
*.key
private keys
credential files
secret stores
```

Do not assume every ignored file is secret, but apply conservative handling to obvious credential material.

---

# 30. Project Context and Shell

Pi may still use shell tools inside a project.

Project context does not replace normal development tooling.

Instead it provides semantic orientation.

---

# 31. Project Actions

Potential actions include:

```text
project.open
project.info
project.context.show
project.ai.open
project.terminal.open
project.editor.open
project.delegate
```

Only stable, useful actions should be added to the registry.

---

# 32. `Super+P`

Project interaction should eventually integrate:

```text
Super+P
│
├── O Open
├── N New
├── R Recent
├── T Terminal
├── E Editor
├── A AI
├── S Send / Delegate
└── C Context
```

This complements rather than duplicates `Super+A`.

---

# 33. Project Context Inspection

The user should eventually be able to inspect:

```text
What does Omivoid currently consider the project?
```

Example:

```text
Project: omivoid-lmde
Root: ~/Projects/omivoid-lmde
Instructions: AGENTS.md
Git: clean
```

---

# 34. Project Context CLI

Potential conceptual commands:

```bash
omivoid project current
omivoid project context
omivoid project open <path>
```

Exact CLI design should follow existing conventions.

---

# 35. Provider Independence

Project context must not be Pi-specific.

Correct:

```text
Project Resolver
      ↓
Project Context
      ↓
Provider Adapter
      ↓
Pi
```

Later:

```text
Project Context
      ↓
Herdr
```

should be possible.

---

# 36. Delegation

Project context is particularly important for remote delegation.

A delegated task should identify:

```text
project
task
required context
constraints
expected result
```

rather than sending an ambiguous natural-language instruction alone.

---

# 37. Remote Project Identity

Remote systems may store the same project at different filesystem paths.

Therefore delegation should not assume:

```text
local path == remote path
```

Project identity must be separate from local filesystem location.

---

# 38. Future Project Registry

A future Omivoid project registry may map:

```text
project identity
     ↓
local path
desktop path
server path
repository
```

This is not required for the initial AI phase.

---

# 39. Phase 1 Proof

Initial project-context proof:

```text
cd ~/Projects/omivoid-lmde
       ↓
Omivoid identifies project
       ↓
reads project instructions
       ↓
Pi receives project identity/instructions
       ↓
user asks architecture question
       ↓
Pi answers with project context
```

---

# 40. Phase 1 Completion Criteria

Project context is sufficiently proven when:

* project root can be identified;
* project identity can be represented;
* `AGENTS.md` can be discovered where present;
* bounded project structure can be supplied;
* one project-aware Pi request works;
* project secrets are not automatically harvested;
* project context remains provider-independent.

---

# 41. Guiding Principle

> **A project gives AI orientation, not unrestricted ingestion.**

Omivoid should provide enough project context for Pi to understand what the user is working on while retaining clear boundaries around what information is supplied.
