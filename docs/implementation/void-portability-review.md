# Void Portability Review (DoD §22)

**Date:** 2026-09-19
**Stage:** Phase 1 close-out
**Status:** Complete

DoD §22 requires a written portability review identifying portable
components, Debian-specific components, expected Void replacements, and
unresolved portability questions. LMDE is the Phase 1 validation platform
(ADR-005); Void Linux is the eventual target (docs/05 §5).

---

## 1. Method

Static review of the repository (adapters, CLI, registry, config,
generator) plus the live environment, against docs/05
(Platform Abstraction) §6–22. No code changes were made.

---

## 2. Portable components

These carry to Void unchanged or with re-validation only.

| Component | Path | Notes |
|---|---|---|
| CLI core | `cli/omivoidlib/` | Pure Python stdlib; no `apt`/`dpkg`/`systemctl` |
| Registry + schema | `actions/*.toml`, `registry.py` | Data + validation only |
| Niri fragment generator | `generator.py` | Emits KDL; no platform calls |
| Common adapters | `adapters/common/` | `app.launch`, `command`, `ai.*` |
| Niri adapter | `adapters/niri/native.py` | Compositor-level, not distro-level |
| DMS adapters | `adapters/dms/` | `dms.ipc`, `dms.theme`, `shell.explorer` — DMS runs on Void |
| Config defaults | `config/` | TOML; overridden by `~/.config/omivoid/` |
| XDG paths | `cli/omivoidlib/config.py`, `ai/project` | `XDG_CONFIG_HOME`, `XDG_STATE_HOME` |

**Evidence:**

```text
$ grep -rnE "apt|dpkg|systemctl" cli/omivoidlib adapters/common  → none (portable)
$ grep -rlE "apt|systemctl" adapters/debian                     → service_restart.py, package_install.py (platform-scoped, by design)
$ grep -rhoE "XDG_[A-Z_]+" cli/omivoidlib adapters              → XDG_CONFIG_HOME, XDG_STATE_HOME
$ grep -rhoE '"/[a-zA-Z0-9/_.-]+"' cli/omivoidlib adapters
    "/etc/os-release"                 # standard on all Linux
    "/usr/share/quickshell/dms"       # DMS shell dir, overridable via DMS_SHELL_DIR
```

Dependency checks use `shutil.which` (PATH-based, portable), not
distro-specific package queries (`runner.py:_requirement_available`).

---

## 3. Debian-specific components

| Component | Path | Nature |
|---|---|---|
| Platform detection | `cli/omivoidlib/platform.py` | Maps `ID=linuxmint`/`ID=debian` → `"debian"`, `ID=void` → `"void"` |
| Debian adapters | `adapters/debian/` | `service_restart.py` (systemd), `package_install.py` (apt) |
| Packaging | `adapters/debian/`, `adapters/void/` | `package.install` adapter: apt implemented (Debian), `xbps-install` reference (Void) — docs/05 §10–11, §5.2 |
| Service management | `adapters/debian/`, `adapters/void/` | `service.restart` adapter: systemd implemented (Debian); runit stub (Void) — see §5.2 |

**Key finding:** Phase 1 implements Debian-specific adapters **only at the
platform boundary**: service control (`service.restart`) and package install
(`package.install`) — exactly the two categories docs/05 §3 names as
platform-specific. Everything else is common/Niri/DMS, so the Void port is: new
`adapters/void/` implementations + packaging, not an interaction-model rewrite.

Application role defaults (`config/apps.toml`: alacritty, librewolf, nemo,
nvim, obsidian, thunderbird) are Debian/LMDE-flavoured but are **user
configuration**, overridable via `~/.config/omivoid/apps.toml`; they are not
code assumptions.

---

## 4. Expected Void replacements

| Concern | LMDE / Debian | Void | Where it belongs |
|---|---|---|---|
| Package install | `apt` | `xbps-install` | `adapters/debian/`, `adapters/void/` (future) |
| Service control | `systemctl` | `sv` (runit) | platform adapter (future) |
| Package names | e.g. `firefox-esr` | e.g. `firefox` | package map (docs/05 §11) |
| Clipboard | `wl-clipboard` | `wl-clipboard` | same (Wayland, portable) |
| Compositor | Niri | Niri | same |
| Shell | DMS (Quickshell) | DMS (Quickshell) | same — DMS supports niri |
| AI runtime | ollama / pi | ollama / pi | same |
| Python | `python3` | `python3` | same |

Because Omivoid's core is Python + TOML + KDL with no distro API calls, the
Void port is primarily a **packaging** exercise, not a rewrite.

---

## 5. Unresolved portability questions

1. **Machine/profile layer unimplemented.** `config/machines/` and
   `config/platforms/` are empty. Adapter resolution implements
   platform → common only (`adapters.py`); the documented
   machine → platform → common order (docs/05 §7) is not yet exercised.
2. **No `package.*` action yet; both platform boundaries now exist.**
   `service.restart` and `package.install` adapters define the systemd/runit
   and apt/xbps boundaries: `adapters/debian/{service_restart,package_install}.py`
   (implemented, systemd + apt), `adapters/void/{service_restart,package_install}.py`
   (reference, runit + `xbps-install`; **user-scope service restart returns
   `PLATFORM_UNSUPPORTED`**, and both package adapters require root →
   `PERMISSION_DENIED` otherwise). No Phase 1 action references
   `package.install` — that is docs/05 §10's "future action" boundary.
3. **`adapters/void/` is a reference, not yet exercised.** Service + package
   stubs exist per docs/05 §5/§20; they are unverified on a Void host (Void-phase
   work).
4. **DMS version compatibility on Void.** DMS is packaged for Debian here;
   its availability/version on Void needs validation before relying on the
   `dms.ipc`/`dms.theme` surface (incl. `dms matugen`).
5. **`niri validate`** is used to validate generated fragments; confirm the
   Void Niri package ships the same CLI.
6. **`/usr/share/quickshell/dms`** default shell path — overridable via
   `DMS_SHELL_DIR`, but the correct Void path must be confirmed.
7. **`wl-clipboard` package name** — assumed identical on Void; verify.
8. **XDG Pictures/State** — `ai/project` and `dms.theme` rely on XDG base
   directories; Void honours XDG, but the actual user layout differs.
9. **Application role binaries** — Void users will need to override
   `apps.toml` (alacritty/librewolf/nemo/obsidian/thunderbird may be named
   or packaged differently).
10. **Init/autostart** — Niri session startup and DMS service integration on
    runit are undocumented (Phase 1 uses systemd user services).

---

## 6. Conclusion

The portability posture is **strong**: the portable core is clean (no
distro-specific calls, XDG paths, PATH-based dependency checks), and the
Debian-specific surface is limited to two platform adapters (service +
package). The expected Void work is packaging plus the two `adapters/void/`
reference implementations being exercised and validated on a Void host, and
re-validation of DMS/Niri paths —
not architectural change. The open questions above should be resolved
before the Void phase begins.
