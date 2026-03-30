from __future__ import annotations

import os

from ..types import ClaudeMcpServer, CodexAgentFile, CodexBundle
from .files import ensure_dir, path_exists, read_text, sanitize_path_name, write_text

MANAGED_AGENT_HEADER_PREFIX = "# Generated from "


def write_codex_bundle(output_root: str, bundle: CodexBundle) -> None:
    paths = _resolve_codex_paths(output_root)
    ensure_dir(paths["root"])
    ensure_dir(paths["agents_dir"])

    for agent in bundle.agents:
        dest = os.path.join(paths["agents_dir"], f"{sanitize_path_name(agent.name)}.toml")
        if path_exists(dest) and not _is_managed_agent_file(dest):
            raise FileExistsError(
                f"Refusing to overwrite unmanaged Codex agent file: {dest}"
            )
        write_text(dest, render_codex_agent_file(agent, output_root))


def render_codex_agent_file(agent: CodexAgentFile, output_root: str) -> str:
    source_label = _display_source_path(agent.source_path, output_root)
    lines = [
        f"{MANAGED_AGENT_HEADER_PREFIX}{source_label}",
        "# Do not edit by hand. Regenerate from the Claude agent source.",
        "",
        f"name = {_format_toml_string(agent.name)}",
        f"description = {_format_toml_string(agent.description)}",
        "developer_instructions = '''",
        agent.developer_instructions.rstrip(),
        "'''",
    ]

    if agent.mcp_servers:
        lines.append("")
        lines.extend(_render_mcp_servers(agent.mcp_servers))

    return "\n".join(lines).rstrip() + "\n"


def _render_mcp_servers(mcp_servers: dict[str, ClaudeMcpServer]) -> list[str]:
    lines: list[str] = []
    for name, server in mcp_servers.items():
        key = _format_toml_key(name)
        lines.append(f"[mcp_servers.{key}]")

        if server.command:
            lines.append(f"command = {_format_toml_string(server.command)}")
            if server.cwd:
                lines.append(f"cwd = {_format_toml_string(server.cwd)}")
            if server.args:
                args = ", ".join(_format_toml_string(arg) for arg in server.args)
                lines.append(f"args = [{args}]")
            if server.env:
                lines.append("")
                lines.append(f"[mcp_servers.{key}.env]")
                for env_key, value in server.env.items():
                    lines.append(
                        f"{_format_toml_key(env_key)} = {_format_toml_string(value)}"
                    )
        elif server.url:
            lines.append(f"url = {_format_toml_string(server.url)}")
            if server.headers:
                lines.append(
                    f"http_headers = {_format_toml_inline_table(server.headers)}"
                )

        lines.append("")

    return lines


def _resolve_codex_paths(output_root: str) -> dict[str, str]:
    if os.path.basename(output_root) == ".codex":
        root = output_root
    else:
        root = os.path.join(output_root, ".codex")
    return {
        "root": root,
        "agents_dir": os.path.join(root, "agents"),
    }


def _display_source_path(source_path: str, output_root: str) -> str:
    try:
        relative = os.path.relpath(source_path, output_root)
    except ValueError:
        return source_path
    if relative.startswith(".."):
        return source_path
    return relative


def _is_managed_agent_file(path: str) -> bool:
    return read_text(path).startswith(MANAGED_AGENT_HEADER_PREFIX)


def _format_toml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _format_toml_key(value: str) -> str:
    return (
        value
        if value.replace("_", "").replace("-", "").isalnum()
        else _format_toml_string(value)
    )


def _format_toml_inline_table(entries: dict[str, str]) -> str:
    parts = [
        f"{_format_toml_key(key)} = {_format_toml_string(value)}"
        for key, value in entries.items()
    ]
    return "{ " + ", ".join(parts) + " }"
