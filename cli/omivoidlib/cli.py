"""Omivoid CLI.

Implements the registry inspection commands from docs/03 §30:

    omivoid action list
    omivoid action show <id>
    omivoid action search <query>
    omivoid action run <id>
    omivoid registry validate
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .generator import DEFAULT_OUTPUT, build_fragment
from .helpdata import build_help_data, format_help_text, search_help_data
from .registry import (
    Action,
    Registry,
    has_errors,
    load_registry,
    validate_registry,
)
from .runner import run_action
from .search import search_actions


def _load() -> Registry:
    """Load the registry (core + user layers)."""
    return load_registry()


def _print_issue(issue) -> None:
    colour = {"ERROR": "\033[31m", "WARNING": "\033[33m", "INFO": "\033[36m"}.get(
        issue.level, ""
    )
    reset = "\033[0m" if colour else ""
    source = f" [{issue.source}]" if issue.source else ""
    print(f"{colour}{issue.level:<7}{reset} {issue.code}: {issue.message}{source}")


def cmd_action_list(args: argparse.Namespace) -> int:
    registry = _load()
    actions = sorted(registry.actions.values(), key=lambda a: a.id)

    if args.category:
        actions = [a for a in actions if a.category == args.category]

    if args.json:
        print(json.dumps([a.to_dict() for a in actions], indent=2))
        return 0

    if not actions:
        print("No actions found.")
        return 0

    width = max(len(a.id) for a in actions)
    for a in actions:
        keys = ", ".join(a.keys) if a.keys else "-"
        print(f"{a.id:<{width}}  {a.name:<28} {a.category:<14} keys: {keys}")
    print(f"\n{len(actions)} action(s)")
    return 0


def cmd_action_show(args: argparse.Namespace) -> int:
    registry = _load()
    action = registry.actions.get(args.action_id)
    if action is None:
        print(f"ACTION_NOT_FOUND: no action '{args.action_id}'", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(action.to_dict(), indent=2))
        return 0

    print(f"ID:           {action.id}")
    print(f"Name:         {action.name}")
    print(f"Description:  {action.description}")
    print(f"Category:     {action.category}")
    print(f"Risk:         {action.risk}")
    print(f"Confirmation: {action.confirmation}")
    print(f"Keywords:     {', '.join(action.keywords) if action.keywords else '-'}")
    print(f"Keys:         {', '.join(action.keys) if action.keys else '-'}")
    if action.primary_key:
        print(f"Primary key:  {action.primary_key}")
    print(f"Adapter:      {action.adapter or '-'}")
    if action.arguments:
        print(f"Arguments:    {json.dumps(action.arguments)}")
    if action.command:
        print(f"Command:      {' '.join(action.command)}")
    print(f"CLI:          {' '.join(action.cli) if action.cli else '-'}")
    print(f"Contexts:     {', '.join(action.contexts)}")
    print(f"Platforms:    {', '.join(action.platforms)}")
    print(f"Requires:     {', '.join(action.requires) if action.requires else '-'}")
    print(f"Discoverable: {action.discoverable}")
    print(f"Palette:      {action.palette}")
    print(f"AI accessible:{action.ai_accessible}")
    print(f"Voice:        {action.voice_accessible}")
    print(f"Source:       {action.source_file}")
    return 0


def cmd_action_search(args: argparse.Namespace) -> int:
    registry = _load()
    query = args.query.lower()
    terms = query.split()

    def score(a: Action) -> int:
        s = 0
        if query in a.id.lower():
            s += 100
        if query in a.name.lower():
            s += 80
        if query in a.description.lower():
            s += 40
        for kw in a.keywords:
            if query in kw.lower():
                s += 30
        for t in terms:
            if t in a.id.lower():
                s += 10
        return s

    results = sorted(
        (a for a in registry.actions.values() if score(a) > 0),
        key=lambda a: (-score(a), a.id),
    )

    if args.json:
        print(json.dumps([a.to_dict() for a in results], indent=2))
        return 0

    if not results:
        print(f"No actions match '{args.query}'.")
        return 0

    for a in results:
        keys = ", ".join(a.keys) if a.keys else "-"
        print(f"{a.id:<40} {a.name:<28} keys: {keys}")
    print(f"\n{len(results)} match(es)")
    return 0


def cmd_action_run(args: argparse.Namespace) -> int:
    if getattr(args, "ai", False):
        from .ai.actions import run_action_as_ai

        result = run_action_as_ai(args.action_id, confirmed=args.confirmed)
    else:
        result = run_action(args.action_id)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result["success"] else 1

    if result["success"]:
        print(f"OK: {result['action']}")
        if "state" in result:
            print(json.dumps(result["state"]))
        return 0

    error = result.get("error", {})
    print(
        f"{error.get('code', 'ERROR')}: {error.get('message', 'unknown error')}",
        file=sys.stderr,
    )
    return 1


def cmd_registry_validate(args: argparse.Namespace) -> int:
    registry = _load()
    issues = validate_registry(registry)

    for issue in issues:
        _print_issue(issue)

    errors = sum(1 for i in issues if i.level == "ERROR")
    warnings = sum(1 for i in issues if i.level == "WARNING")
    infos = sum(1 for i in issues if i.level == "INFO")
    print(
        f"\n{len(registry.actions)} action(s), "
        f"{errors} error(s), {warnings} warning(s), {infos} info"
    )

    if errors:
        print("Validation FAILED — do not generate configuration.", file=sys.stderr)
        return 1
    print("Validation passed.")
    return 0


def cmd_registry_build(args: argparse.Namespace) -> int:
    """Generate the Omivoid-owned Niri bindings fragment (docs/10 §14)."""
    registry = _load()
    issues = validate_registry(registry)
    errors = [i for i in issues if i.level == "ERROR"]
    if errors:
        for issue in errors:
            _print_issue(issue)
        print(
            "Build aborted: registry validation failed — do not generate configuration.",
            file=sys.stderr,
        )
        return 1

    ok, message = build_fragment(
        registry,
        output=args.output,
        dry_run=args.dry_run,
    )
    if not ok:
        print(message, file=sys.stderr)
        return 1
    print(message)
    return 0


def cmd_help(args: argparse.Namespace) -> int:
    """Registry-derived help data for the Super+K explorer (docs/10 §15)."""
    registry = _load()
    help_data = build_help_data(registry)

    if getattr(args, "json", False):
        print(json.dumps(help_data, indent=2))
        return 0

    print(format_help_text(help_data))
    return 0


def cmd_help_search(args: argparse.Namespace) -> int:
    """Search the registry-derived help data (docs/02 §11)."""
    registry = _load()
    help_data = build_help_data(registry)
    results = search_help_data(help_data, args.query)

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    if not results:
        print(f"No help entries match '{args.query}'.")
        return 0

    for entry in results:
        binding = entry["binding"] or "-"
        print(f"{entry['name']:<28} {binding:<18} {entry['id']}")
    print(f"\n{len(results)} match(es)")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Universal action search backend (docs/10 §16)."""
    registry = _load()
    results = search_actions(registry, args.query, palette_only=args.palette)

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    if not results:
        print(f"No actions match '{args.query}'.")
        return 0

    for entry in results:
        binding = entry["binding"] or "-"
        print(f"{entry['id']:<40} {entry['name']:<28} {binding}")
    print(f"\n{len(results)} match(es)")
    return 0


