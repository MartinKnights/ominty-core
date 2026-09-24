# Omivoid LMDE — Theme System Specification

**Project:** `omivoid-lmde`
**Phase:** Phase 1

---

# 1. Purpose

This document defines the Omivoid visual theme architecture.

The design objective is:

> **A wallpaper should be capable of establishing a coherent colour language across the desktop and supported applications.**

The theme system should provide visual consistency without requiring every application to use identical styling.

---

# 2. Core Theme Flow

The intended model is:

```text
Wallpaper
    ↓
Palette Generator
    ↓
Canonical Omivoid Palette
    ↓
Theme Adapters
    ↓
Desktop + Applications
```

The canonical palette is the important architectural concept.

Individual applications should not independently derive unrelated colour sets from the wallpaper where avoidable.

---

# 3. DMS Role

DMS is expected to provide much of the wallpaper and dynamic theme experience.

It may:

* select wallpaper;
* apply wallpaper;
* invoke Matugen;
* style shell components;
* influence GTK/Qt configuration.

Omivoid should reuse this functionality where appropriate.

However:

> DMS should not be the only owner of theme state.

Omivoid needs a clear theme contract that other applications can consume.

---

# 4. Matugen Role

Matugen is the preferred initial palette-generation candidate.

Conceptually:

```text
wallpaper.jpg
      ↓
Matugen
      ↓
colour palette
```

Phase 1 should evaluate DMS's existing Matugen workflow before implementing any parallel process.

---

# 5. Canonical Palette

Omivoid should aim to define a canonical set of colours.

Example conceptual palette:

```toml
[palette]
background = ""
surface = ""
surface_alt = ""
foreground = ""
muted = ""

primary = ""
primary_foreground = ""

secondary = ""
secondary_foreground = ""

accent = ""
accent_foreground = ""

success = ""
warning = ""
error = ""

border = ""
```

The exact field set should be derived from practical application needs.

Avoid creating a huge theoretical colour schema before real adapters require it.

---

# 6. Light and Dark Modes

The palette should support at least:

```text
light
dark
```

Potentially:

```text
auto
```

later.

Canonical action:

```text
theme.mode.toggle
```

may switch between supported modes.

---

# 7. Wallpaper Actions

Initial actions:

```text
theme.wallpaper.select
theme.wallpaper.next
theme.palette.regenerate
theme.mode.toggle
```

Potential later actions:

```text
theme.wallpaper.previous
theme.wallpaper.random
theme.apply
theme.reload
theme.current.get
```

Only implement what Phase 1 actually requires.

---

# 8. Wallpaper Selection Flow

Preferred conceptual behaviour:

```text
User selects wallpaper
       ↓
Wallpaper provider applies image
       ↓
Palette generated
       ↓
Canonical Omivoid palette updated
       ↓
Theme adapters run
       ↓
Applications reload where required
```

The sequence should be deterministic.

---

# 9. Theme Consumers

Potential consumers include:

* DMS;
* GTK;
* Qt;
* terminal;
* Neovim;
* btop;
* Obsidian;
* VSCode/VSCodium;
* browser chrome where practical;
* other supported tools.

Not every application must be supported during Phase 1.

---

# 10. Adapter Categories

Theme consumers fall into three broad categories.

## Native dynamic consumers

Applications or toolkits that already consume dynamic system colours.

Examples may include:

* DMS;
* GTK;
* Qt.

## Template-driven consumers

Applications whose config can be generated from palette values.

Examples:

* Alacritty;
* btop;
* Neovim.

## Application-specific adapters

Applications requiring a bespoke integration mechanism.

Examples may include:

* Obsidian;
* browsers;
* IDEs.

---

# 11. Do Not Force Unsupported Applications

If an application cannot be themed reliably, Omivoid should not introduce fragile hacks merely to claim full theme coverage.

Theme support should be classified as:

```text
native
generated
adapter
unsupported
```

---

# 12. Theme Template Structure

Recommended future layout:

```text
themes/
├── palette.toml
├── templates/
│   ├── alacritty.toml
│   ├── btop.theme
│   ├── neovim.lua
│   ├── gtk.css
│   ├── qt.conf
│   └── obsidian.css
└── adapters/
```

The exact file names may evolve during implementation.

---

# 13. Template Variables

Theme templates should consume canonical values.

Conceptually:

```text
{{ background }}
{{ foreground }}
{{ primary }}
{{ accent }}
{{ border }}
```

Do not allow each template to invent its own independent interpretation of the wallpaper.

---

# 14. Source of Truth

The source of truth should ultimately be:

```text
current wallpaper
       +
current mode
       ↓
current Omivoid palette
```

Generated application configs are outputs.

They are not authoritative theme state.

