from __future__ import annotations

import re
from typing import Literal

from ..frontmatter import format_frontmatter
from ..types import (
    ClaudeAgent,
    ClaudeCommand,
    ClaudeHooks,
    ClaudeMcpServer,
    ClaudePlugin,
    OpenCodeAgentFile,
    OpenCodeBundle,
    OpenCodeCommandFile,
    OpenCodeConfig,
    OpenCodeMcpServer,
    OpenCodePluginFile,
    SkillDir,
)

PermissionMode = Literal["none", "broad", "from-commands"]

TOOL_MAP: dict[str, str] = {
    "bash": "bash",
    "read": "read",
    "write": "write",
    "edit": "edit",
    "grep": "grep",
    "glob": "glob",
    "list": "list",
    "webfetch": "webfetch",
    "skill": "skill",
    "patch": "patch",
    "task": "task",
    "question": "question",
    "todowrite": "todowrite",
    "todoread": "todoread",
}

SOURCE_TOOLS = list(TOOL_MAP.values())

HOOK_EVENT_MAP: dict[str, dict] = {
    "PreToolUse": {"events": ["tool.execute.before"], "type": "tool"},
    "PostToolUse": {"events": ["tool.execute.after"], "type": "tool"},
    "PostToolUseFailure": {
        "events": ["tool.execute.after"],
        "type": "tool",
        "require_error": True,
        "note": "Claude PostToolUseFailure",
    },
    "SessionStart": {"events": ["session.created"], "type": "session"},
    "SessionEnd": {"events": ["session.deleted"], "type": "session"},
    "Stop": {"events": ["session.idle"], "type": "session"},
    "PreCompact": {
        "events": ["experimental.session.compacting"],
        "type": "session",
    },
    "PermissionRequest": {
        "events": ["permission.requested", "permission.replied"],
        "type": "permission",
        "note": "Claude PermissionRequest",
    },
    "UserPromptSubmit": {
        "events": ["message.created", "message.updated"],
        "type": "message",
        "note": "Claude UserPromptSubmit",
    },
    "Notification": {
        "events": ["message.updated"],
        "type": "message",
        "note": "Claude Notification",
    },
    "Setup": {
        "events": ["session.created"],
        "type": "session",
        "note": "Claude Setup",
    },
    "SubagentStart": {
        "events": ["message.updated"],
        "type": "message",
        "note": "Claude SubagentStart",
    },
    "SubagentStop": {
        "events": ["message.updated"],
        "type": "message",
        "note": "Claude SubagentStop",
    },
}

CLAUDE_FAMILY_ALIASES: dict[str, str] = {
    "haiku": "claude-haiku-4-5",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-6",
}


def convert_claude_to_opencode(
    plugin: ClaudePlugin,
    *,
    agent_mode: str = "subagent",
    infer_temperature: bool = True,
    permissions: PermissionMode = "broad",
) -> OpenCodeBundle:
    agent_files = [
        _convert_agent(agent, agent_mode, infer_temperature) for agent in plugin.agents
    ]
    cmd_files = _convert_commands(plugin.commands)
    mcp = _convert_mcp(plugin.mcp_servers) if plugin.mcp_servers else None
    plugins = [_convert_hooks(plugin.hooks)] if plugin.hooks else []

    config = OpenCodeConfig(
        schema="https://opencode.ai/config.json",
        mcp=mcp if mcp else None,
    )

    _apply_permissions(config, plugin.commands, permissions)

    return OpenCodeBundle(
        config=config,
        agents=agent_files,
        command_files=cmd_files,
        plugins=plugins,
        skill_dirs=[
            SkillDir(source_dir=s.source_dir, name=s.name) for s in plugin.skills
        ],
    )


def _convert_agent(
    agent: ClaudeAgent,
    agent_mode: str,
    infer_temp: bool,
) -> OpenCodeAgentFile:
    frontmatter: dict = {
        "description": agent.description,
        "mode": agent_mode,
    }

    if agent.model and agent.model != "inherit":
        frontmatter["model"] = _normalize_model(agent.model)

    if infer_temp:
        temperature = _infer_temperature(agent)
        if temperature is not None:
            frontmatter["temperature"] = temperature

    content = format_frontmatter(frontmatter, _rewrite_claude_paths(agent.body))
    return OpenCodeAgentFile(name=agent.name, content=content)


