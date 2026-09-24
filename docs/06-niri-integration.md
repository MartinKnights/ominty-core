# Omivoid LMDE — Niri Integration Specification

**Project:** `omivoid-lmde`
**Phase:** Phase 1
**Compositor:** Niri
**Current status:** Already installed

---

# 1. Purpose

This document defines how Omivoid integrates with Niri.

Niri is the compositor and remains authoritative for compositor behaviour.

Omivoid provides:

* canonical action naming;
* binding metadata;
* discoverability;
* generated configuration where useful;
* integration with other interaction surfaces.

Omivoid MUST NOT unnecessarily reimplement Niri functionality.

---

# 2. Existing Installation

Niri is already installed on the Phase 1 LMDE system.

The implementation agent MUST begin by inspecting:

* Niri version;
* active configuration location;
* active keybindings;
* input settings;
* output settings;
* startup commands;
* window rules;
* existing include structure if any.

The current configuration should be backed up before modification.

---

# 3. Preservation Rule

The existing Niri configuration is not disposable.

The agent MUST NOT replace the entire configuration with an Omivoid-generated file unless explicitly authorised.

Preferred approach:

```text
existing config
      +
Omivoid generated include
```

or another modular mechanism supported by the installed Niri version.

---

# 4. Niri Responsibility

Niri owns:

* window placement;
* scrolling layout;
* focus;
* window movement;
* workspace movement;
* workspace switching;
* fullscreen;
* floating state;
* output configuration;
* input configuration;
* window rules;
* compositor-level shortcuts;
* compositor lifecycle.

Omivoid should describe these behaviours through canonical actions but not duplicate their implementation.

---

# 5. Native First

For latency-sensitive compositor actions, use native Niri bindings.

Example:

```text
window.close
```

should compile directly to Niri's native close-window behaviour.

Avoid:

```text
key
  ↓
spawn omivoid
  ↓
Niri IPC
  ↓
close window
```

where Niri can perform the operation directly.

---

# 6. Action Registry Relationship

The Action Registry remains authoritative for:

* action ID;
* human-readable name;
* description;
* category;
* keybinding metadata;
* discovery;
* AI exposure;
* risk.

Niri remains authoritative for:

* compositor execution.

Conceptually:

```text
Action Registry
      │
      ▼
Niri binding generator
      │
      ▼
Niri native configuration
```

---

# 7. Native Backend Metadata

Niri-native actions should be identifiable as such.

Conceptually:

```toml
[action."window.close"]
backend = "native-niri"
```

or via adapter metadata such as:

```toml
adapter = "niri.window.close"
```

The final syntax may be determined during implementation.

The important point is that the registry can distinguish native Niri actions from actions requiring the Omivoid runner.

---

# 8. Initial Native Actions

Phase 1 should prioritise native Niri implementation for:

```text
window.close
window.fullscreen.toggle

window.focus.left
window.focus.right
window.focus.up
window.focus.down

window.move.left
window.move.right

workspace.next
workspace.previous
workspace.switch
workspace.window.move
```

Additional native actions may be added once the initial interaction grammar is validated.

---

# 9. Respect Niri's Scrolling Model

Omivoid MUST NOT attempt to force Niri into a Hyprland-style tiling model.

The design should embrace:

* scrolling columns;
* Niri-native focus movement;
* Niri-native workspace concepts;
* Niri-native window movement.

Omivoid borrows useful workflow ideas from Omarchy, not Hyprland mechanics.

---

# 10. Focus Navigation

The initial conceptual mapping is:

```text
Super+Left   → window.focus.left
Super+Right  → window.focus.right
Super+Up     → window.focus.up
Super+Down   → window.focus.down
```

Before applying these mappings, the agent must inspect existing configuration for conflicts.

---

# 11. Workspace Navigation

The Action Registry defines:

```text
workspace.next
workspace.previous
workspace.switch
workspace.window.move
```

Niri determines the actual semantics.

The implementation should not assume fixed workspace behaviour that contradicts Niri's model.

---

# 12. Numeric Workspace Bindings

The proposed Omivoid interaction model includes:

```text
Super+1..9
```

for workspace switching and:

```text
Super+Shift+1..9
```

for moving windows.

These are proposed defaults.

Their suitability must be tested against Niri's workspace model and existing configuration before adoption.

If numeric workspaces are awkward or misleading in Niri, the agent should document the issue rather than force the abstraction.

---

# 13. Generated Bindings

The desired long-term flow is:

```text
Action Registry
      ↓
binding validation
      ↓
Niri generator
      ↓
generated Omivoid binding fragment
```

The generated fragment should contain only bindings owned by Omivoid.

---

# 14. Do Not Generate Unrelated Niri Configuration

The Omivoid generator should not rewrite:

* outputs;
* input;
* window rules;
* layout tuning;
* startup;
* decorations;

