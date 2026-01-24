#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PostToolUse fallback: warn if gemini 2.x output detected.

This hook runs AFTER bash commands complete and checks if the output
suggests a Gemini 2.x model was used (e.g., if the PreToolUse check
was bypassed through an unforeseen method).

This is a defense-in-depth measure.
"""

import re

from cchooks import PostToolUseContext, create_context

# Patterns that suggest Gemini 2.x was used in output
GEMINI_2_OUTPUT_PATTERNS = [
    r"gemini-2\.[0-9]",
    r"gemini-2-",
    r"model.*gemini-2",
    r"Using model:.*2\.",
]


def main() -> None:
    c = create_context()
    if not isinstance(c, PostToolUseContext):
        c.output.exit_success()

    # Only check successful bash commands
    if c.tool_name != "Bash":
        c.output.exit_success()

    output = c.tool_response.get("stdout", "") + c.tool_response.get("stderr", "")

    # Quick check: if "gemini" not in output, skip
    if "gemini" not in output.lower():
        c.output.exit_success()

    # Check for Gemini 2.x patterns in output
    for pattern in GEMINI_2_OUTPUT_PATTERNS:
        if re.search(pattern, output, re.IGNORECASE):
            # Don't block (command already ran), but warn
            c.output.exit_continue(
                "WARNING: Detected possible Gemini 2.x usage in command output.\n"
                "Gemini 2.x models are deprecated. Please use Gemini 3 models.\n"
                "If this was intentional bypass, please review the gemini-model-guard plugin."
            )

    c.output.exit_success()


if __name__ == "__main__":
    main()
