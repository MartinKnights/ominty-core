# AI Context Evaluation — Selection Investigation and Decision

**Date:** 2026-09-18
**Stage:** AI-23, AI-24 (docs/ai/10-ai-phase-1-implementation-plan.md §29–30)
**Status:** Complete

Investigation of reliable selection acquisition in the actual
LMDE / Niri / Wayland / DMS environment, and the resulting classification.

---

## 1. Summary

| Stage | Deliverable | Status |
|---|---|---|
| AI-23 | Selection acquisition investigation + implementation notes | Complete |
| AI-24 | Selection support classification | **CLIPBOARD FALLBACK** |

Direct desktop selection capture is **not reliably available** on this
stack. Phase 1 implements honestly-labelled clipboard alternatives
(`ai.clipboard.explain`, `ai.clipboard.summarise`) instead of faking
`ai.selection.*` (AGENTS.md §19, docs/ai/05 §52, docs/ai/10 §31).

---

## 2. Tested Mechanisms

### 2.1 `wl-paste --primary` (Wayland primary selection)

```text
Status:  NOT AVAILABLE
Reason:  wl-clipboard is not installed (wl-paste/wl-copy missing)
```

The standard Wayland selection reader is absent. Even when installed,
primary-selection support is application-dependent: many Wayland-native
apps do not implement the primary selection protocol, so `wl-paste
--primary` frequently returns nothing even with a visible selection.

### 2.2 `xclip` / `xsel` (X11 selection)

```text
Status:  INSTALLED but X11-only
Reason:  /usr/bin/xclip, /usr/bin/xsel present
```

These read the X11 selection. Under Niri, X11 apps run through
xwayland-satellite, so `xclip -o -selection primary` only sees selections
made inside XWayland clients. Wayland-native selections are invisible to
them. Not a reliable general mechanism.

### 2.3 Niri IPC

```text
Status:  NO SELECTION SURFACE
Evidence: niri msg exposes no selection or clipboard command
```

Niri does not expose selection/clipboard state through its IPC.

### 2.4 DMS clipboard service

```text
Status:  HISTORY ONLY, NO SELECTION
Evidence: dms ipc clipboard → close, open, toggle only
```

DMS maintains a clipboard history (internal `clipboard.getHistory`
request via `DMSService`), but there is no IPC to read the *current*
clipboard content, and no selection surface at all. The history modal is
a UI, not a data API.

### 2.5 Clipboard (regular, not primary)

```text
Status:  AVAILABLE AFTER wl-clipboard INSTALL
Mechanism: wl-paste (regular clipboard)
```

The regular Wayland clipboard is readable with `wl-paste` once
`wl-clipboard` is installed. This is the reliable context source for
Phase 1.

---

## 3. Findings

1. **No direct selection path exists** on the current stack without
   adding wl-clipboard — and even then, primary selection is
   application-dependent and unreliable.
2. **The regular clipboard is the reliable context source.** It is
   explicitly a *different* context type from selection (docs/ai/05 §18).
3. **DMS cannot supply selection or current-clipboard content** through
   its public IPC surface.
4. **Faking selection** (e.g. treating the clipboard as "the selection")
   would violate AGENTS.md §19 and docs/ai/05 §6.

---

## 4. Decision — AI-24

```text
Classification:  CLIPBOARD FALLBACK
```

Per docs/ai/05 §52 and docs/ai/10 §31:

> If direct selection capture is unreliable, Phase 1 may offer
> "copy selection → Explain Clipboard" as an explicit fallback.
> This must be labelled clipboard-based rather than pretending
> direct selection capture works.

Consequences:

* Implement `ai.clipboard.explain` and `ai.clipboard.summarise`
  (accurately named clipboard alternatives).
* Do **not** implement `ai.selection.explain` / `ai.selection.summarise`
  in Phase 1.
* The `Super+A,E` / `Super+A,S` chords remain registry intent, realised
  by the clipboard actions (the user-facing "explain/summarise" slots).
* Direct selection support is **DEFER** — revisit if wl-clipboard is
  installed and a reliable primary-selection path is demonstrated.

---

## 5. Dependency

Clipboard context requires `wl-clipboard` (provides `wl-paste`):

```bash
sudo apt install wl-clipboard
```

The collector degrades gracefully: without `wl-paste` it returns
`CONTEXT_UNAVAILABLE` rather than stale or guessed data (AGENTS.md §19).

---

## 6. Related Records

* `docs/implementation/ai-phase-e.md` — Phase E implementation record
  (AI-21, AI-22, AI-25).
* `docs/ai/05-context-system.md` — context system specification.
* `docs/ai/10-ai-phase-1-implementation-plan.md` §27–31 — Phase E scope.