def _convert_commands(commands: list[ClaudeCommand]) -> list[OpenCodeCommandFile]:
    files: list[OpenCodeCommandFile] = []
    for command in commands:
        if command.disable_model_invocation:
            continue
        frontmatter: dict = {"description": command.description}
        if command.model and command.model != "inherit":
            frontmatter["model"] = _normalize_model(command.model)
        content = format_frontmatter(frontmatter, _rewrite_claude_paths(command.body))
        files.append(OpenCodeCommandFile(name=command.name, content=content))
    return files


def _convert_mcp(
    servers: dict[str, ClaudeMcpServer],
) -> dict[str, OpenCodeMcpServer]:
    result: dict[str, OpenCodeMcpServer] = {}
    for name, server in servers.items():
        if server.command:
            result[name] = OpenCodeMcpServer(
                type="local",
                command=[server.command, *(server.args or [])],
                environment=server.env,
                enabled=True,
            )
            continue
        if server.url:
            result[name] = OpenCodeMcpServer(
                type="remote",
                url=server.url,
                headers=server.headers,
                enabled=True,
            )
    return result


def _convert_hooks(hooks: ClaudeHooks) -> OpenCodePluginFile:
    handler_blocks: list[str] = []
    unmapped_events: list[str] = []

    for event_name, matchers in hooks.hooks.items():
        mapping = HOOK_EVENT_MAP.get(event_name)
        if not mapping:
            unmapped_events.append(event_name)
            continue
        if not matchers:
            continue
        for event in mapping["events"]:
            handler_blocks.append(
                _render_hook_handlers(
                    event,
                    matchers,
                    use_tool_matcher=mapping["type"] in ("tool", "permission"),
                    require_error=mapping.get("require_error", False),
                    note=mapping.get("note"),
                )
            )

    unmapped_comment = (
        f"// Unmapped Claude hook events: {', '.join(unmapped_events)}\n"
        if unmapped_events
        else ""
    )

    content = (
        f'{unmapped_comment}import type {{ Plugin }} from "@opencode-ai/plugin"\n\n'
        f"export const ConvertedHooks: Plugin = async ({{ $ }}) => {{\n"
        f"  return {{\n"
        f"{',\\n'.join(handler_blocks)}\n"
        f"  }}\n"
        f"}}\n\n"
        f"export default ConvertedHooks\n"
    )

    return OpenCodePluginFile(name="converted-hooks.ts", content=content)


def _render_hook_handlers(
    event: str,
    matchers: list,
    *,
    use_tool_matcher: bool,
    require_error: bool,
    note: str | None,
) -> str:
    statements: list[str] = []
    for matcher in matchers:
        statements.extend(_render_hook_statements(matcher, use_tool_matcher))

    rendered = "\n".join(f"    {line}" for line in statements)
    if require_error:
        inner = "\n".join(f"      {line}" for line in statements)
        rendered = f"    if (input?.error) {{\n{inner}\n    }}"

    note_str = f"    // {note}\n" if note else ""
    is_pre_tool_use = event == "tool.execute.before"

    if is_pre_tool_use:
        return (
            f'    "{event}": async (input) => {{\n'
            f"{note_str}"
            f"    try {{\n"
            f"  {rendered}\n"
            f"    }} catch (err) {{\n"
            f'      console.error("[hook] {event} error (non-fatal):", err)\n'
            f"    }}\n"
            f"    }}"
        )
    return f'    "{event}": async (input) => {{\n{note_str}{rendered}\n    }}'


def _render_hook_statements(matcher, use_tool_matcher: bool) -> list[str]:
    if not matcher.hooks:
        return []

    tools = []
    if matcher.matcher:
        tools = [t.strip().lower() for t in matcher.matcher.split("|") if t.strip()]

    use_matcher = use_tool_matcher and tools and "*" not in tools
    condition = (
        " || ".join(f'input.tool === "{t}"' for t in tools) if use_matcher else None
    )
    statements: list[str] = []

    for hook in matcher.hooks:
        if hook.type == "command":
            if condition:
                statements.append(f"if ({condition}) {{ await $`{hook.command}` }}")
            else:
                statements.append(f"await $`{hook.command}`")
            if hook.timeout:
                statements.append(f"// timeout: {hook.timeout}s (not enforced)")
            continue
        if hook.type == "prompt":
            prompt_text = (hook.prompt or "").replace("\n", " ")
            statements.append(
                f"// Prompt hook for {matcher.matcher or '*'}: {prompt_text}"
            )
            continue
        statements.append(f"// Agent hook for {matcher.matcher or '*'}: {hook.agent}")

    return statements


