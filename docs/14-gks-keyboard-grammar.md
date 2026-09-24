# Omivoid — Global Keybindings System (GKS)

**Document:** 14
**Status:** Phase 1 specification (GKS-1)
**Scope:** the keyboard grammar, collision priority, and the tabbed cheat sheet.

---

Yes. I’d frame GKS not as “a giant list of shortcuts,” but as a keyboard grammar for Linux: a small number of modifier namespaces, each with a consistent semantic meaning, so that once you learn the grammar you can predict shortcuts you have never used before.

The important constraint you gave—do not replace established application conventions—is exactly right. GKS should sit around existing conventions rather than fight them.
1. The core idea: modifiers represent domains

I would establish this hierarchy:
Modifier	Domain	Meaning
Ctrl	Application	Do something to the current application's content
Alt	Navigation / focus	Move around the current UI/context
Super	Workspace / system	Manipulate windows, workspaces and the desktop
Shift	Expansion / inverse	Extend, reverse, or modify the base operation
Ctrl+Alt	System tools	Cross-application/system operations
Super+Alt	Window management	Advanced window placement/state
Super+Ctrl	Workspace management	Advanced workspace operations

The key principle is:

    The first modifier tells you what universe you're operating in; the key tells you what operation you're performing.

So:

    Ctrl+S → application says “save”

    Alt+Left → navigate backward

    Super+Left → manipulate the window/workspace

    Super+Shift+Left → same workspace operation, but with an expanded/move interpretation

That makes shortcuts compositional rather than arbitrary.
2. Preserve the "native" application layer

Your first rule should be:
Ctrl = application/content

Don't try to redesign this layer.

Established conventions remain authoritative:

Ctrl+S       Save
Ctrl+O       Open
Ctrl+N       New
Ctrl+W       Close document/tab
Ctrl+Z       Undo
Ctrl+Shift+Z Redo
Ctrl+X       Cut
Ctrl+C       Copy
Ctrl+V       Paste
Ctrl+A       Select all
Ctrl+F       Find
Ctrl+P       Print
Ctrl+Q       Quit

GKS simply says:

    When an action belongs inside an application, Ctrl is its namespace.

This gives you a very powerful boundary.

For example, GKS shouldn't invent Super+S for saving. That's semantically wrong because Super isn't the application namespace.
3. Super becomes the desktop namespace

This is probably the most important part of GKS.
Super = "outside the application"

Use it for:

    windows

    workspaces

    monitors

    desktop

    launching

    application switching

    window positioning

    system-level UI

For example:

Super+1        Go to workspace 1
Super+2        Go to workspace 2
Super+3        Go to workspace 3

Super+Left     Move/focus window left
Super+Right    Move/focus window right
Super+Up       Maximize / move upward
Super+Down     Restore / move downward

But I'd make one important distinction.
Super + direction = navigate/focus

Super+Left
Super+Right
Super+Up
Super+Down

means:

    Change where I am in the desktop/window topology.

Then:
Super + Shift + direction = move

Super+Shift+Left
Super+Shift+Right
Super+Shift+Up
Super+Shift+Down

means:

    Take the current object with me.

This is an extremely useful grammatical rule.

For example:

Super+Right

→ focus the window to the right.

Super+Shift+Right

→ move the current window to the right.

And this can extend to workspaces:

Super+1

→ go to workspace 1.

Super+Shift+1

→ send current window to workspace 1.

That's exactly the sort of consolidation GKS should provide.
4. Shift should mean "apply the operation to the object"

This deserves to become a general GKS law.
Base operation

Super+1 → go to workspace 1

Shifted operation

Super+Shift+1 → move current window to workspace 1

Likewise:

Super+Right

focus/navigate right.

Super+Shift+Right

move current window right.

This gives Shift a predictable meaning rather than assigning random shortcuts to it.

I'd call this the:

    Shift = object transformation principle

It means "don't merely navigate to/change the target; apply the operation to the current object."
5. Alt = navigation inside the current context

I would deliberately avoid making Alt another window-management namespace.

Instead:
Alt = navigate/focus within the current application or interface

Examples:

Alt+Left       Back
Alt+Right      Forward

Alt+Up         Parent / previous level
Alt+Down       Enter / next level

This works particularly well with things such as:

    file managers

    browsers

    IDEs

    terminals

    document viewers

You can think of it as:

Ctrl  → manipulate content
Alt   → navigate content/UI
Super → manipulate environment

