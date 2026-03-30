from __future__ import annotations

from ..types import ClaudeAgent, ClaudePlugin, CodexAgentFile, CodexBundle
from .content import normalize_name, sanitize_description, transform_content_for_codex

RESERVED_CODEX_AGENT_NAMES = {"default", "worker", "explorer"}


def convert_claude_to_codex(plugin: ClaudePlugin) -> CodexBundle:
    agent_targets = _build_agent_targets(plugin.agents)
    agents = [
        _convert_agent(
            agent,
            agent_targets[normalize_name(agent.name)],
            agent_targets,
            plugin.mcp_servers,
        )
        for agent in plugin.agents
    ]
    return CodexBundle(agents=agents)


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
    targets: dict[str, str],
    mcp_servers,
) -> CodexAgentFile:
    description = _codex_description(
        agent.description or f"Converted from Claude agent {agent.name}"
    )

    body = transform_content_for_codex(
        agent.body.strip(),
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


def _codex_description(value: str) -> str:
    shortened = value.split("Examples:", 1)[0]
    shortened = shortened.split("<example>", 1)[0]
    return sanitize_description(shortened, max_length=240)
