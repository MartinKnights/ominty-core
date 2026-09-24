# Omivoid LMDE — Platform Abstraction Specification

**Project:** `omivoid-lmde`
**Phase:** Phase 1
**Current platform:** LMDE
**Future target:** Void Linux

---

# 1. Purpose

This document defines how Omivoid separates portable desktop behaviour from distribution-specific implementation.

The purpose of the platform abstraction is to ensure that Omivoid can move from LMDE to Void Linux without redesigning the interaction model.

The core rule is:

> **Omivoid defines intent above the platform boundary. Distribution-specific details remain below it.**

---

# 2. Architectural Position

The platform abstraction sits below the Omivoid Action Registry and above distribution-specific system tools.

```text
Interaction Surfaces
        │
        ▼
Action Registry
        │
        ▼
Action Resolver
        │
        ▼
Platform Abstraction
        │
   ┌────┴────┐
   │         │
 LMDE       Void
```

The same canonical action should normally exist on both platforms.

Example:

```text
network.wifi.toggle
```

should not become:

```text
debian.network.wifi.toggle
```

or:

```text
void.network.wifi.toggle
```

The platform-specific implementation belongs in adapters.

---

# 3. Platform Independence Goal

The following should remain portable wherever practical:

* action IDs;
* keyboard grammar;
* action metadata;
* command palette;
* `Super+K`;
* AI action exposure;
* application roles;
* theme semantics;
* project workflows;
* Niri interaction conventions;
* shell integration contracts.

Platform-specific implementation should be limited to areas such as:

* package management;
* service management;
* system paths;
* distribution packaging;
* boot configuration;
* hardware-specific utilities where unavoidable.

---

# 4. Current LMDE Role

LMDE is the Phase 1 implementation platform.

It serves as:

1. the development environment;
2. the reference implementation;
3. the environment in which the Omivoid architecture is validated.

LMDE-specific conveniences MUST NOT automatically become Omivoid architecture.

For every LMDE-specific implementation, ask:

> Would the action or interface remain meaningful on Void?

If yes, the platform-specific detail belongs below the abstraction boundary.

---

# 5. Future Void Role

The eventual Void implementation should reuse:

* action IDs;
* action registry;
* interaction semantics;
* Niri configuration model;
* application roles;
* DMS integration principles;
* theme specification;
* AI integration interfaces.

Only the platform adapter should change where necessary.

Conceptually:

```text
Omivoid Core
    │
    ├── common
    │
    ├── debian
    │
    └── void
```

---

# 6. Adapter Structure

Recommended structure:

```text
adapters/
├── common/
├── niri/
├── dms/
├── debian/
└── void/
```

The categories have different responsibilities.

## `common/`

Implementation that works across supported distributions.

Examples:

* NetworkManager actions;
* PipeWire actions;
* generic command launch;
* desktop notifications;
* standard Wayland tooling.

## `niri/`

Compositor-specific integration.

Examples:

* focus window;
* move window;
* workspace navigation;
* native binding generation;
* Niri IPC operations.

## `dms/`

DankMaterialShell-specific integration.

Examples:

* opening DMS panels;
* invoking DMS IPC;
* wallpaper functions;
* shell-specific controls.

## `debian/`

Debian-family implementation.

Examples:

* APT package management;
* systemd service handling where needed;
* Debian paths;
* LMDE package naming.

## `void/`

Void-specific implementation.

Examples:

* XBPS;
* runit;
* Void-specific service layout;
* Void package naming.

---

# 7. Adapter Resolution Order

The initial resolution order should be:

```text
machine override
      ↓
platform adapter
      ↓
common adapter
```

Niri and DMS adapters are capability-specific rather than general precedence layers.

An action may explicitly resolve through them.

---

# 8. Common First

When an implementation works identically on LMDE and Void, it belongs in `common`.

Example:

If both systems use NetworkManager, then:

```text
network.wifi.toggle
```

may use:

```text
adapters/common/network/wifi-toggle
```

Do not create separate Debian and Void implementations merely because two distributions exist.

---

# 9. Platform Adapter Only When Required

Create platform-specific adapters only when:

* the command differs;
* service management differs;
* package names differ;
* filesystem layout differs;
* security configuration differs;
* another platform-specific behaviour genuinely exists.

The existence of LMDE and Void alone is not justification for duplication.

---

# 10. Package Management

Package management is explicitly platform-specific.

Conceptually:

```text
package.install
      │
      ├── Debian → apt
      └── Void   → xbps-install
```

Higher layers should not normally invoke:

```text
apt
```

or:

```text
xbps-install
```

directly.

---

# 11. Package Names

Package names may differ between distributions.

Therefore actions should refer to capabilities or logical package identifiers where practical.

Example:

```text
package.install("neovim")
```

may happen to resolve to the same package name on both platforms.

Other tools may require mapping.

A future package map could take the form:

```toml
[package.firefox]
debian = "firefox-esr"
void = "firefox"
```

Only introduce such mapping where needed.

---

# 12. Service Management

LMDE generally uses systemd.

Void uses runit.

Therefore:

```text
service.start
service.stop
service.restart
service.status
```

must not expose systemd assumptions above the platform adapter.

