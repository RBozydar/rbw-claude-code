from __future__ import annotations

from ..frontmatter import format_frontmatter
from ..types import (
    ClaudeAgent,
    ClaudeCommand,
    ClaudePlugin,
    CodexBundle,
    CodexGeneratedSkill,
    CodexInvocationTargets,
    CodexPrompt,
    SkillDir,
)
from .content import (
    normalize_name,
    sanitize_description,
    transform_content_for_codex,
    unique_name,
)


def convert_claude_to_codex(plugin: ClaudePlugin) -> CodexBundle:
    invocable_commands = [
        command for command in plugin.commands if not command.disable_model_invocation
    ]
    skill_dirs = [SkillDir(name=s.name, source_dir=s.source_dir) for s in plugin.skills]

    prompt_names: set[str] = set()
    used_skill_names: set[str] = {normalize_name(s.name) for s in plugin.skills}

    prompt_targets = _build_prompt_targets(invocable_commands, prompt_names)
    command_skill_targets = _build_generated_skill_targets(
        [command.name for command in invocable_commands],
        used_skill_names,
    )
    agent_targets = _build_generated_skill_targets(
        [agent.name for agent in plugin.agents],
        used_skill_names,
    )
    skill_targets = {normalize_name(skill.name): skill.name for skill in plugin.skills}

    invocation_targets = CodexInvocationTargets(
        prompt_targets=prompt_targets,
        skill_targets=skill_targets,
        agent_targets=agent_targets,
    )

    prompts = [
        _render_prompt(command, command_skill_targets[normalize_name(command.name)], invocation_targets)
        for command in invocable_commands
    ]
    generated_skills = [
        _convert_command_skill(
            command,
            command_skill_targets[normalize_name(command.name)],
            invocation_targets,
        )
        for command in invocable_commands
    ]
    generated_skills.extend(
        _convert_agent(
            agent,
            agent_targets[normalize_name(agent.name)],
            invocation_targets,
        )
        for agent in plugin.agents
    )

    return CodexBundle(
        prompts=prompts,
        skill_dirs=skill_dirs,
        generated_skills=generated_skills,
        invocation_targets=invocation_targets,
        mcp_servers=plugin.mcp_servers,
    )


def _build_prompt_targets(
    commands: list[ClaudeCommand], used_prompt_names: set[str]
) -> dict[str, str]:
    result: dict[str, str] = {}
    for command in commands:
        result[normalize_name(command.name)] = unique_name(
            normalize_name(command.name), used_prompt_names
        )
    return result


def _build_generated_skill_targets(
    names: list[str], used_skill_names: set[str]
) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in names:
        result[normalize_name(name)] = unique_name(normalize_name(name), used_skill_names)
    return result


def _convert_agent(
    agent: ClaudeAgent,
    skill_name: str,
    targets: CodexInvocationTargets,
) -> CodexGeneratedSkill:
    description = sanitize_description(
        agent.description or f"Converted from Claude agent {agent.name}"
    )
    frontmatter = {"name": skill_name, "description": description}

    body = transform_content_for_codex(
        agent.body.strip(),
        prompt_targets=targets.prompt_targets,
        skill_targets=targets.skill_targets,
        agent_targets=targets.agent_targets,
    )
    if agent.capabilities:
        capabilities = "\n".join(f"- {capability}" for capability in agent.capabilities)
        body = f"## Capabilities\n{capabilities}\n\n{body}".strip()
    if not body:
        body = f"Instructions converted from the {agent.name} agent."

    return CodexGeneratedSkill(name=skill_name, content=format_frontmatter(frontmatter, body))


def _convert_command_skill(
    command: ClaudeCommand,
    skill_name: str,
    targets: CodexInvocationTargets,
) -> CodexGeneratedSkill:
    frontmatter = {
        "name": skill_name,
        "description": sanitize_description(
            command.description or f"Converted from Claude command {command.name}"
        ),
    }

    sections: list[str] = []
    if command.argument_hint:
        sections.append(f"## Arguments\n{command.argument_hint}")
    if command.allowed_tools:
        allowed_tools = "\n".join(f"- {tool}" for tool in command.allowed_tools)
        sections.append(f"## Allowed tools\n{allowed_tools}")

    transformed_body = transform_content_for_codex(
        command.body.strip(),
        prompt_targets=targets.prompt_targets,
        skill_targets=targets.skill_targets,
        agent_targets=targets.agent_targets,
    )
    if transformed_body:
        sections.append(transformed_body)

    body = "\n\n".join(sections).strip() or command.body
    return CodexGeneratedSkill(name=skill_name, content=format_frontmatter(frontmatter, body))


def _render_prompt(
    command: ClaudeCommand,
    skill_name: str,
    targets: CodexInvocationTargets,
) -> CodexPrompt:
    frontmatter = {
        "description": command.description,
        "argument-hint": command.argument_hint,
    }
    instructions = (
        f"Use the ${skill_name} skill for this command and follow its instructions."
    )
    transformed_body = transform_content_for_codex(
        command.body.strip(),
        prompt_targets=targets.prompt_targets,
        skill_targets=targets.skill_targets,
        agent_targets=targets.agent_targets,
    )
    body = (
        f"{instructions}\n\n{transformed_body}".strip()
        if transformed_body
        else instructions
    )
    prompt_name = targets.prompt_targets[normalize_name(command.name)]
    return CodexPrompt(name=prompt_name, content=format_frontmatter(frontmatter, body))
