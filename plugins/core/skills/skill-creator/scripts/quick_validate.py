#!/usr/bin/env python3
"""
Quick validation script for skills.

The validator aims to catch the most common problems in new or updated skills:
- malformed or missing frontmatter
- weak trigger descriptions
- unfinished TODO/template content
- missing high-signal sections like Gotchas
- mismatches between mentioned bundled resources and actual files
- suspicious packaging artifacts or oversized SKILL.md files
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


RECOMMENDED_TOP_LEVEL_SECTIONS = [
    "overview",
    "gotchas",
    "verification",
]

TRIGGER_HINTS = [
    "use this skill when",
    "when ",
    "trigger",
    "requests",
    "working with",
    "apply when",
]

PLACEHOLDER_PATTERNS = [
    r"\[TODO:[^\]]*\]",
    r"TODO:",
    r"replace this placeholder",
    r"delete this section",
]

IGNORE_FILE_NAMES = {
    ".ds_store",
    "thumbs.db",
}

IGNORE_DIR_NAMES = {
    "__pycache__",
    ".git",
}

ARCHIVE_EXTENSIONS = {".zip"}


@dataclass
class ValidationReport:
    errors: list[str]
    warnings: list[str]

    @property
    def valid(self) -> bool:
        return not self.errors

    def render(self) -> str:
        parts: list[str] = []
        if self.errors:
            parts.append("Errors:")
            parts.extend(f"- {item}" for item in self.errors)
        if self.warnings:
            if parts:
                parts.append("")
            parts.append("Warnings:")
            parts.extend(f"- {item}" for item in self.warnings)
        if not parts:
            return "Skill is valid!"
        return "\n".join(parts)


def extract_frontmatter(content: str) -> tuple[dict[str, str], str] | tuple[None, None]:
    match = re.match(r"^---\n(.*?)\n---\n?", content, re.DOTALL)
    if not match:
        return None, None

    raw_frontmatter = match.group(1)
    body = content[match.end():]
    data: dict[str, str] = {}

    for line in raw_frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")

    return data, body


def find_headings(markdown: str) -> list[str]:
    headings: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            headings.append(stripped.lstrip("#").strip().lower())
    return headings


def has_heading_keyword(headings: list[str], keyword: str) -> bool:
    keyword = keyword.lower()
    return any(keyword == heading or keyword in heading for heading in headings)


def normalize_inline_code_references(markdown: str) -> set[str]:
    matches = re.findall(r"`([^`]+)`", markdown)
    refs: set[str] = set()
    for match in matches:
        cleaned = match.strip()
        if not cleaned:
            continue
        if "/" in cleaned or cleaned.endswith(".json"):
            refs.add(cleaned)
    return refs


def contains_placeholder(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered, re.IGNORECASE) for pattern in PLACEHOLDER_PATTERNS)


def iter_skill_files(skill_path: Path) -> Iterable[Path]:
    for path in skill_path.rglob("*"):
        if any(part in IGNORE_DIR_NAMES for part in path.parts):
            continue
        yield path


def analyze_skill(skill_path: str | Path) -> ValidationReport:
    skill_path = Path(skill_path)
    errors: list[str] = []
    warnings: list[str] = []

    if not skill_path.exists():
        return ValidationReport([f"Skill folder not found: {skill_path}"], [])
    if not skill_path.is_dir():
        return ValidationReport([f"Path is not a directory: {skill_path}"], [])

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return ValidationReport(["SKILL.md not found"], [])

    try:
        content = skill_md.read_text()
    except Exception as exc:
        return ValidationReport([f"Unable to read SKILL.md: {exc}"], [])

    frontmatter, body = extract_frontmatter(content)
    if frontmatter is None:
        return ValidationReport(["Invalid or missing YAML frontmatter in SKILL.md"], [])

    name = frontmatter.get("name", "").strip()
    description = frontmatter.get("description", "").strip()

    if not name:
        errors.append("Missing 'name' in frontmatter")
    else:
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(
                f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)"
            )
        if name.startswith("-") or name.endswith("-") or "--" in name:
            errors.append(
                f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
            )
        if name != skill_path.name:
            errors.append(
                f"Frontmatter name '{name}' must match directory name '{skill_path.name}'"
            )

    if not description:
        errors.append("Missing 'description' in frontmatter")
    else:
        if "<" in description or ">" in description:
            errors.append("Description cannot contain angle brackets (< or >)")
        if contains_placeholder(description):
            errors.append("Description still contains placeholder or TODO text")
        if len(description) < 80:
            warnings.append(
                "Description is very short; trigger descriptions usually work better when they explicitly mention when the skill should activate"
            )
        lowered_description = description.lower()
        if not any(hint in lowered_description for hint in TRIGGER_HINTS):
            warnings.append(
                "Description does not clearly look trigger-oriented; describe when the skill should be used, not just what it is"
            )

    if contains_placeholder(body):
        errors.append("SKILL.md still contains TODOs or placeholder/template text")

    headings = find_headings(body)
    for section in RECOMMENDED_TOP_LEVEL_SECTIONS:
        if not has_heading_keyword(headings, section):
            warnings.append(f"Recommended section missing: '{section.title()}'")

    if not has_heading_keyword(headings, "gotchas"):
        errors.append("Skill should include a 'Gotchas' section")

    if not has_heading_keyword(headings, "verification"):
        warnings.append("Skill should usually explain how to verify success")

    if len(body.split()) > 3500:
        warnings.append(
            "SKILL.md is quite large; move detailed material into references/ to preserve progressive disclosure"
        )

    if len(body.splitlines()) > 400:
        warnings.append(
            "SKILL.md exceeds 400 lines; consider moving verbose detail into references/"
        )

    resource_refs = normalize_inline_code_references(body)
    for ref in sorted(resource_refs):
        normalized = ref.split(" (", 1)[0].strip()
        if normalized.startswith(("scripts/", "references/", "assets/")) or normalized == "config.json":
            if not (skill_path / normalized).exists():
                errors.append(f"Referenced resource not found: {normalized}")

    bundled_resource_refs = {
        ref for ref in resource_refs
        if ref.startswith(("scripts/", "references/", "assets/")) or ref == "config.json"
    }

    if any(ref.startswith("references/") for ref in bundled_resource_refs) and not (skill_path / "references").exists():
        errors.append("SKILL.md references files under references/ but the directory does not exist")

    if any(ref.startswith("scripts/") for ref in bundled_resource_refs) and not (skill_path / "scripts").exists():
        errors.append("SKILL.md references files under scripts/ but the directory does not exist")

    if any(ref.startswith("assets/") for ref in bundled_resource_refs) and not (skill_path / "assets").exists():
        errors.append("SKILL.md references files under assets/ but the directory does not exist")

    if "config.json" in bundled_resource_refs and not (skill_path / "config.json").exists():
        errors.append("SKILL.md references config.json but the file does not exist")

    stray_files: list[str] = []
    for path in iter_skill_files(skill_path):
        if path.is_dir():
            continue
        if path.name.lower() in IGNORE_FILE_NAMES:
            warnings.append(f"Remove editor/OS artifact before packaging: {path.relative_to(skill_path)}")
        if path.suffix.lower() in ARCHIVE_EXTENSIONS:
            warnings.append(f"Nested archive found inside skill folder: {path.relative_to(skill_path)}")
        if path.name.endswith(("~", ".bak", ".tmp", ".orig")):
            warnings.append(f"Temporary or backup file found: {path.relative_to(skill_path)}")
        if path.name == "example.py" and "example.py" not in body:
            stray_files.append(str(path.relative_to(skill_path)))
        if path.name in {"reference_notes.md", "example_asset.txt"}:
            stray_files.append(str(path.relative_to(skill_path)))

    if stray_files and not contains_placeholder(body):
        warnings.append(
            "Placeholder resource files still exist; remove or replace them if they are no longer needed: "
            + ", ".join(sorted(stray_files))
        )

    return ValidationReport(errors, warnings)


def validate_skill(skill_path: str | Path) -> tuple[bool, str]:
    report = analyze_skill(skill_path)
    return report.valid, report.render()


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: uv run python quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
