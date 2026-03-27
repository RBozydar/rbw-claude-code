from __future__ import annotations

import json
import os

from ..converters.content import transform_content_for_pi
from ..types import PiBundle
from .files import (
    backup_file,
    copy_skill_dir,
    ensure_dir,
    path_exists,
    read_text,
    sanitize_path_name,
    write_text,
)

PI_AGENTS_BLOCK_START = "<!-- BEGIN COMPOUND PI TOOL MAP -->"
PI_AGENTS_BLOCK_END = "<!-- END COMPOUND PI TOOL MAP -->"

PI_AGENTS_BLOCK_BODY = """\
## Compound Engineering (Pi compatibility)

This block is managed by the convert tool.

Compatibility notes:
- Claude Task(agent, args) maps to the subagent extension tool
- For parallel agent runs, batch multiple subagent calls with multi_tool_use.parallel
- AskUserQuestion maps to the ask_user_question extension tool
- MCP access uses MCPorter via mcporter_list and mcporter_call extension tools
- MCPorter config path: .pi/compound-engineering/mcporter.json (project) or ~/.pi/agent/compound-engineering/mcporter.json (global)"""


def write_pi_bundle(output_root: str, bundle: PiBundle) -> None:
    paths = _resolve_pi_paths(output_root)

    ensure_dir(paths["skills_dir"])
    ensure_dir(paths["prompts_dir"])
    ensure_dir(paths["extensions_dir"])

    for prompt in bundle.prompts:
        write_text(
            os.path.join(paths["prompts_dir"], f"{sanitize_path_name(prompt.name)}.md"),
            prompt.content + "\n",
        )

    for skill in bundle.skill_dirs:
        copy_skill_dir(
            skill.source_dir,
            os.path.join(paths["skills_dir"], sanitize_path_name(skill.name)),
            transform_content_for_pi,
        )

    for skill in bundle.generated_skills:
        write_text(
            os.path.join(
                paths["skills_dir"], sanitize_path_name(skill.name), "SKILL.md"
            ),
            skill.content + "\n",
        )

    for extension in bundle.extensions:
        write_text(
            os.path.join(paths["extensions_dir"], extension.name),
            extension.content + "\n",
        )

    if bundle.mcporter_config:
        bp = backup_file(paths["mcporter_config_path"])
        if bp:
            print(f"Backed up existing MCPorter config to {bp}")
        _write_mcporter_json(paths["mcporter_config_path"], bundle.mcporter_config)

    _ensure_pi_agents_block(paths["agents_path"])


def _resolve_pi_paths(output_root: str) -> dict[str, str]:
    base = os.path.basename(output_root)

    if base in ("agent", ".pi"):
        return {
            "skills_dir": os.path.join(output_root, "skills"),
            "prompts_dir": os.path.join(output_root, "prompts"),
            "extensions_dir": os.path.join(output_root, "extensions"),
            "mcporter_config_path": os.path.join(
                output_root, "compound-engineering", "mcporter.json"
            ),
            "agents_path": os.path.join(output_root, "AGENTS.md"),
        }

    return {
        "skills_dir": os.path.join(output_root, ".pi", "skills"),
        "prompts_dir": os.path.join(output_root, ".pi", "prompts"),
        "extensions_dir": os.path.join(output_root, ".pi", "extensions"),
        "mcporter_config_path": os.path.join(
            output_root, ".pi", "compound-engineering", "mcporter.json"
        ),
        "agents_path": os.path.join(output_root, "AGENTS.md"),
    }


def _ensure_pi_agents_block(file_path: str) -> None:
    block = _build_pi_agents_block()

    if not path_exists(file_path):
        write_text(file_path, block + "\n")
        return

    existing = read_text(file_path)
    updated = _upsert_block(existing, block)
    if updated != existing:
        write_text(file_path, updated)


def _build_pi_agents_block() -> str:
    return "\n".join(
        [PI_AGENTS_BLOCK_START, PI_AGENTS_BLOCK_BODY.strip(), PI_AGENTS_BLOCK_END]
    )


def _upsert_block(existing: str, block: str) -> str:
    start_index = existing.find(PI_AGENTS_BLOCK_START)
    end_index = existing.find(PI_AGENTS_BLOCK_END)

    if start_index != -1 and end_index != -1 and end_index > start_index:
        before = existing[:start_index].rstrip()
        after = existing[end_index + len(PI_AGENTS_BLOCK_END) :].lstrip()
        parts = [p for p in [before, block, after] if p]
        return "\n\n".join(parts) + "\n"

    if not existing.strip():
        return block + "\n"

    return existing.rstrip() + "\n\n" + block + "\n"


def _write_mcporter_json(file_path: str, config) -> None:
    ensure_dir(os.path.dirname(file_path))
    data = {"mcpServers": {}}
    for name, server in config.mcp_servers.items():
        entry: dict = {}
        if server.command:
            entry["command"] = server.command
        if server.args:
            entry["args"] = server.args
        if server.env:
            entry["env"] = server.env
        if server.base_url:
            entry["baseUrl"] = server.base_url
        if server.headers:
            entry["headers"] = server.headers
        data["mcpServers"][name] = entry

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