def cmd_ai_provider_status(args: argparse.Namespace) -> int:
    """Show provider availability (docs/ai/10 §7)."""
    from .ai import provider_status

    st = provider_status(args.provider)
    if args.json:
        print(json.dumps(st, indent=2))
        return 0

    print(f"Provider: {st['provider']}")
    print(f"State:    {st['state']}")
    if st.get("detail"):
        print(f"Detail:   {st['detail']}")
    return 0 if st["state"] == "available" else 1


def cmd_ai_provider_list(args: argparse.Namespace) -> int:
    """List all registered providers with status."""
    from .ai import list_providers

    statuses = list_providers()
    if args.json:
        print(json.dumps(statuses, indent=2))
        return 0

    for st in statuses:
        print(f"{st['provider']:<12} {st['state']:<14} {st.get('detail', '')}")
    return 0


def cmd_ai_ask(args: argparse.Namespace) -> int:
    """Ask the default (or named) AI provider (docs/ai/10 §10)."""
    from .ai import ask

    context = None
    if getattr(args, "clipboard", False):
        from .ai.context import collect_clipboard

        collected = collect_clipboard()
        if not collected["success"]:
            error = collected["error"]
            print(
                f"{error.get('code', 'ERROR')}: {error.get('message', 'unknown error')}",
                file=sys.stderr,
            )
            return 1
        context = [collected["context"]]

    result = ask(args.prompt, provider=args.provider, timeout=args.timeout,
                 context=context)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result["success"] else 1

    if result["success"]:
        print(result["response"])
        return 0

    error = result.get("error", {})
    print(
        f"{error.get('code', 'ERROR')}: {error.get('message', 'unknown error')}",
        file=sys.stderr,
    )
    return 1


