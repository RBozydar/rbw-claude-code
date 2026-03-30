from __future__ import annotations

import os

from .frontmatter import parse_frontmatter
from .types import (
    ClaudeAgent,
    ClaudeCommand,
    ClaudeHookEntry,
    ClaudeHookMatcher,
    ClaudeHooks,
    ClaudeManifest,
    ClaudeMcpServer,
    ClaudePlugin,
    ClaudeSkill,
)
from .writers.files import path_exists, read_json, read_text, walk_files

PLUGIN_MANIFEST = os.path.join(".claude-plugin", "plugin.json")


def load_claude_plugin(input_path: str) -> ClaudePlugin:
    root = _resolve_claude_root(input_path)
    manifest_path = os.path.join(root, PLUGIN_MANIFEST)
    raw_manifest = read_json(manifest_path)
    manifest = _parse_manifest(raw_manifest)

    agent_dirs = _resolve_component_dirs(root, "agents", manifest.agents)
    command_dirs = _resolve_component_dirs(root, "commands", manifest.commands)
    skill_dirs = _resolve_component_dirs(root, "skills", manifest.skills)

    agents = _load_agents(agent_dirs)
    commands = _load_commands(command_dirs)
    skills = _load_skills(skill_dirs)
    hooks = _load_hooks(root, manifest.hooks)
    mcp_servers = _load_mcp_servers(root, manifest)

    return ClaudePlugin(
        root=root,
        manifest=manifest,
        agents=agents,
        commands=commands,
        skills=skills,
        hooks=hooks,
        mcp_servers=mcp_servers,
    )


def _parse_manifest(raw: dict) -> ClaudeManifest:
    return ClaudeManifest(
        name=raw["name"],
        version=raw["version"],
        description=raw.get("description"),
        author=raw.get("author"),
        keywords=raw.get("keywords"),
        agents=raw.get("agents"),
        commands=raw.get("commands"),
        skills=raw.get("skills"),
        hooks=raw.get("hooks"),
        mcp_servers=raw.get("mcpServers"),
    )


def _resolve_claude_root(input_path: str) -> str:
    absolute = os.path.abspath(input_path)

    if path_exists(os.path.join(absolute, PLUGIN_MANIFEST)):
        return absolute

    if absolute.endswith(PLUGIN_MANIFEST) or absolute.endswith("plugin.json"):
        return os.path.dirname(os.path.dirname(absolute))

    raise FileNotFoundError(f"Could not find {PLUGIN_MANIFEST} under {input_path}")


def _resolve_component_dirs(
    root: str,
    default_dir: str,
    custom: str | list[str] | None,
) -> list[str]:
    dirs = [os.path.join(root, default_dir)]
    for entry in _to_path_list(custom):
        dirs.append(_resolve_within_root(root, entry, f"{default_dir} path"))
    return dirs


def _to_path_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _load_agents(agent_dirs: list[str]) -> list[ClaudeAgent]:
    files = _collect_markdown_files(agent_dirs)
    agents: list[ClaudeAgent] = []
    for file_path in files:
        raw = read_text(file_path)
        data, body = parse_frontmatter(raw, file_path)
        name = data.get("name") or os.path.splitext(os.path.basename(file_path))[0]
        agents.append(
            ClaudeAgent(
                name=name,
                description=data.get("description"),
                capabilities=data.get("capabilities"),
                model=data.get("model"),
                body=body.strip(),
                source_path=file_path,
            )
        )
    return agents


def _load_commands(command_dirs: list[str]) -> list[ClaudeCommand]:
    files = _collect_markdown_files(command_dirs)
    commands: list[ClaudeCommand] = []
    for file_path in files:
        raw = read_text(file_path)
        data, body = parse_frontmatter(raw, file_path)
        name = data.get("name") or os.path.splitext(os.path.basename(file_path))[0]
        allowed_tools = _parse_allowed_tools(data.get("allowed-tools"))
        disable = True if data.get("disable-model-invocation") is True else None
        commands.append(
            ClaudeCommand(
                name=name,
                description=data.get("description"),
                argument_hint=data.get("argument-hint"),
                model=data.get("model"),
                allowed_tools=allowed_tools,
                disable_model_invocation=disable,
                body=body.strip(),
                source_path=file_path,
            )
        )
    return commands


def _load_skills(skill_dirs: list[str]) -> list[ClaudeSkill]:
    entries = _collect_files(skill_dirs)
    skill_files = [f for f in entries if os.path.basename(f) == "SKILL.md"]
    skills: list[ClaudeSkill] = []
    for file_path in skill_files:
        raw = read_text(file_path)
        data, _ = parse_frontmatter(raw, file_path)
        name = data.get("name") or os.path.basename(os.path.dirname(file_path))
        disable = True if data.get("disable-model-invocation") is True else None
        skills.append(
            ClaudeSkill(
                name=name,
                description=data.get("description"),
                argument_hint=data.get("argument-hint"),
                disable_model_invocation=disable,
                source_dir=os.path.dirname(file_path),
                skill_path=file_path,
            )
        )
    return skills


