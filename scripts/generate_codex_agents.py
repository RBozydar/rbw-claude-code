#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.convert.converters.codex import convert_claude_to_codex
from src.convert.parser import load_claude_plugin
from src.convert.types import CodexAgentFile, CodexBundle, CodexPromptFile
from src.convert.writers.codex import (
    MANAGED_AGENT_HEADER_PREFIX,
    MANAGED_PROMPT_COMMENT_PREFIX,
    write_codex_bundle,
)

AGENTS_DIR = REPO_ROOT / ".codex" / "agents"
AGENTS_MANIFEST_PATH = AGENTS_DIR / ".generated-files.txt"
PROMPTS_DIR = REPO_ROOT / ".codex" / "prompts"
PROMPTS_MANIFEST_PATH = PROMPTS_DIR / ".generated-files.txt"


def main() -> None:
    bundle = _collect_bundle()
    expected_agent_files = {f"{agent.name}.toml" for agent in bundle.agents}
    expected_prompt_files = {f"{prompt.name}.md" for prompt in bundle.prompts}

    _remove_stale_generated_files(
        manifest_path=AGENTS_MANIFEST_PATH,
        generated_dir=AGENTS_DIR,
        expected_files=expected_agent_files,
        managed_prefix=MANAGED_AGENT_HEADER_PREFIX,
        label="agent",
    )
    _remove_stale_generated_files(
        manifest_path=PROMPTS_MANIFEST_PATH,
        generated_dir=PROMPTS_DIR,
        expected_files=expected_prompt_files,
        managed_prefix=MANAGED_PROMPT_COMMENT_PREFIX,
        label="prompt",
    )

    write_codex_bundle(str(REPO_ROOT), bundle)
    _write_manifest(AGENTS_DIR, AGENTS_MANIFEST_PATH, expected_agent_files)
    _write_manifest(PROMPTS_DIR, PROMPTS_MANIFEST_PATH, expected_prompt_files)
    print(
        "Generated "
        f"{len(bundle.agents)} Codex custom agents in {AGENTS_DIR} "
        f"and {len(bundle.prompts)} custom prompts in {PROMPTS_DIR}"
    )


def _collect_bundle() -> CodexBundle:
    agents: list[CodexAgentFile] = []
    prompts: list[CodexPromptFile] = []
    seen_agents: dict[str, str] = {}
    seen_prompts: dict[str, str] = {}

    for manifest_path in sorted(REPO_ROOT.glob("plugins/**/.claude-plugin/plugin.json")):
        plugin_root = manifest_path.parent.parent
        plugin = load_claude_plugin(str(plugin_root))
        bundle = convert_claude_to_codex(plugin)
        for agent in bundle.agents:
            if agent.name in seen_agents:
                raise ValueError(
                    f'Codex agent collision for "{agent.name}": '
                    f"{seen_agents[agent.name]} and {agent.source_path}"
                )
            seen_agents[agent.name] = agent.source_path
            agents.append(agent)
        for prompt in bundle.prompts:
            if prompt.name in seen_prompts:
                raise ValueError(
                    f'Codex prompt collision for "{prompt.name}": '
                    f"{seen_prompts[prompt.name]} and {prompt.source_path}"
                )
            seen_prompts[prompt.name] = prompt.source_path
            prompts.append(prompt)

    return CodexBundle(agents=agents, prompts=prompts)


def _remove_stale_generated_files(
    *,
    manifest_path: Path,
    generated_dir: Path,
    expected_files: set[str],
    managed_prefix: str,
    label: str,
) -> None:
    previous_files: set[str] = set()
    if manifest_path.exists():
        previous_files = {
            line.strip()
            for line in manifest_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }

    for stale_name in sorted(previous_files - expected_files):
        stale_path = generated_dir / stale_name
        if not stale_path.exists():
            continue
        if managed_prefix not in stale_path.read_text(encoding="utf-8"):
            raise ValueError(
                f"Refusing to remove unmanaged Codex {label} file: {stale_path}"
            )
        stale_path.unlink()


def _write_manifest(output_dir: Path, manifest_path: Path, file_names: set[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        "".join(f"{name}\n" for name in sorted(file_names)),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
