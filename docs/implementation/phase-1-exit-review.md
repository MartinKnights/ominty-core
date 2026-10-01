# Phase 1 Exit Review (DoD §33)

**Date:** 2026-09-24
**Stage:** Phase 1 close-out
**Status:** Accepted — by project owner, 2026-09-27
**Reviewed against:** `docs/13-phase-1-definition-of-done.md` §33
**Implementation head:** `f78340e` (44 actions, 173 tests)

---

## Summary

Phase 1 has moved the architecture from *documented idea* to *tested working
reference implementation*. The registry → adapter → generated-bindings chain is
real and exercised; discovery (`Super+K` / `Super+Space` / `Super+A`) and the
GKS cheat sheet (`Super+Shift+S`) run on DMS; AI proposes and Ominty decides,
with policy and confirmation on one execution path. The portable core is clean.

The honest caveats: several **abstractions were validated only lightly**
(chords, the DMS/dsh collision set, machine/profile layer), the **conversational
AI surface is thin**, and **no desktop validation (logout/login/reboot) has been
recorded yet**. Two things introduced near the end — `system.*` restart actions
— are **systemd-specific** and will need a service adapter before Void.

There is no architectural blocker to a Void phase, but the open portability
questions in `void-portability-review.md` §5 should be closed first.

---

## 1. What worked?

- **Registry as the single source of truth.** Every binding the user sees is
  derivable from `actions/*.toml`; the cheat sheet and docs are generated, not
  hand-maintained (`docs/02` §12).
- **The generator contract.** `ominty registry build` emits the Niri fragment,
  validates it with `niri validate`, and refuses to write invalid output; the
  include is `optional=true` and last, so Ominty wins collisions safely. The
  rollback test confirmed a lost fragment regenerates byte-identically.
- **Adapter separation (Contract 2/5).** `common` / `niri` / `dms` / `pi`
  adapters kept the core portable and testable; role indirection
  (`app.browser.open` → role `browser` → librewolf) proved clean.
- **AI with policy, not bypass.** `ai_accessible`, risk gating, `ai-only`
  confirmation, recursion denial, and the confirmation/deny proofs
  (AI Phase C) work — AI never executes implementation commands directly.
- **Discovery surfaces.** `Super+K` explorer, `Super+Space` palette merge,
  `Super+A` AI menu, and the tabbed cheat sheet all run through the registry.
- **Test discipline.** 173 tests, no third-party runtime dependencies.

## 2. What felt awkward?

- **Chords do not exist natively.** Niri allows one action per keybind; DMS has
  no submap. `Super+A,A` etc. are registry *intent* realised by the launcher.
  Workable, but it is a documented compromise, not a real grammar feature.
- **The DMS collision set is static.** `DMS_CLAIMED_KEYS` in `generator.py` is a
  hand-maintained list; it can drift from the live `~/.config/niri/dms/binds.kdl`.
  It already bit us twice (`Mod+Shift+K`, `Mod+Space`).
- **`Super+K` explorer uses a sentinel** (`dms ipc call spotlight openQuery "!!"`)
  because DMS ignores single-character plugin queries — a workaround, not a
  first-class "open explorer" entry point.
- **Binding ownership is split.** Registry actions with keys → Niri fragment;
  chords and `shell.*` adapters are shell-handled and *excluded* from the
  fragment. Knowing which layer owns a key requires knowing the rule.
- **Two similar help actions.** `help.keys.open` (explorer) vs
  `help.keybinds.open` (cheat sheet) read almost identically.
- **Hardware-specific cheat-sheet labels.** Mapping media keys to `F1`–`F11` is
  correct for the Surface Book but is baked into `keybinds.py` — a different
  keyboard needs a different map.
- **`command` adapter has no shell.** Compound commands need `sh -c`, and the
  `arguments.command` vs top-level `command` split caused a real bug.

## 3. Which abstraction was unnecessary?

- **The machine layer (`config/machines/`, `config/platforms/`).** Documented
  (docs/05 §7) and scaffolded, but never exercised — adapter resolution is
  platform → common only. It is speculative surface for Phase 1.
- **Two DMS invocation paths.** `dms.ipc` (structured `arguments.dms`) and the
  generic `command` adapter both end at `dms ipc call …`. One would have done;
  the structured form is nicer but the duplication is real.
- **`shell.explorer` as a distinct adapter** is thin — it is a one-line spawn.
  It earns its place only because Contract 3 requires a canonical action, not
  because it encapsulates behaviour.

*(None of these are wrong — they are candidates to simplify, not defects.)*

## 4. Which abstraction is missing?

- **A live keybinding authority.** Something must reconcile the registry's
  `keys` with the actual DMS/Niri bindings instead of a static exclusion list.
- **A service/package adapter.** `system.audio.restart` already calls
  `systemctl --user`; Void uses runit. This boundary does not exist yet.
- **A "surface" abstraction.** Each DMS plugin (actions, cheat sheet) is
  hand-written QML that re-invokes the CLI. There is no shared contract for
  "render registry data in a DMS surface".
- **An AI action audit log.** Audit metadata exists but is not persisted
  (docs/ai/09 §36).
- **Structured key/action presentation** is currently duplicated between
  `keybinds.py` (labels) and the plugins — a shared presentation layer would help.

