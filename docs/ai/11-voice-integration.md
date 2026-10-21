# Ominty Voice Integration

**Project:** `ominty-core`
**Subsystem:** AI
**Document:** 11
**Status:** Phase 2 Specification

---

# 1. Purpose

This document defines how **voice** becomes a first-class Ominty capability.

Previously "voice" was a single deferred interaction surface (docs/02 §24,
docs/03 §19, `AGENTS.md` §39). This specification splits that surface into its
two independent halves and makes them concrete:

* **TTS** — text to speech (output). Already present locally as Piper; this
  document records its intended integration and later expansion.
* **STT** — speech to text (input). Not yet present; **this is the first
  implementation target**, because dictation is the immediate need.

The registry metadata hook (`voice_accessible`) that already exists on every
action exists precisely so this work could be added without redesigning the
registry. This document uses it.

Related: `docs/ai/00-ai-architecture.md`, `docs/ai/04-ai-action-capabilities.md`,
`docs/ai/09-ai-security-policy.md`, `docs/02-interaction-spec.md` §24,
`docs/03-action-registry-spec.md` §19.

---

# 2. Scope

In scope (this milestone):

* local **STT dictation** — speech → text into the focused application;
* a **recording indicator** (waveform/level popup) shown while recording;
* registry **actions**, an **adapter**, **configuration** and a **keybinding**
  for dictation;
* the documentation, tests and installation steps for the above.

Deferred (recorded, not built now):

* TTS expansion beyond the existing Piper setup;
* `voice.command` (speech → action) and `voice.ask` (speech → AI → speech);
* streaming/partial transcription;
* additional STT engines or models.

---

# 3. Design Objectives

* **Local first.** STT runs on the machine (whisper.cpp). No audio leaves the
  device, matching the local Ollama choice (`PROGRESS.md` D1/D5).
* **Contract-shaped.** Voice is an interaction surface over the action system,
  not a shortcut. Surfaces invoke canonical actions; adapters implement them
  (`AGENTS.md` §7 Contracts 1–3).
* **Platform-clean.** Distribution- and compositor-specific detail stays in
  adapters (`AGENTS.md` §20–21).
* **Reversible.** Nothing here may break the desktop if the engine is missing;
  actions report `DEPENDENCY_MISSING` and the binding simply does nothing
  (`AGENTS.md` §25, ADR-006 §33).

---

# 4. Relationship to the Existing Local Setup

The reference machine already runs a working **TTS** stack, built during the
Cinnamon → Niri migration ([`Ominty/docs/MIGRATION.md`](../../docs/MIGRATION.md)):

| Piece | Role |
| --- | --- |
| `piper` + `~/.piper-venv` + voices | synthesis engine |
| `read-selection` | grab selection/clipboard → strip Markdown → enqueue |
| `piper-daemon` | queue → Piper → WAV → status JSON |
| `piper-indicator` | tray indicator with play/pause/stop (X11 + SNI) |

This stack is **user-level and outside the registry**. §7 records how it is to
be brought inside the contract model; it is **not** rebuilt by this milestone.

STT has no existing implementation of any kind.

---

# 5. Architecture

```text
        Interaction surfaces
   keyboard · CLI · DMS · (later AI/voice)
                 │
                 ▼
          Ominty Action Registry
        voice.dictate · voice.transcribe · voice.stop
                 │
                 ▼
            Action Runner
                 │
                 ▼
      adapters/common/voice_dictate.py
                 │
      ┌──────────┼───────────┬────────────┐
      ▼          ▼           ▼            ▼
   capture     engine      inject      indicator
  pw-record  whisper.cpp   wtype       (Quickshell popup)
```

Each surface invokes a canonical action. The adapter owns capture, transcription
and injection. The indicator is presentation only and never owns semantics
(ADR-006 §5–6).

---

# 6. STT — Dictation

## 6.1 Engine

* **whisper.cpp** (local, C++). Not packaged in apt; built from source by the
  installer/runbook.
* **Model:** `ggml-base.en` (English, ~142 MB). Chosen for latency on the
  reference CPU; a larger model may be configured later.
* CPU by default. Vulkan (AMD RX 580) is an optional acceleration the installer
  may enable if it builds cleanly.

## 6.2 Capture

* **PipeWire** via `pw-record` (the session already runs PipeWire).
* A single mono 16 kHz PCM/WAV recording per dictation session.

## 6.3 Injection

* **`wtype`** types the transcript into the focused window.
* This is viable because Niri implements `zwp_virtual_keyboard_v1`.
* Clipboard-plus-paste is the documented fallback (`wl-copy` + a paste
  keystroke) where `wtype` is unavailable.

## 6.4 Recording mode

Niri has **no key-release bindings**, so true hold-to-talk is not directly
possible. Dictation is therefore **toggle**:

```text
press  → start recording (indicator appears)
speak
press  → stop, transcribe, inject (indicator disappears)
```

A held-key push-to-talk mode may later be owned by the indicator component
(which can listen for the key itself), but it is **not** part of this milestone.

## 6.5 Failure behaviour

