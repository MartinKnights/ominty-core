# Handover — Ominty LMDE (2026-09-28)

> **Historical snapshot.** This document records the state of the project as of
> 2026-09-28, before the OmiVoid → Ominty rebrand. Several references below are
> superseded. For current instructions see [`AGENTS.md`](AGENTS.md) and the
> distribution repo's root `AGENTS.md`.

> Brief handover for the next agent session. Read this first, then the
> documents listed below (and `../PROGRESS.md`, the living progress log).

## Where we are

`ominty-core/` is the **Phase 1 reference implementation**: a keyboard-first,
discoverable, dynamically themed, AI-aware Niri desktop driven by a canonical
Action Registry, on top of **DankMaterialShell (DMS)** as the shell layer.

Current state:

- **Registry:** 44 actions, 0 errors / 0 warnings (`ominty registry validate`).
- **Tests:** 173 passing (`cd ominty-core && PYTHONPATH=cli python3 -m pytest tests/`).
- **Niri bindings:** generated from the registry into
  `~/.config/ominty/generated/niri/bindings.kdl` (included *last* in
  `~/.config/niri/config.kdl`), validated with `niri validate`.
- **Discovery:** `Super+K` = interaction explorer (DMS spotlight, `!!` sentinel);
  `Super+Space` = universal palette; `Super+A` = AI menu.
- **GKS cheat sheet:** `Super+Shift+S` opens the `omintyKeybinds` DMS plugin — a
  read-only, tabbed, human-readable keybinding sheet fed by `ominty keybinds --json`.
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
3. ✅ **Repo boundary** — **split**: `ominty-core/` is its own repository.
4. Remaining: **#13** DMS "surface" contract (go/defer; default defer), **#3**
   `app.files.open` → DEFER, **#5** docs/08 + docs/12 reconciliation, and the
   **#4** dankHooks live wallpaper-change check.

## Key facts to carry

- **Project path:** `~/Projects/Ominty/ominty-core/`, which is now **its own
  git repository** (split from the umbrella repo 2026-09-27) with a **GitHub
  remote** (`origin`, `MartinKnights/ominty-core`). `PROGRESS.md`
  lives in the umbrella repo (`~/Projects/Ominty/PROGRESS.md`) and tracks the
  project from outside.
- **Next phase: Void on this device.** The install kit is staged on the ENYO
  drive (`SB1_backup/void-install/` + `SB1_backup/Projects/OmiVoid-Install`).
  The device will be wiped — this LMDE system is the last one.
- **CLI:** `ominty` — symlinked into `~/.local/bin` → `cli/ominty`. Python 3.13
  stdlib + pytest only; no third-party runtime deps.
- **Compositor:** Niri 26.04 (Surface Book 1). **Shell:** DMS (Quickshell).
- **Contracts (AGENTS.md §7):** the Action Registry is authoritative; adapters
  define implementation; interaction surfaces must not hard-code commands where a
  canonical action exists; do not edit generated files by hand.
- **Generated vs source:** `~/.config/ominty/generated/niri/bindings.kdl` is
  generated — fix the registry or the generator, never the file.
- **Personal paths:** do not commit `/home/mk` paths; use `$OMINTY_CLI` /
  `ominty` on PATH (AGENTS.md §22/§33).

## Recently done (2026-09-28)

- **Void pivot: local install on this device.** Void will replace LMDE 7 on
  the Surface Book 1 itself (not a remote machine over SSH). The
  `OmiVoid-install` repo was rewritten for the local workflow
  (`370133d`): new `docs/void-hardware.md` (verified hardware facts + swap
  recommendation) and `docs/wifi-install.md` (wpa_supplicant + dhcpcd from
  the base glibc image), refreshed `package-list.md` (DMS Void repo at
  `void.danklinux.com`, niri in void-packages, iptsd from source), local
  install sequence in `void-install-plan.md`, `ssh-setup.md` demoted to
  optional. Submodule bumped to `2b29965` (`7b39277`).
- **SB1_backup on the ENYO drive** (`/media/mk/ENYO/SB1_backup/`): configs,
  local tools, 9 AI agent zips, SSH keys, dotfiles, and Ollama models (25G,
  user-run sudo copy). Void install kit staged in `void-install/`: Wi-Fi
  firmware `pcie8897_uapsta.bin`, iptsd source, Void base ISO (downloading).
- Distribution phase (session 19): three GitHub repos + device backup.

## Recently done (2026-09-27)

- **Distribution phase started** — this repo is published on GitHub
  (`github.com/MartinKnights/ominty-core`, public, `main`, 27 commits).
  The Debian distribution layer is `github.com/MartinKnights/Ominty` (renamed from `O-my-Deb`)
  (public; this repo is its submodule). The Void build is
  `github.com/MartinKnights/Ominty-install` (private).
- **Device backed up** to `/media/mk/ENYO/ominty-backup-2026-09-27/`
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
using **DMS as infrastructure**, concentrating Ominty on the workflow above the
shell: keyboard grammar, action registry, discovery, theming, AI integration.
The three `update/` documents are the source for the current architecture (see
`update/01-A-New-Direction.md`).

Earlier Stage 10 adapter work (`adapters/niri/`) that was previously uncommitted
is now committed in `2164e02`.
