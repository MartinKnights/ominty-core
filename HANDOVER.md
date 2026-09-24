# Handover — Omivoid LMDE (2026-09-10)

> Brief handover for the next agent session. Read this first, then the source
> documents listed below.

## Where we are

The Omivoid project has **changed direction**. Instead of rebuilding the Omarchy
Quattro shell layer under Niri, Omivoid will use **DankMaterialShell (DMS)** as
infrastructure and concentrate on the workflow above it: keyboard grammar,
action registry, discovery, theming, and AI integration.

The new project documentation tree exists at `omivoid-lmde/` — **all files are
empty** and awaiting content.

## Source documents (read these first)

- `~/Projects/OmiVoid/update/01-A-New-Direction.md` — the pivot to DMS
- `~/Projects/OmiVoid/update/02-Omivoid-Interaction-Specification.md` — interaction spec draft v0.1
- `~/Projects/OmiVoid/update/03-Omivoid-Action-Registry-Specification.md` — action registry spec draft v0.1

## What the next agent should do

1. **Fill in the empty files** in `omivoid-lmde/`:
   - `AGENTS.md` — agent rules for the new project (adapt from
     `~/Projects/OmiVoid/AGENT.md`)
   - `docs/00-project-overview.md` … `docs/10-phase-1-implementation-plan.md`
   - `docs/decisions/ADR-001-niri-as-compositor.md` … `ADR-005-lmde-validation-platform.md`
2. Content should be derived from the three `update/` documents plus the
   carried project knowledge (Niri adapter work, DMS decision, registry
   architecture, LMDE validation platform).
3. The user has reviewed the structure; confirm before adding content if
   anything is ambiguous.

## Key facts to carry

- **Project path:** `~/Projects/OmiVoid/` (the user sometimes mistypes the
  path with an extra leading `~` — the correct path has none)
- **New project:** `~/Projects/OmiVoid/omivoid-lmde/`
- **Compositor:** Niri 26.04 (installed, validated on Surface Book 1)
- **Shell:** DMS (DankMaterialShell) — Quickshell-based, Niri-optimized,
  wallpaper-based theming (GTK/Qt/terminals/editors)
- **Five principles:** universal interaction model, keyboard-first,
  discoverable (Super+K), visually coherent (DMS + Matugen + app templates),
  AI-native (Pi + Herdr + agent integration)
- **Action registry:** `namespace.subject.action` IDs (e.g. `app.browser.open`,
  `window.focus.left`, `workspace.next`, `system.lock`); registry describes
  meaning, adapters define implementation
- **Phase 1 scope:** ~30–40 actions; TOML → validation → action runner → Niri
  generation → Super+K data → command palette data. Defer: registry daemon,
  event bus, DBus service, plugin sandboxing, etc.

## Uncommitted work in the old project (Stage 10)

The Niri adapter fixes from the previous session are **not committed**:
- `adapters/niri/services/PluginRegistry.qml` (`find -L` fix)
- `adapters/niri/Niri.qml` (idx on focusedWorkspace, layoutChanged signal,
  event-pattern fix, temp DEBUG log)
- `adapters/niri/Workspaces.qml` (idx-based 1–9 workspace widget)
- `adapters/niri/KeyboardLayout.qml` (new niri port)
- `adapters/niri/launch.sh` (PATCHED list additions)

Decide with the user whether to commit these as a wrap-up of Stage 10 or leave
them as reference material for the new architecture.