def cmd_ai_capabilities(args: argparse.Namespace) -> int:
    """List AI-accessible capabilities (docs/ai/04 §26, docs/ai/10 §15–16)."""
    from .ai import capabilities

    caps = capabilities()
    if args.json:
        print(json.dumps(caps, indent=2))
        return 0

    for cap in caps:
        print(f"{cap['id']:<28} {cap['name']}")
    print(f"\n{len(caps)} capability/capabilities")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omivoid",
        description="Omivoid desktop CLI — action registry and execution.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # action
    action_p = sub.add_parser("action", help="action registry operations")
    action_sub = action_p.add_subparsers(dest="action_command", required=True)

    list_p = action_sub.add_parser("list", help="list actions")
    list_p.add_argument("--category", help="filter by category")
    list_p.add_argument("--json", action="store_true", help="JSON output")
    list_p.set_defaults(func=cmd_action_list)

    show_p = action_sub.add_parser("show", help="show action details")
    show_p.add_argument("action_id")
    show_p.add_argument("--json", action="store_true", help="JSON output")
    show_p.set_defaults(func=cmd_action_show)

    search_p = action_sub.add_parser("search", help="search actions")
    search_p.add_argument("query")
    search_p.add_argument("--json", action="store_true", help="JSON output")
    search_p.set_defaults(func=cmd_action_search)

    run_p = action_sub.add_parser("run", help="run an action")
    run_p.add_argument("action_id")
    run_p.add_argument("--json", action="store_true", help="JSON output")
    run_p.add_argument(
        "--ai",
        action="store_true",
        help="evaluate as an AI request (policy enforcement, docs/ai/09)",
    )
    run_p.add_argument(
        "--confirmed",
        action="store_true",
        help="user approved a confirmation-required AI action",
    )
    run_p.set_defaults(func=cmd_action_run)

    # registry
    reg_p = sub.add_parser("registry", help="registry operations")
    reg_sub = reg_p.add_subparsers(dest="registry_command", required=True)

    validate_p = reg_sub.add_parser("validate", help="validate the registry")
    validate_p.set_defaults(func=cmd_registry_validate)

    build_p = reg_sub.add_parser(
        "build", help="generate the Niri bindings fragment"
    )
    build_p.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT),
        help="output path for the generated fragment",
    )
    build_p.add_argument(
        "--dry-run",
        action="store_true",
        help="print the fragment without writing it",
    )
    build_p.set_defaults(func=cmd_registry_build)

    # help
    help_p = sub.add_parser("help", help="registry-derived help data (Super+K)")
    help_p.add_argument("--json", action="store_true", help="JSON output")
    help_p.set_defaults(func=cmd_help)
    help_sub = help_p.add_subparsers(dest="help_command")

    help_list_p = help_sub.add_parser("list", help="list all help entries")
    help_list_p.add_argument("--json", action="store_true", help="JSON output")
    help_list_p.set_defaults(func=cmd_help)

    help_search_p = help_sub.add_parser("search", help="search help entries")
    help_search_p.add_argument("query")
    help_search_p.add_argument("--json", action="store_true", help="JSON output")
    help_search_p.set_defaults(func=cmd_help_search)

    # search
    search_p = sub.add_parser("search", help="universal action search (Super+Space)")
    search_p.add_argument("query")
    search_p.add_argument("--palette", action="store_true", help="palette-eligible actions only")
    search_p.add_argument("--json", action="store_true", help="JSON output")
    search_p.set_defaults(func=cmd_search)

    # ai
    ai_p = sub.add_parser("ai", help="AI provider operations")
    ai_sub = ai_p.add_subparsers(dest="ai_command", required=True)

    provider_p = ai_sub.add_parser("provider", help="AI provider operations")
    provider_sub = provider_p.add_subparsers(dest="provider_command", required=True)

    status_p = provider_sub.add_parser("status", help="show provider status")
    status_p.add_argument("provider")
    status_p.add_argument("--json", action="store_true", help="JSON output")
    status_p.set_defaults(func=cmd_ai_provider_status)

    list_p = provider_sub.add_parser("list", help="list providers")
    list_p.add_argument("--json", action="store_true", help="JSON output")
    list_p.set_defaults(func=cmd_ai_provider_list)

    ask_p = ai_sub.add_parser("ask", help="ask the default AI provider")
    ask_p.add_argument("prompt")
    ask_p.add_argument("--provider", help="provider name (default: configured)")
    ask_p.add_argument("--timeout", type=float, default=None, help="timeout in seconds")
    ask_p.add_argument(
        "--clipboard",
        action="store_true",
        help="attach the current clipboard as context (AI-22)",
    )
    ask_p.add_argument("--json", action="store_true", help="JSON output")
    ask_p.set_defaults(func=cmd_ai_ask)

    caps_p = ai_sub.add_parser("capabilities", help="list AI-accessible capabilities")
    caps_p.add_argument("--json", action="store_true", help="JSON output")
    caps_p.set_defaults(func=cmd_ai_capabilities)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())