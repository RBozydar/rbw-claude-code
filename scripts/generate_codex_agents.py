#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.convert.converters.codex import convert_claude_to_codex
from src.convert.parser import load_claude_plugin
from src.convert.types import CodexAgentFile, CodexBundle
from src.convert.writers.codex import (
    MANAGED_AGENT_HEADER_PREFIX,
    write_codex_bundle,
)

GENERATED_DIR = REPO_ROOT / ".codex" / "agents"
MANIFEST_PATH = GENERATED_DIR / ".generated-files.txt"


def main() -> None:
    agents = _collect_agents()
    expected_files = {f"{agent.name}.toml" for agent in agents}
    _remove_stale_generated_agents(expected_files)
    write_codex_bundle(str(REPO_ROOT), CodexBundle(agents=agents))
    _write_manifest(expected_files)
    print(f"Generated {len(agents)} Codex custom agents in {GENERATED_DIR}")


def _collect_agents() -> list[CodexAgentFile]:
    collected: list[CodexAgentFile] = []
    seen: dict[str, str] = {}

    for manifest_path in sorted(REPO_ROOT.glob("plugins/**/.claude-plugin/plugin.json")):
        plugin_root = manifest_path.parent.parent
        plugin = load_claude_plugin(str(plugin_root))
        bundle = convert_claude_to_codex(plugin)
        for agent in bundle.agents:
            if agent.name in seen:
                raise ValueError(
                    f'Codex agent collision for "{agent.name}": '
                    f"{seen[agent.name]} and {agent.source_path}"
                )
            seen[agent.name] = agent.source_path
            collected.append(agent)

    return collected


def _remove_stale_generated_agents(expected_files: set[str]) -> None:
    previous_files: set[str] = set()
    if MANIFEST_PATH.exists():
        previous_files = {
            line.strip()
            for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }

    for stale_name in sorted(previous_files - expected_files):
        stale_path = GENERATED_DIR / stale_name
        if not stale_path.exists():
            continue
        if not stale_path.read_text(encoding="utf-8").startswith(
            MANAGED_AGENT_HEADER_PREFIX
        ):
            raise ValueError(
                f"Refusing to remove unmanaged Codex agent file: {stale_path}"
            )
        stale_path.unlink()


def _write_manifest(file_names: set[str]) -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        "".join(f"{name}\n" for name in sorted(file_names)),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