That's a very clean three-level model.
6. Ctrl+Alt = system utilities

Now we get into things that don't naturally belong to an application or workspace.

I'd reserve:
Ctrl+Alt = global/system action

Potential namespace:

Ctrl+Alt+T       Terminal
Ctrl+Alt+L       Lock
Ctrl+Alt+Delete  System/security action
Ctrl+Alt+Esc     Emergency/system interaction

The exact bindings are configurable, but the semantic territory is important.

You can then look at an unfamiliar GKS shortcut:

Ctrl+Alt+X

and immediately know:

    "This is probably a system-level operation."

7. Super + Alt = window state

I'd reserve the combination for properties of the current window, rather than movement.

For example:

Super+Alt+M     Maximize
Super+Alt+F     Fullscreen
Super+Alt+H     Hide/minimize
Super+Alt+T     Always-on-top

Conceptually:

Super       = window/workspace domain
Super+Shift = move the window
Super+Alt   = change window state

That's a useful subdivision.
8. Super + Ctrl = workspace topology

This is where GKS can become particularly interesting.

Super alone deals with using workspaces.

Super+Ctrl deals with changing the workspace structure.

For example:

Super+1              Go to workspace 1
Super+Shift+1        Move window to workspace 1

Super+Ctrl+N         Create workspace
Super+Ctrl+D         Delete workspace
Super+Ctrl+Left      Move workspace left
Super+Ctrl+Right     Move workspace right

So there are three distinct levels:

Super
  └── operate within workspace environment

Super+Shift
  └── operate on current window

Super+Ctrl
  └── modify workspace environment

That is much more memorable than a collection of unrelated shortcuts.
9. Introduce a "verb vocabulary"

I'd actually go one step further.

GKS should define verbs, independent of individual programs.

For example:
Key	GKS verb
H/J/K/L or arrows	directional movement
1–9	numbered targets
Tab	cycle
Enter	activate
Esc	cancel/exit
Space	toggle/select
Backspace	reverse/up/remove
Delete	destroy/remove
Home	beginning
End	end
PageUp/PageDown	large movement

Then modifiers supply the domain.

For example:

Super+1

workspace 1.

Alt+1

application/UI target 1, where applicable.

Ctrl+1

application-defined target 1, such as a tab.

Same key, different namespace.

That's the heart of a keyboard grammar.
10. The direction keys become particularly powerful

I'd make the four directions a foundational part of GKS.

Left
Right
Up
Down

mean:

    movement in the relevant domain

Then the modifier determines the domain.
Application

Ctrl+Left
Ctrl+Right

Application-specific/content movement.
Navigation

Alt+Left
Alt+Right

Navigate backward/forward.
Desktop

Super+Left
Super+Right

Window/workspace navigation.
Window movement

Super+Shift+Left
Super+Shift+Right

Move window.
Workspace topology

Super+Ctrl+Left
Super+Ctrl+Right

Rearrange workspaces.

This creates an almost mathematical system.
11. Tabs get their own convention

Tabs are ubiquitous enough that GKS can establish a common convention without overriding established application shortcuts.

I'd recommend:

Ctrl+Tab          Next tab
Ctrl+Shift+Tab    Previous tab

where applications don't already provide a conflicting established convention.

But there's an important distinction:
Ctrl = content/application

So tabs are still legitimately inside the application domain.

Then:

Super+Tab

should mean application/window switching, not tabs.

That creates a beautiful distinction:

Ctrl+Tab   → next thing inside this application
Super+Tab  → next thing outside this application

This is exactly the sort of relationship GKS should exploit.
12. Think in concentric circles

I'd define GKS's conceptual architecture like this:

                 SYSTEM
                   │
             Ctrl+Alt / Super
                   │
        ┌──────────┴──────────┐
        │                     │
     DESKTOP               APPLICATION
      Super                   Ctrl
        │                     │
   ┌────┴────┐          ┌─────┴─────┐
   │         │          │           │
 Window   Workspace   Content     Navigation
   │         │
 Shift      Ctrl

Or even more simply:

Ctrl       = IN the application
Alt        = AROUND the current context
Super      = OUTSIDE the application
Ctrl+Alt   = SYSTEM

That is a very strong foundation.
13. A proposed GKS specification

I'd formalize the first version as something like:
GKS-1: Modifier semantics
Ctrl

Application operations

    Operate on content, documents, tabs, selections, or application state.

Alt

Context navigation

    Navigate within the current interface/context.

Super