| Condition | Result |
| --- | --- |
| engine or model missing | action fails `DEPENDENCY_MISSING`; binding is inert |
| no microphone / capture fails | action fails `ADAPTER_FAILED`, indicator never appears |
| empty transcript | action succeeds with no injection; nothing typed |

---

# 7. TTS — Existing and Intended

TTS is **not** re-implemented here. The intended integration (later milestone):

* registry actions `voice.speak.selection`, `voice.speak.clipboard`,
  `voice.speak` (text argument), `voice.stop`;
* an adapter `voice_speak` that delegates to the Piper daemon/indicator rather
  than duplicating synthesis;
* the existing `Ctrl+Alt+S` behaviour re-expressed as
  `ominty action run voice.speak.selection`.

The Piper daemon and indicator remain the playback service; the adapter is the
contract boundary.

## 7.1 Tray dependency (Debian and Ubuntu)

On Wayland the indicator publishes over **StatusNotifierItem**; the DMS bar
tray is an SNI host and has no XEmbed support (`docs/MIGRATION.md` §2). That
requires the AyatanaAppIndicator3 typelib.

| Family | Packages | Notes |
|---|---|---|
| Debian 13 / LMDE 7 | `gir1.2-ayatanaappindicator3-0.1`, `libayatana-appindicator3-1` | present in the apt archive (0.5.94) |
| Ubuntu 24.04 / Mint 22.x | same names | present in `noble` (0.5.93) |

Both packages are in the **`tts` layer** of the inspect manifest, so
`install.sh` provisions them through the same layer-driven apt path on either
family. The `tts` layer is *optional*: a missing dependency warns, it never
blocks the desktop install.

When apt cannot be used (no root), `scripts/tts/ensure-ayatana-appindicator.sh`
extracts the `.debs` into `~/.local/opt/ayatana-appindicator`; the indicator
re-execs with `LD_LIBRARY_PATH` and `GI_TYPELIB_PATH` set, before `import gi`.

---

# 8. Recording Indicator

A focused **Quickshell popup** (`AGENTS.md` §12: components stay focused and
isolated) shown while recording:

* live **input level / waveform**, driven by the Quickshell PipeWire peak
  monitor (`Quickshell.Services.Pipewire`);
* appears on record start, disappears on stop;
* **presentation only** — it holds no dictation state and invokes no engine.

DMS plugins cannot register an OSD (their capabilities are bar/desktop widget,
launcher, daemon, control-centre), so the indicator is an Ominty Quickshell
component rather than a DMS plugin. Its start/stop stimulus is the adapter's
recording state (an IPC call, socket or marker file — an implementation detail
fixed in Phase 3).

---

# 9. Registry Actions

Proposed canonical IDs (to be added to the registry with metadata):

| Action | Purpose | Adapter |
| --- | --- | --- |
| `voice.dictate` | toggle recording; transcribe; inject into focused window | `voice_dictate` |
| `voice.transcribe` | transcribe an audio file to text | `voice_transcribe` |
| `voice.stop` | stop recording / playback | `voice_dictate` |

`voice.speak.*` (TTS) is listed in §7 for the later milestone.

Every voice action carries:

```toml
risk = "routine"          # dictation types text; it does not run commands
confirmation = "never"
contexts = ["global"]
ai_accessible = false     # do not let the AI invoke the recorder by accident
voice_accessible = true
discoverable = true
palette = true
```

`voice.dictate` and `voice.stop` carry the keybinding (§13). `voice.transcribe`
carries none.

---

# 10. Adapters

Following the existing convention (`adapters/<platform|common>/<name>.py`):

| Adapter | Responsibility |
| --- | --- |
| `voice_dictate` | capture → engine → inject; signal the indicator |
| `voice_transcribe` | file → engine → text (shared engine helper) |
| `voice_speak` *(later)* | delegate to the Piper service |

Adapters are the only place that knows `pw-record`, `whisper.cpp` and `wtype`.
The engine invocation is shared by `voice_dictate` and `voice_transcribe`.

---

# 11. Configuration

`~/.config/ominty/voice.toml` (user config wins over the shipped default, as
with `ai.toml`):

```toml
[voice]
enabled = true

[voice.stt]
engine = "whisper.cpp"
binary = "whisper-cli"          # or the built binary path
model = "~/.local/share/ominty/models/ggml-base.en.bin"
language = "en"
threads = 0                      # 0 = auto

[voice.stt.capture]
command = "pw-record"
sample_rate = 16000
channels = 1

[voice.stt.inject]
method = "wtype"                 # or "clipboard"
```

`voice.toml` follows the absence-wins rule: an existing user file is never
overwritten.

---

# 12. Policy — `voice_accessible`

`voice_accessible` mirrors `ai_accessible` (`docs/03` §19, `AGENTS.md` §17):

* voice commands may only invoke actions marked `voice_accessible = true`;
* risk, confirmation and recursion rules apply unchanged;
* `voice_accessible` defaults to `false` — opt-in per action;
* AI actions keep `ai_accessible = false` where they already do.

This milestone sets `voice_accessible = true` only on the new `voice.*` actions.
Widening it (so spoken commands can drive the desktop) is the `voice.command`
milestone and requires its own review.

