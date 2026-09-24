Having looked at the **current DMS plugin registry**, I think the DMS decision is even more useful for Omivoid than we originally anticipated. DMS already supplies a substantial desktop platform—launcher, clipboard, notifications, system controls, theming, monitoring, etc.—and its plugin model supports widgets, daemons, launcher providers, desktop widgets and composites. ([GitHub][1])

That means I would **not install lots of plugins simply because they are available**. I would choose plugins that strengthen the three things your laptop is becoming particularly good at: **project/research work, infrastructure access, and AI-assisted workflows**.

## My shortlist for Omivoid

| Priority | Plugin                 | Why it fits                                                                   |
| -------- | ---------------------- | ----------------------------------------------------------------------------- |
| ★★★★★    | **Dank Launcher Keys** | Almost exactly our `Super+K` requirement                                      |
| ★★★★★    | **Dank Hooks**         | Excellent bridge between DMS and the Omivoid Action Registry                  |
| ★★★★★    | **Tailscale Manager**  | Directly relevant to your distributed IBIS environment                        |
| ★★★★★    | **Command Runner**     | Very useful foundation for Omivoid actions                                    |
| ★★★★☆    | **Taskwarrior**        | Excellent local-first project/task workflow                                   |
| ★★★★☆    | **Phone Connect**      | Useful laptop ↔ Android integration                                           |
| ★★★★☆    | **AI Assistant**       | Useful prototype/reference for `Super+A`                                      |
| ★★★★☆    | **Wallabag**           | Particularly interesting for research/book-writing workflow                   |
| ★★★☆☆    | **SSH Monitor**        | Conceptually excellent for IBIS infrastructure, but currently awkward on LMDE |
| ★★★☆☆    | **PortWatch**          | Great web-development idea, but currently Hyprland-specific                   |

There are a few others I'd investigate later, but these are the ones that map unusually well to what we're building.

### 1. Dank Launcher Keys — this could replace much of our planned `Super+K`

This is the first one I would install.

It's a **first-party DMS plugin** specifically designed to *search and browse keyboard shortcuts from your compositor and applications*. It's compositor- and distro-independent. ([GitHub][2])

That maps almost perfectly onto one of our core Omivoid principles:

> Keyboard-first, but discoverable.

Rather than immediately writing our own Interaction Explorer, I would see whether Launcher Keys can consume or be extended to consume our **Omivoid Action Registry**.

Potential architecture:

```text
Omivoid Action Registry
        │
        ├── generates Niri bindings
        │
        └── generates shortcut metadata
                    │
                    ▼
            Dank Launcher Keys
                    │
                    ▼
                 Super+K
```

If that works, **delete the custom `Super+K` UI from our implementation workload**. Omivoid should supply the authoritative data; DMS supplies the polished interface.

That's exactly the sort of simplification we wanted from DMS.

---

### 2. Dank Hooks — potentially one of the most important plugins for Omivoid

This one looks innocuous but is architecturally very interesting.

It's another first-party plugin and its purpose is simply:

> Trigger scripts based on various system events. ([GitHub][3])

That gives us a lightweight event mechanism **without building `omivoidd`**.

For example:

```text
DMS event
   │
   ├── wallpaper changed
   ├── session event
   ├── display event
   └── other DMS event
          │
          ▼
      Dank Hooks
          │
          ▼
omivoid action run ...
```

This could solve a number of things we had deliberately deferred to a future Omivoid daemon.

For Phase 1 I would investigate:

```text
Wallpaper changed
    → theme.palette.regenerate

Display change
    → Omivoid display action

Session event
    → Omivoid hook

DMS event
    → Omivoid Action Registry
```

**This may allow us to postpone an Omivoid daemon indefinitely.**

---

### 3. Tailscale Manager — definite install

There is a DMS **Tailscale Manager** plugin. It is a DankBar widget, supports any compositor and distro, and provides Tailscale toggle functionality. ([GitHub][4])

This fits your architecture unusually well because your laptops are not supposed to do everything locally. They're the planning/research/development endpoints, while heavier work can move elsewhere.

So I would eventually expose:

```text
network.tailscale.status
network.tailscale.connect
network.tailscale.disconnect
network.tailscale.open
```

Then DMS becomes the graphical surface while the Omivoid Action Registry remains authoritative.

Longer term this becomes especially useful with Herdr:

```text
                    OMIVOID LAPTOP
                         │
                      Tailscale
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
       Desktop PC                IBIS Office
     heavy compute                  server
                                      │
                                     Agno
```

The Tailscale plugin gives you a nice visible representation of part of that infrastructure.

---

### 4. Command Runner — very useful, but use it carefully

The **Command Runner** adds shell-command execution directly to the DMS launcher, including command history, shortcuts, and terminal/background execution modes. ([GitHub][5])

For you, that could be extremely useful.

But I wouldn't make arbitrary shell commands the primary Omivoid interface.

Instead:

```text
DMS Launcher

> omivoid project open
> omivoid ai research
> omivoid action run theme.wallpaper.select
> omivoid action run app.editor.open
```

