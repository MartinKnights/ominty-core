# ADR-001 — Niri as the Omivoid Compositor

**Status:** Accepted
**Project:** `omivoid-lmde`
**Phase:** Phase 1
**Decision scope:** Omivoid desktop architecture

---

# 1. Context

Omivoid requires a Wayland compositor capable of supporting a keyboard-first desktop environment.

The project takes inspiration from aspects of the Omarchy user experience, but Omivoid is not intended to reproduce Omarchy's underlying implementation.

Omarchy uses Hyprland.

Omivoid uses Niri.

Niri is already installed on the Phase 1 LMDE development system and is part of the intended eventual Void Linux architecture.

---

# 2. Decision

> **Niri is the canonical compositor for Omivoid.**

Omivoid will be designed around Niri's interaction and window-management model rather than treating Niri as a substitute implementation of Hyprland.

Niri-specific behaviour belongs behind the compositor integration boundary where appropriate, but Omivoid is not currently intended to be compositor-neutral.

---

# 3. Rationale

Niri provides a distinctive scrolling window-management model well suited to keyboard-oriented workflows.

Its strengths include:

* keyboard-driven navigation;
* efficient window movement;
* strong Wayland architecture;
* dynamic scrolling layout;
* workspace support;
* IPC capabilities;
* compatibility with Quickshell;
* compatibility with DankMaterialShell.

Using Niri also gives Omivoid its own desktop character rather than producing a direct reproduction of Omarchy.

---

# 4. Important Distinction

Omivoid adopts selected **interaction principles** from Omarchy.

It does not adopt Hyprland's mechanics.

Therefore:

```text
Omarchy concept
      ↓
evaluate user value
      ↓
translate into Omivoid interaction
      ↓
implement naturally with Niri
```

is correct.

The following is not:

```text
Hyprland behaviour
      ↓
force Niri to imitate it
```

---

# 5. Niri Responsibilities

Niri remains authoritative for:

* window focus;
* window movement;
* scrolling layout;
* workspace management;
* fullscreen;
* floating state;
* output configuration;
* input configuration;
* window rules;
* compositor-level keyboard handling.

Omivoid may represent these operations as canonical actions but does not take ownership of their implementation.

---

# 6. Native Execution

Where an action maps directly to a Niri operation, native Niri execution should be preferred.

Example:

```text
window.close
```

may be represented in the Action Registry while executing directly through:

```text
Niri keybinding
    ↓
native close-window
```

This avoids unnecessary process invocation and latency.

---

# 7. External Invocation

The same canonical action may require Niri IPC when invoked through another interaction surface.

Example:

```text
CLI / AI / command palette
          ↓
window.close
          ↓
Niri adapter
          ↓
Niri IPC
```

This means one canonical action may legitimately have different execution paths depending on invocation context.

---

# 8. Existing Configuration

Niri is already installed and configured on the Phase 1 machine.

The existing configuration must therefore be treated as user state rather than disposable installation output.

The implementation agent must:

1. inspect it;
2. back up affected files;
3. identify conflicts;
4. preserve unrelated configuration;
5. integrate incrementally.

---

# 9. Consequences

## Positive

Omivoid can deliberately optimise its interaction model for Niri.

This reduces unnecessary compositor abstraction and allows use of Niri-native capabilities.

The resulting desktop should feel designed for Niri rather than merely compatible with it.

## Negative

Omivoid will not automatically work on Hyprland, Sway or other compositors.

Supporting another compositor would require a new compositor adapter and potentially interaction decisions where compositor semantics differ.

This is accepted.

---

# 10. Rejected Alternative — Hyprland

Hyprland was not selected simply because Omarchy uses it.

Doing so would make the project more derivative and would discard the intended Niri-based architecture.

Omivoid is intended to reproduce useful workflow qualities rather than the original implementation stack.

---

# 11. Rejected Alternative — Compositor-Neutral Core From Phase 1

A fully compositor-neutral architecture would require abstraction before Omivoid has enough implementation experience to know which abstractions are useful.

This would increase Phase 1 complexity.

Instead:

```text
design for Niri
      ↓
keep sensible boundaries
      ↓
generalise later only if required
```

---

# 12. Revisit Conditions

This decision should be reconsidered only if:

* Niri cannot support a fundamental Omivoid interaction requirement;
* Niri development becomes unsuitable for the project;
* a future requirement explicitly demands multi-compositor support;
* substantial technical evidence demonstrates that another compositor provides a significantly better architectural fit.

Preference alone is not sufficient reason to destabilise the compositor layer.

---

# 13. Result

Niri is a foundational Omivoid component.

The design principle is:

> **Omivoid should feel native to Niri, not like an Omarchy/Hyprland interaction model translated mechanically onto Niri.**
