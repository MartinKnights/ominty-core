# Omivoid LMDE — Project Overview

**Project:** Omivoid LMDE
**Repository:** `omivoid-lmde`
**Phase:** Phase 1 — LMDE Reference Implementation
**Status:** Design and initial implementation
**Target platform:** LMDE
**Desktop stack:** Niri + Quickshell
**Shell candidate:** DankMaterialShell (DMS)

---

## 1. Purpose

Omivoid is a keyboard-first, AI-native Linux desktop environment and interaction architecture built around Niri.

The project is inspired by aspects of the user experience and philosophy of Omarchy, particularly:

* universal and memorable keyboard bindings;
* keyboard-first operation;
* discoverable keyboard shortcuts;
* wallpaper-driven colour selection;
* unified visual theming across applications;
* AI as a first-class desktop capability.

Omivoid is not intended to reproduce Omarchy's implementation.

Instead, Omarchy serves as a reference for useful interaction concepts. Omivoid reimplements selected concepts using an architecture designed around Niri, Quickshell, portability, local-first AI and the user's actual computing environment.

---

## 2. Phase 1 Project

`omivoid-lmde` is the first reference implementation of Omivoid.

Its purpose is to develop and validate the Omivoid interaction architecture on LMDE before implementing the eventual Void Linux version.

LMDE is therefore not merely a temporary development environment. It is the first platform implementation of a desktop architecture intended to remain portable.

The relationship should be understood as:

```text
                    Omivoid
                       │
              Omivoid Interaction
                       │
             Omivoid Action Registry
                       │
              Platform Abstraction
                 ┌─────┴─────┐
                 │           │
               LMDE         Void
              Phase 1      Later
```

The majority of Omivoid behaviour above the platform abstraction should remain identical between the LMDE and Void implementations.

---

## 3. Current Baseline

The Phase 1 machine already has:

* LMDE installed and operational;
* Niri installed and operational;
* Quickshell installed.

These are existing prerequisites.

Phase 1 MUST NOT begin by reinstalling Niri or Quickshell.

Before modifying either component, the implementation agent must:

1. inspect the existing installation;
2. identify installed versions where relevant;
3. locate the active configuration;
4. document relevant existing behaviour;
5. back up configuration files that will be modified;
6. preserve unrelated existing configuration.

The agent MUST NOT replace a working configuration wholesale merely because a generated configuration is easier to implement.

Changes should be deliberate and incremental.

---

## 4. DankMaterialShell

DankMaterialShell (DMS) is being considered as the primary desktop shell implementation.

DMS potentially provides much of the conventional shell functionality Omivoid requires, including areas such as:

* desktop bar;
* status indicators;
* notifications;
* OSDs;
* system controls;
* wallpaper selection;
* dynamic theming;
* launcher functionality.

Phase 1 should therefore evaluate and integrate DMS rather than unnecessarily recreate functionality already provided well by DMS.

However:

> DMS is an implementation component, not the definition of Omivoid.

The Omivoid interaction architecture must not become unnecessarily dependent on DMS internals.

If DMS is later replaced, the Omivoid Action Registry and interaction model should remain substantially unchanged.

---

## 5. What Omivoid Is

Omivoid should be understood primarily as an **interaction architecture**, not a Linux distribution.

Its defining characteristics are:

### 5.1 Keyboard-first

Frequent desktop operations should be accessible efficiently from the keyboard.

Pointer interaction remains supported.

Keyboard-first does not mean keyboard-only.

### 5.2 Discoverable

Users should not have to memorise the entire keyboard interface before becoming productive.

`Super+K` provides a discoverable interaction and keybinding explorer.

Chorded keyboard namespaces should display available next actions where practical.

### 5.3 Action-driven

Meaningful desktop operations are represented by canonical Omivoid actions.

Examples:

```text
app.browser.open
window.close
workspace.next
theme.wallpaper.select
ai.ask
project.delegate
```

Interaction mechanisms invoke actions rather than independently implementing behaviour.

### 5.4 Portable

The user-facing interaction model should not depend unnecessarily on:

* Debian;
* Void;
* systemd;
* runit;
* a particular package manager;
* a particular application executable.

Platform-specific behaviour belongs behind adapters.

### 5.5 AI-native

AI is a first-class interaction surface.

AI capabilities should integrate with the desktop through controlled Omivoid actions rather than relying solely on unrestricted shell execution.

### 5.6 Visually coherent

Wallpaper, desktop shell and supported applications should participate in a common colour system.

A wallpaper change should be capable of producing a corresponding system-wide visual theme.

---

## 6. Interaction Surfaces

A core Omivoid action may be exposed through several interaction surfaces:

```text
                Omivoid Action
                      │
       ┌──────────────┼──────────────┐
       │              │              │
   Keyboard          GUI            CLI
       │              │              │
       └──────────────┼──────────────┘
                      │
                 AI / Voice
```

Where practical, these surfaces should invoke the same canonical action.

For example:

```text
theme.wallpaper.select
```

might be invoked by:

* a keyboard shortcut;
* DMS;
* the Omivoid command palette;
* `omivoid theme wallpaper select`;
* an authorised AI agent;
* eventually a voice request.

None of those surfaces should need to know the underlying implementation details.

---

## 7. Core Architecture

The initial architecture is:

