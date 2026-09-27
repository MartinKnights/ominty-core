# Desktop Validation Checklist (DoD §25/§26)

**Date:** ___________
**Operator:** ___________
**Implementation head:** ___________
**Session:** Niri + DMS (Surface Book 1)

DoD §25 requires the manual desktop interaction tests to be completed and
recorded; §26 requires the system to survive a clean session restart or reboot.
This checklist is run by the user at the keyboard; tick each box and note any
failure (with the `Expected` / `Actual` columns in §E).

> Before you start: confirm a known-good restore path exists
> (`docs/implementation/rollback-test.md`; Niri config backups
> `~/.config/niri/config.kdl.bak-*`). Reboot validation is safe — nothing here
> modifies configuration.

---

## A. Automated pre-checks (terminal)

Run these before the interactive tests and again after reboot (§D).

| Check             | Command                                                                                                     | Expected                                                 | Pass |
| ----------------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ---- |
| Registry valid    | `omivoid registry validate`                                                                                 | `44 action(s), 0 error(s), 0 warning(s)`                 | [x]  |
| Niri config valid | `niri validate -c ~/.config/niri/config.kdl`                                                                | `config is valid`                                        | [x]  |
| DMS running       | `systemctl --user is-active dms`                                                                            | `active`                                                 | [x]  |
| Fragment present  | `tail -3 ~/.config/niri/config.kdl`                                                                         | includes `~/.config/omivoid/generated/niri/bindings.kdl` | [x]  |
| omivoid on PATH   | `command -v omivoid`                                                                                        | a path (e.g. `~/.local/bin/omivoid`)                     | [x]  |
| Plugin installed  | `ls ~/.config/DankMaterialShell/plugins/omivoidKeybinds ~/.config/DankMaterialShell/plugins/omivoidActions` | both present (symlinks)                                  | [x]  |

---

## B. Discovery & keybindings (interactive)

| #   | Test                  | How                                   | Expected                                                                                                    | Pass |
| --- | --------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ---- |
| B1  | Interaction explorer  | Press `Super+K`                       | DMS spotlight opens showing the Omivoid actions ("explorer" mode)                                           | [x]  |
| B2  | Explorer search       | With B1 open, type `browser`          | The browser action filters in                                                                               | [x]  |
| B3  | Universal palette     | Press `Super+Space`, type `volume`    | Apps **and** Omivoid actions appear together                                                                | [x]  |
| B4  | **Cheat sheet (GKS)** | Press `Super+Shift+S`                 | Read-only tabbed overlay opens (Apps / Navigate / Desktop / Workspaces / System / AI / Projects / Hardware) | [x]  |
| B5  | Cheat-sheet search    | In B4, type `workspace`               | Rows filter live; text is legible (white on dark)                                                           | [x]  |
| B6  | Cheat-sheet tabs      | In B4, click each tab                 | No overlapping labels; `Workspaces` tab populated; `Hardware` shows `F1`–`F7`                               | [x]  |
| B7  | Close cheat sheet     | `Esc` (and click outside)             | Overlay closes                                                                                              | [x]  |
| B8  | AI menu               | Press `Super+A`                       | Spotlight opens in AI mode (Ask AI / Open Pi entries)                                                       | [x]  |
| B9  | App launch            | Press `Super+Enter` / `Super+Shift+B` | Terminal / browser launch                                                                                   | [x]  |
| B10 | Wallpaper carousel    | Press `Super+Ctrl+P`                  | Carousel opens (Enter applies a wallpaper)                                                                  | [x]  |

---

## C. Power-menu restart buttons

Open the DMS power menu (`Super+X`), then exercise each custom button.

| #   | Test                        | Expected                                                                    | Pass |
| --- | --------------------------- | --------------------------------------------------------------------------- | ---- |
| C1  | **Restart Audio** visible   | Button present with a volume icon                                           | [x]  |
| C2  | Restart Audio works         | Audio returns; `systemctl --user is-active pipewire wireplumber` → `active` | [x]  |
| C3  | **Restart Network** visible | Button present with a wifi icon                                             | [x]  |
| C4  | Restart Network works       | Wi-Fi drops and reconnects within a few seconds; no password prompt         | [x]  |
| C5  | **Reload Niri** visible     | Button present with a refresh icon                                          | [x]  |
| C6  | Reload Niri works           | No session interruption; windows stay; config reloads                       | [x]  |
| C7  | Restart DMS (existing)      | The built-in "Restart DMS" button still works                               | [x]  |

> C4 briefly interrupts networking — run it when that is acceptable. Do **not**
> press "Restart Network" while depending on a remote session.

---

## D. Session lifecycle (DoD §26)

| #   | Test                   | Expected                                                      | Pass |
| --- | ---------------------- | ------------------------------------------------------------- | ---- |
| D1  | Log out                | Session returns to the display manager cleanly                | [x]  |
| D2  | Log back in            | Niri session starts; DMS bar appears                          | [x]  |
| D3  | Bindings after login   | `Super+K` and `Super+Shift+S` work                            | [x]  |
| D4  | Re-run §A checks       | All pass after login                                          | [x]  |
| D5  | Reboot                 | System reboots cleanly                                        | [x]  |
| D6  | After reboot           | Niri + DMS start automatically; run §A again                  | [x]  |
| D7  | Bindings after reboot  | `Super+K`, `Super+Space`, `Super+Shift+S`, `Super+A` all work | [x]  |
| D8  | No manual start needed | No undocumented command was required after reboot             | [x]  |

---

## E. Results / failures

Record anything that did not meet `Expected`:

| Test | Expected | Actual | Severity | Notes |
| ---- | -------- | ------ | -------- | ----- |
|      |          |        |          |       |
|      |          |        |          |       |
|      |          |        |          |       |

Regression check (must remain true):

- [x] Existing DMS functionality unaffected (bar, notifications, control centre, lock).
- [x] Native Niri actions unaffected (focus/move/close/workspaces — `Mod+…`).
- [x] No duplicate/omitted keybindings introduced.

---

## F. Sign-off

- [x] All §A checks pass **and** all §B–D tests pass → Phase 1 desktop
  validation complete (DoD §25/§26).
- [x] Recorded in this file and referenced from `PROGRESS.md`.

**Result:** [x] PASS ☐ PASS WITH NOTES ☐ FAIL
**Sign-off:** mk  **Date:** 27-09-2026

---

*File this record under `docs/implementation/`. If any test fails, capture the
exact key/command, the observed behaviour, and `journalctl --user -u dms -n 50`
output before retrying.*
