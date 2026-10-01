# Herdr Readiness Review (AI-33)

**Date:** 2026-09-18
**Stage:** AI-33 (docs/ai/10 §39)
**Status:** Audit complete — implementation deferred (docs/ai/07 §30)

Readiness audit of the actual Herdr integration surface, per docs/ai/07 §31
("Do not design an adapter against assumptions"). No Herdr adapter is
implemented in this stage.

---

## 1. Summary

Herdr **is present on this machine** and running. It is a
*terminal workspace manager for AI coding agents* (v0.9.0), not a general
chat surface. That matches the docs/ai/07 §3–5 separation: Pi is the
interactive AI; Herdr is the workspace/agent orchestration layer.

| Aspect | Finding | Ready? |
|---|---|---|
| Interface | Local socket API + CLI | Yes |
| Task model | session → workspace → tab → pane → agent | Yes (model differs from docs/ai/07 §16) |
| Workers | Herdr "agents" + saved SSH machines | Yes |
| Authentication | SSH for remote; local socket for local | Yes (infra-level) |
| Transport | SSH over Tailscale | Yes |
| Results | `herdr agent read` / session snapshot | Yes |
| Lifecycle | `herdr agent wait` states | Yes |
| Ominty adapter | Not implemented | N/A (deferred) |

**Verdict:** the orchestration surface Ominty needs exists. The delegation
adapter (`ai/delegation/herdr/`, docs/ai/07 §23) is feasible but remains
deferred until local Pi integration is stable (docs/ai/07 §30, §34).

---

## 2. Observed interface

```text
$ herdr --version
herdr 0.9.0

$ herdr status
client:  version 0.9.0, channel stable, protocol 22
server:  status running, socket ~/.config/herdr/herdr.sock
```

CLI command groups (all over the socket API):

```text
herdr api            # snapshot | schema   (live runtime state / API schema)
herdr workspace      # workspace helpers
herdr worktree       # git worktree helpers
herdr tab            # tab helpers
herdr pane           # pane control
herdr agent          # control and inspect agent panes
herdr notification   # show notifications
herdr session        # named persistent sessions
herdr machine        # saved SSH machines
herdr integration    # built-in agent integrations
```

Remote entry points:

```text
herdr --remote <ssh-target> [--session <name>]
herdr machine add  # prepare the remote Herdr server and save an SSH machine
herdr machine list | enable | disable | rename | remove
```

Current machine state:

```text
$ herdr machine list
No saved SSH machines.
```

---

## 3. Task / object model

Herdr's object model is:

```text
session
  └── workspace
        └── tab
              └── pane
                    └── agent        # a running AI coding agent
```

This differs from the conceptual `created → queued → assigned → running →
…` task lifecycle in docs/ai/07 §16. Herdr models **workspaces of running
agents**, not a queue of discrete jobs. The delegation adapter must map an
Ominty *delegation request* onto a Herdr session/workspace/agent rather
than assuming a job queue.

Agent control verbs (the practical task surface):

```text
herdr agent list | get | read | send-keys | prompt |
             rename | focus | wait | attach | start | explain
```

`agent prompt` submits work; `agent wait` blocks until an agent reaches a
requested state; `agent read` retrieves output. These three are the
minimum needed for a delegation round-trip.

---

## 4. Workers

docs/ai/07 §10–11 describe capability-based workers (laptop, desktop,
server, container, Agno agent). Observed reality:

* **Local** — Herdr's own server on the laptop; agents run in panes.
* **Remote** — `herdr machine add <ssh-target>` prepares a remote Herdr
  server and records it as a logical machine; `herdr --remote <target>`
  attaches to it.

Workers are therefore identified by **saved machine name + session**, not
by raw IP. This already satisfies docs/ai/07 §9 (intent over destination)
and docs/ai/08 §9 (stable logical worker identity) at the Herdr layer.

Capability advertisement (docs/ai/07 §10) is **not** observed in 0.9.0 —
machines are saved, not described by capability. Capability-based routing
(docs/ai/08 §25) would need an Ominty-side mapping layer.

