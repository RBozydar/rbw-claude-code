"""Content transformation utilities for Pi conversions."""

from __future__ import annotations

import re
from typing import Literal

# Unix paths that should never be rewritten as slash commands
_UNIX_PATH_PREFIXES = {"dev", "tmp", "etc", "usr", "var", "bin", "home"}


def normalize_name(value: str) -> str:
    """Normalize a name to lowercase-kebab form."""
    trimmed = value.strip()
    if not trimmed:
        return "item"
    normalized = trimmed.lower()
    normalized = re.sub(r"[\\/]+", "-", normalized)
    normalized = re.sub(r"[:\s]+", "-", normalized)
    normalized = re.sub(r"[^a-z0-9_-]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized)
    normalized = normalized.strip("-")
    return normalized or "item"


def unique_name(base: str, used: set[str]) -> str:
    if base not in used:
        used.add(base)
        return base
    index = 2
    while f"{base}-{index}" in used:
        index += 1
    name = f"{base}-{index}"
    used.add(name)
    return name


def sanitize_description(value: str, max_length: int = 1024) -> str:
    normalized = re.sub(r"\s+", " ", value).strip()
    if len(normalized) <= max_length:
        return normalized
    ellipsis = "..."
    return normalized[: max(0, max_length - len(ellipsis))].rstrip() + ellipsis


# --- Pi content transforms ---


def transform_content_for_codex(
    body: str,
    *,
    prompt_targets: dict[str, str] | None = None,
    skill_targets: dict[str, str] | None = None,
    agent_targets: dict[str, str] | None = None,
    unknown_slash_behavior: Literal["prompt", "preserve"] = "prompt",
) -> str:
    """Transform Claude Code content to Codex-compatible content."""
    result = body
    prompt_targets = prompt_targets or {}
    skill_targets = skill_targets or {}
    agent_targets = agent_targets or {}

    def _render_task(prefix: str, agent_name: str, args: str) -> str:
        final_segment = agent_name.split(":")[-1] if ":" in agent_name else agent_name
        normalized = normalize_name(final_segment)
        skill_name = agent_targets.get(normalized, normalized)
        trimmed_args = re.sub(r"\s+", " ", args.strip())
        if trimmed_args:
            return f"{prefix}Use the ${skill_name} skill to: {trimmed_args}"
        return f"{prefix}Use the ${skill_name} skill"

    def _replace_task(m: re.Match) -> str:
        return _render_task(m.group(1), m.group(2), m.group(3))

    result = re.sub(
        r"^(\s*-?\s*)Task\s+([a-z][a-z0-9:-]*)\(([^)]*)\)",
        _replace_task,
        result,
        flags=re.MULTILINE,
    )
    result = re.sub(
        r"\bTask\s+([a-z][a-z0-9:-]*)\(([^)]*)\)",
        lambda m: _render_task("", m.group(1), m.group(2)),
        result,
    )

    def _replace_slash(m: re.Match) -> str:
        command_name = m.group(1)
        if "/" in command_name:
            return m.group(0)
        if command_name in _UNIX_PATH_PREFIXES:
            return m.group(0)

        normalized_name = normalize_name(command_name)
        if normalized_name in prompt_targets:
            return f"/prompts:{prompt_targets[normalized_name]}"
        if normalized_name in skill_targets:
            return f"the {skill_targets[normalized_name]} skill"
        if unknown_slash_behavior == "preserve":
            return m.group(0)
        return f"/prompts:{normalized_name}"

    result = re.sub(
        r"(?<![:\w])/([a-z][a-z0-9_:-]*?)(?=[\s,.\"')\]}`]|$)",
        _replace_slash,
        result,
        flags=re.IGNORECASE,
    )

    result = result.replace("~/.claude/", "~/.codex/")
    result = result.replace(".claude/", ".codex/")

    def _replace_agent_ref(m: re.Match) -> str:
        normalized = normalize_name(m.group(1))
        skill_name = agent_targets.get(normalized, normalized)
        return f"${skill_name} skill"

    result = re.sub(
        r"@([a-z][a-z0-9-]*-(?:agent|reviewer|researcher|analyst|specialist|oracle|sentinel|guardian|strategist))",
        _replace_agent_ref,
        result,
        flags=re.IGNORECASE,
    )

    return result


# --- Pi content transforms ---


def transform_content_for_pi(body: str) -> str:
    """Transform Claude Code content to Pi-compatible content."""
    result = body

    # Task agent-name(args) -> Run subagent with agent="name" and task="args"
    def _replace_task(m: re.Match) -> str:
        prefix = m.group(1)
        agent_name = m.group(2)
        args = m.group(3)
        final_segment = agent_name.split(":")[-1] if ":" in agent_name else agent_name
        skill_name = normalize_name(final_segment)
        trimmed_args = re.sub(r"\s+", " ", args.strip())
        if trimmed_args:
            return f'{prefix}Run subagent with agent="{skill_name}" and task="{trimmed_args}".'
        return f'{prefix}Run subagent with agent="{skill_name}".'

    result = re.sub(
        r"^(\s*-?\s*)Task\s+([a-z][a-z0-9:-]*)\(([^)]*)\)",
        _replace_task,
        result,
        flags=re.MULTILINE,
    )

    # Claude-specific tool references
    result = re.sub(r"\bAskUserQuestion\b", "ask_user_question", result)
    result = re.sub(
        r"\bTodoWrite\b", "file-based todos (todos/ + /skill:todo-create)", result
    )
    result = re.sub(
        r"\bTodoRead\b", "file-based todos (todos/ + /skill:todo-create)", result
    )

    # Slash commands
    def _replace_slash(m: re.Match) -> str:
        command_name = m.group(1)
        if "/" in command_name:
            return m.group(0)
        if command_name in _UNIX_PATH_PREFIXES:
            return m.group(0)
        if command_name.startswith("skill:"):
            skill_name = command_name[len("skill:") :]
            return f"/skill:{normalize_name(skill_name)}"
        without_prefix = (
            command_name[len("prompts:") :]
            if command_name.startswith("prompts:")
            else command_name
        )
        return f"/{normalize_name(without_prefix)}"

    result = re.sub(
        r"(?<![:\w])/([a-z][a-z0-9_:-]*?)(?=[\s,.\"')\]}`]|$)",
        _replace_slash,
        result,
        flags=re.IGNORECASE,
    )

    return result
