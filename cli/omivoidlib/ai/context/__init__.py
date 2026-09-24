"""Context envelope and collectors (docs/ai/05-context-system.md).

Phase E implements the structured context envelope plus the clipboard
collector (AI-22). Selection is classified CLIPBOARD FALLBACK
(docs/implementation/ai-context-evaluation.md, AI-23/24): direct
selection capture is not reliable on this stack, so `collect_selection`
returns CONTEXT_UNAVAILABLE rather than guessing.

Collector contract (docs/ai/05 §58):

    collect_*() -> {"success": True, "context": ContextObject}
                  {"success": False, "error": {"code", "message"}}

A collector returns either a context object or a clear failure. Context
must come from a known source; the clipboard is never relabelled as a
selection (docs/ai/05 §6, §18).
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any

# Maximum clipboard content accepted as context (docs/ai/05 §21).
MAX_CLIPBOARD_BYTES = 32 * 1024

# Timeout for reading the clipboard (seconds).
_CLIPBOARD_TIMEOUT = 5.0


@dataclass
class ContextObject:
    """A single structured context item (docs/ai/05 §5)."""

    type: str  # canonical context type: "clipboard", "selection", "file", ...
    content: str
    source: str  # provenance: "clipboard", "selection", "filesystem", ...
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict (for JSON output)."""
        return {
            "type": self.type,
            "content": self.content,
            "source": self.source,
            "metadata": dict(self.metadata),
        }


def _unavailable(message: str) -> dict:
    """Build a CONTEXT_UNAVAILABLE result."""
    return {
        "success": False,
        "error": {"code": "CONTEXT_UNAVAILABLE", "message": message},
    }


def collect_clipboard() -> dict:
    """Collect the current clipboard as context (AI-22).

    Reads the Wayland clipboard via ``wl-paste`` (wl-clipboard). Without
    wl-clipboard the collector fails explicitly — never stale or guessed
    data (AGENTS.md §19).

    Returns:
        {"success": True, "context": ContextObject}
        {"success": False, "error": {"code": "CONTEXT_UNAVAILABLE" |
                                     "CONTEXT_TOO_LARGE", "message": str}}
    """
    if shutil.which("wl-paste") is None:
        return _unavailable(
            "wl-paste not found — install wl-clipboard to read the clipboard"
        )

    try:
        result = subprocess.run(
            ["wl-paste", "--no-newline"],
            capture_output=True,
            text=True,
            timeout=_CLIPBOARD_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return _unavailable("clipboard read timed out")
    except OSError as e:
        return _unavailable(f"clipboard read failed: {e}")

    if result.returncode != 0:
        # wl-paste exits non-zero when the clipboard is empty or the
        # owning client has gone away — both mean "no usable context".
        return _unavailable(
            result.stderr.strip() or "clipboard is empty or unavailable"
        )

    content = result.stdout
    if not content.strip():
        return _unavailable("clipboard is empty")

    if len(content.encode("utf-8")) > MAX_CLIPBOARD_BYTES:
        return {
            "success": False,
            "error": {
                "code": "CONTEXT_TOO_LARGE",
                "message": (
                    f"clipboard content exceeds {MAX_CLIPBOARD_BYTES} bytes"
                ),
            },
        }

    return {
        "success": True,
        "context": ContextObject(
            type="clipboard",
            content=content,
            source="clipboard",
            metadata={"bytes": len(content.encode("utf-8"))},
        ),
    }


def collect_selection() -> dict:
    """Collect the current selection as context.

    Classified CLIPBOARD FALLBACK (docs/implementation/
    ai-context-evaluation.md, AI-24): direct selection capture is not
    reliably available on LMDE/Niri/Wayland/DMS. This collector always
    fails explicitly rather than substituting the clipboard
    (docs/ai/05 §6, §33).
    """
    return _unavailable(
        "selection capture is not available on this stack "
        "(see docs/implementation/ai-context-evaluation.md); "
        "use clipboard context instead"
    )


def build_prompt(prompt: str, contexts: list[ContextObject]) -> str:
    """Compose a provider prompt from context objects (docs/ai/05 §38).

    Phase 1 providers are text-prompt based, so context is rendered as
    labelled blocks above the user prompt. Provider-specific conversion
    may move into provider adapters later without changing this contract.
    """
    if not contexts:
        return prompt

    blocks: list[str] = []
    for ctx in contexts:
        label = ctx.type.upper()
        blocks.append(f"[{label} CONTEXT]\n{ctx.content}\n[/{label} CONTEXT]")

    return "\n\n".join(blocks) + "\n\n" + prompt