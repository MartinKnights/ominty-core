# AI Phase F — Project Context & Validation

**Date:** 2026-09-18
**Stage:** AI-26 → AI-35 (docs/ai/10 §32–41)
**Status:** Complete

Implementation record for project-aware AI: project discovery, project
context, project security, the Phase 1 security validation, failure
isolation, performance review, and the Herdr / remote-delegation readiness
audits.

Implementations for the audits live in `herdr-readiness-review.md` (AI-33)
and `remote-delegation-readiness.md` (AI-34).

---

## 1. Summary

| Stage | Deliverable | Status |
|---|---|---|
| AI-26 | Project discovery | Complete |
| AI-27 | Project context + one project-aware request | Complete (proven) |
| AI-28 | Project security (secret exclusion) | Complete |
| AI-29 | Security validation (docs/ai/09 §48) | Complete |
| AI-30 | Failure isolation | Complete (CLI-verified) |
| AI-31 | Restart validation | Startup-safety verified; logout/reboot user step |
| AI-32 | Performance review | Complete (measured) |
| AI-33 | Herdr readiness audit | Complete (`herdr-readiness-review.md`) |
| AI-34 | Remote delegation readiness | Complete (`remote-delegation-readiness.md`) |
| AI-35 | Documentation reconciliation | Complete (docs/ai/06, docs/ai/07) |

---

## 2. AI-26/27 — Project discovery and context

`cli/omintylib/ai/project/__init__.py`:

```text
discover_project(cwd, explicit) -> {root, name, method}
collect_project(cwd, explicit)  -> ContextObject(type="project")
```

Resolution precedence (refined during implementation — see §8):

```text
explicit root (--root / OMINTY_PROJECT)
    → nearest AGENTS.md (walk-up, bounded by home)
    → Git root
    → current working directory
```

`collect_project` is compositional (docs/ai/06 §4) and never
"read every file → send everything":

* identity — name, root, inferred type (`software` | `generic`)
* instructions — `AGENTS.md`, bounded to `MAX_INSTRUCTIONS_BYTES`
* structure — bounded top-level tree (excludes `.git` and secrets)
* git — branch + clean/dirty, absent gracefully when not a repo

CLI:

```text
ominty project current [--root R] [--json]
ominty project context [--root R] [--json]
ominty ai ask "<prompt>" --project     # attach project context
```

`--project` composes with `--clipboard` (a list of context objects).

---

## 3. AI-28/29 — Project security and validation

**Secret exclusion** (docs/ai/06 §29, docs/ai/09 §17): `SECRET_PATTERNS`
covers `.env`, `.env.*`, `*.key`, `*.pem`, `*.p12`, `*.pfx`, `*.crt`,
`id_rsa`/`id_ed25519`/…, `credentials*`, `secrets`, `secret`, `.netrc`,
`.pgpass`, `*.token`, `*.secret`. Excluded names never appear in the bounded
structure and are never read.

**Security validation** (docs/ai/09 §48) — covered by tests:

| Case | Test |
|---|---|
| allowed action | `test_run_action_as_ai_allowed_executes` |
| denied action | `test_run_action_as_ai_denied_recursion`, `test_policy_denies_*` |
| unknown action | `test_run_action_as_ai_unknown` |
| invalid argument | `test_ai_ask_adapter_missing_prompt` |
| hostile shell-like argument | `test_command_adapter_hostile_argument_not_shell_interpreted` |
| confirmation | `test_run_action_as_ai_confirmation_required`, `test_wallpaper_next_*` |
| context unavailable | `test_clipboard_explain_context_unavailable`, `test_collect_selection_unavailable` |
| secret file excluded | `test_collect_project_secret_exclusion`, `test_is_secret` |
| provider unavailable | `test_ask_provider_unavailable`, `test_ai_ask_adapter_provider_error` |

The hostile-argument test confirms the `command` adapter uses argument
arrays (no shell), so an AI-supplied `$(…)` is literal data and executes
nothing (docs/ai/09 §33).

---

## 4. AI-30 — Failure isolation

Pi is genuinely unavailable on this machine (`misconfigured`), which
provided a real failure case:

```text
$ ominty ai provider status pi
State:  misconfigured
Detail: OPENAI_API_BASE 'http://localhost:4000' is not reachable

$ ominty ai ask "hello" --provider pi
PROVIDER_UNAVAILABLE: provider 'pi' is misconfigured: … not reachable

# with Pi down:
$ ominty action run workspace.previous      → exit 0
$ ominty search palette                     → 1 match(es)
$ ominty ai ask "Reply with just OK"        → OK        (default ollama)
$ pgrep -f ominty                           → none      (no daemon)
```

Niri IPC verified live, DMS running (`/usr/bin/dms run --session`), and a
reversible native action round-tripped (`workspace.next` 1→2,
`workspace.previous` 2→1). AI failure does not touch the desktop.

Desktop-only checks (Super+K, Super+Space) remain user-verifiable; their
CLI backing (`ominty help`, `ominty search`) works with Pi down.

---

## 5. AI-31 — Restart validation

Startup-safety verified:

```text
$ grep spawn-at-startup ~/.config/niri/config.kdl     → none (for ominty)
$ tail ~/.config/ominty/generated/niri/bindings.kdl  → spawn only inside keybinds
$ grep "include optional" ~/.config/niri/config.kdl   → include optional=true ".../bindings.kdl"
```

The AI integration adds **no** startup dependency: the generated fragment is
`include optional=true`, and no `spawn-at-startup` entry was introduced. A
missing generated file cannot prevent Niri from starting.

