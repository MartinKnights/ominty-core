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

| Check | Command | Expected | Pass |
|---|---|---|---|
| Registry valid | `omivoid registry validate` | `44 action(s), 0 error(s), 0 warning(s)` | [ ] |
| Niri config valid | `niri validate -c ~/.config/niri/config.kdl` | `config is valid` | [ ] |
| DMS running | `systemctl --user is-active dms` | `active` | [ ] |
| Fragment present | `tail -3 ~/.config/niri/config.kdl` | includes `~/.config/omivoid/generated/niri/bindings.kdl` | [ ] |
| omivoid on PATH | `command -v omivoid` | a path (e.g. `~/.local/bin/omivoid`) | [ ] |
| Plugin installed | `ls ~/.config/DankMaterialShell/plugins/omivoidKeybinds ~/.config/DankMaterialShell/plugins/omivoidActions` | both present (symlinks) | [ ] |

---

## B. Discovery & keybindings (interactive)

| # | Test | How | Expected | Pass |
|---|---|---|---|---|
| B1 | Interaction explorer | Press `Super+K` | DMS spotlight opens showing the Omivoid actions ("explorer" mode) | [ ] |
| B2 | Explorer search | With B1 open, type `browser` | The browser action filters in | [ ] |
| B3 | Universal palette | Press `Super+Space`, type `volume` | Apps **and** Omivoid actions appear together | [ ] |
| B4 | **Cheat sheet (GKS)** | Press `Super+Shift+S` | Read-only tabbed overlay opens (Apps / Navigate / Desktop / Workspaces / System / AI / Projects / Hardware) | [ ] |
| B5 | Cheat-sheet search | In B4, type `workspace` | Rows filter live; text is legible (white on dark) | [ ] |
| B6 | Cheat-sheet tabs | In B4, click each tab | No overlapping labels; `Workspaces` tab populated; `Hardware` shows `F1`–`F7` | [ ] |
| B7 | Close cheat sheet | `Esc` (and click outside) | Overlay closes | [ ] |
| B8 | AI menu | Press `Super+A` | Spotlight opens in AI mode (Ask AI / Open Pi entries) | [ ] |
| B9 | App launch | Press `Super+Enter` / `Super+Shift+B` | Terminal / browser launch | [ ] |
| B10 | Wallpaper carousel | Press `Super+Ctrl+P` | Carousel opens (Enter applies a wallpaper) | [ ] |

---

## C. Power-menu restart buttons

Open the DMS power menu (`Super+X`), then exercise each custom button.

| # | Test | Expected | Pass |
|---|---|---|---|
| C1 | **Restart Audio** visible | Button present with a volume icon | [ ] |
| C2 | Restart Audio works | Audio returns; `systemctl --user is-active pipewire wireplumber` → `active` | [ ] |
| C3 | **Restart Network** visible | Button present with a wifi icon | [ ] |
| C4 | Restart Network works | Wi-Fi drops and reconnects within a few seconds; no password prompt | [ ] |
| C5 | **Reload Niri** visible | Button present with a refresh icon | [ ] |
| C6 | Reload Niri works | No session interruption; windows stay; config reloads | [ ] |
| C7 | Restart DMS (existing) | The built-in "Restart DMS" button still works | [ ] |

> C4 briefly interrupts networking — run it when that is acceptable. Do **not**
> press "Restart Network" while depending on a remote session.

---

## D. Session lifecycle (DoD §26)

| # | Test | Expected | Pass |
|---|---|---|---|
| D1 | Log out | Session returns to the display manager cleanly | [ ] |
| D2 | Log back in | Niri session starts; DMS bar appears | [ ] |
| D3 | Bindings after login | `Super+K` and `Super+Shift+S` work | [ ] |
| D4 | Re-run §A checks | All pass after login | [ ] |
| D5 | Reboot | System reboots cleanly | [ ] |
| D6 | After reboot | Niri + DMS start automatically; run §A again | [ ] |
| D7 | Bindings after reboot | `Super+K`, `Super+Space`, `Super+Shift+S`, `Super+A` all work | [ ] |
| D8 | No manual start needed | No undocumented command was required after reboot | [ ] |

---

## E. Results / failures

Record anything that did not meet `Expected`:

| Test | Expected | Actual | Severity | Notes |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |

Regression check (must remain true):

- [ ] Existing DMS functionality unaffected (bar, notifications, control centre, lock).
- [ ] Native Niri actions unaffected (focus/move/close/workspaces — `Mod+…`).
- [ ] No duplicate/omitted keybindings introduced.

---

## F. Sign-off

- [ ] All §A checks pass **and** all §B–D tests pass → Phase 1 desktop
  validation complete (DoD §25/§26).
- [ ] Recorded in this file and referenced from `PROGRESS.md`.

**Result:** ☐ PASS ☐ PASS WITH NOTES ☐ FAIL
**Sign-off:** ___________  **Date:** ___________

---

*File this record under `docs/implementation/`. If any test fails, capture the
exact key/command, the observed behaviour, and `journalctl --user -u dms -n 50`
output before retrying.*
