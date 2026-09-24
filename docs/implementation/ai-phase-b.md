# AI Phase B — Capability Catalogue, Pi Tool Bridge, AI-to-Action Proof

**Date:** 2026-09-15
**Stage:** AI-10, AI-11, AI-12 (docs/ai/10-ai-phase-1-implementation-plan.md §16–18)
**Status:** Complete

This document records the Phase B implementation of the Omivoid AI layer:
exposing AI-accessible capabilities, bridging them into Pi's tool mechanism,
and proving the first AI-to-action path. It is part of the implementation
record (AGENTS.md §28).

---

## 1. Summary

| Stage | Deliverable | Status |
|---|---|---|
| AI-10 | Capability catalogue derived from the Action Registry | Complete |
| AI-11 | Pi tool bridge (`adapters/pi/omivoid-tools.ts`) | Complete |
| AI-12 | First AI-to-action proof ("Open my browser") | Complete |

The architecture proof required by docs/ai/10 §18 now holds end-to-end:

```text
User: "Open my browser."
    ↓
Pi (qwen2.5:3b)
    ↓
app.browser.open
    ↓
Omivoid capability catalogue (policy boundary)
    ↓
Action runner (omivoid action run)
    ↓
app.launch adapter, role = browser
    ↓
librewolf
```

Pi never learns the configured browser executable — it requests the canonical
capability and Omivoid resolves the role.

---

## 2. AI-10 — Capability Catalogue

### 2.1 Implementation

`cli/omivoidlib/ai/capabilities/__init__.py` derives the AI-accessible
capability set from the Action Registry (the registry remains the source of
truth — docs/ai/02 §18, AGENTS.md §7–8).

Filtering:

* `ai_accessible = true` (AGENTS.md §17);
* `ai.*` actions excluded to prevent recursive tool invocation (AGENTS.md §18).

Each entry carries policy metadata for later stages:

```json
{
  "id": "app.browser.open",
  "name": "Open Browser",
  "description": "Open the default web browser.",
  "risk": "routine",
  "confirmation": "never"
}
```

### 2.2 CLI

```bash
omivoid ai capabilities          # human-readable
omivoid ai capabilities --json   # machine-readable (docs/ai/04 §26)
```

Result on the current registry: **13 capabilities**. The recommended first set
in docs/ai/04 §28 could not be used verbatim — `app.editor.open` does not exist,
and `help.keys.open` / `help.actions.search` are `ai_accessible = false`
(DMS spotlight actions). The catalogue therefore reflects actual registry IDs,
as permitted by docs/ai/10 §16.

Exposed capabilities:

```text
app.browser.open            media.next
app.terminal.open           media.play_pause
audio.microphone.toggle     media.previous
audio.mute.toggle           theme.wallpaper.next
audio.volume.decrease       theme.wallpaper.select
audio.volume.increase
display.brightness.decrease
display.brightness.increase
```

### 2.3 Tests

Six tests added to `tests/test_ai.py`: ai_accessible filtering, `ai.*`
exclusion, id sorting, empty registry, policy metadata, and the public
`ai.capabilities()` interface.

---

## 3. AI-11 — Pi Tool Bridge

### 3.1 Implementation

`adapters/pi/omivoid-tools.ts` is a Pi extension that exposes the capability
catalogue as Pi tools. Tool definitions are generated at session start from
`omivoid ai capabilities --json` — no hand-written catalogue (docs/ai/02 §18).

| Concern | Approach |
|---|---|
| Tool naming | Pi restricts names to `[a-z0-9_]`; `app.browser.open` → `app_browser_open`. Canonical ID preserved and passed to the runner. |
| Execution | `omivoid action run <id> --json` — Pi never runs implementation commands directly (docs/ai/02 §19). |
| Policy boundary | Only capabilities in the catalogue are registered; the catalogue is the policy filter (AGENTS.md §17). |
| CLI resolution | `$OMIVOID_CLI` if set, otherwise `omivoid` from `PATH` (no hard-coded paths — AGENTS.md §33). |
| Errors | Missing CLI / non-zero exit / failed action are surfaced to Pi (`throw` → `isError`). |

### 3.2 Installation

The extension is distributed from the repository and symlinked into Pi's
auto-discovery directory:

```text
adapters/pi/omivoid-tools.ts
    → ~/.pi/agent/extensions/omivoid-tools.ts   (symlink)
```

A symlink keeps a single source of truth — repository edits take effect on the
next Pi session without copying (`/reload` re-reads extensions).

### 3.3 Configuration

Point Pi at the Omivoid CLI (the CLI is not installed on `PATH`):

```bash
export OMIVOID_CLI=/path/to/omivoid-lmde/cli/omivoid
```

---

## 4. AI-12 — First AI-to-Action Proof

### 4.1 Procedure

```bash
OMIVOID_CLI=/home/mk/Projects/OmiVoid/omivoid-lmde/cli/omivoid \
  pi --print --mode json --no-session "Open my browser"
```

Provider: Ollama `qwen2.5:3b` (local, CPU-only). Pi's default provider/model
(`~/.pi/agent/settings.json`) target Ollama.

### 4.2 Evidence

Pi emitted a tool call, Omivoid executed it, and the model confirmed:

```text
assistant → toolCall name="app_browser_open" arguments={}
tool_result → "Omivoid action app.browser.open executed successfully."
              details.state = {"role": "browser", "app": "librewolf"}
assistant → "Your default web browser has been opened."
```

`librewolf` was confirmed running on the desktop after the turn. The full
request (Pi system prompt + 13 tool definitions) measured **2387 tokens**,
within the 4096-token context; the turn completed in ~26 s on CPU.

### 4.3 Notes

* `--mode text` may render nothing for tool-call turns in non-interactive mode;
  `--mode json` is the reliable surface for verification.
* Pi does not require knowledge of the browser executable — the role indirection
  (`app.launch role=browser`) is preserved (Contract 3, AGENTS.md §7).

---

## 5. Files

| File | Change |
|---|---|
| `cli/omivoidlib/ai/capabilities/__init__.py` | Capability catalogue (was Phase A stub) |
| `cli/omivoidlib/ai/__init__.py` | Public `capabilities()` |
| `cli/omivoidlib/cli.py` | `ai capabilities` subcommand |
| `tests/test_ai.py` | 6 capability tests |
| `adapters/pi/omivoid-tools.ts` | Pi tool bridge (new) |
| `docs/implementation/ai-phase-b.md` | This record (new) |

---

## 6. Limitations and Deferred Work

* **Arguments** — the initial capability set takes no arguments; provider tool
  arguments are untrusted and require validation (docs/ai/04 §388). Deferred.
* **Policy enforcement** — `risk` / `confirmation` are surfaced but not yet
  enforced at execution; that is AI-14 (Phase C).
* **Result detail** — structured success/failure return to Pi is AI-13.
* **Recursive protection** — `ai.*` exclusion is implemented; broader recursion
  protection is AI-16.
* **CLI discovery** — `omivoid` is not installed on `PATH`; `OMIVOID_CLI` must
  be set for the bridge.
