# AI Phase E — Context: Clipboard, Explain/Summarise, Notification Delivery

**Date:** 2026-09-18
**Stage:** AI-21, AI-22, AI-23, AI-24, AI-25 (docs/ai/10-ai-phase-1-implementation-plan.md §27–31)
**Status:** Complete

Implementation record for AI context: the context envelope, clipboard
acquisition, the selection investigation + decision, the clipboard
explain/summarise actions, and notification-based reply delivery.

---

## 1. Summary

| Stage | Deliverable | Status |
|---|---|---|
| AI-23/24 | Selection acquisition investigation + decision | Complete (`ai-context-evaluation.md`) |
| AI-22 | Clipboard context (collector + `ask(context=...)` + CLI `--clipboard`) | Complete |
| AI-25 | `ai.clipboard.explain` / `ai.clipboard.summarise` | Complete |
| AI-21 | Context indicator in AI menu + notification reply delivery | Complete |

The selection investigation (AI-23/24) concluded **CLIPBOARD FALLBACK**:
direct selection acquisition is not reliably available on this stack
(Niri has no selection IPC, `xclip`/`xsel` are X11-only, DMS clipboard IPC
is close/open/toggle only), so the explain/summarise actions are honestly
named `ai.clipboard.*` and read the clipboard. Selection is never faked
(AGENTS.md §19).

---

## 2. Context envelope (AI-22)

`cli/omintylib/ai/context/__init__.py` defines the context system:

```python
@dataclass
class ContextObject:
    type: str          # "clipboard" (implemented), "selection" (unavailable)
    content: str
    source: str        # where the content came from
    metadata: dict     # e.g. {"bytes": 123}
```

Collectors return a structured envelope — never a guessed value:

```python
{"success": True,  "context": ContextObject(...)}
{"success": False, "error": {"code": "CONTEXT_UNAVAILABLE", "message": "..."}}
{"success": False, "error": {"code": "CONTEXT_TOO_LARGE",   "message": "..."}}
```

* `collect_clipboard()` — `wl-paste --no-newline` (Wayland-native, no X11
  dependency). Missing binary → `CONTEXT_UNAVAILABLE`; empty clipboard →
  `CONTEXT_UNAVAILABLE`; content over `MAX_CLIPBOARD_BYTES` (32 KiB) →
  `CONTEXT_TOO_LARGE`.
* `collect_selection()` — always `CONTEXT_UNAVAILABLE` (CLIPBOARD FALLBACK
  decision, AI-24). The function exists so the selection path is explicit
  and honest rather than absent.

`build_prompt(prompt, contexts)` renders labelled blocks into the provider
prompt:

```text
[CLIPBOARD CONTEXT]
<content>
[/CLIPBOARD CONTEXT]

<original prompt>
```

`ask(prompt, provider=None, timeout=None, context=None)` composes the prompt
via `build_prompt` before calling the provider. Providers stay plain-prompt
based (docs/ai/05 §38).

---

## 3. CLI `--clipboard` (AI-22)

`ominty ai ask "<prompt>" --clipboard` collects the clipboard and attaches
it as context. On collection failure it prints the structured error to
stderr and exits 1:

```text
$ ominty ai ask "say ok" --clipboard
CONTEXT_UNAVAILABLE: wl-paste not found — install wl-clipboard to read the clipboard
```

---

## 4. Clipboard actions (AI-25)

`actions/ai.toml`:

```toml
[action."ai.clipboard.explain"]
keys = ["Super+A,E"]
adapter = "ai.clipboard.explain"
contexts = ["clipboard"]
ai_accessible = false

[action."ai.clipboard.summarise"]
keys = ["Super+A,S"]
adapter = "ai.clipboard.summarise"
contexts = ["clipboard"]
ai_accessible = false
```

The chords are registry intent (Niri/DMS have no chords); the actions are
realised by the DMS AI menu. Both are `ai_accessible = false` (AGENTS.md §18).

Adapters (`adapters/common/ai_clipboard_explain.py`,
`ai_clipboard_summarise.py`) delegate to the shared
`omintylib.ai.clipboard_actions.run_with_clipboard(instruction)`, which
composes the collector with the provider layer:

```text
action invoked
    ↓
collect_clipboard()          (context collector)
    ↓
ask(instruction, context=[clipboard])   (provider layer)
    ↓
response
```

The shared helper lives in the `omintylib` ai layer (not the adapters
directory) because `adapters/` is not a Python package and adapters are
loaded standalone via `importlib` — a relative import between adapter files
would not resolve.