---

# 13. Interaction Surfaces

| Surface | Binding | Notes |
| --- | --- | --- |
| Niri | `Super+Alt+D` | `voice.dictate` — start/stop dictation (toggle) |
| Niri | `Shift+Alt+T` | launch the recording indicator / push-to-talk UI |
| Niri | `Ctrl+Alt+S` | unchanged — TTS read-aloud (existing) |
| CLI | `ominty voice dictate`, `ominty voice transcribe <file>` | new subcommands |

Bindings are declared in the user-owned part of `config.kdl`, not in generated
fragments. The existing `Ctrl+Alt+S` read-aloud is left exactly as it is.

---

# 14. Platform and Portability

* Engine, capture and injection live in `adapters/common/`, with
  distribution-specific detail (package names, install paths) in
  `adapters/debian/` and, later, `adapters/void/` (`AGENTS.md` §20–21).
* Niri-specific facts (virtual-keyboard support; no key-release bindings) are
  recorded here rather than assumed by portable code.
* The indicator is compositor-agnostic Quickshell.

---

# 15. Testing

* **Unit:** adapter argument construction, config parsing, missing-dependency
  paths (engine/model absent), empty-transcript handling.
* **Registry:** `ominty registry validate` stays at 0 errors; new actions carry
  required metadata.
* **Live (documented manual):** record a phrase → correct text typed into a
  target window; indicator appears/disappears; nothing typed on empty input;
  desktop unaffected when the engine is absent.

---

# 16. Consequences

Positive:

* dictation becomes a first-class, discoverable, scriptable Ominty capability;
* voice is no longer a monolithic deferred item — TTS and STT can progress
  independently;
* the existing Piper work is given a contract home rather than being lost;
* the registry's `voice_accessible` hook is finally used as intended.

Negative / costs:

* a new build dependency (whisper.cpp) and model download;
* a new runtime dependency for injection (`wtype`);
* Niri cannot provide true hold-to-talk, so the interaction is a toggle until
  the indicator owns the key.

---

# 17. Revisit Conditions

* whisper.cpp accuracy or latency proves inadequate → evaluate a larger model,
  a different engine, or GPU acceleration;
* Niri gains key-release bindings → revisit push-to-talk;
* DMS gains a supported OSD/overlay plugin capability → the indicator may move
  into DMS (ADR-006 §42);
  * `voice.command` (speech → action) is taken up → widen `voice_accessible`
    under its own review.

---

# 18. Implementation Status

Implemented on the reference machine (2026-10-05):

| Piece | State |
| --- | --- |
| whisper.cpp built from source (CPU) | ✅ build dir `~/.cache/ominty/build/whisper.cpp` |
| `ggml-base.en` model | ✅ `~/.local/share/ominty/models/` |
| Round-trip verified (Piper → whisper) | ✅ ~2.2 s; only the invented word "Ominty" mis-rendered |
| `omintylib/voice.py` (config, engine, capture, transcribe, inject, state) | ✅ |
| `voice.dictate` / `voice.stop` / `voice.transcribe` actions | ✅ registry validates 0 errors |
| `voice.dictate` / `voice.transcribe` adapters | ✅ |
| `ominty voice status` / `transcribe` / `dictate` CLI | ✅ |
| `Super+Alt+D` binding (generated) | ✅ `niri validate` clean |
| Recording indicator (`shell/quickshell/ominty-voice`) | ✅ loads, connects to PipeWire peak monitor |
| `wtype` (injection) | ✅ user-scope install |

**TTS document layer (2026-10-07):**

| Piece | State |
| --- | --- |
| `omintylib/tts.py` — extraction + cleaning + chunking for `.md` `.txt` `.pdf` `.doc` `.docx` `.epub` | ✅ (pandoc, pdftotext, catdoc) |
| Overlapping player `omintylib/tts_player.py` — synthesises chunk *i* while chunk *i-1* plays | ✅ (verified next/prev/pause/resume/stop via FIFO) |
| MP3 export (`synthesize_segments` + ffmpeg concat) | ✅ (sample: 3-chunk → valid MP3) |
| `ominty tts say|mp3|status|next|prev|pause|resume|stop` CLI | ✅ |
| Player control popup `shell/quickshell/ominty-tts` (title, `current/total`, transport) | ✅ loads; resident |
| File picker `Ctrl+Alt+O` → `~/bin/tts-pick` → `ominty tts say` | ✅ |

Not yet done:

* installer/runbook support for the whisper.cpp build, the model download and
  `wtype` (Objective 2);
* live microphone dictation verified end-to-end by the user;
* `voice.speak.*` (TTS) integration — deferred;
* `voice.command` / `voice.ask` — deferred.

Implementation notes that matter for the installer:

* `whisper-cli` carries an **absolute RUNPATH** into the build dir — the same
  class of problem as gap **G6**; a relocated build tree breaks it.
* The generator originally emitted bindings only for a fixed set of adapters;
  it now emits the canonical action-runner spawn for any non-`shell.*` adapter,
  which is what gives `voice.dictate` its key.

