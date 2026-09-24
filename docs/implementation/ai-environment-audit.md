# AI Environment Audit — omivoid-lmde

**Date:** 2026-09-12
**Stage:** AI-0 (docs/ai/10-ai-phase-1-implementation-plan.md §4)
**Status:** Complete

This document records the state of the AI environment on the target machine before the AI integration begins. It is part of the implementation record (AGENTS.md §28) and the basis for the provider adapters (docs/ai/01-provider-interface.md).

---

## 1. Summary

Two AI providers are available on this machine:

| Provider | Version | Binary | Status |
|---|---|---|---|
| Pi | 0.85.1 | `/home/mk/.nvm/versions/node/v22.22.3/bin/pi` | Ready (openai provider) |
| Ollama | 0.12.10 | `/usr/local/bin/ollama` | Ready (server running, 5 models) |

Pi is the preferred initial provider (docs/ai/02-pi-integration.md §1). Ollama provides a fully local, offline-capable alternative and is incorporated as a second provider from Phase A (docs/ai/00-ai-architecture.md §7 "local model runner").

---

## 2. Pi

### 2.1 Installation

| Field | Value |
|---|---|
| Version | **0.85.1** |
| Executable | `/home/mk/.nvm/versions/node/v22.22.3/bin/pi` |
| Install method | npm (nvm-managed Node v22.22.3) |
| In PATH | yes (`pi` resolves) |

### 2.2 Configuration

| Field | Value |
|---|---|
| Config directory | `~/.pi/agent/` |
| `settings.json` | empty (`{}`) |
| `auth.json` | empty (`{}`) |
| `models-store.json` | empty (`{}`) |
| Extensions | none installed |

Pi is unconfigured at the Pi-native level. Provider readiness is currently satisfied by environment variables (see §2.4).

### 2.3 CLI interface (verified 0.85.1)

Key invocation options relevant to Omivoid integration:

| Option | Purpose |
|---|---|
| `--print`, `-p` | Non-interactive mode: process prompt and exit |
| `--mode <text\|json\|rpc>` | Output mode (default: text) |
| `--provider <name>` | Provider name (default: google) |
| `--model <pattern>` | Model pattern or ID (`provider/id`, optional `:thinking`) |
| `--api-key <key>` | API key (defaults to env vars) |
| `--no-tools`, `-nt` | Disable all tools |
| `--tools, -t <list>` | Comma-separated tool allowlist |
| `--no-session` | Ephemeral session (no history saved) |
| `--session <path\|id>` | Use a specific session |
| `--system-prompt <text>` | Override system prompt |
| `--append-system-prompt <text>` | Append to system prompt |
| `--no-context-files`, `-nc` | Disable AGENTS.md/CLAUDE.md discovery |
| `--offline` | Disable startup network operations |
| `--version`, `-v` | Version |

Commands: `pi install/remove/uninstall/update/list/config/auth <...>`.

`pi auth check --provider <name>` reports provider readiness. Verified: `pi auth check --provider openai` → `ready`.

### 2.4 Environment

| Variable | Value | Notes |
|---|---|---|
| `OPENAI_API_KEY` | set | Used by Pi's openai provider |
| `OPENAI_API_BASE` | `http://localhost:4000` | Local proxy endpoint |

`OPENAI_API_BASE` points at a local proxy (`localhost:4000`), not the default OpenAI endpoint. This is a machine-specific detail; the Pi adapter must not assume a particular base URL.

### 2.5 Discrepancy — placeholder credentials (docs/ai/10 §5)

Verified during AI-5 (CLI ask proof):

| Check | Result |
|---|---|
| `pi auth check --provider openai` | `ready` |
| Real ask (`pi --print --mode text ...`) | **401 invalid_api_key** |

Root cause:

1. `OPENAI_API_KEY` is the literal placeholder value `anything` (8 chars) — not a real credential.
2. `OPENAI_API_BASE` (`http://localhost:4000`) is **not reachable** — no proxy is running on that port.

`pi auth check` reports "ready" merely because a key env var exists; it does not validate the key or the base URL. The Pi provider adapter therefore validates **key plausibility** (rejects known placeholders and keys shorter than 20 chars) and **base reachability** before reporting `available`. With the current environment, `omivoid ai provider status pi` correctly reports `misconfigured`.

**Impact:** the Pi CLI proof cannot succeed until either a real key is provided or the `localhost:4000` proxy is started. Ollama provides the working local proof path (fully local, no key required).

### 2.5 Provider/model catalogue

`pi --list-models` exposes the openai provider catalogue (gpt-4, gpt-4o, gpt-5.x, etc.). Model selection belongs below the Omivoid interaction contract (docs/ai/00-ai-architecture.md §16) and is not hard-coded in Omivoid.

---

## 3. Ollama

### 3.1 Installation

| Field | Value |
|---|---|
| Version | **0.12.10** |
| Executable | `/usr/local/bin/ollama` |
| In PATH | yes (`ollama` resolves) |

### 3.2 Server

| Field | Value |
|---|---|
| Server endpoint | `http://localhost:11434` |
| Running | yes (`/api/tags` responds) |
| Data directory | `~/.ollama/` |

### 3.3 Local models

| Model | Size |
|---|---|
| `gemma3:4b` | 3.3 GB |
| `mistral:latest` | 4.4 GB |
| `nomic-embed-text:latest` | 274 MB |
| `phi3:3.8b` | 2.2 GB |
| `llama3.2:3b` | 2.0 GB |

Ollama provides a fully local inference path: no API key required, works offline. This satisfies the local-first principle (docs/ai/00-ai-architecture.md §15) and offline behaviour (§33).

---

## 4. DMS AI-Related Plugins

The DMS `aiAssistant` plugin exists in the DMS source tree and is documented in `docs/implementation/dms-plugin-inventory.md` §4.4.

**Status: REFERENCE ONLY.** DMS aiAssistant is a presentation-layer reference. Omivoid's `ai_accessible`/`risk`/`confirmation` registry policy remains authoritative (AGENTS.md §17). No DMS AI plugin is enabled or required for Phase A.

---

## 5. Existing AI Shortcuts

None. No AI-related key bindings exist in the Niri configuration or the action registry.

---

## 6. Existing Project AI Configuration

None. No `[ai]` configuration exists in `config/` or `~/.config/omivoid/`. The `ai` namespace is registered in the registry (docs/03 §4) but no `ai.*` actions exist yet.

---

## 7. Implications for Implementation

1. **Pi adapter** must invoke `pi --print --mode text` for non-interactive asks (AI-5 proof), and `pi` (interactive) for `ai.pi.open` (AI-3).
2. **Pi readiness** is determined by: binary in PATH + `pi auth check --provider openai` **plus** key plausibility and base reachability (§2.5). Pi-native config is empty, so env-based readiness is the practical check.
3. **Ollama adapter** must check the server at `http://localhost:11434` (`/api/tags`) and select a default local model (e.g. `gemma3:4b`).
4. **Provider selection** is configurable via `[ai] default_provider` (docs/ai/10 §9). Phase A ships `default_provider = "pi"` with Ollama selectable.
5. **No secrets** are committed (AGENTS.md §32): `OPENAI_API_KEY` lives in the environment, never in the repo.
6. **No personal paths** are committed (AGENTS.md §33): the Pi binary path above is machine state, not project configuration.
7. **Pi CLI proof is environment-blocked** (§2.5): requires a real key or a running `localhost:4000` proxy. Ollama is the working local proof path.