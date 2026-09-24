# Omivoid LMDE — Design Principles

## 1. Purpose

This document defines the architectural and UX principles that govern Omivoid.

These principles take precedence over implementation convenience.

When choosing between two implementations, prefer the solution that better preserves these principles unless there is a documented technical reason not to do so.

---

# 2. Keyboard First

Omivoid is a keyboard-first desktop.

A frequent operation should normally be possible without requiring pointer interaction.

Examples include:

* launching applications;
* changing windows;
* changing workspaces;
* opening system controls;
* selecting actions;
* invoking AI;
* selecting wallpaper;
* capturing screenshots;
* opening projects.

This does not prohibit graphical interfaces.

The preferred model is:

```text
Keyboard first
      ↓
GUI discoverable
      ↓
CLI accessible
      ↓
AI callable
```

Keyboard operation should be the fastest path, not the only path.

---

# 3. Discoverability Is Part of the Interface

Keyboard-driven systems often become difficult to use because their functionality exists only in the user's memory.

Omivoid must avoid this.

A shortcut that cannot reasonably be discovered is incomplete.

`Super+K` is therefore a core part of the interaction architecture rather than merely documentation.

It should allow users to discover:

* actions;
* bindings;
* categories;
* chord namespaces;
* descriptions.

Chorded interaction should also reveal available continuation keys where practical.

The desired progression is:

```text
discover
   ↓
use
   ↓
remember
   ↓
operate without UI assistance
```

The system should help users become faster naturally.

---

# 4. Predictability Over Memorisation

Bindings should follow a grammar.

Users should increasingly be able to infer how to perform an operation rather than memorising unrelated key combinations.

Examples of namespaces include:

```text
Super            Desktop/navigation
Super+Shift      Applications
Super+Ctrl       System operations
Super+A          AI
Super+K          Help/discovery
Super+P          Projects
Super+Space      Universal command palette
```

Individual exceptions are permitted when ergonomically justified, but arbitrary bindings should not accumulate.

---

# 5. Actions Before Bindings

An operation is first defined as an Omivoid action.

Only then is a keyboard binding assigned.

For example:

```text
app.browser.open
```

exists independently of:

```text
Super+Shift+B
```

This distinction allows the same action to be invoked from:

* keyboard;
* GUI;
* CLI;
* AI;
* voice;
* automation.

Bindings are interaction metadata.

They are not the implementation.

---

# 6. Intent Must Be Separate From Implementation

The fundamental architectural rule is:

> **The Action Registry defines what an action means; adapters define how it is performed.**

For example:

```text
network.wifi.toggle
```

describes intent.

It does not specify:

```text
nmcli radio wifi ...
```

The underlying implementation may change between:

* machines;
* LMDE;
* Void;
* desktop components.

The action should remain stable.

---

# 7. One Source of Truth

Information should not be independently maintained in multiple places where it can be generated from a canonical source.

In particular, the Action Registry should eventually provide source data for:

* keybindings;
* `Super+K`;
* command palette;
* CLI mappings;
* AI capabilities;
* documentation metadata.

Avoid maintaining:

```text
Niri shortcuts
+
separate shortcut documentation
+
separate AI commands
+
separate palette definitions
```

when all represent the same action.

---

# 8. Preserve Native Strengths

Omivoid uses Niri because Niri provides useful interaction characteristics of its own.

Do not force Niri to reproduce another compositor's internal behaviour.

In particular, Omivoid should embrace Niri's scrolling layout rather than attempt to make it behave exactly like Hyprland.

The design goal is:

> reproduce useful workflow principles, not implementation quirks.

---

# 9. Integrate Before Reimplementing

Before writing an Omivoid component, determine whether an existing component already provides the required functionality adequately.

This is especially important for DankMaterialShell.

If DMS provides a high-quality implementation of:

* bar;
* notifications;
* OSD;
* system tray;
* audio controls;
* network controls;
* wallpaper selector;
* theme integration;

Omivoid should normally integrate with it.

A custom implementation requires a concrete reason.

---

# 10. DMS Is Not Omivoid

DMS may become an important shell component, but the architecture must distinguish:

```text
Omivoid
    │
    └── uses DMS
```

