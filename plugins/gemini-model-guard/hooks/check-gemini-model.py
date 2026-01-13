#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""Block Gemini 2.x models, enforce Gemini 3 models only.

This hook scans the entire command for gemini invocations, catching:
- Pipes: echo "prompt" | gemini -m model
- Chaining: cd /tmp && gemini -m model
- Subshells: (gemini -m model), $(gemini -m model)
- Wrappers: env/timeout/exec/nohup gemini -m model
- Paths: /usr/bin/gemini, ./gemini
- Env vars: VAR=x gemini -m model
- Indirect: bash -c 'gemini -m model', eval 'gemini ...'
- Blocks: gemini --version, gemini --help (introspection)
"""

import re
import shlex

from cchooks import PreToolUseContext, create_context

# Blocked introspection flags - these reveal CLI info or bypass model checks
BLOCKED_FLAGS = ["--version", "-v", "--help", "-h"]

# Allowed models - Gemini 3 only
ALLOWED_MODELS = [
    "gemini-3-pro-preview",
    "gemini-3-flash-preview",
]

# Pattern to find gemini command invocations anywhere in the command
# Matches after: start of string, separators (;&|), grouping (({`), newlines, pipes, whitespace
GEMINI_INVOCATION_PATTERN = re.compile(
    r"""
    (?:^|[;&|`({\n])              # Start or separator/grouping
    \s*                            # Optional whitespace
    (?:                            # Optional prefix group:
        (?:env|exec|nohup|nice|ionice|time|strace|ltrace)\s+  # Simple command wrappers (no args)
        |
        timeout\s+\S+\s+           # timeout with its duration argument
        |
        (?:[A-Z_][A-Z0-9_]*=\S*\s+)*  # Env var assignments (VAR=value)
    )?
    (?:["'])?                      # Optional opening quote on command
    (?:[./~][^\s"']*)?             # Optional path prefix (/, ./, ~/, ../etc)
    gemini                         # The command itself
    (?:["'])?                      # Optional closing quote
    (?=\s|$)                       # Must be followed by whitespace or end (word boundary)
    """,
    re.VERBOSE | re.MULTILINE,
)

# Pattern for bash -c / sh -c containing gemini
BASH_C_PATTERN = re.compile(
    r"""(?:ba)?sh\s+-c\s+(['"])(.+?)\1""",
    re.DOTALL,
)

# Pattern for eval containing potential gemini calls
EVAL_PATTERN = re.compile(
    r"""eval\s+(['"])(.+?)\1""",
    re.DOTALL,
)

# Pattern for xargs potentially invoking gemini
XARGS_PATTERN = re.compile(
    r"""xargs\s+(?:-[^\s]*\s+)*(?:[^\s|;&]+\s+)*gemini\b""",
)

# Pattern to extract model from a command segment
MODEL_FLAG_PATTERN = re.compile(
    r"""(?:--model[=\s]|-m\s+)([\w./-]+)""",
)


def normalize_command(command: str) -> str:
    """Normalize command for easier parsing."""
    # Remove backslash-newline continuations
    return re.sub(r"\\\n\s*", " ", command)


def extract_model_from_segment(segment: str) -> str | None:
    """Extract model from a command segment containing gemini."""
    # First try regex (handles more edge cases)
    match = MODEL_FLAG_PATTERN.search(segment)
    if match:
        return match.group(1)

    # Fall back to shlex parsing for clean commands
    try:
        parts = shlex.split(segment)
        for i, part in enumerate(parts):
            if part in ("--model", "-m") and i + 1 < len(parts):
                return parts[i + 1]
            if part.startswith("--model="):
                return part.split("=", 1)[1]
    except ValueError:
        pass  # Malformed command, rely on regex result

    return None


def find_gemini_segments(command: str) -> list[str]:
    """Find all segments of command that invoke gemini with arguments."""
    command = normalize_command(command)
    segments: list[str] = []

    # Find direct gemini invocations
    for match in GEMINI_INVOCATION_PATTERN.finditer(command):
        # Get position right after the match
        start = match.end()
        # Find the rest of this command (until separator or end)
        rest = command[start:]
        # End at next unquoted separator
        end_match = re.search(r"""(?<!['"\\])[;&|`)\n]|$""", rest)
        segment = "gemini " + rest[: end_match.start() if end_match else len(rest)]
        segments.append(segment.strip())

    # Find gemini inside bash -c / sh -c
    for match in BASH_C_PATTERN.finditer(command):
        inner_command = match.group(2)
        if "gemini" in inner_command:
            # Recursively find gemini in the inner command
            inner_segments = find_gemini_segments(inner_command)
            segments.extend(inner_segments)

    # Find gemini inside eval
    for match in EVAL_PATTERN.finditer(command):
        inner_command = match.group(2)
        if "gemini" in inner_command:
            inner_segments = find_gemini_segments(inner_command)
            segments.extend(inner_segments)

    # Find xargs to gemini
    for match in XARGS_PATTERN.finditer(command):
        segment = match.group(0)
        segments.append(segment)

    return segments


def is_gemini_2_model(model: str) -> bool:
    """Check if model name indicates Gemini 2.x family."""
    # Match patterns like gemini-2, gemini-2.0, gemini-2.5-pro-preview-05-06, etc.
    return bool(re.search(r"gemini-2", model, re.IGNORECASE))


def has_blocked_flag(segment: str) -> str | None:
    """Check if segment contains a blocked introspection flag.

    Returns the blocked flag if found, None otherwise.
    """
    try:
        parts = shlex.split(segment)
    except ValueError:
        parts = segment.split()

    for part in parts:
        if part in BLOCKED_FLAGS:
            return part
    return None


def main() -> None:
    c = create_context()
    if not isinstance(c, PreToolUseContext):
        c.output.exit_success()

    command = c.tool_input.get("command", "")

    # Quick check: if "gemini" not in command at all, skip
    if "gemini" not in command.lower():
        c.output.exit_success()

    # Find all gemini invocations in the command
    segments = find_gemini_segments(command)

    if not segments:
        c.output.exit_success()

    # Check each segment for problematic models or blocked flags
    for segment in segments:
        # Check for blocked introspection flags first
        blocked_flag = has_blocked_flag(segment)
        if blocked_flag:
            c.output.exit_block(
                f"Gemini CLI flag '{blocked_flag}' is blocked.\n"
                "Direct gemini CLI introspection is not allowed."
            )

        model = extract_model_from_segment(segment)

        if model is None:
            continue  # No model specified, will use default

        if is_gemini_2_model(model):
            c.output.exit_block(
                f"Gemini model '{model}' is deprecated.\n"
                "Use Gemini 3 models only:\n"
                "  --model gemini-3-pro-preview (recommended)\n"
                "  --model gemini-3-flash-preview (faster/cheaper)"
            )

    c.output.exit_success()


if __name__ == "__main__":
    main()