## 5. Is DMS the correct long-term shell?

**For Phase 1, yes — decisively.** Adopting DMS avoided rebuilding the bar,
notifications, OSD, control centre, lock, screenshots, media and theming; the
project concentrated its effort on the differentiators (registry, grammar,
discovery, AI). ADR-006 (plugin-first) was the right call.

**For Void, it is a managed risk, not a conclusion.** DMS is packaged for
Debian here; its Void availability/version and the `dms ipc`/`dms matugen`
surface must be validated (`void-portability-review.md` §5.4, §5.6). The
mitigation is already in place: the registry, generator and adapters are
shell-agnostic, so DMS is replaceable behind the `dms.*` adapters.

**Recommendation:** keep DMS, but treat it as a *dependency behind adapters*,
not as the architecture. Avoid new hard couplings to DMS internals.

## 6. Is the Action Registry schema sufficient?

**Mostly yes.** Required fields, categories, risk, confirmation, contexts,
platforms, requirements, AI/voice accessibility, keywords, icon/priority hints
and namespace rules were enough to express 44 real actions across 12 categories.

**Gaps found:**

1. **No ownership/claim field.** Nothing records that a key is owned by DMS/Niri
   vs Ominty, so collision handling lives in the generator instead of the data.
2. **Adapter/argument shape is loose.** `dms.ipc` uses `arguments.dms`, the
   `command` adapter uses top-level `command`; the schema allows both with no
   stated rule.
3. **Chords are not first-class.** They are valid syntax but not bindable.
4. **No service/package vocabulary** (needed for Void).
5. **No `surface`/presentation hint** — plugins hard-code how rows render.

None block Phase 1; #1 and #2 are worth fixing before the action count grows.

## 7. Is the keyboard grammar comfortable?

**Broadly yes, with rough edges.** Eight domains map cleanly to modifiers; the
priority algorithm (include order + `DMS_CLAIMED_KEYS`) resolves collisions
predictably; `Super+K/Space/A` and `Super+Shift+S` are easy to reach.

Rough edges:

- **The grammar needed tuning under real use:** the `Window state` tier collapsed
  into `Desktop`, and tab labels were shortened — evidence the original tiering
  was designed more than used.
- **Media keys are hardware-shaped.** The `F1`–`F11` mapping is Surface-Book
  specific.
- **Cross-desktop collisions persist.** DMS owns a lot (`Mod+Shift+H/J/K/L`,
  media keys), so the "grammar" is really "the grammar within what DMS leaves".
- **Chords** (the most expressive part) are unavailable natively.

## 8. Is AI integration useful rather than decorative?

**Useful as an executor; thin as a conversation.** The proof that matters is
real: *"Open my browser"* → Pi → `app.browser.open` → role → librewolf, with
policy, confirmation and recursion protection on the single runner path. AI also
carries clipboard and project context, and delivers replies as notifications.

**Honest limits:** the ask surface has no streaming/markdown; the local model
(`qwen2.5:3b`, CPU-only) is deliberately small, so quality is modest; and
selection capture, delegation (Herdr), and voice remain deferred. Today AI is
*an action executor with a basic chat front*, not a co-pilot — which is exactly
what Phase 1 set out to prove, and no more.

## 9. What must change before Void?

1. **Close the portability questions** in `void-portability-review.md` §5.
2. **Abstract services.** `system.audio.restart` (`systemctl --user`) and the
   `dms`/`niri` restart commands are systemd/NM-shaped; introduce a service
   adapter (systemd ↔ runit) and a package adapter (`apt` ↔ `xbps-install`).
3. **Validate DMS + Niri packaging on Void** (versions, `DMS_SHELL_DIR`,
   `niri validate` CLI, `wl-clipboard` package name).
4. **Document runit autostart** for the Niri session + DMS (Phase 1 uses systemd
   user services).
5. **Settle application-role defaults for Void** (packages may be named
   differently).
6. **Resolve the repo-boundary decision** and keep the personal-path/portability
   scrub enforced.

No **architectural** change is required — the Void phase is packaging plus two
new adapters, exactly as the portability review concluded.

## 10. What should remain exactly the same?

- The **contracts** (AGENTS.md §7): registry authoritative; adapters define
  implementation; surfaces never hard-code commands; generated files never
  hand-edited.
- The **registry → generator → `niri validate` → include-last** pipeline.
- The **one execution path** for AI (`ai/actions.py` composing policy + runner).
- **Shell-agnostic core** with DMS/Niri behind adapters.
- **XDG paths**, PATH-based dependency checks, no third-party runtime deps.
- The **audit discipline**: environment/binding/DMS/portability records kept
  current, decisions logged, deferred work explicit.

---

## Exit decision

**Phase 1 meets its architectural goal.** The remaining DoD items are close-out,
not architecture:

- desktop validation (§25/§26) and this review's sign-off (§33);
- the `app.files.open` binding decision and the `dankHooks` evaluation;
- docs/08 (theme) and docs/12 (config layout) reconciliation.

**Recommendation:** sign off Phase 1 once the desktop validation is recorded,
then begin the **Void phase** starting with the service + package adapters and
the portability-question resolutions above. Do **not** carry speculative
abstractions (machine layer) or the static `DMS_CLAIMED_KEYS` approach forward
without revisiting them.
