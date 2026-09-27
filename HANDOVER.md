# Handover — Omivoid LMDE (2026-09-27)

> Brief handover for the next agent session. Read this first, then the
> documents listed below (and `../PROGRESS.md`, the living progress log).

## Where we are

`omivoid-lmde/` is the **Phase 1 reference implementation**: a keyboard-first,
discoverable, dynamically themed, AI-aware Niri desktop driven by a canonical
Action Registry, on top of **DankMaterialShell (DMS)** as the shell layer.

Current state:

- **Registry:** 44 actions, 0 errors / 0 warnings (`omivoid registry validate`).
- **Tests:** 173 passing (`cd omivoid-lmde && PYTHONPATH=cli python3 -m pytest tests/`).
- **Niri bindings:** generated from the registry into
  `~/.config/omivoid/generated/niri/bindings.kdl` (included *last* in
  `~/.config/niri/config.kdl`), validated with `niri validate`.
- **Discovery:** `Super+K` = interaction explorer (DMS spotlight, `!!` sentinel);
  `Super+Space` = universal palette; `Super+A` = AI menu.
- **GKS cheat sheet:** `Super+Shift+S` opens the `omivoidKeybinds` DMS plugin — a
  read-only, tabbed, human-readable keybinding sheet fed by `omivoid keybinds --json`.
  Reference: `docs/implementation/keybindings-reference.md`.
- **AI:** provider layer (Pi + Ollama), policy + confirmation, capability
  catalogue + Pi tool bridge; local model = ollama `qwen2.5:3b`.
- **Theme:** DMS + Matugen; `Super+Ctrl+P` wallpaper carousel;
  `theme.palette.regenerate`, `theme.mode.toggle`.
- **Power menu:** DMS restart buttons for audio / network / niri via
  `customPowerButtons` (`system.audio.restart`, `system.network.restart`,
  `system.niri.reload`).

## Read these first

- `docs/00-project-overview.md` … `docs/13-phase-1-definition-of-done.md`
- `docs/decisions/` — ADRs 001–006
- `docs/implementation/` — audits, evaluations, implementation records
- `../PROGRESS.md` — living progress log + decisions log
- `AGENTS.md` — operating rules (contracts, code-quality, commit discipline)

## Outstanding (Phase 1 close-out)

Tracking: `docs/implementation/phase-1-completion-plan.md`. For the owner's
view of everything needing a decision/signature, see
`docs/implementation/user-sign-offs.md`.

**Close-out status (2026-09-27):**
1. ✅ **Desktop validation** — PASS, recorded (`desktop-validation.md`, DoD §25/§26).
2. ✅ **Exit review** — Accepted by the owner (`phase-1-exit-review.md`).
3. ✅ **Repo boundary** — **split**: `omivoid-lmde/` is its own repository.
4. Remaining: **#13** DMS "surface" contract (go/defer; default defer), **#3**
   `app.files.open` → DEFER, **#5** docs/08 + docs/12 reconciliation, and the
   **#4** dankHooks live wallpaper-change check.

## Key facts to carry

- **Project path:** `~/Projects/OmiVoid/omivoid-lmde/`, which is now **its own
  git repository** (split from the umbrella repo 2026-09-27) with a **GitHub
  remote** (`origin`, `MartinKnights/omivoid-lmde`). `PROGRESS.md`
  lives in the umbrella repo (`~/Projects/OmiVoid/PROGRESS.md`) and tracks the
  project from outside.
- **CLI:** `omivoid` — symlinked into `~/.local/bin` → `cli/omivoid`. Python 3.13
  stdlib + pytest only; no third-party runtime deps.
- **Compositor:** Niri 26.04 (Surface Book 1). **Shell:** DMS (Quickshell).
- **Contracts (AGENTS.md §7):** the Action Registry is authoritative; adapters
  define implementation; interaction surfaces must not hard-code commands where a
  canonical action exists; do not edit generated files by hand.
- **Generated vs source:** `~/.config/omivoid/generated/niri/bindings.kdl` is
  generated — fix the registry or the generator, never the file.
- **Personal paths:** do not commit `/home/mk` paths; use `$OMIVOID_CLI` /
  `omivoid` on PATH (AGENTS.md §22/§33).

## Recently done (2026-09-27)

- **Distribution phase started** — this repo is published on GitHub
  (`github.com/MartinKnights/omivoid-lmde`, public, `main`, 27 commits).
  The Debian distribution layer is `github.com/MartinKnights/O-my-Deb`
  (public; this repo is its submodule). The Void build is
  `github.com/MartinKnights/OmiVoid-install` (private).
- **Device backed up** to `/media/mk/ENYO/omivoid-backup-2026-09-27/`
  (git bundles, live configs, debs, package inventory, RESTORE.md) —
  ready for the Void transfer.
- Desktop validation PASS + exit review Accepted + repo split (session 18).

## Recently done (2026-09-24)

- GKS cheat-sheet DMS plugin + plain-English labels + keybindings reference —
  `c7c2764`.
- DMS power-menu restart buttons (`actions/system.toml`) — `4c587f0`.
- Stage 10 Niri-adapter wrap-up committed — `2164e02`.
- DMS pivot source docs (`update/`) + `The-Dank-Difference.md` — `5357759`.

## Background

The project pivoted on 2026-09-10 from rebuilding the Omarchy Quattro shell to
using **DMS as infrastructure**, concentrating Omivoid on the workflow above the
shell: keyboard grammar, action registry, discovery, theming, AI integration.
The three `update/` documents are the source for the current architecture (see
`update/01-A-New-Direction.md`).

Earlier Stage 10 adapter work (`adapters/niri/`) that was previously uncommitted
is now committed in `2164e02`.
