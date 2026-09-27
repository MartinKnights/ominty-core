# Omivoid Phase 1 — User Sign-off Package

**Purpose:** everything *you* (the project owner) need to decide or sign during
Phase 1 close-out, each explained. Agent-owned items and the one open design
item (#13) are covered in the appendix.

**Tracking** (`phase-1-completion-plan.md`): items 1 and 2 are Tier 1 **sign-off
blockers** — Phase 1 is declared complete only when both are done. Item 7 is a
Tier 1 decision (does not block declaration, but should be settled before the
Void phase). Item 13 (appendix) is Tier 2 and opportunistic.

| Item                                        | What you decide/sign                               | Blocker?          | After you sign, I will…                           |
| ------------------------------------------- | -------------------------------------------------- | ----------------- | ------------------------------------------------- |
| **1. Desktop validation**                   | Perform and record the manual desktop tests        | Yes (DoD §25/§26) | Reference the filled checklist from `PROGRESS.md` |
| **2. Exit review acceptance**               | Accept `phase-1-exit-review.md` (Draft → Accepted) | Yes               | Flip status, commit                               |
| **3. Repo-boundary decision**               | Keep one repo, or split `omivoid-lmde/` out        | No                | Record the decision                               |
| **13. DMS "surface" contract** *(appendix)* | Say go / defer                                     | No                | Write the design note, or park it                 |

---

## Status — resolved 2026-09-27

- **1. Desktop validation** — ✅ **done:** `desktop-validation.md` §A–D all pass,
  regression checks clear, **Result: PASS** (date 27-09-2026, DoD §25/§26).
- **2. Exit review acceptance** — ✅ **done:** accepted by the owner,
  `phase-1-exit-review.md` status → **Accepted** (2026-09-27).
- **3. Repo boundary** — ✅ **decided: split.** `omivoid-lmde/` is now its own
  git repository (history-preserving, 2026-09-27); the umbrella repo keeps
  `PROGRESS.md`. Decisions on #1/#2/#3 also logged in `PROGRESS.md`.
- **13. DMS "surface" contract** — still open; default recommendation remains
  **defer to Phase 2**.

---

## 1. Desktop validation (completion plan #1)

**What it is.** The manual, at-the-keyboard test run that proves Phase 1 actually
works on your hardware: discovery surfaces, the power-menu buttons, and that the
system survives a logout and a reboot. Everything here is safe — nothing in the
checklist modifies configuration, and a known-good restore path is documented.

**Why it's yours.** These are physical, visual, interactive checks only you can
run on the machine. An agent cannot press `Super+K` or verify the wallpaper
carousel.

**What you do.** Open:

```text
docs/implementation/desktop-validation.md
```

Fill in **Date / Operator / Implementation head**, then work through the five
sections, ticking boxes:

| Section | What it tests                                                                                                                                          |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **A**   | Automated pre-checks (`omivoid registry validate`, `niri validate`, DMS active, fragment present, `omivoid` on PATH, plugins installed)                |
| **B**   | Discovery & keybindings: `Super+K` explorer, `Super+Space` palette, `Super+Shift+S` GKS cheat sheet, `Super+A` AI menu, app launch, wallpaper carousel |
| **C**   | Power-menu buttons (`Super+X`): Restart Audio, Restart Network, Reload Niri, built-in Restart DMS                                                      |
| **D**   | Session lifecycle (**DoD §26**): log out, log in, reboot, verify everything still works after each                                                     |
| **E**   | Results/failures: any test that failed `Expected`, plus the three regression checks                                                                    |
| **F**   | Sign-off: overall **PASS / PASS WITH NOTES / FAIL** + your signature                                                                                   |

**Estimate:** ~30–45 minutes, including one reboot. Run section **C4** (Restart
Network) only when briefly losing Wi-Fi is acceptable.

**Evidence produced:** the completed `desktop-validation.md`. When done, tell me
and I'll reference it from `PROGRESS.md` (completion plan #1 → ✅ DONE).

**If a test fails:** don't try to fix it yourself — note it in §E with the exact
key, expected vs actual, and I'll take it from there.

---

## 2. Exit review acceptance (completion plan #2)

**What it is.** `docs/implementation/phase-1-exit-review.md` is the close-out
review of the whole phase — what the implementation achieved, what it didn't,
and the recommendations (including the ones that fed Tier 2 work like #8–#12).
It is currently:

```text
Status: Draft — for user review
```

**Why it's yours.** It's the final judgement on Phase 1. The document itself
makes the point that the architecture was validated — but *accepting* that
judgement is your call as the owner.

**What you do.** Read it (about 20 minutes — it's 200 lines). If you agree with
its findings and recommendations, reply **Accepted**. If anything in it seems
wrong or over-optimistic, tell me which section and why; I'll amend it.

**Evidence produced:** the document's status flips to `Accepted` and is
committed.

---

## 3. Repo-boundary decision (completion plan #7)

**What it is.** A structural decision: today there is **one** git repository
(`~/Projects/OmiVoid`) that contains both the design/umbrella material
(`docs/`, `PROGRESS.md`, `hardware/`, `niri/`, `quickshell/`, `upstream/`, …)
**and** the implementing tree `omivoid-lmde/` as a plain subdirectory. There is
no separate `omivoid-lmde.git`. Do we keep that, or split `omivoid-lmde/` into
its own repository?

**Why it's yours.** It decides where history, remotes and CI live long-term —
an ownership decision, not an implementation detail. It matters most if/when
the project becomes public (AGENTS.md §32/§37) and as the Void phase begins.

**Option A — keep one repo (current state).**

- *Advantages:* single history; everything stays cross-linked (`PROGRESS.md`
  one level up, `HANDOVER.md` inside the tree); zero migration; this Phase-1
  history stays contiguous.
- *Disadvantages:* one repo mixes design docs with the implementer; commit
  hygiene needs care so umbrella noise and implementation noise don't tangle;
  publishing just the implementation is harder.

**Option B — split `omivoid-lmde/` into its own repository.**

- *Advantages:* clean separation of design vs implementation; independent
  remote/CI; `omivoid-lmde` can be published on its own; context stays tight
  for future agents.
- *Disadvantages:* a migration step (fresh history or filter-repo); the
  cross-references to `PROGRESS.md`/umbrella docs would need explaining or
  duplicating; two-repo maintenance.

**Recommendation:** keep one repo **for now**. Phase 1 is nearly finished and
there's no benefit in a mid-close-out migration. Revisit the split at the start
of the Void phase, when the repo may go public and a clean line between "design
umbrella" and "implementing project" becomes valuable.

**What you do.** Reply **keep** or **split**. I record the decision in this
document and `PROGRESS.md` (completion plan #7).

---

## Appendix — Step #13 explained (shared DMS "surface" contract)

This is the last open Tier 2 item. The completion plan calls it:

> **Shared DMS "surface" contract** — one way to render registry data in a DMS
> plugin | design note (may defer to Phase 2) | L | opportunistic

### The problem it solves

Three DMS plugins currently consume Omivoid's action registry, and each
hard-codes its own idea of what an "action row" is:

1. **`omivoidActions`** — the `Super+Space` palette shows actions alongside
   apps;
2. **`omivoidKeybinds` / GKS** — the `Super+Shift+S` cheat sheet renders
   actions as keybinding rows;
3. **the DMS power menu** — `customPowerButtons` renders the three system
   restart actions as buttons.

The exit review (§6, gap 5) phrased it as:

> **No `surface`/presentation hint** — plugins hard-code how rows render.

Each plugin re-implements the same logic by hand: which fields exist (`name`,
`description`, `keys`, `icon`, `priority`, …), how rows are indexed/searchable,
and which actions belong to which surface.

### What "the contract" would be

One canonical way to render registry data in any DMS plugin:

1. **A generated, disposable runtime registry** — e.g.
   `~/.cache/omivoid/registry.json`, exactly the pattern docs/03 §33 already
   reserves. The TOML stays the source of truth; the JSON is a stale-able
   snapshot.
2. **A defined row shape** — a small, documented schema every plugin consumes:
   `id`, `name`, `short_name`, `description`, `category`, `keywords`, `keys`,
   `primary_key`, `icon`, `priority`, `contexts`, `key_owner`.
3. **One rendering/indexing rule** — shared logic for "show this action as a
   row" (title, subtitle, icon, sort) and one search prefix behaviour, instead
   of each plugin replicating it.

The result (ADR-006 §2.2): DMS remains a **consumer** of Omivoid actions — it
just stops hand-duplicating how it renders them.

### Why it's marked L and "may defer to Phase 2"

It is a design **plus** implementation task: the JSON shape, a registry build
step, and changes to **three** plugins. It is the largest open Tier 2 item, and
nothing currently *breaks* without it — the plugins work, they're just
repetitive. AGENTS.md §12/§13 also say to prefer DMS's own capability before
building parallel machinery. Hence "opportunistic".

### What you decide

- **Default recommendation: defer to Phase 2.** The exit review already judged
  it non-blocking, and Phase 1 close-out doesn't need it. Revisit when a *fourth*
  consumer appears or when the registry build (`~/.cache/omivoid/registry.json`)
  is needed for another reason.
- **Want it now:** the actual deliverable for #13 is the **design note** (row
  schema + JSON shape + consumer list), not the full implementation. I'd write
  that first — it's a small document — and treat plugin work as follow-on.

Reply **defer** or **go** (optionally *go, design note only*), and I'll action it.