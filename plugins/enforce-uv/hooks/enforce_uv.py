#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PreToolUse hook to enforce uv usage in commands."""

import re

from cchooks import PreToolUseContext, create_context


c = create_context()

assert isinstance(c, PreToolUseContext)

if c.tool_name != "Bash":
    c.output.exit_success()

command = c.tool_input.get("command", "")

# Skip if already using uv
if command.startswith(("uv ", "uvx ")):
    c.output.exit_success()

# Separator pattern for detecting commands after && || ; or at start
SEP = r"(?:^|&&|\|\||;)\s*"

# Detect problematic patterns at start of command or after && || ;
patterns = {
    # Standard Python interpreters (including version-specific like python3.11, python2.7)
    "python": (rf"{SEP}python(?:\d+(?:\.\d+)?)?(?:\s|$)", "uv run python"),
    "python3": (rf"{SEP}python3(?:\.\d+)?(?:\s|$)", "uv run python"),
    "python2": (
        rf"{SEP}python2(?:\.\d+)?(?:\s|$)",
        "uv run python (Python 2 is deprecated)",
    ),
    # Absolute paths to Python (including versioned paths like /usr/bin/python3.11)
    "/usr/bin/python": (
        rf"{SEP}/usr/bin/python[23]?(?:\.\d+)?(?:\s|$)",
        "uv run python",
    ),
    "/usr/local/bin/python": (
        rf"{SEP}/usr/local/bin/python[23]?(?:\.\d+)?(?:\s|$)",
        "uv run python",
    ),
    # Alternative Python interpreters
    "pypy": (rf"{SEP}pypy[3]?(?:\s|$)", "uv run python (use standard CPython via uv)"),
    "ipython": (rf"{SEP}ipython[3]?(?:\s|$)", "uv run ipython"),
    "jython": (rf"{SEP}jython(?:\s|$)", "uv run python (Jython is not recommended)"),
    # pip commands (direct and module invocation)
    "pip install": (rf"{SEP}pip\s+install", "uv add"),
    "pip3 install": (rf"{SEP}pip3\s+install", "uv add"),
    "python -m pip": (rf"{SEP}python(?:\d+(?:\.\d+)?)?\s+-m\s+pip\s+install", "uv add"),
    # Alternative package managers
    "conda install": (rf"{SEP}conda\s+install", "uv add (use uv instead of conda)"),
    "mamba install": (rf"{SEP}mamba\s+install", "uv add (use uv instead of mamba)"),
    "poetry add": (rf"{SEP}poetry\s+add", "uv add"),
    "poetry install": (rf"{SEP}poetry\s+install", "uv sync"),
    "pipenv install": (rf"{SEP}pipenv\s+install", "uv add (use uv instead of pipenv)"),
    # Testing tools
    "pytest": (rf"{SEP}pytest(?:\s|$)", "uv run pytest"),
    # Linting/formatting tools
    "ruff": (rf"{SEP}ruff(?:\s|$)", "uvx ruff"),
    "black": (rf"{SEP}black(?:\s|$)", "uvx black"),
    "mypy": (rf"{SEP}mypy(?:\s|$)", "uvx mypy"),
    "flake8": (rf"{SEP}flake8(?:\s|$)", "uvx flake8"),
    "pylint": (rf"{SEP}pylint(?:\s|$)", "uvx pylint"),
}

# Check for eval/bash -c bypasses with Python commands
# These patterns match Python commands ANYWHERE in the wrapped string (not just at start)
# and use word boundaries to avoid matching strings like "echo python"
SHELL_WRAPPER_PATTERNS = [
    # Python interpreter inside shell wrapper - match as command (after ;, &&, ||, or at start)
    # Includes version-specific invocations like python3.11
    (
        r"""(?:ba)?sh\s+-c\s+['"](?:[^'"]*(?:^|[;&|]\s*))?python(?:\d+(?:\.\d+)?)?(?:\s|$)""",
        "python command inside bash -c",
    ),
    (
        r"""eval\s+['"](?:[^'"]*(?:^|[;&|]\s*))?python(?:\d+(?:\.\d+)?)?(?:\s|$)""",
        "python command inside eval",
    ),
    # pip install inside shell wrapper
    (
        r"""(?:ba)?sh\s+-c\s+['"][^'"]*\bpip[3]?\s+install\b""",
        "pip install inside bash -c",
    ),
    (r"""eval\s+['"][^'"]*\bpip[3]?\s+install\b""", "pip install inside eval"),
    # pytest inside shell wrapper
    (r"""(?:ba)?sh\s+-c\s+['"][^'"]*\bpytest\b""", "pytest inside bash -c"),
    (r"""eval\s+['"][^'"]*\bpytest\b""", "pytest inside eval"),
]

# Check standard patterns
for cmd, (pattern, suggestion) in patterns.items():
    if re.search(pattern, command):
        c.output.exit_block(
            f"Use '{suggestion}' instead of bare '{cmd}' in uv projects"
        )

# Check shell wrapper bypass attempts
for pattern, description in SHELL_WRAPPER_PATTERNS:
    if re.search(pattern, command, re.IGNORECASE):
        c.output.exit_block(
            f"Detected {description}. Use uv commands directly without shell wrappers."
        )

c.output.exit_success()
