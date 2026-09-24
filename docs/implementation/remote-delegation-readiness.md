# Remote Delegation Readiness Review (AI-34)

**Date:** 2026-09-18
**Stage:** AI-34 (docs/ai/10 §40)
**Status:** Review complete — implementation deferred (docs/ai/08 §34)

How the current Omivoid infrastructure could support later remote
delegation. No delegation is implemented in this stage; this document
records the surface, the project-identity concern, and the security
boundary. It complements `herdr-readiness-review.md` (AI-33).

---

## 1. Summary

The substrate is present: Tailscale is installed and running, Herdr
provides SSH-based remote machines and agent lifecycle, and the project
context module already derives a logical project identity. What is missing
is the delegation layer itself (action, adapter, result contract), which
docs/ai/08 §34 defers until local Pi + local context + local capabilities
are stable.

---

## 2. Logical worker roles

docs/ai/08 §9–11 prefer stable logical roles over hostnames/IPs. Observed
against the current tailnet:

| Logical role | Candidate node | Observed state |
|---|---|---|
| `interactive-laptop` | `sb1` (100.127.65.41) | online — this machine |
| `heavy-desktop` | `t7910` (100.94.103.58) | online |
| `agent-server` (IBIS) | not present locally | absent |
| (mobile / other) | `hp-eb-840`, `s110` | offline |

`agno` is **not** installed on this machine (agent server only). So Phase 1
has exactly two online candidates: the laptop and the desktop. The desktop
(`t7910`) is the realistic first `heavy-desktop` worker (docs/ai/08 §3).

Roles, not addresses, must be canonical (docs/ai/08 §9). The tailnet IPs
above are recorded here as *observed evidence only* and must not appear in
code, Pi prompts, or delegation payloads (docs/ai/10 §40).

---

## 3. Tailscale availability

```text
$ tailscale version   → 1.102.3
$ pgrep tailscaled    → running
$ tailscale status    → 4 peers, 2 online (sb1, t7910)
```

Tailscale provides connectivity and identity (WireGuard + SSO). Per
docs/ai/08 §22 it must remain transport only — not a task queue, project
registry, provider, or scheduler. Reachability through Tailscale does not
by itself authorise an action (docs/ai/09 §28): application permission is a
separate decision.

---

## 4. Project identity concerns

This is the sharpest gap between the current implementation and remote
delegation.

docs/ai/06 §37 and docs/ai/08 §13: **project identity must be independent
of local filesystem location**, because the same project lives at different
paths on different machines.

Current state (Phase F, and therefore most tractable now):

* `discover_project()` already yields a logical **name** (`omivoid-lmde`)
  in addition to the local **root** (`~/Projects/OmiVoid/omivoid-lmde`).
* `ContextObject.metadata` carries `name`, `root`, `method`, `type`, `git`.

That `name` is the seed of a portable project identity. The local `root`
must **not** be sent as identity (docs/ai/08 §13 example is explicitly a
bad one). A future project registry (docs/ai/06 §38) would map
`identity → {local path, desktop path, server path, repository}`.

Consequences to preserve:

* delegation requests carry `project = <name>`, never a home path;
* the worker resolves the path environment-specifically;
* Git revision (docs/ai/08 §15) is the natural context-transfer unit for
  software projects, chosen over copying directories.

---

## 5. Security concerns

docs/ai/09 §24–28 and docs/ai/08 §20–23 govern delegation. Mapped to the
current implementation:

| Concern | Current support | Needed for delegation |
|---|---|---|
| No credentials in payloads | Provider layer never embeds secrets | Enforce on delegation payloads |
| Secret exclusion in context | Project module excludes `.env`, `*.key`, credentials (AI-28) | Reuse as the outbound filter |
| Only required context moves | Context is compositional and bounded | Apply per-task selection + budget |
| Confirmation | Registry `confirmation` + policy allow/deny/confirm (Phase C) | `ai.delegate` should confirm |
| No auto-applied changes | — | Result → review → apply (docs/ai/08 §19) |
| Failure must be safe | Policy fails closed (docs/ai/09 §37) | Distinguish the four network failure modes (docs/ai/08 §31) |
| Auditability | AI action audit metadata (docs/ai/09 §36) | Add destination/worker to audit |

Non-negotiables for the future adapter:

* **SSH/Tailscale auth stays in infrastructure** — never in an AI prompt
  (docs/ai/09 §26).
* **Offline worker returns a clear state**; never silently re-route
  sensitive work (docs/ai/08 §23).
* **Remote changes are proposed, not applied** (docs/ai/08 §19).

---

## 6. How current infrastructure would carry delegation

The existing layers map cleanly onto docs/ai/08 §4:

```text
User Intent      → registry action (ai.delegate / project.delegate)
Delegation       → a delegation adapter (ai/delegation/…/)
Routing          → Herdr machine/session resolution (logical role)
Transport        → SSH over Tailscale
Remote Worker    → Herdr agent on the desktop/IBIS
Execution        → agent prompt + wait
Result           → structured wrapper over agent read / api snapshot
```

Reusable pieces already built:

* **Policy + confirmation** (Phase C) — `ai.delegate` inherits allow/deny/
  confirm and recursion protection.
* **Structured results** — the `{success, state|error}` envelope is the
  natural result contract (docs/ai/08 §17 can extend `state`).
* **Project context** (Phase F) — supplies portable identity + bounded
  context, already secret-filtered.
* **Provider independence** (docs/ai/06 §35) — a delegation target is
  another backend behind the same abstraction; Pi must not learn topology.

Missing pieces:

* `ai.delegate` / `project.delegate` registry action
* delegation adapter + Herdr availability probe
* structured remote result contract
* project identity registry (docs/ai/06 §38)

---

## 7. First future proof (recommended)

docs/ai/08 §35 proposes the simplest meaningful proof:

```text
"Run project tests on the desktop."
   → Pi → delegation action → Herdr → t7910 worker → tests
   → structured result → DMS notification
```

No automatic file modification. This exercises identity (project name, not
path), policy (confirmation), transport (SSH/Tailscale), and results —
without requiring change-application.

---

## 8. Evidence

```text
$ tailscale version          → 1.102.3
$ tailscale status           → sb1 online, t7910 online, 2 offline
$ tailscale status --json    → tailnet "MartinKnights@"
$ which agno                 → not found on this machine
$ herdr machine list         → No saved SSH machines (none prepared yet)
$ omivoid project current    → omivoid-lmde (name) @ ~/Projects/... (root)
```