Outstanding (user step): logout/login and reboot smoke test on the desktop.

---

## 6. AI-32 — Performance review

Measured on the reference machine (4 vCPU, no GPU, qwen2.5:3b Q4_K_M):

**Non-AI (no provider involvement):**

| Operation | Latency |
|---|---|
| `registry validate` | 0.16 s |
| `action list --json` | 0.18 s |
| `search` | 0.15 s |
| `action run workspace.next` | 0.19 s |
| `dms ipc call spotlight openQuery "!ai "` (Super+A path) | 0.06 s |

**AI provider (ollama, 100% CPU):**

| Metric | Value |
|---|---|
| model load (cold) | ~9 s |
| prompt evaluation | ~15 tok/s (1 KB ≈ 14 s, 4 KB ≈ 27 s) |
| generation | ~4 tok/s |
| runtime context window | 4096 tokens |
| clipboard ask (~200 B) | ~30 s |
| project ask (4 KB context) | 46.8 s |
| project ask (8.5 KB context) | >120 s → `PROVIDER_FAILED: timed out` |
| project ask (14 KB context) | >270 s → timed out |

**Memory / processes:**

| Component | Footprint |
|---|---|
| `dms` (RSS) | 75 MiB |
| ollama server (RSS) | 49 MiB |
| loaded model | 2.2 GB (unloads ~4 min idle) |
| persistent Ominty process | none |

**Finding:** prompt evaluation dominates; on CPU-only inference a large
project context can exceed the 120 s provider timeout. Mitigation in this
phase: `MAX_INSTRUCTIONS_BYTES = 4 KiB`, which keeps the total project
prompt within the effective 4096-token window and inside the default
timeout. This is the "simple limit" docs/ai/05 §36 permits for Phase 1.
Larger instruction files are truncated with an explicit path pointer so a
tool-capable provider can read the remainder.

No persistent process was introduced (docs/ai/09 §47).

---

## 7. AI-33/34 — Readiness audits

* `docs/implementation/herdr-readiness-review.md` — Herdr 0.9.0 is present
  and running; documented interface (socket API + CLI), object model
  (`session → workspace → tab → pane → agent`), workers (saved SSH
  machines), authentication (SSH / local socket), transport
  (SSH over Tailscale), results (`agent read` / `api snapshot`), lifecycle
  (`agent wait`). Adapter deferred to `ai/delegation/herdr/`.
* `docs/implementation/remote-delegation-readiness.md` — worker roles
  (`interactive-laptop` = sb1, `heavy-desktop` = t7910; IBIS absent),
  Tailscale availability, the project-identity concern (logical name vs
  local path), and the security boundary. Delegation deferred.

---

## 8. AI-35 — Documentation reconciliation

Two specification assumptions were corrected from implementation evidence:

1. **docs/ai/06 §6 — project discovery precedence.** The Git root and the
   instruction boundary can differ (here the Git root is the parent
   directory; `AGENTS.md` is in `ominty-core/`). Recorded precedence now
   puts the nearest `AGENTS.md` above the Git root.
2. **docs/ai/07 §16 — Herdr task lifecycle.** Herdr 0.9.0 does not expose a
   `created/queued/assigned/…` job queue; it models sessions and agents with
   `agent wait`. The spec now notes the actual model and directs the adapter
   to map onto it.

Phase E's selection decision (CLIPBOARD FALLBACK) was already reconciled in
`ai-context-evaluation.md`.

---

## 9. Evidence

```text
$ ominty project current
Project: ominty-core
Root:    ~/Projects/Ominty/ominty-core
Method:  AGENTS.md

$ ominty project context | wc -c
4477

$ ominty ai ask "In one sentence, what is this project?" --project
This project is the Phase 1 reference implementation of Ominty, a
keyboard-first, action-driven system, validated on the LMDE platform.

$ ominty registry validate
26 action(s), 0 error(s), 0 warning(s), 0 info
```

Tests: **149 passing** (was 137). New coverage: secret patterns, project
discovery (explicit / AGENTS.md / git / cwd), secret exclusion, git
degradation, git state, instructions truncation, `ask(context=[project])`,
hostile-argument safety.

---

## 10. Files

| File | Change |
|---|---|
| `cli/omintylib/ai/project/__init__.py` | discovery + context collector (new) |
| `cli/omintylib/cli.py` | `project current` / `project context`, `ai ask --project` |
| `tests/test_ai.py` | Phase F + security-validation tests |
| `docs/ai/06-project-context.md` | discovery precedence note (AI-35) |
| `docs/ai/07-herdr-integration.md` | actual Herdr model note (AI-35) |
| `docs/implementation/ai-phase-f.md` | this record (new) |
| `docs/implementation/herdr-readiness-review.md` | AI-33 audit (new) |
| `docs/implementation/remote-delegation-readiness.md` | AI-34 audit (new) |

---

## 11. Limitations and Deferred Work

* **Delegation is deferred** (docs/ai/07 §30, docs/ai/08 §34): no
  `ai.delegate` action or Herdr adapter yet; the audits establish the
  boundary and semantics only.
* **Project identity is name-based, not registry-backed** — sufficient now,
  but a project registry (docs/ai/06 §38) is needed before remote
  delegation can resolve per-machine paths.
* **Context budget is a simple byte limit** — a priority-based budget
  (docs/ai/05 §36) remains future work; CPU-only prompt evaluation is the
  practical constraint.
* **Restart validation** — logout/login and reboot smoke tests remain a
  user step.
* **`OMINTY_CLI`/paths** — the DMS plugin still uses an absolute `cliPath`
  default; installing `ominty` on `PATH` remains outstanding.