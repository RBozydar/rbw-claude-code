from __future__ import annotations

from ..types import (
    ClaudeAgent,
    ClaudeCommand,
    ClaudePlugin,
    CodexAgentFile,
    CodexBundle,
    CodexPromptFile,
)
from .content import normalize_name, sanitize_description, transform_content_for_codex

RESERVED_CODEX_AGENT_NAMES = {"default", "worker", "explorer"}


def convert_claude_to_codex(plugin: ClaudePlugin) -> CodexBundle:
    prompt_targets = _build_prompt_targets(plugin.commands)
    agent_targets = _build_agent_targets(plugin.agents)
    prompts = [
        _convert_prompt(command, prompt_targets, agent_targets)
        for command in plugin.commands
        if not command.disable_model_invocation
    ]
    agents = [
        _convert_agent(
            agent,
            agent_targets[normalize_name(agent.name)],
            prompt_targets,
            agent_targets,
            plugin.mcp_servers,
        )
        for agent in plugin.agents
    ]
    return CodexBundle(agents=agents, prompts=prompts)


def _build_prompt_targets(commands: list[ClaudeCommand]) -> dict[str, str]:
    result: dict[str, str] = {}
    original_names: dict[str, str] = {}

    for command in commands:
        if command.disable_model_invocation:
            continue
        normalized = normalize_name(command.name)
        if normalized in result:
            raise ValueError(
                f'Claude commands "{original_names[normalized]}" and "{command.name}" '
                f'normalize to the same Codex prompt name "{normalized}"'
            )
        result[normalized] = normalized
        original_names[normalized] = command.name

    return result


def _build_agent_targets(agents: list[ClaudeAgent]) -> dict[str, str]:
    result: dict[str, str] = {}
    original_names: dict[str, str] = {}

    for agent in agents:
        normalized = normalize_name(agent.name)
        if normalized in RESERVED_CODEX_AGENT_NAMES:
            raise ValueError(
                f'Claude agent "{agent.name}" normalizes to reserved Codex agent '
                f'name "{normalized}"'
            )
        if normalized in result:
            raise ValueError(
                f'Claude agents "{original_names[normalized]}" and "{agent.name}" '
                f'normalize to the same Codex agent name "{normalized}"'
            )
        result[normalized] = normalized
        original_names[normalized] = agent.name

    return result


def _convert_agent(
    agent: ClaudeAgent,
    agent_name: str,
    prompt_targets: dict[str, str],
    targets: dict[str, str],
    mcp_servers,
) -> CodexAgentFile:
    description = _codex_description(
        agent.description or f"Converted from Claude agent {agent.name}"
    )

    body = transform_content_for_codex(
        agent.body.strip(),
        prompt_targets=prompt_targets,
        agent_targets=targets,
        unknown_slash_behavior="preserve",
    )
    if agent.capabilities:
        capabilities = "\n".join(f"- {capability}" for capability in agent.capabilities)
        body = f"## Capabilities\n{capabilities}\n\n{body}".strip()
    if not body:
        body = f"Instructions converted from the {agent.name} agent."

    return CodexAgentFile(
        name=agent_name,
        description=description,
        developer_instructions=body,
        source_path=agent.source_path,
        mcp_servers=mcp_servers,
    )


def _convert_prompt(
    command: ClaudeCommand,
    prompt_targets: dict[str, str],
    agent_targets: dict[str, str],
) -> CodexPromptFile:
    sections: list[str] = []
    if command.allowed_tools:
        allowed_tools = "\n".join(f"- {tool}" for tool in command.allowed_tools)
        sections.append(f"## Allowed tools\n{allowed_tools}")

    body = transform_content_for_codex(
        command.body.strip(),
        prompt_targets=prompt_targets,
        agent_targets=agent_targets,
        unknown_slash_behavior="preserve",
    )
    if body:
        sections.append(body)

    developer_text = "\n\n".join(section for section in sections if section.strip())
    if not developer_text:
        developer_text = f"Instructions converted from the {command.name} command."

    return CodexPromptFile(
        name=prompt_targets[normalize_name(command.name)],
        source_path=command.source_path,
        description=_codex_description(command.description)
        if command.description
        else None,
        argument_hint=_stringify_argument_hint(command.argument_hint),
        body=developer_text,
    )


def _codex_description(value: str) -> str:
    shortened = value.split("Examples:", 1)[0]
    shortened = shortened.split("<example>", 1)[0]
    return sanitize_description(shortened, max_length=240)


def _stringify_argument_hint(value: str | list | dict | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [
            item
            for item in (_stringify_argument_hint(entry) for entry in value)
            if item
        ]
        return ", ".join(parts) if parts else None
    if isinstance(value, dict):
        parts = [f"{key}: {value[key]}" for key in sorted(value)]
        return ", ".join(parts) if parts else None
    return str(value)
