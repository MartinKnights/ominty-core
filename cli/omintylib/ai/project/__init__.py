"""Project discovery and project context (docs/ai/06, AI-26/27).

Phase F implements minimum project identification:

    explicit root (OMINTY_PROJECT / --root)
        → Git root
        → AGENTS.md walk-up (bounded by home)
        → current working directory

Project context is compositional (docs/ai/06 §4): identity, instructions
(AGENTS.md), bounded structure, minimal git state. It is never
"read every file → send everything" (docs/ai/06 §41).

Secret exclusion (docs/ai/06 §29, docs/ai/09 §17): project context never
auto-ingests .env, *.key, *.pem, credentials, secret stores. The bounded
structure listing excludes them and no secret file is ever read.

Collector contract (docs/ai/05 §58):

    collect_project() -> {"success": True, "context": ContextObject}
                         {"success": False, "error": {"code", "message"}}
"""

from __future__ import annotations

import fnmatch
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ..context import ContextObject

# Maximum AGENTS.md size accepted as inline instructions (docs/ai/05 §36).
# Phase 1 uses a simple limit (docs/ai/06 §27): a large instruction file
# inflates the provider prompt and, on CPU-only models, prompt evaluation
# can exceed the provider timeout. The full file path is appended when
# truncation occurs so a tool-capable provider (Pi) can read the rest.
MAX_INSTRUCTIONS_BYTES = 4 * 1024

# Obvious credential material never auto-ingested (docs/ai/06 §29,
# docs/ai/09 §17). Matched against file/dir names with fnmatch.
SECRET_PATTERNS = (
    ".env", ".env.*",
    "*.key", "*.pem", "*.p12", "*.pfx", "*.crt",
    "id_rsa", "id_ed25519", "id_dsa", "id_ecdsa",
    "credentials", "credentials.json", "credentials.yml",
    "secrets", "secret", ".secret",
    ".netrc", ".pgpass", "*.token", "*.secret",
)

# Common software-project manifest signals (docs/ai/06 §21).
_SOFTWARE_SIGNALS = (
    "AGENTS.md", "package.json", "pyproject.toml", "Cargo.toml",
    "go.mod", "requirements.txt", "Makefile", "CMakeLists.txt",
)


def is_secret(name: str) -> bool:
    """True when a file/dir name matches obvious credential material."""
    return any(fnmatch.fnmatch(name, pat) for pat in SECRET_PATTERNS)


def _git_root(cwd: Path) -> Path | None:
    """Return the Git repository root containing cwd, or None."""
    if shutil.which("git") is None:
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5.0,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode != 0:
        return None
    root = Path(result.stdout.strip())
    return root if root.is_dir() else None


def _find_agents_md(start: Path) -> Path | None:
    """Walk up from start (bounded by the home directory) for AGENTS.md.

    Stops before the home directory's parent so a stray AGENTS.md above
    the user's home is never picked up.
    """
    home_parent = Path.home().resolve().parent
    for parent in [start, *start.parents]:
        if parent == home_parent:
            break
        candidate = parent / "AGENTS.md"
        if candidate.is_file():
            return candidate
    return None


def _project_type(root: Path) -> str:
    """Infer a coarse project type (docs/ai/06 §18, §21)."""
    if (root / "AGENTS.md").is_file():
        return "software"
    for signal in _SOFTWARE_SIGNALS:
        if (root / signal).exists():
            return "software"
    return "generic"


def _bounded_structure(root: Path) -> list[str]:
    """Top-level project tree, excluding .git and secret material.

    Bounded by design (docs/ai/06 §12): never a recursive dump.
    """
    entries: list[str] = []
    try:
        names = sorted(os.listdir(root))
    except OSError:
        return entries
    for name in names:
        if name == ".git" or is_secret(name):
            continue
        path = root / name
        entries.append(name + "/" if path.is_dir() else name)
    return entries


