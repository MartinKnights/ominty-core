# Phase 1 Completion Plan

**Date:** 2026-09-24
**Status:** Active
**Source:** `phase-1-exit-review.md`, `docs/13-phase-1-definition-of-done.md`, `../PROGRESS.md`

This plan closes out Phase 1 and settles the pre-Void items the exit review
flagged. Items are grouped: **Tier 1** must finish for Phase 1 sign-off;
**Tier 2** should finish before the Void phase; **Tier 3** is the Void phase
itself.

Size: S ≈ <1 h, M ≈ half day, L ≈ multi-session.

---

## Tier 1 — Phase 1 completion (sign-off blockers)

| # | Task | Owner | Size | Deliverable | Status |
|---|---|---|---|---|---|
| 1 | **Desktop validation** — Super+K, Super+Space, Super+Shift+S, Super+A, logout/login, reboot | **User** | S | `docs/implementation/desktop-validation.md` (filled checklist) | ✅ DONE (PASS, 27-09-2026) |
| 2 | **Exit review sign-off** — accept `phase-1-exit-review.md` | **User** | S | status Draft → Accepted | ✅ DONE (Accepted 2026-09-27) |
| 3 | **`app.files.open` binding decision** — recommend **DEFER** (no key; reachable via palette/CLI/AI) | Agent | S | `niri-binding-audit.md` item #4 → DEFER | TODO |
| 4 | **`dankHooks` evaluation** — event bridge for `theme.palette.regenerate` on wallpaper change | Agent (+User to install) | M | `docs/implementation/dankhooks-evaluation.md` | ✅ DONE (activated 2026-09-27) |
| 5 | **docs/08 (theme) + docs/12 (config layout) reconciliation** | Agent | S | both docs reflect the implementation | TODO |
| 6 | **Link + commit** the exit review from `PROGRESS.md` / `HANDOVER.md` | Agent | S | commit | ✅ DONE (`de0a001`-era; Accepted + linked 2026-09-27) |
| 7 | **Repo-boundary decision** — keep `ominty-core/` inside the `Ominty` repo, or split | **User** | S | decision recorded | ✅ DONE (**split**, 2026-09-27) |

**Exit criterion:** items 1–2 done + Tier-1 agent items committed → Phase 1
declared complete. **Met 2026-09-27** — items 1 and 2 are done; remaining
Tier-1 rows are non-blocking housekeeping (#3, #5).

> **User sign-offs:** everything needing your decision or signature — the three
> Tier-1 items below plus the #13 go/defer choice — is explained in
> `docs/implementation/user-sign-offs.md`. All decided 2026-09-27 (see top of
> that file); status per row.

> **Repo note:** with the 2026-09-27 split, this document (and everything under
> `ominty-core/`) now lives in its **own git repository**. `../PROGRESS.md`
> is external — it lives in the umbrella repo `~/Projects/Ominty`.

---

## Tier 2 — Pre-Void hardening (exit-review findings)

| # | Task | Owner | Size | Deliverable | Status |
|---|---|---|---|---|---|
| 8 | **Live keybinding authority** — replace the static `DMS_CLAIMED_KEYS` set in `generator.py` with a parse of the live `~/.config/niri/dms/binds.kdl` (fall back to the static set) | Agent | M | generator change + tests | ✅ DONE (`456d81d`) |
| 9 | **Service adapter** — abstract `systemctl --user` ↔ runit (`sv`); route `system.audio.restart` through it | Agent | M | `adapters/{debian,void}/service_restart.py` + action update | ✅ DONE |
| 10 | **Package adapter** — `apt` ↔ `xbps-install` boundary (docs/05 §10–11) | Agent | M | `adapters/{debian,void}/package_install.py` + spec note | ✅ DONE |
| 11 | **Schema: ownership/claim + adapter/command shape** — add an `key_owner` field (docs/03 §11); state and enforce the `arguments.command` vs top-level `command` rule | Agent | S | `docs/03` + `registry.py` | ✅ DONE (`cebf7b7`) |
| 12 | **Machine layer** — implement platform→common resolution or mark the machine layer explicitly deferred | Agent | S | `docs/05` + decision | ✅ DONE (deferred, 2026-09-27) |
| 13 | **Shared DMS "surface" contract** — one way to render registry data in a DMS plugin | Agent | L | design note (may defer to Phase 2) | TODO |

Ordering: 8 and 9 first (highest drift/portability risk); then 10–12; 13 is
opportunistic.

---

## Tier 3 — Void phase (next phase)

Packaging (`xbps`), DMS/Niri packaging validation, runit autostart, Void
application-role defaults, and closing `void-portability-review.md` §5. No
architectural change expected.

---

## Immediate next actions

- **Declared Phase 1 complete** (DoD §38): items 1–2 done 2026-09-27; repo
  boundary decided (split).
- **Agent items still open:** #13 (DMS surface contract — user to say go/defer;
  default defer), #3 (`app.files.open` → DEFER), #5 (docs/08 + docs/12
  reconciliation).
- #4 dankHooks manual desktop test (real wallpaper change) remains a live
  verification item.