def _load_hooks(
    root: str,
    hooks_field: str | list[str] | dict | None,
) -> ClaudeHooks | None:
    hook_configs: list[ClaudeHooks] = []

    default_path = os.path.join(root, "hooks", "hooks.json")
    if path_exists(default_path):
        hook_configs.append(_parse_hooks_json(read_json(default_path)))

    if hooks_field is not None:
        if isinstance(hooks_field, (str, list)):
            for hook_path in _to_path_list(hooks_field):
                resolved = _resolve_within_root(root, hook_path, "hooks path")
                if path_exists(resolved):
                    hook_configs.append(_parse_hooks_json(read_json(resolved)))
        elif isinstance(hooks_field, dict):
            hook_configs.append(_parse_hooks_json(hooks_field))

    if not hook_configs:
        return None
    return _merge_hooks(hook_configs)


def _parse_hooks_json(raw: dict) -> ClaudeHooks:
    hooks_data = raw.get("hooks", {})
    hooks: dict[str, list[ClaudeHookMatcher]] = {}
    for event, matchers in hooks_data.items():
        hooks[event] = []
        for m in matchers:
            entries = []
            for h in m.get("hooks", []):
                entries.append(
                    ClaudeHookEntry(
                        type=h.get("type", "command"),
                        command=h.get("command"),
                        timeout=h.get("timeout"),
                        prompt=h.get("prompt"),
                        agent=h.get("agent"),
                    )
                )
            hooks[event].append(
                ClaudeHookMatcher(matcher=m.get("matcher"), hooks=entries)
            )
    return ClaudeHooks(hooks=hooks)


def _load_mcp_servers(
    root: str,
    manifest: ClaudeManifest,
) -> dict[str, ClaudeMcpServer] | None:
    field = manifest.mcp_servers
    if field is not None:
        if isinstance(field, (str, list)):
            return _merge_mcp_configs(_load_mcp_paths(root, field))
        if isinstance(field, dict):
            return _parse_mcp_dict(field)

    mcp_path = os.path.join(root, ".mcp.json")
    if path_exists(mcp_path):
        raw = read_json(mcp_path)
        return _unwrap_mcp_servers(raw)

    return None


def _parse_mcp_dict(raw: dict) -> dict[str, ClaudeMcpServer]:
    result: dict[str, ClaudeMcpServer] = {}
    for name, server_data in raw.items():
        if not isinstance(server_data, dict):
            continue
        result[name] = ClaudeMcpServer(
            type=server_data.get("type"),
            command=server_data.get("command"),
            args=server_data.get("args"),
            url=server_data.get("url"),
            cwd=server_data.get("cwd"),
            env=server_data.get("env"),
            headers=server_data.get("headers"),
        )
    return result


def _load_mcp_paths(
    root: str,
    value: str | list[str],
) -> list[dict[str, ClaudeMcpServer]]:
    configs: list[dict[str, ClaudeMcpServer]] = []
    for entry in _to_path_list(value):
        resolved = _resolve_within_root(root, entry, "mcpServers path")
        if path_exists(resolved):
            raw = read_json(resolved)
            configs.append(_parse_mcp_dict(_unwrap_mcp_servers_raw(raw)))
    return configs


def _unwrap_mcp_servers(raw: dict) -> dict[str, ClaudeMcpServer]:
    inner = _unwrap_mcp_servers_raw(raw)
    return _parse_mcp_dict(inner)


def _unwrap_mcp_servers_raw(raw: dict) -> dict:
    if "mcpServers" in raw and isinstance(raw["mcpServers"], dict):
        return raw["mcpServers"]
    return raw


def _merge_mcp_configs(
    configs: list[dict[str, ClaudeMcpServer]],
) -> dict[str, ClaudeMcpServer]:
    result: dict[str, ClaudeMcpServer] = {}
    for config in configs:
        result.update(config)
    return result


def _merge_hooks(hooks_list: list[ClaudeHooks]) -> ClaudeHooks:
    merged: dict[str, list[ClaudeHookMatcher]] = {}
    for hooks in hooks_list:
        for event, matchers in hooks.hooks.items():
            if event not in merged:
                merged[event] = []
            merged[event].extend(matchers)
    return ClaudeHooks(hooks=merged)


def _parse_allowed_tools(value: object) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return None


def _collect_markdown_files(dirs: list[str]) -> list[str]:
    return [f for f in _collect_files(dirs) if f.endswith(".md")]


def _collect_files(dirs: list[str]) -> list[str]:
    files: list[str] = []
    for directory in dirs:
        if not path_exists(directory):
            continue
        files.extend(walk_files(directory))
    return files


def _resolve_within_root(root: str, entry: str, label: str) -> str:
    resolved_root = os.path.abspath(root)
    resolved_path = os.path.abspath(os.path.join(root, entry))
    if resolved_path == resolved_root or resolved_path.startswith(
        resolved_root + os.sep
    ):
        return resolved_path
    raise ValueError(
        f"Invalid {label}: {entry}. Paths must stay within the plugin root."
    )
