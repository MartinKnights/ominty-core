# DMS AI Evaluation — AI-17

**Date:** 2026-09-15
**Stage:** AI-17 (docs/ai/10-ai-phase-1-implementation-plan.md §23)
**Status:** Complete — decision recorded

This document evaluates DMS AI options before building an AI surface, per
ADR-006 (check DMS core → existing plugin → extend → Ominty component →
standalone) and docs/ai/10 §23. It is part of the implementation record
(AGENTS.md §28).

---

## 1. Scope

Evaluate:

```text
DMS core
installed DMS plugins
AI Assistant plugin (aiAssistant)
launcher provider capabilities
plugin API
```

and classify per ADR-006:

```text
ADOPT · ADOPT WITH CONFIGURATION · EXTEND · REFERENCE ONLY · DEFER · REJECT
```

---

## 2. DMS core

`dms ipc` exposes **no AI target**. Relevant targets are launcher surfaces:

```text
launcher     close, open, openQuery, openWith, toggle, toggleQuery, toggleWith
spotlight    close, open, openQuery, openWith, toggle, toggleQuery, toggleWith
```

DMS owns no AI provider, prompt, or policy layer. It provides presentation
surfaces only.

**Classification: REFERENCE ONLY** for AI (no AI capability to adopt).

---

## 3. Installed plugins

```text
dankLauncherKeys  launcher
dankKDEConnect    widget
omintyActions    launcher   (Ominty)
quickCapture      composite
wallpaperCarousel daemon
```

No AI plugin is installed. None provides AI capability access.

---

## 4. AI plugins in the community registry

Two AI-related plugins exist (registry: `plugins.danklinux.com`):

### 4.1 `aiAssistant` — AI Assistant (`devnullvoid/dms-ai-assistant`)

| Field | Value |
|---|---|
| Capabilities | `slideout`, `ai` |
| Dependencies | curl, wl-copy |
| Purpose | Chat assistant: streaming, markdown, history, multi-provider (OpenAI, Anthropic, Gemini, Ollama, Inception, custom OpenAI-compatible) |
| Trigger | `dms ipc call plugins toggle aiAssistant` |

It talks to providers **directly over curl** with its own configuration and
key handling. Adopting it as the AI surface would:

* create a **second AI invocation path** (docs/ai/10 §25);
* bypass the Ominty provider layer (`ai.ask`, `ai.pi.open`);
* bypass Action Registry policy (`ai_accessible`, `risk`, `confirmation`) —
  docs/ai/09 §2, §5–6;
* require forking to route through Ominty (discouraged — AGENTS.md §13,
  ADR-006).

**Classification: REFERENCE ONLY.** Useful as a presentation reference; may be
revisited as **ADOPT WITH CONFIGURATION** only if Ominty's provider layer can
back a presentation surface without a second invocation path.

### 4.2 `dmsAgent` — DMS Agent (`Francisdelca/dms-agent`)

| Field | Value |
|---|---|
| Capabilities | `dankbar-widget` |
| Dependencies | claude |
| Compositors | niri |
| Purpose | Agentic desktop control via Claude Code (open apps, switch windows, play music, web search) |

It controls the desktop through an agent with shell access, bypassing the
Action Registry and Ominty policy entirely.

**Classification: REJECT.** Directly conflicts with AGENTS.md §16–17 and
docs/ai/09 §2 ("avoid an unrestricted privileged shell as the normal desktop
control architecture").

---

## 5. Launcher provider capabilities

The DMS launcher API is the interaction surface available to plugins:

```text
type: "launcher"
trigger: string
getItems(query)  → launcher items
executeItem(item) → run item action
signal itemsChanged()
```

Our `omintyActions` plugin already bridges the Action Registry into it
(ADR-006 §10–11). No key-chord or submap API is exposed.

---

## 6. Platform limitation: chords

Verified directly:

```text
$ niri validate   # nested keybind config
Error: only one action is allowed per keybind
```

* **Niri has no keybinding chords** (no `Super+A` → then `A` sequences).
* **DMS has no submap/chord mode.**
* The registry supports chord notation (`Super+A,A`, docs/03 §12) and the
  generator already excludes chords from the Niri fragment (they are
  shell-handled).

**Consequence:** the `Super+A` AI prefix cannot be a native two-key chord. It
is realised through the DMS launcher: `Super+A` opens the spotlight in **AI
mode**, where continued typing filters the AI actions and Enter executes.

---

## 7. Decision

| Layer | Decision |
|---|---|
| DMS core AI | REFERENCE ONLY |
| `aiAssistant` plugin | REFERENCE ONLY (revisit as ADOPT WITH CONFIGURATION only behind the Ominty provider layer) |
| `dmsAgent` plugin | REJECT |
| AI presentation | **EXTEND DMS** — extend the `omintyActions` launcher plugin with an AI mode |
| `Super+A` binding | Niri bind → `dms ipc call spotlight openQuery "!ai "` (AI-mode sentinel) |
| Chords (`Super+A,A`, `Super+A,P`) | Registry intent/hint only; realised via the AI menu (no native chord support) |

The AI surface therefore remains:

```text
Super+A
   ↓
DMS spotlight (AI mode, "!ai" sentinel)
   ↓
Ominty Actions launcher plugin
   ↓
ai.ask / ai.pi.open  (Action Registry)
   ↓
Ominty provider layer + policy
```

No second AI invocation path; no custom AI UI; the Action Registry and
Ominty policy remain authoritative.
