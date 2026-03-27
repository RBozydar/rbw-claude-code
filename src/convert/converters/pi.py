from __future__ import annotations

import re

from ..frontmatter import format_frontmatter
from ..types import (
    ClaudeAgent,
    ClaudeCommand,
    ClaudeMcpServer,
    ClaudePlugin,
    PiBundle,
    PiExtensionFile,
    PiGeneratedSkill,
    PiMcporterConfig,
    PiMcporterServer,
    PiPrompt,
    PiSkillDir,
)
from .content import (
    normalize_name,
    sanitize_description,
    transform_content_for_pi,
    unique_name,
)

PI_COMPAT_EXTENSION_SOURCE = """\
// Pi compatibility extension for compound-engineering plugin conversions.
// Provides subagent invocation, MCPorter integration, and user interaction tools.
// See: https://github.com/EveryInc/compound-engineering-plugin
"""


def convert_claude_to_pi(plugin: ClaudePlugin) -> PiBundle:
    prompt_names: set[str] = set()
    used_skill_names: set[str] = {normalize_name(s.name) for s in plugin.skills}

    prompts = [
        _convert_prompt(c, prompt_names)
        for c in plugin.commands
        if not c.disable_model_invocation
    ]

    generated_skills = [_convert_agent(a, used_skill_names) for a in plugin.agents]

    extensions = [
        PiExtensionFile(
            name="compound-engineering-compat.ts",
            content=PI_COMPAT_EXTENSION_SOURCE,
        )
    ]

    return PiBundle(
        prompts=prompts,
        skill_dirs=[
            PiSkillDir(name=s.name, source_dir=s.source_dir) for s in plugin.skills
        ],
        generated_skills=generated_skills,
        extensions=extensions,
        mcporter_config=(
            _convert_mcp_to_mcporter(plugin.mcp_servers) if plugin.mcp_servers else None
        ),
    )


def _convert_prompt(command: ClaudeCommand, used_names: set[str]) -> PiPrompt:
    name = unique_name(normalize_name(command.name), used_names)
    frontmatter = {
        "description": command.description,
        "argument-hint": command.argument_hint,
    }

    body = transform_content_for_pi(command.body)
    body = _append_compatibility_note_if_needed(body)

    return PiPrompt(
        name=name,
        content=format_frontmatter(frontmatter, body.strip()),
    )


def _convert_agent(agent: ClaudeAgent, used_names: set[str]) -> PiGeneratedSkill:
    name = unique_name(normalize_name(agent.name), used_names)
    description = sanitize_description(
        agent.description or f"Converted from Claude agent {agent.name}"
    )

    frontmatter = {"name": name, "description": description}

    sections: list[str] = []
    if agent.capabilities:
        capabilities = "\n".join(f"- {c}" for c in agent.capabilities)
        sections.append(f"## Capabilities\n{capabilities}")

    body_text = (
        agent.body.strip()
        if agent.body.strip()
        else f"Instructions converted from the {agent.name} agent."
    )
    sections.append(body_text)

    body = "\n\n".join(sections)

    return PiGeneratedSkill(
        name=name,
        content=format_frontmatter(frontmatter, body),
    )


def _append_compatibility_note_if_needed(body: str) -> str:
    if not re.search(r"\bmcp\b", body, re.IGNORECASE):
        return body

    note = "\n".join(
        [
            "",
            "## Pi + MCPorter note",
            "For MCP access in Pi, use MCPorter via the generated tools:",
            "- `mcporter_list` to inspect available MCP tools",
            "- `mcporter_call` to invoke a tool",
            "",
        ]
    )
    return body + note


def _convert_mcp_to_mcporter(
    servers: dict[str, ClaudeMcpServer],
) -> PiMcporterConfig:
    mcp_servers: dict[str, PiMcporterServer] = {}

    for name, server in servers.items():
        if server.command:
            mcp_servers[name] = PiMcporterServer(
                command=server.command,
                args=server.args,
                env=server.env,
                headers=server.headers,
            )
            continue
        if server.url:
            mcp_servers[name] = PiMcporterServer(
                base_url=server.url,
                headers=server.headers,
            )

    return PiMcporterConfig(mcp_servers=mcp_servers)