That effectively makes the DMS launcher a front end to the Omivoid CLI.

There's a nice distinction here:

```text
Command Runner
     │
     ├── arbitrary shell command      ← expert escape hatch
     │
     └── omivoid ...                  ← preferred workflow
```

So I would install it, but retain our Action Registry architecture.

---

### 5. Taskwarrior — very strong fit for your laptop workflow

The Taskwarrior plugin shows pending tasks in the DMS status bar, allows creation using Taskwarrior syntax, and lets you complete tasks directly from DMS. It works across compositors and distributions. ([GitHub][6])

I particularly like this for your setup because **Taskwarrior is local-first, CLI-native and scriptable**.

That means it can sit underneath multiple interfaces:

```text
                    Taskwarrior
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
         DMS            CLI          Omivoid
                                      │
                                      ▼
                                     AI
```

You could eventually say:

> "Add a task to the Omivoid project to investigate DMS selection capture."

and Pi could invoke something such as:

```text
project.task.create
```

with Taskwarrior as the adapter.

That's much more aligned with Omivoid than adopting a large proprietary task-management application.

---

### 6. Phone Connect — especially useful on the laptops

The first-party **Phone Connect** plugin integrates KDE Connect or Valent into DMS. It exposes connected-device battery state, file transfer, find-phone and other controls in the bar/control centre. ([GitHub][7])

Given that you're using an Android phone alongside these laptops, I'd install this fairly early.

It also gives us another interesting future Action Registry namespace:

```text
device.phone.status
device.phone.send
device.phone.find
device.phone.share
```

It fits the philosophy of making Omivoid a **workflow surface**, rather than treating each integration as a separate application.

---

### 7. AI Assistant — install as a reference, not as the Omivoid AI architecture

There's already an **AI Assistant** DMS plugin with multiple provider support, streaming responses, Markdown rendering and persistent chat history. ([GitHub][8])

I would definitely test it.

But I would **not replace our Pi + Herdr architecture with it**.

Instead, evaluate it as a possible DMS presentation layer:

```text
                 Super+A
                    │
                    ▼
             Omivoid AI layer
              /           \
             /             \
           Pi              Herdr
          local           delegation
             \             /
              \           /
               DMS UI
```

If the AI Assistant UI is good, we may be able to adapt/fork/extend the presentation rather than writing our own AI panel.

More importantly, studying how it handles streaming, history and providers could save us implementation work.

---

### 8. Wallabag — surprisingly good fit for your research workflow

This one stood out because of how you intend to use the laptops.

The Wallabag plugin gives you a read-it-later queue directly in DMS, including unread count, excerpts, search, quick-add, archive/star/delete and batch operations. It stores OAuth secrets in the system keyring. ([GitHub][9])

For general users I wouldn't necessarily prioritise it.

For **your** research/book-writing/project-development workflow, I would.

Imagine:

```text
Web research
     │
     ├── interesting article
     │
     ▼
  Wallabag
     │
     ▼
Research queue
     │
     ├── Read
     ├── Summarise with Pi
     ├── Extract references
     ├── Send to project
     └── Add to Obsidian knowledge
```

That starts to look very much like the workflow layer we've been discussing.

I would therefore put Wallabag in the **Phase 2 productivity group**, even if you aren't currently running Wallabag.

---

## Two plugins I like but would **not install yet**

**SSH Monitor** is conceptually excellent for your infrastructure work: it monitors active SSH, SFTP, FTP and Yazi VFS connections. Unfortunately, the registry currently declares it specifically for **Niri but Arch only**, with Fish, procps-ng and net-tools dependencies. ([GitHub][10]) So I would examine its implementation rather than immediately putting it on `omivoid-lmde`. It could be worth making an LMDE/Void-compatible version later.

**PortWatch** is even more relevant to your web-development work: it shows listening ports/development servers in DankBar and lets you stop them. Unfortunately, its current registry entry explicitly depends on `hyprctl` and declares Hyprland support, so it isn't an appropriate Niri install as-is. ([GitHub][11])

But I really like the concept for Omivoid:

```text
DEV
──────────────────────────
PHP       :8000     ●
Vite      :5173     ●
MySQL     :3306     ●
Redis     :6379     ●
```

For your Trongate/web work, an **Omivoid/Niri-compatible Dev Services plugin** could eventually be considerably more useful than the existing PortWatch.

---

# More importantly: DMS changes our Phase 1 plan again

The plugin registry is now large and actively maintained—the official registry contains both first- and third-party extensions, while DMS itself supports reproducible plugin installs through its plugin lockfile. ([GitHub][12])

So I would change our development philosophy slightly:

```text
OLD QUESTION

"What Omivoid component should we build?"

              ↓

NEW QUESTION

"Does DMS already provide this?"
              │
       ┌──────┴──────┐
      YES            NO
       │              │
       ▼              ▼
   integrate      Can a plugin
                    provide it?
                       │
                ┌──────┴──────┐
               YES            NO
                │              │
                ▼              ▼
          use/extend       build Omivoid
            plugin          component
```