---

# 15. Theme State Location

A future runtime representation may exist under:

```text
~/.cache/omivoid/
```

or:

```text
~/.local/share/omivoid/
```

For example:

```text
current-theme.json
```

Phase 1 should prefer simple plain-text state.

---

# 16. Existing Application Configuration

Theme integration must preserve user configuration.

Incorrect approach:

```text
replace entire alacritty.toml
```

Preferred:

* generated include;
* imported theme fragment;
* dedicated theme file;
* minimal managed section.

The implementation should use each application's supported include/import mechanism where available.

---

# 17. Generated Files

Generated theme fragments should be clearly marked.

Example:

```text
# Generated by Omivoid
# Source: current palette
# Do not edit directly
```

Do not overwrite hand-maintained configuration unnecessarily.

---

# 18. Terminal Theme

The terminal is a high-priority theme target because it is central to the intended Omivoid workflow.

The preferred terminal should consume generated Omivoid colours where practical.

Application role configuration determines which terminal is active.

---

# 19. Neovim Theme

Neovim should be considered a high-value theme consumer.

Possible strategies:

* generated Lua palette;
* compatible colour scheme parameters;
* theme variant selection.

Do not tightly couple Omivoid to one Neovim distribution.

---

# 20. GTK and Qt

GTK and Qt should visually align with the Omivoid palette as far as practical.

The implementation should prefer existing DMS/Matugen support before adding custom generation.

---

# 21. Shell Theme

DMS should remain visually synchronized with the canonical theme.

If DMS generates the initial palette, Omivoid should either:

* consume that palette;
* export equivalent canonical state;
* or derive from the same source in a deterministic way.

Avoid two independent colour-generation engines.

---

# 22. Wallpaper Directory

Wallpaper storage should be configurable.

Do not hard-code a personal path.

Example configuration:

```toml
[theme]
wallpaper_dir = "~/Pictures/Wallpapers"
```

Expansion should be handled correctly.

---

# 23. Theme Change Feedback

A successful theme change should provide lightweight feedback where useful.

Example:

```text
Theme applied
```

Avoid excessive notifications for automated palette refreshes.

---

# 24. Failure Handling

If one theme adapter fails:

* the wallpaper should not necessarily be reverted;
* successful adapters should remain applied;
* the failure should be reported;
* the failed consumer should be identifiable.

Example:

```text
Theme applied with warnings:
Obsidian adapter failed.
```

---

# 25. Atomicity

Where practical, generate theme files before replacing active files.

Avoid leaving partially written configuration.

A preferred sequence is:

```text
generate temporary file
validate
replace target
reload application
```

---

# 26. Application Reloading

Some applications can reload theme state live.

Others may require restart.

Adapters should document whether they:

```text
reload automatically
require manual reload
require restart
```

Do not force-kill user applications merely to update colours.

---

# 27. Theme Regeneration

Canonical action:

```text
theme.palette.regenerate
```

should regenerate application colours from the current source without requiring a wallpaper change.

This is useful after:

* installing a new adapter;
* editing templates;
* recovering from a failed update.

---

# 28. User Overrides

Users should be able to override generated colours or disable adapters.

Example concept:

```toml
[theme.adapters]
obsidian = false
browser = false
```

Potential custom values:

```toml
[theme.override]
accent = "#..."
```

Advanced override behaviour may be deferred beyond Phase 1.

---

# 29. Theme Profiles

A future system may support named theme profiles.

Example:

```text
dynamic
high-contrast
presentation
writing
night
```

This is not required for Phase 1.

The initial focus is wallpaper-derived dynamic theming.

---

# 30. Accessibility

Visual coherence must not override readability.

Generated themes should maintain sufficient contrast.

If the palette generator produces unsuitable combinations, Omivoid should prefer readability over strict wallpaper colour matching.

---

# 31. Phase 1 Priorities

Implement in this order:

1. confirm DMS wallpaper workflow;
2. confirm Matugen integration;
3. identify generated colour outputs;
4. define the minimal canonical palette;
5. integrate shell;
6. integrate GTK/Qt where already supported;
7. integrate terminal;
8. integrate one additional application as proof of template/adaptor architecture.

Do not attempt to theme every installed application initially.

---

# 32. Phase 1 Acceptance Criteria

The theme system is successful when:

* selecting a wallpaper changes the desktop colour language;
* DMS and core desktop surfaces remain coherent;
* a canonical palette can be identified or generated;
* at least one non-shell application consumes the same palette;
* hand-maintained configs are preserved;
* regeneration is possible;
* failed adapters produce understandable diagnostics;
* the architecture is not tied irreversibly to DMS or Matugen.

The objective is:

> **one visual source, many controlled consumers.**
