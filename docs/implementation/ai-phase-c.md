# AI Phase C — Policy Enforcement, Structured Results, Confirmation & Recursion Protection

**Date:** 2026-09-15
**Stage:** AI-13, AI-14, AI-15, AI-16 (docs/ai/10-ai-phase-1-implementation-plan.md §19–22)
**Status:** Complete

This document records the Phase C implementation of the Omivoid AI layer:
enforcing AI action policy, returning structured results to the provider,
proving the confirmation boundary, and blocking recursive AI invocation.
It is part of the implementation record (AGENTS.md §28).

---

## 1. Summary

| Stage | Deliverable | Status |
|---|---|---|
| AI-13 | Structured action result return | Complete |
| AI-14 | Policy enforcement (`ai_accessible`/`risk`/`confirmation`) | Complete |
| AI-15 | Confirmation proof | Complete |
| AI-16 | Recursive action protection | Complete |

Guiding principle (docs/ai/09 §50):

> **AI can propose and request. Omivoid remains the authority that decides what the desktop actually does.**

---

## 2. Architecture

One execution path (docs/ai/10 §25) — the AI layer composes policy with the
existing runner rather than re-implementing execution:

```text
AI request
    ↓
ai.policy.evaluate(action)        (docs/ai/09)
    ↓ allow / confirm
runner.run_action(action_id)      (cli/omivoidlib/runner.py)
    ↓
adapter → system
```

| Module | Responsibility |
|---|---|
| `cli/omivoidlib/ai/policy/__init__.py` | `evaluate(action)` → allow / deny / confirm |
| `cli/omivoidlib/ai/actions.py` | `run_action_as_ai(action_id, confirmed)` — policy gate + runner |
| `cli/omivoidlib/cli.py` | `action run <id> --ai [--confirmed]` |
| `adapters/pi/omivoid-tools.ts` | Confirmation UI + structured results |

---

## 3. AI-14 — Policy Enforcement

`evaluate(action)` returns a decision with the stable error vocabulary
(docs/03 §32):

| Condition | Decision | Code | `reason` |
|---|---|---|---|
| id starts `ai.` | deny | `PERMISSION_DENIED` | `ai_recursion` |
| `ai_accessible = false` | deny | `PERMISSION_DENIED` | `not_ai_accessible` |
| risk ∈ {privileged, destructive, critical} | deny | `PERMISSION_DENIED` | `risk_not_permitted` |
| confirmation ∈ {ai-only, always} | confirm | `CONFIRMATION_REQUIRED` | `confirmation_required` |
| otherwise | allow | — | `allowed` |

Policy failure favours deny (docs/ai/09 §37). Recursion is evaluated first,
so an AI-invoking action is always refused regardless of its other metadata.

**Risk gating:** Phase 1 permits `read`, `routine`, and `state-change`
(with confirmation where declared) and refuses `privileged`, `destructive`,
and `critical` (docs/ai/09 §8). No privileged/destructive action was added
merely to test policy.

**Confirmation interpretation:** confirmation is source-scoped (docs/03 §17 —
"different treatment of trusted direct interaction and AI invocation").
`ai-only` and `always` require an AI-initiated confirmation; `interactive` is
scoped to human surfaces and does not; `never` requires none. No action
currently uses `interactive`, so behaviour is conservative today.

---

## 4. AI-13 — Structured Results

`run_action_as_ai` returns the runner's structured result or a policy refusal:

| Case | Result |
|---|---|
| success | `{"success": true, "action", "state"}` |
| unknown action | `ACTION_NOT_FOUND` |
| no implementation / dependency | `ACTION_UNAVAILABLE` / `DEPENDENCY_MISSING` (runner passthrough) |
| policy refusal | `PERMISSION_DENIED` (+ `reason`) |
| needs approval | `{"confirmation_required": true, "error": {"code": "CONFIRMATION_REQUIRED"}}` |
| invalid argument | `INVALID_ARGUMENT` (adapter) |

