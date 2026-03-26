#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --path <path>

Examples:
    init_skill.py my-new-skill --path skills/public
    init_skill.py my-api-helper --path skills/private
    init_skill.py custom-skill --path /custom/location
"""

import sys
from pathlib import Path


SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: Describe when this skill should trigger. Mention the kinds of requests, files, systems, or failure modes that should cause Claude to use it. Do not write a vague summary.]
---

# {skill_title}

## Overview

[TODO: In 1-3 sentences, explain what capability this skill gives Claude and what non-obvious value it adds. Focus on the delta from Claude's default behavior.]

## Trigger Examples

[TODO: Add 3-6 concrete examples of requests that should trigger this skill.
Examples:
- "..."
- "..."
- "..."
]

## Skill Category

[TODO: Choose the primary category for this skill and delete the others.
- Library and API reference
- Product verification
- Data fetching and analysis
- Business process and team automation
- Code scaffolding and templates
- Code quality and review
- CI/CD and deployment
- Runbooks
- Infrastructure operations

If the skill spans multiple categories, state the primary one and keep the skill focused.]

## Workflow / Decision Structure

[TODO: Replace this with the main operating structure for the skill.
Pick the structure that best fits the task:

1. Workflow-based
   - Best for sequential procedures
   - Example shape: Overview -> Decision Tree -> Step 1 -> Step 2

2. Task-based
   - Best for a collection of operations or capabilities
   - Example shape: Quick Start -> Task A -> Task B -> Task C

3. Reference/guidelines
   - Best for standards, requirements, or domain conventions
   - Example shape: Overview -> Core Rules -> Exceptions -> Examples

4. Capabilities-based
   - Best when the skill bundles several related powers
   - Example shape: Overview -> Capability 1 -> Capability 2 -> Capability 3

Keep the structure helpful, but avoid railroading Claude into an overly rigid tool sequence unless safety or correctness requires it.]

## Bundled Resources

[TODO: List every bundled resource this skill ships and explain when to use it.
Examples:
- `scripts/fetch_data.py` - Use when retrieving canonical metrics from the warehouse
- `references/api.md` - Read when endpoint details or request shapes are needed
- `assets/template.md` - Copy or adapt when generating the final deliverable
- `config.json` - Read for install-specific IDs, enum values, or environment names

Delete this section if the skill truly has no bundled resources, but most strong skills should at least consider scripts, references, assets, or config.]

## Gotchas

[TODO: Add the highest-signal mistakes, edge cases, and footguns.
This is often the most valuable section in the entire skill.
Include things Claude would otherwise get wrong, such as:
- misleading defaults
- unsupported approaches
- environment-specific constraints
- schema quirks
- common failure patterns

Start with at least one real gotcha.]

## Verification

[TODO: Explain how Claude should verify success.
Prefer concrete checks over vague advice.
Examples:
- run a script with assertions
- inspect output files
- compare against expected state
- capture screenshots, logs, or videos
- verify downstream side effects

If verification is not applicable, say why.]

## Progressive Disclosure Notes

[TODO: Keep SKILL.md lean.
Move long API details, schemas, examples, or policy documents into `references/`.
Put deterministic helper logic into `scripts/`.
Put templates and boilerplate into `assets/`.
Mention where detailed information lives so Claude can load it on demand.]

## Iteration Notes

[TODO: Describe how this skill should improve after real use.
Examples:
- add new gotchas when Claude fails in practice
- add scripts when helper logic keeps being rewritten
- refine the description if the skill under-triggers or over-triggers
- move bulky details out of SKILL.md if context usage gets noisy]
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example helper script for {skill_name}

Replace this placeholder with a real helper when deterministic execution,
repeatability, or lower token usage would help.

Good candidates for scripts:
- repeated data fetching or transformation logic
- assertions and verification helpers
- file conversion or scaffolding steps
- CLI wrappers for awkward or verbose commands
"""


