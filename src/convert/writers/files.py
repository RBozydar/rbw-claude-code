from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path
from typing import Callable


def ensure_dir(dir_path: str) -> None:
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def write_text(file_path: str, content: str) -> None:
    ensure_dir(os.path.dirname(file_path))
    Path(file_path).write_text(content, encoding="utf-8")


def write_json(file_path: str, data: object) -> None:
    ensure_dir(os.path.dirname(file_path))
    Path(file_path).write_text(
        json.dumps(data, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )


def read_text(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def read_json(file_path: str) -> dict:
    return json.loads(Path(file_path).read_text(encoding="utf-8"))


def path_exists(file_path: str) -> bool:
    return Path(file_path).exists()


def backup_file(file_path: str) -> str | None:
    if not Path(file_path).exists():
        return None
    backup_path = f"{file_path}.bak"
    counter = 1
    while Path(backup_path).exists():
        backup_path = f"{file_path}.bak.{counter}"
        counter += 1
    shutil.copy2(file_path, backup_path)
    return backup_path


def copy_dir(src: str, dst: str) -> None:
    if Path(dst).exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copy_skill_dir(
    src: str,
    dst: str,
    transform: Callable[[str], str] | None = None,
) -> None:
    """Copy a skill directory, optionally transforming .md file content."""
    if Path(dst).exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst)

    if transform is None:
        return

    for root, _dirs, files in os.walk(dst):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            content = Path(fpath).read_text(encoding="utf-8")
            transformed = transform(content)
            if transformed != content:
                Path(fpath).write_text(transformed, encoding="utf-8")


def sanitize_path_name(name: str) -> str:
    sanitized = re.sub(r"[^\w\-.]", "-", name)
    sanitized = re.sub(r"-+", "-", sanitized)
    return sanitized.strip("-")


def walk_files(directory: str) -> list[str]:
    result: list[str] = []
    for root, _dirs, files in os.walk(directory):
        for fname in sorted(files):
            result.append(os.path.join(root, fname))
    return result


def _json_default(obj: object) -> object:
    """Default JSON serializer for dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        d = {}
        for k, _v in obj.__dataclass_fields__.items():
            val = getattr(obj, k)
            if val is not None:
                # Convert snake_case keys to camelCase for JSON output
                camel_key = _to_camel_case(k)
                d[camel_key] = val
        return d
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _to_camel_case(name: str) -> str:
    if name == "schema":
        return "$schema"
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])