Desktop operations

    Operate on windows, applications, workspaces and the desktop.

Shift

Transformation

    Apply the base operation to the current object, or select/extend where appropriate.

Ctrl+Alt

System operations

    Operate on the operating system rather than an individual application.

Super+Alt

Window state

    Modify properties/state of the current window.

Super+Ctrl

Workspace topology

    Modify the workspace environment itself.

14. A useful "grammar"

We could express GKS formally as:

[DOMAIN] + [VERB] + [MODIFIER]

Where:

DOMAIN
  Ctrl       Application
  Alt        Navigation
  Super      Desktop
  Ctrl+Alt   System

and:

VERB
  Left/Right/Up/Down   Move
  1–9                  Select target
  Tab                  Cycle
  Enter                Activate
  Esc                  Cancel
  S                    Save
  F                    Find
  ...

and:

MODIFIER
  Shift       Apply to current object
  Ctrl        Modify environment/topology
  Alt         Modify state

Not every combination needs to exist. The grammar is there to constrain the design space.
15. The most important GKS rule

I'd make this the project's central philosophy:

    Never invent a shortcut when a predictable shortcut can be derived from the grammar.

For example, suppose you want:

    Move the current window to workspace 4.

Don't arbitrarily choose:

Super+M

Instead derive it:

Super       = workspace
4           = workspace 4
Shift       = operate on current window

→ Super+Shift+4

Likewise:

    Navigate to the window on the right.

Super       = desktop
Right       = direction

→ Super+Right

    Move the window right.

Super       = desktop
Right       = direction
Shift       = transform current object

→ Super+Shift+Right

The user doesn't have to memorize three shortcuts. They learn three rules.
16. Don't make GKS absolute

There is one architectural issue I'd explicitly bake into the project.

GKS should have three levels of authority:
Level 1 — Universal

Things like:

Ctrl+C
Ctrl+V
Ctrl+S
Ctrl+Z
Alt+F4

Leave them alone.
Level 2 — GKS

Shortcuts where Linux desktop environments have fragmented conventions.

These are the main target.

For example:

Super+Shift+1
Super+Shift+2
...

Level 3 — Application-specific

Applications are allowed to override GKS when the operation is intrinsically application-specific.

So GKS isn't:

    "Every Linux program must obey these keys."

It's:

    "Linux programs should share a predictable keyboard vocabulary whenever there is no strong existing convention."

That distinction will make the system much more practical.
17. I'd also define "collision priority"

This will become important if you actually implement GKS.

I suggest:

1. Established universal convention
2. Application-specific established convention
3. GKS global convention
4. Desktop-environment convention
5. User customization

But there's a subtlety that turns this list from a simple ranking into an algorithm: **priority is resolved per-namespace, not globally.**

Because GKS deliberately keeps `Ctrl` (application) and `Super` (desktop) in different universes (§2, §3), most apparent collisions never actually happen. `Ctrl+C` does not compete with a desktop action, because GKS never puts a desktop action on bare `Ctrl`. A collision only needs resolving when two layers claim **the same combo in the same namespace**.

Two qualifications make the list usable:

- **Namespace first, then priority.** `Alt+F4` (universal) never collides with `Super+F4` (desktop) — Alt ≠ Super.
- **User customization is a re-map, not a trump card.** A user override re-points one slot; it should not *silently* disable a universal convention. If the user re-points `Ctrl+S`, GKS should warn, not assume.

### 17.1 The four collision cases

| Case | Example | Resolution |
|---|---|---|
| Same combo, different namespace | `Alt+F4` vs `Super+F4` | Not a collision — different domains |
| Same combo, universal vs GKS | `Ctrl+Alt+Delete` | Universal/system wins (§6) |
| Same combo, GKS vs DE default | `Super+K` (GKS explorer vs Niri `focus-window-up`) | **GKS wins** — the GKS layer sits above the DE default |
| Same combo, user override | user re-points `Super+E` | User wins for that slot |

The third row is exactly the `Mod+K` shadow already found in this project: Omivoid's include sits *after* DMS's, so the GKS claim wins. GKS makes that **intentional** rather than accidental.

### 17.2 The resolution algorithm

```
resolve(combo):
    namespace = namespace_of(combo)        # Ctrl | Alt | Super | …
    for layer in [universal, application, gks, desktop, user]:
        if layer.claims(combo) and layer.namespace == namespace:
            return layer.owner(combo)
    return unbound
```

