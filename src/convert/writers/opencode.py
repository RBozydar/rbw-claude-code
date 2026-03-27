from __future__ import annotations

import json
import os

from ..types import OpenCodeBundle, OpenCodeConfig
from .files import (
    backup_file,
    copy_dir,
    ensure_dir,
    path_exists,
    read_json,
    sanitize_path_name,
    write_text,
)


def write_opencode_bundle(output_root: str, bundle: OpenCodeBundle) -> None:
    paths = _resolve_opencode_paths(output_root)
    ensure_dir(paths["root"])

    had_existing_config = path_exists(paths["config_path"])
    bp = backup_file(paths["config_path"])
    if bp:
        print(f"Backed up existing config to {bp}")

    merged = _merge_opencode_config(paths["config_path"], bundle.config)
    _write_config_json(paths["config_path"], merged)
    if had_existing_config:
        print(
            "Merged plugin config into existing opencode.json (user settings preserved)"
        )

    seen_agents: set[str] = set()
    for agent in bundle.agents:
        safe_name = sanitize_path_name(agent.name)
        if safe_name in seen_agents:
            print(
                f'Skipping agent "{agent.name}": sanitized name "{safe_name}" collides'
            )
            continue
        seen_agents.add(safe_name)
        write_text(
            os.path.join(paths["agents_dir"], f"{safe_name}.md"),
            agent.content + "\n",
        )

    for cmd_file in bundle.command_files:
        dest = os.path.join(
            paths["command_dir"], f"{sanitize_path_name(cmd_file.name)}.md"
        )
        cmd_bp = backup_file(dest)
        if cmd_bp:
            print(f"Backed up existing command file to {cmd_bp}")
        write_text(dest, cmd_file.content + "\n")

    if bundle.plugins:
        for plugin in bundle.plugins:
            write_text(
                os.path.join(paths["plugins_dir"], plugin.name),
                plugin.content + "\n",
            )

    if bundle.skill_dirs:
        for skill in bundle.skill_dirs:
            copy_dir(
                skill.source_dir,
                os.path.join(paths["skills_dir"], sanitize_path_name(skill.name)),
            )


def _resolve_opencode_paths(output_root: str) -> dict[str, str]:
    base = os.path.basename(output_root)
    if base in ("opencode", ".opencode"):
        return {
            "root": output_root,
            "config_path": os.path.join(output_root, "opencode.json"),
            "agents_dir": os.path.join(output_root, "agents"),
            "plugins_dir": os.path.join(output_root, "plugins"),
            "skills_dir": os.path.join(output_root, "skills"),
            "command_dir": os.path.join(output_root, "commands"),
        }

    return {
        "root": output_root,
        "config_path": os.path.join(output_root, "opencode.json"),
        "agents_dir": os.path.join(output_root, ".opencode", "agents"),
        "plugins_dir": os.path.join(output_root, ".opencode", "plugins"),
        "skills_dir": os.path.join(output_root, ".opencode", "skills"),
        "command_dir": os.path.join(output_root, ".opencode", "commands"),
    }


def _merge_opencode_config(
    config_path: str,
    incoming: OpenCodeConfig,
) -> dict:
    incoming_dict = _config_to_dict(incoming)

    if not path_exists(config_path):
        return incoming_dict

    try:
        existing = read_json(config_path)
    except (json.JSONDecodeError, ValueError):
        print(
            f"Warning: existing {config_path} is not valid JSON. "
            "Writing plugin config without merging."
        )
        return incoming_dict

    merged_mcp = {**(incoming_dict.get("mcp") or {}), **(existing.get("mcp") or {})}
    merged_permission = (
        {
            **(incoming_dict.get("permission") or {}),
            **(existing.get("permission") or {}),
        }
        if incoming_dict.get("permission")
        else existing.get("permission")
    )
    merged_tools = (
        {**(incoming_dict.get("tools") or {}), **(existing.get("tools") or {})}
        if incoming_dict.get("tools")
        else existing.get("tools")
    )

    result = {**existing}
    result["$schema"] = incoming_dict.get("$schema") or existing.get("$schema")
    if merged_mcp:
        result["mcp"] = merged_mcp
    if merged_permission:
        result["permission"] = merged_permission
    if merged_tools:
        result["tools"] = merged_tools

    return result


def _config_to_dict(config: OpenCodeConfig) -> dict:
    d: dict = {}
    if config.schema:
        d["$schema"] = config.schema
    if config.mcp:
        mcp_dict = {}
        for name, server in config.mcp.items():
            entry: dict = {"type": server.type, "enabled": server.enabled}
            if server.command:
                entry["command"] = server.command
            if server.url:
                entry["url"] = server.url
            if server.environment:
                entry["environment"] = server.environment
            if server.headers:
                entry["headers"] = server.headers
            mcp_dict[name] = entry
        d["mcp"] = mcp_dict
    if config.permission:
        d["permission"] = config.permission
    if config.tools:
        d["tools"] = config.tools
    return d


def _write_config_json(path: str, data: dict) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