The Pi bridge maps these to Pi tool results: success → text + `details`;
any non-success → thrown error carrying the code and message (Pi `isError`).

---

## 5. AI-15 — Confirmation Proof

Test action: **`theme.wallpaper.next`** — a harmless, reversible state change,
declared `confirmation = "ai-only"` (docs/ai/09 §9, AI-15 requires a
non-destructive action).

### 5.1 Deny path (via Pi)

```text
User: "Cycle to the next wallpaper"
    ↓
Pi → app_theme_wallpaper_next (tool)
    ↓
omivoid action run theme.wallpaper.next --ai
    ↓ CONFIRMATION_REQUIRED
Pi bridge → user confirmation prompt
    ↓ denied
tool error: PERMISSION_DENIED: user denied 'theme.wallpaper.next'
```

The wallpaper was **not** changed. In non-interactive (`--print`) sessions the
confirmation UI fails safe to **deny** (docs/ai/09 §37).

### 5.2 Approve path (CLI)

```text
omivoid action run theme.wallpaper.next --ai
    → CONFIRMATION_REQUIRED, confirmation_required: true

omivoid action run theme.wallpaper.next --ai --confirmed
    → SUCCESS: Cycling to next wallpaper
```

The model can never set `--confirmed`: Pi tools expose no parameters
(`parameters: Type.Object({})`), and the bridge only adds `--confirmed` after
the user approves (docs/ai/09 §10 — the provider cannot approve its own action).

---

## 6. AI-16 — Recursive Action Protection

Two independent layers:

1. **Catalogue** — `ai.*` actions are excluded from `omivoid ai capabilities`
   (Phase B, AGENTS.md §18).
2. **Policy** — `evaluate()` denies any `ai.`-prefixed action with
   `reason = ai_recursion`, even if it were marked `ai_accessible`.

`ai.ask` and `ai.pi.open` remain `ai_accessible = false`.

```text
$ omivoid action run ai.ask --ai --json
{"success": false, "error": {"code": "PERMISSION_DENIED",
                             "reason": "ai_recursion"}}
```

---

## 7. Evidence

Policy decisions (live CLI):

```text
ai.ask                --ai   → PERMISSION_DENIED (ai_recursion)
window.close          --ai   → PERMISSION_DENIED (not_ai_accessible)
theme.wallpaper.next  --ai   → CONFIRMATION_REQUIRED
theme.wallpaper.next  --ai --confirmed → SUCCESS
app.terminal.open     --ai   → SUCCESS {role: terminal, app: alacritty}
```

Via Pi (Ollama qwen2.5:3b):

```text
"Open my terminal"          → app_terminal_open → executed → confirmed
"Cycle to the next wallpaper" → theme_wallpaper_next → PERMISSION_DENIED (denied)
```

Tests: **121 passing** (was 107).

---

## 8. Files

| File | Change |
|---|---|
| `cli/omivoidlib/ai/policy/__init__.py` | Policy evaluator (was Phase A stub) |
| `cli/omivoidlib/ai/actions.py` | AI-aware executor (new) |
| `cli/omivoidlib/cli.py` | `action run --ai [--confirmed]` |
| `adapters/pi/omivoid-tools.ts` | `--ai`, confirmation flow, structured results |
| `actions/theme.toml` | `theme.wallpaper.next` → `confirmation = "ai-only"` |
| `tests/test_ai.py` | +14 policy/execution tests |
| `docs/implementation/ai-phase-c.md` | This record (new) |

---

## 9. Limitations and Deferred Work

* **Argument validation** — the current capability set takes no arguments;
  provider-supplied arguments are untrusted and must be validated before
  capabilities with parameters are exposed (docs/ai/09 §32–34). Deferred.
* **Confirmation UI** — Phase 1 confirmation is surfaced through Pi's UI.
  A DMS-native confirmation surface is AI-17/AI-18 territory.
* **`interactive` semantics** — documented above; revisit if an action adopts it.
* **Auditability** — the metadata fields for audit (docs/ai/09 §36) are
  available but not yet persisted to a log.
