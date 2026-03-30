"""CLI entry point for converting Claude Code plugins to OpenCode and Pi formats."""

from __future__ import annotations

import argparse
import os
import sys

from .converters.codex import convert_claude_to_codex
from .converters.opencode import convert_claude_to_opencode
from .converters.pi import convert_claude_to_pi
from .parser import load_claude_plugin
from .writers.codex import write_codex_bundle
from .writers.opencode import write_opencode_bundle
from .writers.pi import write_pi_bundle

TARGETS = ("codex", "opencode", "pi")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="convert",
        description="Convert a Claude Code plugin into Codex, OpenCode, or Pi format",
    )
    parser.add_argument(
        "source",
        help="Path to the Claude plugin directory",
    )
    parser.add_argument(
        "--to",
        default="opencode",
        dest="target",
        help=f"Target format: {' | '.join(TARGETS)} | all (default: opencode)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output directory (project root). Defaults to cwd.",
    )
    parser.add_argument(
        "--pi-home",
        default=None,
        help="Write Pi output to this Pi root (e.g. ~/.pi/agent or ./.pi)",
    )
    parser.add_argument(
        "--also",
        default=None,
        help="Comma-separated extra targets to generate (e.g. pi)",
    )
    parser.add_argument(
        "--permissions",
        default="broad",
        choices=("none", "broad", "from-commands"),
        help="Permission mapping mode (default: broad)",
    )
    parser.add_argument(
        "--agent-mode",
        default="subagent",
        choices=("primary", "subagent"),
        help="Default agent mode (default: subagent)",
    )
    parser.add_argument(
        "--infer-temperature",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Infer agent temperature from name/description (default: true)",
    )

    args = parser.parse_args(argv)

    plugin = load_claude_plugin(args.source)
    output_root = os.path.abspath(args.output) if args.output else os.getcwd()
    pi_home = _expand(args.pi_home) or os.path.join(
        os.path.expanduser("~"), ".pi", "agent"
    )

    target_name = args.target
    extra_targets = _parse_extra_targets(args.also)

    if target_name == "all":
        targets_to_run = list(TARGETS)
    else:
        if target_name not in TARGETS:
            print(f"Unknown target: {target_name}", file=sys.stderr)
            sys.exit(1)
        targets_to_run = [target_name] + [
            t for t in extra_targets if t not in (target_name,)
        ]

    for target in targets_to_run:
        if target not in TARGETS:
            print(f"Skipping unknown target: {target}")
            continue

        root = _resolve_target_output(target, output_root, pi_home)
        _run_conversion(
            target,
            plugin,
            root,
            permissions=args.permissions,
            agent_mode=args.agent_mode,
            infer_temperature=args.infer_temperature,
        )
        print(f"Converted {plugin.manifest.name} to {target} at {root}")


def _run_conversion(
    target: str,
    plugin,
    output_root: str,
    *,
    permissions: str,
    agent_mode: str,
    infer_temperature: bool,
) -> None:
    if target == "opencode":
        bundle = convert_claude_to_opencode(
            plugin,
            agent_mode=agent_mode,
            infer_temperature=infer_temperature,
            permissions=permissions,
        )
        write_opencode_bundle(output_root, bundle)
    elif target == "codex":
        bundle = convert_claude_to_codex(plugin)
        write_codex_bundle(output_root, bundle)
    elif target == "pi":
        bundle = convert_claude_to_pi(plugin)
        write_pi_bundle(output_root, bundle)


def _resolve_target_output(
    target: str,
    output_root: str,
    pi_home: str,
) -> str:
    if target == "pi":
        return pi_home
    return output_root


def _expand(value: str | None) -> str | None:
    if not value or not value.strip():
        return None
    return os.path.abspath(os.path.expanduser(value.strip()))


def _parse_extra_targets(value: str | None) -> list[str]:
    if not value:
        return []
    return [t.strip() for t in value.split(",") if t.strip()]


if __name__ == "__main__":
    main()
