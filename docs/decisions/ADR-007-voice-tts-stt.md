# ADR-007 — Voice Split into TTS and STT

**Status:** Accepted
**Project:** `ominty-core`
**Phase:** Phase 2
**Decision scope:** Voice interaction surface; registry metadata; STT engine; recording indicator

---

# 1. Context

Ominty has carried a single deferred item called **"voice"** since Phase 1:

* `AGENTS.md` §39 (deferred features list);
* `docs/13` §30 (deferred work must be explicit);
* `docs/10` (implementation plan);
* `docs/02` §24 — "Voice is considered a future interaction surface over the
  same action system… Phase 1 should preserve this possibility but does not
  require full voice implementation";
* `docs/03` §19 — the `voice_accessible` registry field exists "to avoid
  redesigning the registry later";
* `docs/ai/00` — voice listed under future interfaces.

That single word conflates two independent capabilities:

* **TTS** — text to speech (output);
* **STT** — speech to text (input).

They have different engines, different failure modes, different surfaces and
different milestones. Treating them as one deferred blob blocked progress on the
half that is actually needed.

On the reference machine a working **TTS** stack (Piper + daemon + indicator)
already exists from the Cinnamon → Niri migration, but sits outside the action
contract. **STT** does not exist at all, and dictation is the immediate need.

---

# 2. Decision

> **Ominty un-defers voice, splits it into TTS and STT, and implements STT
> first. Voice becomes an interaction surface over the Action Registry, with
> implementation in adapters — not a standalone application.**

Concretely:

1. TTS and STT are specified separately (`docs/ai/11-voice-integration.md`).
2. **STT is the first milestone**; TTS is recorded and integrated later,
   reusing the existing Piper stack rather than rebuilding it.
3. The STT engine is **local whisper.cpp** (model `ggml-base.en`).
4. Dictation is a **registry action** (`voice.dictate`) implemented by an
   **adapter**, not a shell script invoked directly by a keybinding.
5. The recording indicator is a **focused Quickshell popup**, presentation only.

---

# 3. Rationale for the split

* TTS and STT share no code path, no engine and no failure mode.
* Keeping "voice" deferred blocked the useful half (STT) behind the unneeded
  half.
* The registry already anticipated the split with a per-action
  `voice_accessible` flag; only the surface was monolithic.

---

# 4. Rationale for STT first

* Dictation is the immediate user need; TTS already works locally.
* STT is the larger unknown (engine, model, capture, injection) and therefore
  the larger risk to retire early.
* Proving STT also validates the voice plumbing (capture, indicator, policy)
  that TTS expansion will reuse.

---

# 5. Registry and contract relationship

Voice is **not** exempt from the core contracts:

* the **Registry** defines what `voice.dictate` means (Contract 1);
* the **adapter** defines how it is performed (Contract 2);
* surfaces (keyboard, CLI, DMS) invoke the canonical action and do not embed
  `pw-record`/`whisper`/`wtype` themselves (Contract 3);
* platform-specific detail stays in adapters (Contract 5);
* existing user configuration is preserved (Contract 6).

`voice_accessible` is the policy gate for what voice may invoke, mirroring
`ai_accessible` (`docs/03` §19, `AGENTS.md` §17).

---

# 6. Local-first engine

whisper.cpp is chosen because it is local, permissively licensed, buildable from
source with the toolchain already present, and consistent with the project's
local-Ollama stance. No audio leaves the machine.

The engine is **not packaged in apt**; the installer/runbook builds it and
fetches a model, and the action reports `DEPENDENCY_MISSING` when it is absent
rather than failing the desktop.

---

# 7. Interaction mode

Niri provides **no key-release bindings**, so true hold-to-talk is not directly
expressible. Dictation is therefore **toggle** (press to start, press to stop).
Push-to-talk may return later, owned by the indicator component, without
changing the registry or adapter.

---

# 8. Indicator placement

DMS plugins cannot register an OSD (their capabilities are bar widget, desktop
widget, launcher, daemon, control-centre). Under ADR-006's plugin-first
hierarchy this is the "standalone component" branch, justified because no DMS
core or plugin surface provides a transient recording overlay.

The indicator is therefore a focused Ominty Quickshell component, driven by the
Quickshell PipeWire peak monitor. It is presentation only.

---

# 9. Rejected alternatives

**Leave voice deferred until both halves can be built.** Rejected — blocks the
needed half behind the unneeded one.

**Build STT as a standalone script bound to a key.** Rejected — violates
Contracts 1–3, loses discoverability, palette and CLI exposure, and repeats the
mistake the existing Piper scripts already made.

**Use a cloud STT API.** Rejected for the default — inconsistent with the
local-first stance; may be offered later as a configured provider.

**Make the recording indicator a DMS plugin.** Rejected — DMS plugins cannot
register an OSD; a plugin would misrepresent the surface.

**Implement hold-to-talk now.** Rejected — Niri cannot express it; a toggle is
honest and works.

---

# 10. Consequences

Positive:

* the deferred item is retired and replaced by two tractable capabilities;
* dictation becomes discoverable, scriptable and AI-policy-consistent;
* the existing Piper work gains a contract home;
* `voice_accessible` is used as originally intended.

Costs:

* a new build dependency (whisper.cpp) and a model download;
* a new runtime dependency (`wtype`) for injection;
* a Quickshell component to maintain;
* the indicator's start/stop signalling mechanism must be defined (Phase 3).

---

# 11. Revisit conditions

* Niri gains key-release bindings → reconsider push-to-talk;
* DMS gains a supported OSD/overlay plugin capability → consider moving the
  indicator into DMS (ADR-006 §42);
* STT accuracy/latency is inadequate → larger model, other engine, or GPU
  acceleration;
* `voice.command` (speech → action) is taken up → widen `voice_accessible`
  under its own review.
