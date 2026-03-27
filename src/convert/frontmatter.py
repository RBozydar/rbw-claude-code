from __future__ import annotations

import json
from typing import Any

import yaml


def parse_frontmatter(
    raw: str, source_path: str | None = None
) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from a markdown file. Returns (data, body)."""
    lines = raw.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, raw

    end_index = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break

    if end_index == -1:
        return {}, raw

    yaml_text = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :])

    try:
        parsed = yaml.safe_load(yaml_text)
        data = parsed if isinstance(parsed, dict) else {}
        return data, body
    except yaml.YAMLError:
        # Fallback: parse simple key: value lines manually.
        # Handles frontmatter with unquoted colons in values (common in descriptions).
        data = _parse_simple_yaml(yaml_text)
        return data, body


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Fallback parser for simple single-line key: value YAML."""
    data: dict[str, Any] = {}
    current_key: str | None = None
    list_items: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        # List item under current key
        if stripped.startswith("- ") and current_key is not None:
            list_items.append(stripped[2:].strip())
            continue

        # Flush any pending list
        if current_key is not None and list_items:
            data[current_key] = list_items
            list_items = []
            current_key = None

        # key: value — split only on the FIRST colon followed by space
        colon_pos = stripped.find(": ")
        if colon_pos > 0:
            key = stripped[:colon_pos].strip()
            value = stripped[colon_pos + 2 :].strip()
            if value == "":
                current_key = key  # might be followed by list items
            elif value == "true":
                data[key] = True
            elif value == "false":
                data[key] = False
            else:
                # Strip surrounding quotes if present
                if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                    value = value[1:-1]
                data[key] = value
            if value != "":
                current_key = None
        elif stripped.endswith(":"):
            current_key = stripped[:-1].strip()

    if current_key is not None and list_items:
        data[current_key] = list_items

    return data


def format_frontmatter(data: dict[str, Any], body: str) -> str:
    """Format data as YAML frontmatter + body."""
    lines = []
    for key, value in data.items():
        if value is None:
            continue
        lines.append(_format_yaml_line(key, value))

    yaml_block = "\n".join(lines)
    if not yaml_block.strip():
        return body

    return "\n".join(["---", yaml_block, "---", "", body])


def _format_yaml_line(key: str, value: Any) -> str:
    if isinstance(value, list):
        items = [f"  - {_format_yaml_value(item)}" for item in value]
        return "\n".join([f"{key}:"] + items)
    return f"{key}: {_format_yaml_value(value)}"


def _format_yaml_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float, bool)):
        return str(value).lower() if isinstance(value, bool) else str(value)
    raw = str(value)
    if "\n" in raw:
        indented = "\n".join(f"  {line}" for line in raw.split("\n"))
        return f"|\n{indented}"
    if ":" in raw or raw.startswith("[") or raw.startswith("{") or raw == "*":
        return json.dumps(raw)
    return raw