from:

```text
Omivoid = DMS configuration
```

The first is intended.

The second is not.

Canonical actions, interaction conventions and platform abstraction belong to Omivoid.

---

# 11. Portable Above the Adapter Boundary

Core Omivoid behaviour should not need to know whether it is running on LMDE or Void.

Prefer:

```text
session.shutdown
```

over platform-specific commands.

Prefer:

```text
app.browser.open
```

over:

```text
firefox
```

Prefer:

```text
package.install
```

over embedding:

```text
apt
```

or:

```text
xbps-install
```

in high-level interfaces.

Platform-specific implementation belongs in adapters.

---

# 12. Application Roles Over Application Names

User intent is generally to open a type of application.

Therefore:

```text
app.browser.open
```

should resolve a configured browser role.

Example configuration:

```toml
[apps]
browser = "firefox"
terminal = "alacritty"
files = "nemo"
editor = "nvim"
notes = "obsidian"
mail = "thunderbird"
```

Changing the preferred browser should not require changing:

* keybindings;
* AI tools;
* help documentation;
* workflow definitions.

---

# 13. AI Is a First-Class Interaction Surface

AI must not be treated merely as another application icon.

Omivoid should provide a coherent AI namespace.

The initial convention is:

```text
Super+A
```

AI operations may include:

* ask;
* explain;
* summarise;
* research;
* write;
* code;
* interact with Pi;
* interact with Herdr;
* eventually delegate work.

AI should participate in the same Action Registry used by human interaction.

---

# 14. Prefer Capabilities to Unrestricted Shell Access

Where practical, AI should invoke:

```text
theme.wallpaper.select
```

rather than constructing shell commands to manipulate the theme.

Likewise:

```text
network.bluetooth.toggle
```

is preferable to giving an agent detailed knowledge of the current Bluetooth implementation.

This provides:

* portability;
* validation;
* auditability;
* permissions;
* predictable error handling;
* reduced implementation coupling.

Shell access may still exist for development and advanced tasks.

The Action Registry is not intended to make Linux inaccessible.

It is intended to provide a safer, stable capability interface.

---

# 15. AI Actions Must Be Governable

Every AI-callable action should eventually expose sufficient metadata to determine:

* whether AI may invoke it;
* its risk;
* whether confirmation is required;
* its valid context.

An AI agent should not automatically gain authority merely because an action exists.

---

# 16. Context Should Improve Interaction

Omivoid should become context-aware where this provides genuine value.

For example, when text is selected, relevant actions might include:

```text
Explain Selection
Summarise Selection
Rewrite Selection
Research Selection
```

A file context might expose:

```text
Open
Summarise
Compare
Add to Project
```

Do not display context actions when their required context is unavailable.

---

# 17. Visual Coherence

The desktop should feel like one environment.

Wallpaper-derived colours should be capable of influencing:

* shell;
* GTK;
* Qt;
* terminal;
* editor;
* supported applications.

The objective is not to force every application into identical styling.

The objective is coherent colour language.

---

# 18. One Palette, Multiple Adapters

Where possible:

```text
Wallpaper
    ↓
Palette generation
    ↓
Canonical Omivoid palette
    ↓
Application adapters
```

is preferable to each application independently deriving colours from the wallpaper.

This creates a single visual source of truth.

---

# 19. User Configuration Must Survive Updates

Users should not have to edit core project files for ordinary customisation.

Prefer:

```text
core defaults
      ↓
platform defaults
      ↓
machine profile
      ↓
user overrides
      ↓
local overrides
```

A project update should not erase user preferences.

---

# 20. Existing Configuration Must Be Respected

The Phase 1 LMDE machine already has Niri and Quickshell installed.

Implementation must therefore begin with inspection, not replacement.

The agent should:

* identify current configuration;
* preserve unrelated configuration;
* back up files before modification;
* make incremental changes;
* avoid destructive regeneration.

Generated files should be clearly identifiable as generated.

---

# 21. Native Operations Should Remain Native Where Beneficial

Not every action needs to pass through an Omivoid process.

For latency-sensitive Niri actions:

```text
window.focus.left
window.close
workspace.next
```