```text
┌───────────────────────────────────────┐
│          Interaction Surfaces         │
│ Keyboard / GUI / CLI / AI / Voice     │
├───────────────────────────────────────┤
│          Omivoid Action Registry      │
│ Canonical intent and metadata         │
├───────────────────────────────────────┤
│          Omivoid Action Layer         │
│ Resolution / validation / execution   │
├───────────────────────────────────────┤
│               Adapters                │
│ Niri / DMS / Common / Platform / AI   │
├───────────────────────────────────────┤
│       Linux Desktop Infrastructure    │
│ Wayland / PipeWire / D-Bus / etc.     │
├───────────────────────────────────────┤
│                 LMDE                  │
└───────────────────────────────────────┘
```

The central architectural distinction is:

> **The Action Registry defines what an action means. An adapter defines how that action is performed.**

---

## 8. Component Responsibilities

### Niri

Niri remains authoritative for compositor functionality, including:

* window focus;
* window movement;
* scrolling layout;
* workspace management;
* fullscreen behaviour;
* floating windows;
* output management;
* input configuration;
* window rules.

Omivoid should expose useful Niri operations through canonical actions without unnecessarily reimplementing them.

### Quickshell

Quickshell provides the framework from which shell interfaces can be constructed.

Omivoid should not assume that Quickshell itself defines the desktop interaction architecture.

### DMS

If adopted, DMS provides much of the graphical shell and presentation layer.

Omivoid should integrate with it rather than fork or duplicate it unless there is a clear requirement.

### Omivoid

Omivoid owns:

* interaction conventions;
* keyboard grammar;
* canonical actions;
* action metadata;
* action discovery;
* platform abstraction;
* application roles;
* AI integration policy;
* Omivoid-specific workflows.

### LMDE

LMDE supplies the Phase 1 operating-system platform.

LMDE-specific implementation details must remain below the Omivoid platform boundary wherever practical.

---

## 9. Phase 1 Objectives

Phase 1 must prove that the architecture works.

The primary objectives are:

1. establish the Omivoid keyboard interaction grammar;
2. establish the Action Registry;
3. implement an initial action catalogue;
4. expose application roles rather than hard-coded application assumptions;
5. integrate native Niri operations;
6. provide `Super+K` interaction discovery;
7. provide a universal command/action palette;
8. establish the `Super+A` AI namespace;
9. establish wallpaper-driven coherent theming;
10. define the LMDE platform adapter boundary;
11. demonstrate that the design can later be transferred to Void.

---

## 10. Phase 1 Is Not a Desktop Rewrite

The implementation agent should favour integration over replacement.

In particular:

```text
Existing Niri
     +
Existing Quickshell
     +
DMS where suitable
     +
Omivoid interaction architecture
```

is preferable to:

```text
Replace everything
     +
Build custom shell
     +
Reimplement existing functionality
```

New components require a demonstrated need.

---

## 11. Phase 1 Minimum Experience

A successful Phase 1 should provide a recognisable Omivoid experience consisting of at least:

### Keyboard navigation

Predictable keyboard operation for:

* applications;
* windows;
* workspaces;
* system functions.

### `Super+K`

A searchable or browsable representation of available Omivoid interactions and bindings.

### `Super+Space`

A universal command/action palette.

### `Super+A`

An AI interaction namespace.

### Dynamic theming

Wallpaper selection should trigger or participate in a coherent colour/theme workflow.

### Action abstraction

The above capabilities should be backed by canonical Omivoid actions rather than independent ad-hoc scripts.

---

## 12. AI Architecture

AI should be treated as part of the desktop interaction architecture.

The intended environment includes:

```text
Omivoid laptop
     │
     ├── Pi
     │
     ├── Herdr
     │
     └── Remote IBIS capabilities
```

The laptop is not expected to host every heavy AI workload.

Omivoid should therefore support a model in which tasks can eventually be performed:

* locally;
* by a local agent;
* through Herdr;
* by remote infrastructure.

The interaction model should remain consistent regardless of where execution occurs.

Remote task routing itself is outside the minimum Phase 1 implementation.

---

## 13. Portability Target

Phase 1 must avoid architecture that makes the later Void implementation unnecessarily difficult.

The desired relationship is:

```text
               Omivoid Core
                    │
       ┌────────────┴────────────┐
       │                         │
   Debian adapter             Void adapter
       │                         │
      LMDE                      Void
```

A successful abstraction means most actions and interaction specifications require no changes when moving between platforms.

---

## 14. Repository Purpose

The `omivoid-lmde` repository serves three purposes:

1. the working LMDE implementation;
2. the reference implementation for Omivoid concepts;
3. a reusable project that may later be published for other LMDE/Debian users.

Code and configuration should therefore be understandable outside the original development machine.

Machine-specific values should not be embedded in portable core files.

---

## 15. Documentation Authority

The documents under `docs/` define the architecture and requirements.

Implementation should follow them.

Where implementation reveals that a specification is incorrect or impractical, the implementation agent should:

1. identify the conflict;
2. explain the technical reason;
3. propose a change;
4. avoid silently changing the architecture.

The implementation must not become the undocumented specification.

---

## 16. Success Criterion

Phase 1 succeeds when Omivoid feels like a coherent desktop environment rather than a collection of Niri configuration files, scripts and shell widgets.

The user should experience:

> **One keyboard language, one action model, one coherent visual system and one controlled interface through which humans and AI can operate the desktop.**