And DMS's plugin architecture makes this much more practical than I initially expected: plugins can be **widgets, daemons, launcher providers, desktop components or composites**, so an Omivoid-specific capability doesn't necessarily require modifying DMS itself. ([GitHub][13])

### The first Omivoid plugin I would eventually build

Interestingly, I now think we should consider an **`Omivoid Actions` DMS plugin** rather than a separate Omivoid shell UI.

It could be a composite plugin:

```text
Omivoid Actions
│
├── Launcher provider
│      └── searches Action Registry
│
├── Widget
│      └── optional Omivoid status/context
│
├── Daemon
│      └── listens for useful DMS events
│
└── Control Centre
       └── Omivoid / AI / project controls
```

Then:

```text
                   DMS
                    │
             Omivoid Plugin
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Actions      AI      Projects
          │         │         │
          └─────────┼─────────┘
                    ▼
            Omivoid Action Registry
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
      Niri          Pi          Herdr
                                  │
                              Tailscale
                                  │
                      Desktop / IBIS Server
```

**That is probably cleaner than the UI architecture in our existing Phase 1 documents.** DMS becomes the desktop presentation framework; Omivoid becomes the **interaction, action, AI and workflow layer built into it**.

So before your agent starts Stage 0 implementation, I would make one small addition to the specification pack: **`ADR-006-dms-plugin-first-integration.md`**. It would establish the rule *DMS core → existing plugin → extend plugin → Omivoid plugin → standalone component*, in that order. That could prevent the agent from rebuilding capabilities that the rapidly growing DMS ecosystem already provides.

[1]: https://github.com/AvengeMedia/DankMaterialShell?utm_source=chatgpt.com "GitHub - AvengeMedia/DankMaterialShell: Desktop shell for wayland compositors built with Quickshell & GO, optimized for niri, hyprland, sway, MangoWC, labwc, and MiracleWM. · GitHub"
[2]: https://github.com/AvengeMedia/dms-plugin-registry/blob/master/plugins/dank-launcherkeys.json "dms-plugin-registry/plugins/dank-launcherkeys.json at master · AvengeMedia/dms-plugin-registry · GitHub"
[3]: https://github.com/AvengeMedia/dms-plugin-registry/blob/master/plugins/dank-hooks.json "dms-plugin-registry/plugins/dank-hooks.json at master · AvengeMedia/dms-plugin-registry · GitHub"
[4]: https://github.com/AvengeMedia/dms-plugin-registry/blob/master/plugins/cglavin50-tailscale.json "dms-plugin-registry/plugins/cglavin50-tailscale.json at master · AvengeMedia/dms-plugin-registry · GitHub"
[5]: https://github.com/AvengeMedia/dms-plugin-registry/blob/master/plugins/devnullvoid-command-runner.json "dms-plugin-registry/plugins/devnullvoid-command-runner.json at master · AvengeMedia/dms-plugin-registry · GitHub"
[6]: https://github.com/AvengeMedia/dms-plugin-registry/blob/master/plugins/cyrylas-taskwarrior.json "dms-plugin-registry/plugins/cyrylas-taskwarrior.json at master · AvengeMedia/dms-plugin-registry · GitHub"
[7]: https://github.com/AvengeMedia/dms-plugin-registry/blob/master/plugins/dank-kdeconnect.json "dms-plugin-registry/plugins/dank-kdeconnect.json at master · AvengeMedia/dms-plugin-registry · GitHub"
[8]: https://github.com/AvengeMedia/dms-plugin-registry/blob/master/plugins/devnullvoid-ai-assistant.json "dms-plugin-registry/plugins/devnullvoid-ai-assistant.json at master · AvengeMedia/dms-plugin-registry · GitHub"
[9]: https://github.com/AvengeMedia/dms-plugin-registry/blob/master/plugins/arqueon-wallabag.json "dms-plugin-registry/plugins/arqueon-wallabag.json at master · AvengeMedia/dms-plugin-registry · GitHub"
[10]: https://github.com/AvengeMedia/dms-plugin-registry/blob/master/plugins/boutabong-sshmonitor.json "dms-plugin-registry/plugins/boutabong-sshmonitor.json at master · AvengeMedia/dms-plugin-registry · GitHub"
[11]: https://github.com/AvengeMedia/dms-plugin-registry/blob/master/plugins/alamin147-port-watch.json "dms-plugin-registry/plugins/alamin147-port-watch.json at master · AvengeMedia/dms-plugin-registry · GitHub"
[12]: https://github.com/AvengeMedia/dms-plugin-registry "GitHub - AvengeMedia/dms-plugin-registry: Official and Third Party Plugins & Themes for DankMaterialShell · GitHub"
[13]: https://github.com/AvengeMedia/DankMaterialShell/blob/master/.agents/skills/dms-plugin-dev/SKILL.md?utm_source=chatgpt.com "DankMaterialShell/.agents/skills/dms-plugin-dev/SKILL.md at master · AvengeMedia/DankMaterialShell · GitHub"