Avoid core scripts containing:

```text
systemctl ...
```

unless they live explicitly inside the Debian adapter.

Likewise avoid exposing:

```text
sv ...
```

outside the Void adapter.

---

# 13. Desktop Services Are Different From Init Services

Do not route every operation through the platform abstraction merely because it invokes a daemon.

Examples such as:

* PipeWire;
* NetworkManager;
* D-Bus;
* portals;
* user-session services;

may use common interfaces.

The platform abstraction should only intervene where the underlying implementation genuinely differs.

---

# 14. Application Launching

Application launch actions should use application roles.

Example:

```text
app.browser.open
```

should resolve:

```text
role = browser
```

The role may be configured in:

```text
config/apps.toml
```

Example:

```toml
[apps]
browser = "firefox"
terminal = "alacritty"
files = "nemo"
editor = "nvim"
notes = "obsidian"
mail = "thunderbird"
```

Application roles are user configuration, not platform adapters.

---

# 15. Platform Detection

The Omivoid runtime should be capable of identifying the active platform.

Phase 1 may use `/etc/os-release`.

Conceptually:

```text
ID=linuxmint
ID_LIKE=debian
```

or equivalent.

The implementation should normalize this into an Omivoid platform identifier such as:

```text
debian
```

Future Void systems resolve to:

```text
void
```

Do not spread raw `/etc/os-release` parsing throughout the codebase.

Use one detection function or module.

---

# 16. Machine Profiles

Some behaviour may depend on specific hardware rather than distribution.

The architecture should leave room for:

```text
config/machines/
```

or:

```text
adapters/machine/
```

A machine profile may define:

* display layout;
* touchscreen behaviour;
* battery tuning;
* Surface Book specifics;
* hardware buttons;
* GPU-specific options.

Machine-specific behaviour should not contaminate common platform code.

---

# 17. Capability Model

Long term, Omivoid should prefer capabilities over package names.

Example:

```text
capability.audio
capability.bluetooth
capability.wallpaper
capability.palette-generation
capability.notifications
```

A provider may satisfy the capability.

For example:

```text
capability.palette-generation
        ↓
      matugen
```

Phase 1 may use direct dependencies where simpler.

The architecture should nevertheless avoid unnecessary provider lock-in.

---

# 18. Dependency Checks

Adapters should be able to report whether their requirements are present.

Examples:

```text
AVAILABLE
MISSING_DEPENDENCY
UNSUPPORTED_PLATFORM
MISCONFIGURED
```

Actions should not fail silently.

---

# 19. Paths

Core Omivoid files should not hard-code machine-specific paths such as:

```text
/home/martin/...
```

Use:

```text
$HOME
XDG_CONFIG_HOME
XDG_CACHE_HOME
XDG_DATA_HOME
```

where practical.

Recommended runtime locations:

```text
~/.config/omivoid/
~/.cache/omivoid/
~/.local/share/omivoid/
```

---

# 20. XDG Compliance

Prefer XDG base directories.

Conceptually:

```text
config:
$XDG_CONFIG_HOME/omivoid

cache:
$XDG_CACHE_HOME/omivoid

data:
$XDG_DATA_HOME/omivoid
```

Fallbacks may use:

```text
~/.config
~/.cache
~/.local/share
```

---

# 21. Generated Files

Generated files should be clearly separated from user-maintained files.

Example:

```text
niri/
├── templates/
└── generated/
```

Generated files should include a warning header where supported:

```text
GENERATED BY OMIVOID
DO NOT EDIT DIRECTLY
```

The source definition should be identified.

---

# 22. Platform Commands Must Be Encapsulated

Incorrect:

```text
actions/network.toml
    ↓
nmcli
```

when a reusable adapter exists.

Preferred:

```text
actions/network.toml
    ↓
network.wifi.toggle
    ↓
adapter
    ↓
nmcli
```

This allows the backend to change independently.

---

# 23. Portable Failure Semantics

Errors should use Omivoid-level codes.

For example:

```text
DEPENDENCY_MISSING
```

rather than exposing different errors from:

```text
apt
xbps
systemctl
sv
```

Raw stderr may still be retained for diagnostics.

---

# 24. Installation Responsibilities

Phase 1 should distinguish between:

```text
environment discovery
dependency validation
configuration
integration
```

and:

```text
operating-system installation
```

Niri and Quickshell are already installed.

The agent MUST NOT treat the project as a system bootstrap script.

Missing supporting dependencies may be identified and installed if appropriate to the implementation plan.

---

# 25. Platform Abstraction Acceptance Criteria

The platform layer is successful when:

* core actions do not contain unnecessary Debian assumptions;
* package management is isolated;
* service management is isolated;
* Niri operations remain compositor-specific rather than distro-specific;
* DMS operations remain shell-specific rather than distro-specific;
* common adapters are reused across platforms where possible;
* machine-specific behaviour can be isolated;
* the future Void port can reuse the majority of the Omivoid codebase.

---

# 26. Architectural Test

For every new implementation ask:

> If this machine changed from LMDE to Void tomorrow, what would have to change?

A good Omivoid implementation should usually answer:

> Only the relevant adapter.