def _read_agents_md(path: Path) -> str | None:
    """Read AGENTS.md, bounded to MAX_INSTRUCTIONS_BYTES.

    Truncation is explicit and includes the full path so a tool-capable
    provider can read the remainder itself (docs/ai/06 §30).
    """
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    encoded = data.encode("utf-8")
    if len(encoded) <= MAX_INSTRUCTIONS_BYTES:
        return data
    truncated = encoded[:MAX_INSTRUCTIONS_BYTES].decode("utf-8", errors="ignore")
    return f"{truncated}\n…(truncated; full file at {path})"


def _git_state(root: Path) -> dict[str, Any] | None:
    """Minimal git state: branch + clean/dirty. None when not a repo."""
    if shutil.which("git") is None:
        return None
    try:
        branch = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5.0,
        )
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5.0,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if branch.returncode != 0:
        return None
    dirty = bool(status.stdout.strip())
    return {"branch": branch.stdout.strip() or "detached", "clean": not dirty}


def discover_project(cwd: Path | None = None, explicit: str | None = None) -> dict:
    """Identify the project root (docs/ai/06 §6, AI-26).

    Signal precedence: explicit root (argument or OMINTY_PROJECT) →
    nearest AGENTS.md walk-up → Git root → cwd. AGENTS.md outranks the
    Git root because it is the strongest project-instruction boundary
    (docs/ai/06 §8–9): a repository may contain several instruction
    scopes, and the nearest AGENTS.md defines the one the user is in.
    Explicit selection always wins (docs/ai/06 §6).

    Returns:
        {"success": True, "root": Path, "name": str, "method": str}
        {"success": False, "error": {"code", "message"}}
    """
    start = Path(cwd or os.getcwd()).resolve()
    explicit = explicit or os.environ.get("OMINTY_PROJECT")

    if explicit:
        root = Path(explicit).expanduser().resolve()
        if not root.is_dir():
            return {
                "success": False,
                "error": {
                    "code": "INVALID_ARGUMENT",
                    "message": f"explicit project root does not exist: {root}",
                },
            }
        return {
            "success": True,
            "root": root,
            "name": root.name,
            "method": "explicit",
        }

    agents = _find_agents_md(start)
    if agents is not None:
        root = agents.parent
        return {"success": True, "root": root, "name": root.name, "method": "AGENTS.md"}

    git = _git_root(start)
    if git is not None:
        return {"success": True, "root": git, "name": git.name, "method": "git"}

    return {"success": True, "root": start, "name": start.name, "method": "cwd"}


def collect_project(cwd: Path | None = None, explicit: str | None = None) -> dict:
    """Collect project context as a ContextObject (docs/ai/06 §27, AI-27).

    Compositional: identity + instructions + bounded structure + git state.
    Never auto-ingests secret material (docs/ai/06 §29).

    Returns:
        {"success": True, "context": ContextObject(type="project")}
        {"success": False, "error": {"code", "message"}}
    """
    discovered = discover_project(cwd, explicit)
    if not discovered["success"]:
        return {"success": False, "error": discovered["error"]}

    root: Path = discovered["root"]
    agents_path = root / "AGENTS.md"
    agents_md = _read_agents_md(agents_path) if agents_path.is_file() else None
    structure = _bounded_structure(root)
    git = _git_state(root)
    ptype = _project_type(root)

    parts = [
        f"Project: {discovered['name']}",
        f"Root: {root}",
        f"Type: {ptype}",
    ]
    if agents_md:
        parts.append(f"\nProject instructions (AGENTS.md):\n{agents_md}")
    if structure:
        parts.append("\nProject structure:\n" + "\n".join(f"- {e}" for e in structure))
    if git:
        state = "clean" if git["clean"] else "dirty"
        parts.append(f"\nGit: {git['branch']} ({state})")

    return {
        "success": True,
        "context": ContextObject(
            type="project",
            content="\n".join(parts),
            source="project",
            metadata={
                "root": str(root),
                "name": discovered["name"],
                "method": discovered["method"],
                "type": ptype,
                "has_instructions": agents_md is not None,
                "git": git,
            },
        ),
    }