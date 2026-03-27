"""Content transformation utilities for Pi conversions."""

from __future__ import annotations

import re

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
