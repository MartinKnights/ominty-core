# Omivoid LMDE — Configuration Layout Specification

**Project:** `omivoid-lmde`
**Phase:** Phase 1

---

# 1. Purpose

This document defines where Omivoid configuration, generated state, runtime state and user overrides should live.

The goals are:

* clear ownership;
* safe upgrades;
* easy debugging;
* portability;
* minimal modification of third-party configuration.

---

# 2. Configuration Principles

Omivoid configuration should distinguish between:

```text
project defaults
user configuration
machine configuration
generated configuration
runtime cache
third-party configuration
```

These must not be mixed unnecessarily.

---

# 3. Repository Layout

Recommended Phase 1 layout:

```text
omivoid-lmde/
├── actions/
│
├── adapters/
│   ├── common/
│   ├── niri/
│   ├── dms/
│   └── debian/
│
├── ai/
│
├── cli/
│
├── config/
│   ├── defaults.toml
│   ├── apps.toml
│   ├── platforms/
│   └── machines/
│
├── niri/
│   ├── templates/
│   └── generated/
│
├── shell/
│
├── themes/
│   ├── templates/
│   └── adapters/
│
├── tests/
│
└── docs/
```

Only directories actually required should be populated.

---

# 4. Installed User Configuration

Runtime user configuration should live under:

```text
$XDG_CONFIG_HOME/omivoid/
```

with fallback:

```text
~/.config/omivoid/
```

Recommended layout:

```text
~/.config/omivoid/
├── config.toml
├── apps.toml
├── actions/
├── overrides/
├── themes/
├── machines/
└── local/
```

---

# 5. Core Defaults

Project defaults belong in the repository.

Example:

```text
config/defaults.toml
```

These should define sensible behaviour without containing machine-specific information.

---

# 6. Application Roles

Portable defaults may exist in:

```text
config/apps.toml
```

but user-selected application roles should ultimately be overridable through:

```text
~/.config/omivoid/apps.toml
```

---

# 7. Configuration Precedence

Recommended precedence:

```text
core defaults
      ↓
platform defaults
      ↓
machine profile
      ↓
user configuration
      ↓
user overrides
      ↓
local overrides
```

Later layers override earlier layers.

---

# 8. Platform Configuration

Platform-specific defaults should live under:

```text
config/platforms/
```

Example:

```text
config/platforms/debian.toml
```

Future:

```text
config/platforms/void.toml
```

Keep platform configuration minimal.

**Phase 1 status (2026-09-24):** `config/platforms/` is empty; adapter
resolution implements **platform → common** only (`cli/omivoidlib/adapters.py`).
No platform-specific adapter is implemented (`adapters/debian/` is empty).

---

# 9. Machine Profiles

Hardware-specific settings should live under:

```text
config/machines/
```

Examples might include:

```text
surface-book-gen1.toml
desktop-main.toml
```

Machine profiles may include:

* display layout references;
* input adjustments;
* hardware capability flags;
* battery behaviour.

Do not place personal data in reusable machine profiles.

**Phase 1 status (2026-09-24):** the machine layer is **not implemented** —
`config/machines/` is empty and adapter resolution does not consult it. Recorded
as an unnecessary/deferred abstraction in `phase-1-exit-review.md` §3.

---

# 10. Action Sources

Canonical project actions:

```text
actions/*.toml
```

User actions:

```text
~/.config/omivoid/actions/
```

Official and user action identity must remain distinguishable.

---

# 11. User Overrides

User overrides should live separately from full action definitions.

Recommended:

```text
~/.config/omivoid/overrides/
```

Example:

```toml
[override."app.browser.open"]
keys = ["Super+B"]
```

This avoids copying core actions.

---

# 12. Local Overrides

Machine-local or experimental settings that should not normally be shared may live under:

```text
~/.config/omivoid/local/
```

This is useful for:

* temporary testing;
* local executable paths;
* machine-specific experiments.

---

# 13. Generated Runtime Registry

Compiled runtime registry may live under:

```text
$XDG_CACHE_HOME/omivoid/
```

fallback:

```text
~/.cache/omivoid/
```

Example:

```text
registry.json
```

Generated registry is disposable.

---

# 14. Runtime State

Persistent non-configuration state may live under:

```text
$XDG_DATA_HOME/omivoid/
```

fallback:

```text
~/.local/share/omivoid/
```

Examples:

* current theme metadata;
* usage history if added;
* project state if needed later.

Do not use config directories for transient state.

---

# 15. Cache

Use cache for data that can be rebuilt.

Examples:

```text
registry.json
search-index.json
generated-preview
temporary theme output
```

Deleting cache should not destroy user preferences.

---

# 16. Niri Configuration

User's active Niri configuration remains owned by the user/Niri.

Omivoid-generated fragments should ideally live in an Omivoid-controlled location.

Example:

```text
~/.config/omivoid/generated/niri/
```

or project/install equivalent.

The active Niri config may include/import these where supported.

---

# 17. Generated Niri File

Example:

```text
~/.config/omivoid/generated/niri/bindings.kdl
```