the registry may generate native Niri configuration.

The registry remains authoritative for the meaning and binding.

Niri remains authoritative for execution.

Avoid:

```text
key
→ spawn process
→ Omivoid
→ Niri IPC
```

when:

```text
key
→ native Niri action
```

provides the same semantics.

---

# 22. Simple Before Sophisticated

Phase 1 is an architectural proof.

Do not prematurely introduce:

* persistent daemon;
* event bus;
* DBus service;
* plugin marketplace;
* distributed action routing;
* complex policy engine;
* machine-learning ranking;
* graphical registry editor.

A simple implementation that proves the contract is preferable.

---

# 23. No Architecture by Accident

Implementation convenience must not silently establish architectural policy.

If an implementation requires violating a documented principle, the agent should identify the issue before making the change.

The correct process is:

```text
Requirement
    ↓
Implementation attempt
    ↓
Conflict discovered
    ↓
Document conflict
    ↓
Architecture decision
    ↓
Implementation
```

not:

```text
Requirement
    ↓
Developer changes architecture silently
```

---

# 24. Failure Should Be Explicit

Omivoid actions should fail predictably.

Prefer:

```text
DEPENDENCY_MISSING
```

with an explanation over raw tool output.

Prefer:

```text
ACTION_UNAVAILABLE
```

over silently doing nothing.

This is especially important for AI and automation.

---

# 25. Configuration Should Be Inspectable

Users and agents should be able to determine:

* which actions exist;
* which bindings are active;
* which adapters are selected;
* which dependencies are unavailable;
* which platform is active.

The architecture should favour plain-text configuration and human-readable diagnostics.

---

# 26. Local First

Omivoid should remain useful without a permanent external cloud dependency.

Local operation should be preferred where appropriate for:

* configuration;
* action execution;
* interaction state;
* themes;
* keyboard operation;
* local AI workflows.

Remote capabilities can extend the system but should not unnecessarily become prerequisites for normal desktop operation.

---

# 27. Build for the Actual Machine Role

The Omivoid laptop is primarily intended for:

* planning;
* research;
* writing;
* project ideation;
* web development;
* light development;
* interaction with AI;
* handing larger tasks to more capable systems.

It is not intended to reproduce the entire IBIS infrastructure locally.

Desktop design should optimise for this role.

---

# 28. Composable Rather Than Monolithic

Omivoid should consist of replaceable components with clear contracts.

For example:

```text
Interaction
     │
Action Registry
     │
Adapters
     │
Niri / DMS / Linux services
```

Replacing a component should not require redesigning every layer above it.

---

# 29. Escape Must Mean Escape

For Omivoid-created transient interfaces:

```text
Esc
```

should consistently mean:

```text
cancel / close / leave
```

This applies to:

* command palette;
* keybinding explorer;
* chord overlays;
* AI palette;
* project selector;
* wallpaper selector where controllable.

Consistency is more important than novelty.

---

# 30. Common Navigation Semantics

Omivoid interfaces should generally use:

```text
Enter       Select / execute
Esc         Cancel / close
Arrow keys  Navigate
Tab         Next region
Shift+Tab   Previous region
```

Individual components may have additional controls, but should avoid contradicting these without good reason.

---

# 31. Public Project Quality

`omivoid-lmde` may become a reusable public project.

Implementation should therefore avoid assumptions that only make sense on the original development machine.

Prefer:

* documented dependencies;
* relative paths;
* configurable applications;
* machine profiles;
* readable error messages;
* reproducible configuration.

Avoid:

* hard-coded home directories;
* undocumented dependencies;
* personal paths in core files;
* configuration that only works because of unrecorded machine state.

---

# 32. Guiding Test

When evaluating a new feature, ask:

1. What user intent does this represent?
2. Is there already an Omivoid action for it?
3. Which component should actually own execution?
4. Can an existing component provide it?
5. Is it discoverable?
6. Does it fit the keyboard grammar?
7. Does it unnecessarily depend on LMDE?
8. Should AI be allowed to invoke it?
9. Does it preserve the existing working system?
10. Does it make Omivoid simpler or merely larger?

If those questions cannot be answered clearly, the feature probably needs more design before implementation.