---

## 5. AI menu context indicator + notification delivery (AI-21)

`shell/dms/ominty-actions/OmintyActions.qml`:

* **Context indicator** — AI actions declaring `contexts = ["clipboard"]`
  show a `[Clipboard]` chip in their menu comment, so the user can see what
  is being sent (docs/ai/03 §11, docs/ai/05 §9). Only implemented context
  types are shown (docs/ai/10 §27).
* **Notification delivery** — AI replies are delivered via
  `notify-send` → DMS notification centre (persistent, dismissible) instead
  of a transient toast (docs/ai/03 §34). The "Asking…" toast remains as
  immediate feedback. `ai.clipboard.*` menu items route through the
  ask-process path (which parses the `--json` response envelope); failures
  notify with `-u critical`.

---

## 6. Supporting changes

| Change | Reason |
|---|---|
| `registry.py` — `clipboard` added to `VALID_CONTEXTS` | new context type |
| `registry.py` — `ai.clipboard.explain`/`summarise` added to `KNOWN_ADAPTERS` | validator warning → clean |
| `adapters/common/ai_clipboard.py` removed | shared helper moved into `omintylib.ai.clipboard_actions` (import resolution) |

---

## 7. Evidence

Registry:

```text
$ ominty registry validate
26 action(s), 0 error(s), 0 warning(s), 0 info
Validation passed.

$ ominty action list --json | (AI category)
ai.ask            | ['Super+A,A'] | ['global']    | False
ai.clipboard.explain   | ['Super+A,E'] | ['clipboard'] | False
ai.clipboard.summarise | ['Super+A,S'] | ['clipboard'] | False
ai.menu.open      | ['Super+A']   | ['global']    | False
ai.pi.open        | ['Super+A,P'] | ['global']    | False
```

Generated fragment rebuilt and validated (`niri validate` → config is
valid); Niri config reloaded live.

Graceful degradation (wl-clipboard not yet installed):

```text
$ ominty ai ask "say ok" --clipboard        → CONTEXT_UNAVAILABLE, exit 1
$ ominty action run ai.clipboard.explain    → CONTEXT_UNAVAILABLE, exit 1
```

Tests: **137 passing** (was 124). New coverage: context envelope,
clipboard collector (missing/empty/success/too-large), selection
unavailable, `build_prompt`, `ask(context=...)`, both clipboard adapters
(success + unavailable), registry integration (chords, contexts,
`ai_accessible`).

---

## 8. Files

| File | Change |
|---|---|
| `docs/implementation/ai-context-evaluation.md` | AI-23/24 investigation + CLIPBOARD FALLBACK decision (new) |
| `cli/omintylib/ai/context/__init__.py` | `ContextObject`, collectors, `build_prompt` (rewritten) |
| `cli/omintylib/ai/__init__.py` | `ask(..., context=...)` |
| `cli/omintylib/ai/clipboard_actions.py` | shared `run_with_clipboard` (new) |
| `adapters/common/ai_clipboard_explain.py` | explain adapter (new) |
| `adapters/common/ai_clipboard_summarise.py` | summarise adapter (new) |
| `cli/omintylib/adapters.py` | adapter registration |
| `actions/ai.toml` | `ai.clipboard.explain`/`summarise` |
| `cli/omintylib/cli.py` | `ai ask --clipboard` |
| `cli/omintylib/registry.py` | `clipboard` context, new adapters known |
| `shell/dms/ominty-actions/OmintyActions.qml` | context chip, notify-send delivery |
| `tests/test_ai.py` | Phase E tests |

---

## 9. Limitations and Deferred Work

* **Direct selection is deferred** (CLIPBOARD FALLBACK, AI-24). If a
  reliable Wayland selection mechanism appears (e.g. a future Niri IPC or a
  maintained `wl-clipboard` selection read), `collect_selection()` can be
  implemented behind the same envelope without changing the actions.
* **`Ask About Clipboard`** (docs/ai/05 §19) is not implemented — the two
  fixed-intent actions cover the Phase E scope; a prompt-carrying clipboard
  action can follow the same pattern.
* **wl-clipboard must be installed** for the feature to function:
  `sudo apt install wl-clipboard`. Until then the actions degrade honestly
  to `CONTEXT_UNAVAILABLE`.
* **`OMINTY_CLI`/paths** — the plugin still uses an absolute `cliPath`
  default; installing `ominty` on `PATH` remains outstanding.