---

## 5. Authentication

* **Remote:** SSH to the saved machine (`herdr machine add` performs remote
  server preparation over SSH). Herdr does not carry credentials in task
  payloads.
* **Local:** Unix socket at `~/.config/herdr/herdr.sock` (filesystem
  permissions).

This aligns with docs/ai/09 §26 and docs/ai/08 §21: authentication belongs
to transport/orchestration infrastructure and must never be packaged inside
AI prompts.

---

## 6. Transport

Observed network substrate:

```text
$ tailscale status
100.127.65.41   sb1        (this laptop)   online
100.94.103.58   t7910      (desktop)       online
100.126.182.37  hp-eb-840                  offline, last seen 11d ago
100.85.130.92   s110       (android)       offline, last seen 12d ago
```

Tailscale (v1.102.3) is installed and `tailscaled` is running. Herdr's
remote transport is SSH, which can ride the tailnet. Per docs/ai/07 §12 and
docs/ai/08 §22, Tailscale is transport only — it must not become a task
queue, project registry, or scheduler, and Ominty must not hard-code
`100.x` addresses (docs/ai/10 §40).

---

## 7. Results

Results are retrievable as agent terminal output (`herdr agent read`) and
as a structured live snapshot (`herdr api snapshot`). Herdr has no
structured result contract equivalent to docs/ai/08 §17 (`status`,
`summary`, `artifacts`, `changes`); an Ominty adapter would need to wrap
raw agent output into that shape.

Notifications: `herdr notification show` — usable for completion signals
(compare docs/ai/08 §28, which prefers DMS notifications).

---

## 8. Lifecycle

`herdr agent wait` lets a caller block until an agent reaches one of a set
of states. This is the lifecycle primitive. It is **pull/wait based**, not
the event/queue model of docs/ai/07 §16. docs/ai/07 §16 explicitly warns:
"Do not implement a parallel Ominty task engine if Herdr already provides
suitable lifecycle management." Herdr does provide lifecycle for *sessions
of agents*; Ominty should not duplicate it.

---

## 9. Alignment and gaps

| docs/ai/07 requirement | Observed Herdr 0.9.0 | Gap |
|---|---|---|
| §2 Pi → Herdr → workers | `--remote`, `machine` | Ominty adapter missing (deferred) |
| §7 `ai.delegate` action | — | Action not in registry |
| §9 intent over destination | machine names, not IPs | Capability routing not present |
| §16 task lifecycle | `agent wait` states | Different model; adapter must map |
| §17 result return | `agent read`, `api snapshot` | No structured result contract |
| §23 adapter location | `ai/delegation/herdr/` | Not created (deferred) |
| §24 availability probe | `herdr status` | Not wired into Ominty |
| §25 failure isolation | — | To verify when implemented |

---

## 10. Recommendation

1. **Keep delegation deferred** (docs/ai/07 §30): local Pi + local context
   + local capabilities must be stable first. This stage only establishes
   the boundary, adapter location, and semantics.
2. **Adapter location confirmed:** `cli/omintylib/ai/delegation/herdr/`,
   exposing availability, a delegation-request → Herdr mapping, and a
   structured result wrapper.
3. **Availability probe:** `herdr status` (server running) is the natural
   check; treat Herdr as optional so its absence never affects local AI,
   Niri, DMS, or non-AI actions (docs/ai/07 §25).
4. **Do not model a job queue.** Map delegation onto Herdr sessions and
   agents; rely on `agent wait` / `agent read` for lifecycle and results.
5. **No addresses in prompts.** Resolve `herdr machine` names; never embed
   `100.x` targets in AI-authored content (docs/ai/10 §40).

---

## 11. Evidence

```text
$ which herdr                → ~/.local/bin/herdr
$ herdr --version            → herdr 0.9.0
$ herdr status               → server running, socket ~/.config/herdr/herdr.sock
$ herdr machine list         → No saved SSH machines.
$ tailscale status           → sb1 (online), t7910 (online), 2 offline
$ which agno                 → agno: not found (server-side only)
```