def main():
    print("TODO: replace scripts/example.py with a real helper or delete it")


if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Reference Notes for {skill_title}

Use reference docs for detailed information that should not live in SKILL.md.
This file should hold material Claude may need to consult on demand, such as:
- API details
- schemas
- command references
- internal conventions
- long examples
- policy notes

## Suggested contents

- Overview of the system or domain
- Important IDs, enums, or identifiers
- Concrete examples
- Known incompatibilities or caveats
- Search hints if the file becomes large

## Keep in mind

Do not duplicate the entire contents of this file back into SKILL.md.
SKILL.md should point here when detailed reference information is needed.
"""

EXAMPLE_ASSET = """# Example Asset Placeholder

Replace this placeholder with a real asset or delete it.

Useful assets include:
- templates
- starter projects
- boilerplate files
- logos or images
- sample data
- example output documents

Assets are usually meant to be copied, referenced, or modified during the task,
not pasted into SKILL.md.
"""

EXAMPLE_CONFIG = """{
  "example_note": "Store user- or team-specific constants here when needed.",
  "examples": {
    "slack_channel": "C0123456789",
    "dashboard_uid": "abc123",
    "environment": "staging"
  }
}
"""


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def init_skill(skill_name, path):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created

    Returns:
        Path to created skill directory, or None if error
    """
    skill_dir = Path(path).resolve() / skill_name

    if skill_dir.exists():
        print(f"❌ Error: Skill directory already exists: {skill_dir}")
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ Created skill directory: {skill_dir}")
    except Exception as e:
        print(f"❌ Error creating directory: {e}")
        return None

    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title,
    )

    skill_md_path = skill_dir / 'SKILL.md'
    try:
        skill_md_path.write_text(skill_content)
        print("✅ Created SKILL.md")
    except Exception as e:
        print(f"❌ Error creating SKILL.md: {e}")
        return None

    try:
        scripts_dir = skill_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        example_script = scripts_dir / 'example.py'
        example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
        example_script.chmod(0o755)
        print("✅ Created scripts/example.py")

        references_dir = skill_dir / 'references'
        references_dir.mkdir(exist_ok=True)
        example_reference = references_dir / 'reference_notes.md'
        example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
        print("✅ Created references/reference_notes.md")

        assets_dir = skill_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        example_asset = assets_dir / 'example_asset.txt'
        example_asset.write_text(EXAMPLE_ASSET)
        print("✅ Created assets/example_asset.txt")

        config_path = skill_dir / 'config.json'
        config_path.write_text(EXAMPLE_CONFIG)
        print("✅ Created config.json")
    except Exception as e:
        print(f"❌ Error creating resource directories: {e}")
        return None

    print(f"\n✅ Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Rewrite the description so it clearly describes when the skill should trigger")
    print("2. Replace placeholder sections with real workflow guidance and at least one gotcha")
    print("3. Customize or delete the example files in scripts/, references/, assets/, and config.json")
    print("4. Keep SKILL.md lean; move bulky details into references/ and helper logic into scripts/")
    print("5. Run the validator when ready to check the skill structure")

    return skill_dir


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print("Usage: init_skill.py <skill-name> --path <path>")
        print("\nSkill name requirements:")
        print("  - Hyphen-case identifier (e.g., 'data-analyzer')")
        print("  - Lowercase letters, digits, and hyphens only")
        print("  - Max 40 characters")
        print("  - Must match directory name exactly")
        print("\nExamples:")
        print("  init_skill.py my-new-skill --path skills/public")
        print("  init_skill.py my-api-helper --path skills/private")
        print("  init_skill.py custom-skill --path /custom/location")
        sys.exit(1)

    skill_name = sys.argv[1]
    path = sys.argv[3]

    print(f"🚀 Initializing skill: {skill_name}")
    print(f"   Location: {path}")
    print()

    result = init_skill(skill_name, path)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
