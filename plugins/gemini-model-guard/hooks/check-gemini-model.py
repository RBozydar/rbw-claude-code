#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""Block Gemini 2.x models, enforce Gemini 3 models only."""

import shlex

from cchooks import PreToolUseContext, create_context

# Allowed models - Gemini 3 only
ALLOWED_MODELS = [
    "gemini-3-pro-preview",
    "gemini-3-flash-preview",
]


def extract_model(parts: list[str]) -> str | None:
    """Extract the model name from parsed gemini command parts."""
    for i, part in enumerate(parts):
        if part in ("--model", "-m") and i + 1 < len(parts):
            return parts[i + 1]
        # Handle --model=value format
        if part.startswith("--model="):
            return part.split("=", 1)[1]
    return None


def has_gemini_2_in_name(model: str) -> bool:
    """Check if model name contains '2' (indicating Gemini 2.x family)."""
    return "2" in model


def main() -> None:
    c = create_context()
    if not isinstance(c, PreToolUseContext):
        c.output.exit_success()

    command = c.tool_input.get("command", "")

    # Only check gemini commands
    stripped = command.strip()
    if not (stripped.startswith("gemini ") or stripped == "gemini"):
        c.output.exit_success()

    try:
        parts = shlex.split(command)
    except ValueError:
        c.output.exit_success()  # Let it fail naturally
        return  # For type checker

    # Extract model from command
    model = extract_model(parts)

    # If no model specified, that's fine (will use default)
    if model is None:
        c.output.exit_success()
        return  # For type checker

    # Check if model contains "2" (Gemini 2.x family)
    if has_gemini_2_in_name(model):
        c.output.exit_block(
            f"Gemini model '{model}' is deprecated.\n"
            "Use Gemini 3 models only:\n"
            "  --model gemini-3-pro-preview (recommended)\n"
            "  --model gemini-3-flash-preview (faster/cheaper)"
        )
        return

    c.output.exit_success()


if __name__ == "__main__":
    main()