def _rewrite_claude_paths(body: str) -> str:
    result = body.replace("~/.claude/", "~/.config/opencode/")
    return result.replace(".claude/", ".opencode/")


def _normalize_model(model: str) -> str:
    if "/" in model:
        return model
    if model in CLAUDE_FAMILY_ALIASES:
        return f"anthropic/{CLAUDE_FAMILY_ALIASES[model]}"
    if model.startswith("claude-"):
        return f"anthropic/{model}"
    if re.match(r"^(gpt-|o1-|o3-)", model):
        return f"openai/{model}"
    if model.startswith("gemini-"):
        return f"google/{model}"
    return f"anthropic/{model}"


def _infer_temperature(agent: ClaudeAgent) -> float | None:
    sample = f"{agent.name} {agent.description or ''}".lower()
    if re.search(
        r"(review|audit|security|sentinel|oracle|lint|verification|guardian)",
        sample,
    ):
        return 0.1
    if re.search(r"(plan|planning|architecture|strategist|analysis|research)", sample):
        return 0.2
    if re.search(r"(doc|readme|changelog|editor|writer)", sample):
        return 0.3
    if re.search(r"(brainstorm|creative|ideate|design|concept)", sample):
        return 0.6
    return 0.3


def _apply_permissions(
    config: OpenCodeConfig,
    commands: list[ClaudeCommand],
    mode: PermissionMode,
) -> None:
    if mode == "none":
        return

    enabled: set[str] = set()
    patterns: dict[str, set[str]] = {}

    if mode == "broad":
        enabled = set(SOURCE_TOOLS)
    else:
        for command in commands:
            if not command.allowed_tools:
                continue
            for tool_spec in command.allowed_tools:
                parsed = _parse_tool_spec(tool_spec)
                if not parsed["tool"]:
                    continue
                enabled.add(parsed["tool"])
                if parsed.get("pattern"):
                    normalized_pattern = _normalize_pattern(
                        parsed["tool"], parsed["pattern"]
                    )
                    patterns.setdefault(parsed["tool"], set()).add(normalized_pattern)

    permission: dict = {}
    tools: dict[str, bool] = {}

    for tool in SOURCE_TOOLS:
        tools[tool] = True if mode == "broad" else tool in enabled

    if mode == "broad":
        for tool in SOURCE_TOOLS:
            permission[tool] = "allow"
    else:
        for tool in SOURCE_TOOLS:
            tool_patterns = patterns.get(tool)
            if tool_patterns:
                pattern_permission: dict[str, str] = {"*": "deny"}
                for p in tool_patterns:
                    pattern_permission[p] = "allow"
                permission[tool] = pattern_permission
            else:
                permission[tool] = "allow" if tool in enabled else "deny"

    if mode != "broad":
        for tool, tool_patterns in patterns.items():
            if not tool_patterns:
                continue
            pattern_permission = {"*": "deny"}
            for p in tool_patterns:
                pattern_permission[p] = "allow"
            permission[tool] = pattern_permission

    if "write" in enabled or "edit" in enabled:
        if isinstance(permission.get("edit"), str):
            permission["edit"] = "allow"
        if isinstance(permission.get("write"), str):
            permission["write"] = "allow"

    if "write" in patterns or "edit" in patterns:
        combined: set[str] = set()
        combined.update(patterns.get("write", set()))
        combined.update(patterns.get("edit", set()))
        combined_permission: dict[str, str] = {"*": "deny"}
        for p in combined:
            combined_permission[p] = "allow"
        permission["edit"] = combined_permission
        permission["write"] = combined_permission

    config.permission = permission
    config.tools = tools


def _parse_tool_spec(raw: str) -> dict:
    trimmed = raw.strip()
    if not trimmed:
        return {"tool": None}
    parts = trimmed.split("(", 1)
    name = parts[0].strip().lower()
    tool = TOOL_MAP.get(name)
    if len(parts) == 1:
        return {"tool": tool}
    pattern_part = parts[1]
    if pattern_part.endswith(")"):
        pattern_part = pattern_part[:-1]
    return {"tool": tool, "pattern": pattern_part.strip()}


def _normalize_pattern(tool: str, pattern: str) -> str:
    if tool == "bash":
        return pattern.replace(":", " ").strip()
    return pattern