A binding is only "won" by a layer if it shares the namespace. This is why the grammar matters: **it prevents most collisions from ever existing.**

---

18. GKS has three levels of authority, and four physical layers

The authorities from §16 land on four concrete layers in a real system:

| Layer | Owner | Namespace | Editable by |
|---|---|---|---|
| Universal convention | applications | `Ctrl`, `Alt` (content) | nobody — leave alone |
| GKS grammar | the project | `Super`, `Super+Shift`, `Super+Alt`, `Super+Ctrl`, `Ctrl+Alt` | the project |
| Desktop implementation | Niri + DMS | Niri binds / DMS binds | config |
| User customization | the user | any | the user |

Authority flows one way:

```
GKS grammar            (what a combo means)
      ↓
Action Registry        (canonical action ids + declared keys)
      ↓
generator              (emits the Niri bindings fragment)
      ↓
Niri (dispatch)  +  DMS (shell-level binds)
```

**GKS is a design law; the registry is its implementation.** The generator is the only thing allowed to write Omivoid's Niri binds — never a hand-edited fragment.

---

19. Reserved namespaces and prefixes

GKS should reserve a few **prefixes** as sub-namespaces, so a domain can grow without consuming the whole keyboard:

| Prefix | Domain | Examples |
|---|---|---|
| `Super+A` | AI | `Super+A` menu · `Super+A,A` ask · `Super+A,P` Pi · `Super+A,E` explain · `Super+A,S` summarise |
| `Super+P` | Projects (reserved) | `Super+P,O` open · `Super+P,T` terminal · `Super+P,A` AI · `Super+P,C` context |
| `Super+Ctrl` | Workspace topology | `Super+Ctrl+Left/Right` rearrange · `Super+Ctrl+N/D` create/delete |
| `Super+Alt` | Window state | `Super+Alt+M/F/H/T` maximize/fullscreen/hide/on-top |
| `Ctrl+Alt` | System | `Ctrl+Alt+T` terminal · `Ctrl+Alt+L` lock · `Ctrl+Alt+Delete` security |

**The prefix rule:** *a prefix is a promise.* If `Super+A,*` is AI, it must only ever be AI. That predictability is the entire point.

---

20. The consistency laws

§1–§15 restated as laws an implementation must obey:

1. **Namespace law** — the first modifier selects the domain (§1).
2. **Derive-don't-invent law** — never invent a shortcut a rule can derive (§15).
3. **Direction law** — arrows / `HJKL` mean "move in the current domain" (§10).
4. **Number law** — `1–9` mean "numbered target" in the current domain (§9).
5. **Shift = object law** — Shift applies the base operation to the current object (§4).
6. **State law** — `Super+Alt` changes window *state*, not position (§7).
7. **Topology law** — `Super+Ctrl` changes the workspace *structure* (§8).
8. **Cycle law** — `Tab` cycles; `Ctrl+Tab` cycles *inside* the app, `Super+Tab` *outside* it (§11).
9. **Universal law** — never shadow a universal convention (§2, §16).

---

21. Mapping GKS onto this implementation (Niri / DMS / Omivoid)

| GKS concern | Where it lives today |
|---|---|
| Canonical meaning | `actions/*.toml` (registry) |
| Omivoid-owned bindings | `cli/omivoidlib/generator.py` → `~/.config/omivoid/generated/niri/bindings.kdl` |
| Shell / system / media keys | DMS `dms/binds.kdl` |
| Compositor dispatch | Niri |
| Collision handling | include order (Omivoid after DMS) + `DMS_CLAIMED_KEYS` |

Two GKS changes fall out of this:

1. The generator should treat `Super+Ctrl` and `Super+Alt` as first-class grammar tiers, not just "other keys".
2. Every combo the user sees must be **derivable** from the grammar — which is what the cheat sheet has to teach.

> Naming note: this document writes `Super`. In Niri/KDL this is `Mod`; the cheat sheet and registry should render it as `Mod` for consistency with the generated config.

---

22. The Keyboard Cheat Sheet — tabbed per domain

The cheat sheet is where GKS becomes usable. **One dialog, one tab per domain**, each tab a continuous list.

**Invocation:** `Super+K` (interaction explorer) and/or `Super+Shift+Slash` (hotkey overlay).

**Tabs (one per GKS tier):**

