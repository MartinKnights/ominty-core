"""AI policy (docs/ai/09-ai-security-policy.md).

Phase A: provider asks are read-only (Pi invoked with --no-tools; Ollama
generate API has no tool use). Action policy enforcement arrives with
AI-to-action (Phase B).
"""

from __future__ import annotations