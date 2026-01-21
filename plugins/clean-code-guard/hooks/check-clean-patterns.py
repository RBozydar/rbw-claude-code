#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""Block messy code execution patterns and nudge toward clean alternatives.

Blocks:
1. python -c with multi-line scripts (should write proper tests)
2. gemini with heredocs/variable expansion (should use stdin piping)

Escape hatch:
  Add "# clean-code-guard: disable" comment to bypass checks.

Limitations:
- Variable assignment pattern is intentionally broad and may have false positives
  when a variable is assigned early and gemini is called much later with a
  different variable that happens to have a similar name.
- Regex patterns use non-greedy matching which may not handle all edge cases
  with nested quotes perfectly.

When in doubt, use the escape hatch and document why.
"""

import re

from cchooks import PreToolUseContext, create_context

# Threshold for "simple" one-liner python -c scripts (characters)
PYTHON_C_LENGTH_THRESHOLD = 100

# Escape hatch pattern - if present, skip all checks
DISABLE_PATTERN = re.compile(r"#\s*clean-code-guard:\s*disable", re.IGNORECASE)


def check_python_c_pattern(command: str) -> str | None:
    """Check for python -c with substantial inline code.

    Allows simple one-liners but blocks multi-line or complex scripts.

    Limitations:
    - Non-greedy matching may not handle all nested quote scenarios
    - Length threshold is a heuristic, not perfect
    """
    # Pattern: python -c or uv run python -c followed by quoted code
    python_c_pattern = re.compile(
        r"""(?:uv\s+run\s+)?python[3]?\s+-c\s+(['"])(.*?)\1""",
        re.DOTALL,
    )

    match = python_c_pattern.search(command)
    if not match:
        return None

    code = match.group(2)

    # Allow simple one-liners (no newlines, short)
    if "\n" not in code and len(code) < PYTHON_C_LENGTH_THRESHOLD:
        return None

    # Block multi-line or complex inline scripts
    return (
        "Inline python -c scripts are blocked.\n\n"
        "Instead:\n"
        "  1. Write a proper test in tests/ and run pytest\n"
        "  2. For simple checks, read the code and reason about it\n"
        "  3. If you need a REPL, use: uv run python (interactive)\n\n"
        "Escape hatch: Add '# clean-code-guard: disable' comment to bypass.\n\n"
        "See: templates/rules/clean-execution.md"
    )


def check_gemini_heredoc_pattern(command: str) -> str | None:
    """Check for gemini invoked with heredoc or variable expansion patterns.

    Limitations:
    - Variable assignment pattern is intentionally broad to catch the common
      case of VAR=$(cat file); gemini "$VAR". This may false-positive if:
      - Variable is assigned much earlier in a multi-command string
      - A different variable with similar name is used
    - Direct heredoc pattern may match literal strings containing the pattern

    Use escape hatch if you have a legitimate use case.
    """
    if "gemini" not in command.lower():
        return None

    # Pattern 1: $(cat <<EOF or $(cat <<'EOF'
    heredoc_pattern = re.compile(r"""\$\(cat\s+<<['"]?EOF""", re.IGNORECASE)

    # Pattern 2: Variable assignment followed by gemini using that variable
    # e.g., CONTENT=$(cat file); gemini "$CONTENT"
    # Note: Intentionally broad - may have false positives
    var_assign_pattern = re.compile(
        r"""([A-Z_][A-Z0-9_]*)\s*=\s*\$\(.*?\).*?gemini.*?\$\{?\1\}?""",
        re.DOTALL | re.IGNORECASE,
    )

    # Pattern 3: Direct heredoc in gemini args
    direct_heredoc = re.compile(r"""gemini.*["']\$\(cat\s+<<""", re.IGNORECASE)

    if heredoc_pattern.search(command):
        return _gemini_block_message("heredoc")

    if var_assign_pattern.search(command):
        return _gemini_block_message("variable assignment")

    if direct_heredoc.search(command):
        return _gemini_block_message("heredoc")

    return None


def _gemini_block_message(pattern_type: str) -> str:
    return (
        f"Gemini invocation with {pattern_type} is blocked.\n\n"
        "Use stdin piping or @ syntax instead:\n"
        '  cat file.md | gemini --sandbox -o text "Review this"\n'
        '  gemini --sandbox -o text "Review this" @file.md\n'
        '  git diff | gemini --sandbox -o text "Review this diff"\n\n'
        "Or use the wrapper script:\n"
        "  scripts/gemini-review.sh --plan file.md\n"
        "  scripts/gemini-review.sh --diff\n\n"
        "Escape hatch: Add '# clean-code-guard: disable' comment to bypass.\n\n"
        "See: plugins/python-backend/skills/gemini-cli/SKILL.md"
    )


def main() -> None:
    c = create_context()
    if not isinstance(c, PreToolUseContext):
        c.output.exit_success()

    if c.tool_name != "Bash":
        c.output.exit_success()

    command = c.tool_input.get("command", "")

    # Check for escape hatch
    if DISABLE_PATTERN.search(command):
        c.output.exit_success()

    # Check python -c pattern
    python_block = check_python_c_pattern(command)
    if python_block:
        c.output.exit_block(python_block)

    # Check gemini heredoc pattern
    gemini_block = check_gemini_heredoc_pattern(command)
    if gemini_block:
        c.output.exit_block(gemini_block)

    c.output.exit_success()


if __name__ == "__main__":
    main()