| Tab | Modifier | Contents |
|---|---|---|
| **Application** | `Ctrl` | universal app conventions (reference — not owned by GKS) |
| **Navigation** | `Alt` | back/forward, level up/down |
| **Desktop** | `Super` | focus, launch, windows, workspaces, media |
| **Window state** | `Super+Alt` | maximize, fullscreen, hide, always-on-top |
| **Workspace topology** | `Super+Ctrl` | create/delete/reorder workspaces |
| **System** | `Ctrl+Alt` | terminal, lock, security |
| **AI** | `Super+A` | AI menu and chords |
| **Projects** | `Super+P` | reserved |
| **All** | — | every binding, searchable |

**Behaviour:**

- Each tab groups by prefix and lists `key → action` — the same shape as the generated `omivoid-keybindings-by-modifier.md`.
- Search filters across *all* tabs.
- Rows are generated from the **live** sources (registry + Niri + DMS) so the sheet can never drift from reality.
- Where a universal `Ctrl` convention is shown, it is marked as *reference only*.

**Implementation sketch (DMS + Quickshell):**

- Today `Super+K` opens the DMS spotlight in explorer mode (`!` / `!!` sentinel) via the `omivoidActions` plugin.
- A tabbed cheat sheet is a **DMS plugin surface** — a `PluginComponent` containing a `TabBar` + `ListView`.
- Its data comes from a new command, `omivoid keybinds --json`, which merges the three sources and tags each row with its GKS domain.
- Fallback: extend DMS's built-in hotkey overlay (`show-hotkey-overlay`) if it can accept pre-grouped data.

---

23. What GKS does not do

- It does **not** replace application `Ctrl` conventions.
- It does **not** impose one desktop's keys on another — it describes a grammar; the DE supplies the bindings.
- It does **not** require every combination to exist (§14).
- It does **not** let a user override silently break a universal convention.

---

24. Implementation order

1. **Lock the grammar** ("GKS-1") and the reserved prefixes (§18, §19).
2. **Resolve known collisions** (`Mod+K`, `Mod+P`) using the priority algorithm (§17).
3. **Add `omivoid keybinds --json`** — merge registry + Niri + DMS, tag with domain.
4. **Build the tabbed cheat-sheet plugin** on that data (§22).
5. **Audit the existing bindings** against the laws (§20); fix violations.
6. **Freeze and version the grammar** as `docs/14-gks-keyboard-grammar.md`.

---

25. Open questions

1. Does `Super+Tab` (outside-app cycling) get adopted, or stay with DMS?
2. Which four `Super+Alt` window-state keys — maximize / fullscreen / hide / always-on-top?
3. `Super+Ctrl+N` / `Super+Ctrl+D` (create/delete workspace) — Niri uses *dynamic* workspaces; do these apply, or map to something else?
4. Is the cheat sheet read-only (reference), or can the user rebind from inside it?
5. Do we surface the universal `Ctrl` conventions in the cheat sheet even though GKS does not own them?

---

*End of GKS design document.*

---

### Definitions

| Term | Meaning |
|---|---|
| **GKS** | Global Keybindings System — the keyboard grammar defined here |
| **Domain** | The universe selected by the first modifier (Application, Navigation, Desktop, …) |
| **Namespace** | Synonym for domain in collision terms; combos only collide within one |
| **Prefix** | A reserved first half of a chord (`Super+A`, `Super+P`) |
| **Layer** | One of the four authorities: universal, application, GKS, desktop, user |
| **Grammar law** | One of the nine rules in §20 |


---

## GKS-1 — resolved decisions (2026-09-20)

Decisions taken when adopting GKS (answering §25):

| # | Question (§25) | Decision |
|---|---|---|
| 1 | `Super+Tab` | **Adopted** — outside-application cycling (`Ctrl+Tab` stays inside-app) |
| 2 | `Super+Alt` window state | **Adopted** — maximize / fullscreen / hide-minimize / always-on-top |
| 3 | `Super+Ctrl+N` / `D` | **Not adopted** — Niri uses **dynamic workspaces**, so workspace create/delete are unnecessary |
| 4 | Cheat sheet editable? | **Read-only** — reference only |
| 5 | Show universal `Ctrl` conventions? | **Yes** — shown as reference rows (source `Universal`) |

Implementation decisions:

| Item | Decision |
|---|---|
| Cheat sheet | **Own DMS plugin** (`popoutContent` surface), *not* a fork of DMS's `KeybindsModal` |
| Invocation | `Super+K` opens the tabbed cheat sheet |
| Data source | `omivoid keybinds --json` (merges registry + Niri + DMS, tags each row with its GKS domain) |