unless those sections are explicitly managed by Omivoid.

The binding generator should initially concern itself only with relevant interaction configuration.

---

# 15. Binding Conflict Audit

Before generating Omivoid bindings, the implementation should build a conflict report.

Example:

```text
Super+Q
Existing: close-window
Omivoid:  window.close
Status: compatible
```

or:

```text
Super+K
Existing: spawn application
Omivoid:  help.keys.open
Status: conflict
```

The agent should not silently overwrite a conflicting behaviour.

---

# 16. Compatible Existing Bindings

If an existing binding already provides the exact intended behaviour:

```text
Super+Q → close-window
```

and Omivoid defines:

```text
Super+Q → window.close
```

the implementation may preserve the existing native binding and simply register/document it as satisfying the Omivoid action.

It does not need to rewrite working configuration merely for ownership purity.

---

# 17. Binding Generation Is Not Binding Ownership

An action may be defined by Omivoid while the actual Niri configuration remains manually maintained.

Phase 1 should prioritise correctness and safety over full automation.

Generation can become more comprehensive after the model is proven.

---

# 18. Non-Native Actions

Actions such as:

```text
app.browser.open
theme.wallpaper.select
ai.open
help.keys.open
```

may require Niri to spawn the Omivoid action runner or another defined command.

Example concept:

```kdl
Mod+Shift+B {
    spawn "omivoid" "action" "run" "app.browser.open"
}
```

These actions should be routed through the appropriate Omivoid layer.

---

# 19. Startup Integration

If Omivoid components need to start with the Niri session, startup configuration should be minimal and documented.

Potential examples:

* DMS;
* Omivoid helper;
* generated shell component.

Do not add persistent background components unless required.

---

# 20. IPC

Niri IPC may be used when:

* an action is invoked outside a native keybinding;
* DMS needs compositor state;
* the command palette invokes a Niri operation;
* AI invokes an authorised window action.

Example:

```text
AI
 ↓
window.focus.left
 ↓
Niri adapter
 ↓
Niri IPC
```

The same canonical action can therefore have two execution paths:

```text
keyboard → native Niri

AI/CLI → Niri IPC
```

This is acceptable.

---

# 21. State Queries

Useful future queries include:

```text
window.active.get
workspace.current.get
```

These may be implemented through Niri IPC.

They should generally be:

```text
risk = read
```

and may remain hidden from normal command-palette display.

---

# 22. Window Rules

Window rules are outside the initial Action Registry implementation.

They remain part of Niri configuration.

However, Omivoid may eventually maintain documented rules for:

* floating utility windows;
* AI palettes;
* command palettes;
* picture-in-picture;
* shell overlays.

Do not prematurely move all window rules into Omivoid.

---

# 23. Output Configuration

Monitor/output configuration is hardware-sensitive.

It should remain in:

```text
Niri configuration
```

or a future machine profile.

It should not be generated from generic Omivoid action definitions.

---

# 24. Input Configuration

Keyboard, mouse and touchpad tuning belong primarily to Niri and machine/user configuration.

Omivoid may document recommended settings but should not overwrite existing preferences without need.

---

# 25. Quickshell Relationship

Niri and Quickshell have different responsibilities.

Niri provides compositor behaviour.

Quickshell/DMS may render:

* bar;
* overlays;
* palettes;
* help;
* system UI.

Omivoid should not ask Quickshell to emulate native compositor functions that Niri already provides well.

---

# 26. DMS Relationship

If DMS integrates directly with Niri, preserve that integration where useful.

Omivoid should not insert itself into every Niri↔DMS interaction merely for architectural ownership.

The Action Registry should govern Omivoid actions, not become a mandatory proxy for all desktop communications.

---

# 27. Performance Requirement

Navigation must remain immediate.

Actions such as:

```text
focus
move
close
workspace
```

must not incur visible latency from:

* scripting runtimes;
* registry loading;
* unnecessary process launches.

Native bindings are preferred for this reason.

---

# 28. Failure Behaviour

If generated Niri configuration is invalid:

* the original working configuration must remain recoverable;
* the generated fragment should fail validation before activation where possible;
* rollback should be straightforward.

The agent should never leave the user without a usable compositor session because of an automated config rewrite.

---

# 29. Backup Policy

Before the first Omivoid modification, create a timestamped or otherwise clearly named backup of the active Niri configuration.

Do not create repeated uncontrolled backup files on every run.

Backups should be deterministic and documented.

---

# 30. Phase 1 Acceptance Criteria

Niri integration is successful when:

* existing Niri remains functional;
* Omivoid bindings do not unexpectedly destroy existing behaviour;
* native Niri actions remain native;
* registry actions map correctly to compositor functions;
* `Super+K` can describe Niri bindings;
* command-palette invocation can reach appropriate Niri actions where useful;
* future Void migration requires no interaction-model redesign.

The objective is integration, not takeover.
