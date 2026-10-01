# AI Phase D — DMS Evaluation, `Super+A` AI Namespace

**Date:** 2026-09-15
**Stage:** AI-17, AI-18, AI-19, AI-20 (docs/ai/10-ai-phase-1-implementation-plan.md §23–26)
**Status:** Complete

Implementation record for the `Super+A` AI namespace. The DMS AI evaluation
and mechanism decision are recorded separately in
`docs/implementation/ai-dms-evaluation.md` (AI-17).

---

## 1. Summary

| Stage | Deliverable | Status |
|---|---|---|
| AI-17 | DMS AI evaluation + mechanism decision | Complete (`ai-dms-evaluation.md`) |
| AI-18 | `Super+A` opens discoverable AI actions | Complete |
| AI-19 | `Super+A,A` → `ai.ask` | Complete (via AI menu) |
| AI-20 | `Super+A,P` → `ai.pi.open` | Complete (via AI menu) |

The AI namespace reuses the DMS launcher (EXTEND DMS) and the Ominty
provider layer — no second AI invocation path, no custom AI UI.

---

## 2. Mechanism

Niri cannot bind keybinding chords and DMS has no submap
(`ai-dms-evaluation.md` §6), so the `Super+A` prefix is realised through the
DMS spotlight:

```text
Super+A
   ↓  (Niri bind: dms ipc call spotlight openQuery "!ai ")
DMS spotlight — AI mode ("!ai" sentinel)
   ↓  (Ominty Actions launcher plugin)
AI items:  Ask AI  ·  Open Pi      (plus "Ask AI: <text>" once typed)
   ↓
ominty ai ask "<text>"   /   ominty action run ai.pi.open
   ↓
Ominty provider layer + policy
```

---

## 3. AI-18 — `Super+A` opens the AI surface

Registry (`actions/ai.toml`):

```toml
[group.ai]
name = "AI"
prefix = "Super+A"

[action."ai.menu.open"]
keys = ["Super+A"]
adapter = "command"
command = ["dms", "ipc", "call", "spotlight", "openQuery", "!ai "]
ai_accessible = false
```

The generator emits the Niri bind:

```kdl
// ai.menu.open
Mod+A {
    spawn "dms" "ipc", "call" "spotlight" "openQuery" "!ai "
}
```

The `omintyActions` DMS plugin gains an **AI mode**: a query starting `!ai`
returns the AI-category actions, independently of its normal palette filter.

---

## 4. AI-19 — `Super+A,A` → `ai.ask`

The chord (`Super+A,A`) is declared in the registry as intent. It is realised
by the AI menu:

* typing after `Super+A` produces an **"Ask AI: <text>"** entry that runs
  `ominty ai ask "<text>"` — the same provider architecture proven by the CLI
  (AI-5) and used by the `ai.ask` action adapter. The response is shown via a
  DMS toast.
* With no text, an **"Ask AI"** hint entry reminds the user to type a question
  (it never runs an empty prompt).

---

## 5. AI-20 — `Super+A,P` → `ai.pi.open`

The **"Open Pi"** entry runs `ominty action run ai.pi.open` — the existing
registry action. The chord (`Super+A,P`) is registry intent.

`ai.pi.open` metadata corrected to `ai_accessible = false` (AGENTS.md §18 —
actions that invoke AI must not be exposed back to AI).

---

## 6. Supporting changes

| Change | Reason |
|---|---|
| `generator.py` emits a bind for the `command` adapter's top-level `command` | `ai.menu.open` declares its DMS command like `help.actions.search`; only `arguments.command` was handled before |
| `registry.py` suppresses `CHORD_PREFIX_CONFLICT` for a declared group prefix | `Super+A` (group prefix) intentionally prefixes the `Super+A,*` chords (docs/03 §13) — not a conflict |
| `ai.pi.open` `ai_accessible` → `false` | Recursion protection consistency (AGENTS.md §18) |

---

## 7. Evidence

Registry:

```text
$ ominty registry validate
24 action(s), 0 error(s), 0 warning(s), 0 info
Validation passed.

$ ominty action list --json | (AI category)
['ai.ask', 'ai.menu.open', 'ai.pi.open']
```

Generated fragment (`~/.config/ominty/generated/niri/bindings.kdl`):

```kdl
// ai.menu.open
Mod+A { spawn "dms" "ipc" "call" "spotlight" "openQuery" "!ai " }
```

`niri validate` → **config is valid**; config reloaded live.

DMS launcher AI mode (journal):

```text
[OmintyActions] AI mode: 2 items        # "!ai "        → Ask AI, Open Pi
[OmintyActions] AI mode: 2 items        # "!ai <text>"  → Ask AI: <text>, Open Pi
```

Provider path:

```text
$ ominty ai ask "Reply with just the number: what is 2+2?"
4
```

---

## 8. Files

| File | Change |
|---|---|
| `actions/ai.toml` | `[group.ai]`, `ai.menu.open`, chord keys, `ai_accessible` fix |
| `cli/omintylib/generator.py` | top-level `command` bind |
| `cli/omintylib/registry.py` | group-prefix chord-conflict suppression |
| `shell/dms/ominty-actions/OmintyActions.qml` | AI mode (`!ai`), ask entry, toast |
| `tests/test_generator.py` | top-level command test |
| `tests/test_registry.py` | group-prefix suppression test |
| `tests/test_ai.py` | AI namespace integration test |
| `docs/implementation/ai-dms-evaluation.md` | AI-17 evaluation (new) |
| `docs/implementation/ai-phase-d.md` | This record (new) |

Tests: **124 passing** (was 121).

---

## 9. Limitations and Deferred Work

* **No true chords** (Niri/DMS). The chord notation is intent only; the second
  key is realised by the launcher. A native prefix would require a key-grab
  helper (deferred — AGENTS.md §35).
* **Ask response presentation** is a DMS toast (no streaming/markdown). A richer
  presentation is deferred; `aiAssistant` remains a REFERENCE ONLY candidate
  (`ai-dms-evaluation.md` §4.1).
* **Context indicators** (AI-21) and clipboard/selection context (AI-22+) are
  not yet implemented.
* **`OMINTY_CLI`/paths** — the plugin still uses an absolute `cliPath`
  default; installing `ominty` on `PATH` remains outstanding.