The file should contain a generated header.

Example:

```text
// Generated by Omivoid.
// Source: Action Registry.
// Do not edit directly.
```

**Phase 1 implementation (2026-09-24):** `omivoid registry build` writes this
file, validating it with `niri validate` first (invalid output is removed). The
active config includes it **last** in `~/.config/niri/config.kdl`:

```text
include optional=true "~/.config/omivoid/generated/niri/bindings.kdl"
```

`optional=true` means a missing fragment degrades to a warning, never a config
failure. See `docs/implementation/rollback-test.md`.

---

# 18. Existing Niri Config

Do not convert all existing Niri configuration into Omivoid-managed files.

Only configuration deliberately owned by Omivoid should move under Omivoid control.

---

# 19. Quickshell Configuration

Existing Quickshell configuration must be inspected.

Custom Omivoid shell components should be isolated rather than mixed unpredictably into unrelated user components.

Exact location may depend on Quickshell conventions.

---

# 20. DMS Configuration

DMS remains responsible for its own native configuration.

Omivoid should maintain only:

* adapter data;
* required integration;
* documented managed settings.

Do not duplicate the whole DMS configuration tree inside Omivoid.

**Phase 1 implementation (2026-09-24):** DMS config lives at
`~/.config/DankMaterialShell/`; Omivoid plugins are symlinked into
`.../plugins/` (the repo remains the source of truth). Documented managed
settings include `customPowerButtons` (the audio / network / niri restart
buttons).

---

# 21. Theme Files

Recommended source structure:

```text
themes/
├── templates/
└── adapters/
```

Generated theme files should be stored separately from templates.

Possible runtime location:

```text
~/.cache/omivoid/theme/
```

before being installed/imported by consuming applications.

---

# 22. Application Theme Fragments

Where supported, create dedicated files.

Example:

```text
~/.config/alacritty/omivoid-theme.toml
```

and import that from the main configuration.

Prefer this to rewriting:

```text
~/.config/alacritty/alacritty.toml
```

on every theme change.

---

# 23. Backups

Backups should not be scattered randomly throughout config directories.

Recommended location:

```text
~/.local/share/omivoid/backups/
```

Example:

```text
niri/
dms/
quickshell/
```

Backups should record when and why they were created.

---

# 24. Backup Scope

Back up only files Omivoid will modify.

Do not recursively duplicate all user configuration.

---

# 25. Documentation Generated During Implementation

Implementation findings belong under:

```text
docs/implementation/
```

Suggested files:

```text
environment-audit.md
niri-binding-audit.md
dms-evaluation.md
void-portability-review.md
```

These are technical records, not canonical architecture.

---

# 26. Secrets

Secrets MUST NOT be stored in:

* action registry;
* repository config;
* committed machine profiles;
* generated documentation.

Future provider tokens should use appropriate secret/environment mechanisms.

---

# 27. Environment Variables

Environment variables may be used for:

* secrets;
* temporary overrides;
* integration paths where appropriate.

Do not turn every user preference into an environment variable.

Configuration files remain the primary interface.

---

# 28. Path Expansion

Configuration should correctly support paths such as:

```text
~/Pictures/Wallpapers
```

and XDG paths.

Do not rely on the shell to expand paths when the application parses TOML directly.

---

# 29. Symlinks

Symlinks may be used during development, but the project should not depend on undocumented manual symlinks.

If symlinks are required, creation must be reproducible and documented.

---

# 30. Repository vs Installed State

Keep a clear distinction:

```text
repository
    = source

~/.config/omivoid
    = user configuration

~/.cache/omivoid
    = generated cache

~/.local/share/omivoid
    = persistent state/backups
```

---

# 31. Public Repository Requirement

The repository must not contain:

* private credentials;
* personal absolute paths;
* machine-specific secrets;
* unnecessary user data;
* generated runtime cache.

Use `.gitignore` appropriately.

---

# 32. Suggested `.gitignore`

At minimum consider excluding:

```text
.cache/
generated-local/
*.tmp
*.bak
.env
.env.*
```

Exact patterns should reflect the implementation.

Do not ignore source-generated files that are intentionally version-controlled.

---

# 33. Generated vs Versioned Niri Files

If Niri generated files are reproducible from registry source, prefer not to make hand-edited changes to them.

Whether they are committed to Git should be decided based on:

* usefulness for review;
* reproducibility;
* development workflow.

Whichever policy is chosen must remain consistent.

---

# 34. Configuration Inspection

The CLI should eventually make configuration easy to inspect.

Potential future commands:

```text
omivoid config show
omivoid config paths
omivoid config validate
```

Not required for initial Phase 1.

---

# 35. Phase 1 Acceptance Criteria

Configuration layout is successful when:

* project source and user config are distinct;
* generated state is clearly identifiable;
* user settings survive project updates;
* existing Niri/Quickshell/DMS config is preserved;
* no personal paths leak into portable core;
* XDG locations are used appropriately;
* backups are organised;
* the future Void implementation can reuse the same structure.
