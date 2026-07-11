#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""Allow read-only GitHub CLI operations and block explicit mutations."""

import os
import re
import shlex
from collections.abc import Iterator, Sequence

from cchooks import PreToolUseContext, create_context


DANGEROUS_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
FIELD_FLAGS = frozenset({"-f", "-F", "--raw-field", "--field"})
INPUT_FLAGS = frozenset({"--input"})
SHELL_PUNCTUATION = frozenset("();<>|&")
GH_GLOBAL_FLAGS_WITH_VALUES = frozenset({"-R", "--repo", "--hostname"})

# Only the mutating members of mixed command families belong here. Read-only
# commands such as `gh ruleset view` and `gh ruleset list` must remain usable.
BLOCKED_SUBCOMMANDS = {
    ("repo", "delete"): "gh repo delete permanently destroys repositories",
    ("repo", "archive"): "gh repo archive requires manual approval",
    ("pr", "merge"): "gh pr merge requires manual approval",
    ("pr", "close"): "gh pr close requires manual approval",
    ("issue", "close"): "gh issue close requires manual approval",
    ("issue", "delete"): "gh issue delete requires manual approval",
    ("secret", "set"): "gh secret set modifies repository secrets",
    ("secret", "delete"): "gh secret delete removes repository secrets",
    ("variable", "set"): "gh variable set modifies repository variables",
    ("variable", "delete"): "gh variable delete removes repository variables",
    ("release", "delete"): "gh release delete requires manual approval",
    ("ruleset", "create"): "gh ruleset create modifies branch protection",
    ("ruleset", "delete"): "gh ruleset delete modifies branch protection",
    ("run", "cancel"): "gh run cancel requires manual approval",
    ("run", "delete"): "gh run delete requires manual approval",
    ("cache", "delete"): "gh cache delete requires manual approval",
}


def tokenize_shell(command: str) -> list[str]:
    """Tokenize a shell command while retaining command separators."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars="();<>|&")
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def split_shell_segments(parts: Sequence[str]) -> Iterator[list[str]]:
    """Yield command segments separated by shell control operators."""
    segment: list[str] = []
    for part in parts:
        if part and all(character in SHELL_PUNCTUATION for character in part):
            if segment:
                yield segment
                segment = []
            continue
        segment.append(part)
    if segment:
        yield segment


def _skip_command_prefix(parts: Sequence[str]) -> int:
    """Return the likely executable position after common command prefixes."""
    index = 0
    while index < len(parts) and re.match(r"^[A-Za-z_]\w*=", parts[index]):
        index += 1

    if index < len(parts) and parts[index] == "env":
        index += 1
        while index < len(parts) and (
            parts[index].startswith("-") or re.match(r"^[A-Za-z_]\w*=", parts[index])
        ):
            index += 1

    while index < len(parts) and parts[index] in {"command", "nohup", "sudo"}:
        index += 1
        while index < len(parts) and parts[index].startswith("-"):
            index += 1

    if index < len(parts) and parts[index] == "timeout":
        index += 1
        while index < len(parts) and parts[index].startswith("-"):
            index += 1
        if index < len(parts):
            index += 1

    return index


def iter_gh_invocations(command: str) -> Iterator[list[str]]:
    """Yield parsed ``gh`` invocations, including safe shell wrappers."""
    parts = tokenize_shell(command)
    for segment in split_shell_segments(parts):
        executable_index = _skip_command_prefix(segment)
        if executable_index >= len(segment):
            continue

        executable = os.path.basename(segment[executable_index])
        if executable in {"bash", "sh", "zsh"}:
            wrapper_args = segment[executable_index + 1 :]
            command_flag_index = next(
                (
                    index
                    for index, argument in enumerate(wrapper_args)
                    if argument == "--command"
                    or re.fullmatch(r"-[^-]*c[^-]*", argument)
                ),
                None,
            )
            if command_flag_index is not None:
                command_index = command_flag_index + 1
                if command_index < len(wrapper_args):
                    yield from iter_gh_invocations(wrapper_args[command_index])
            continue
        if executable == "eval":
            inner_command = " ".join(segment[executable_index + 1 :])
            if inner_command:
                yield from iter_gh_invocations(inner_command)
            continue
        if executable == "gh":
            yield segment[executable_index:]


def extract_endpoint(parts: list[str]) -> str | None:
    """Extract the API endpoint from a parsed ``gh api`` invocation."""
    flags_with_args = {
        "-X",
        "--method",
        "-H",
        "--header",
        "-f",
        "--raw-field",
        "-F",
        "--field",
        "--input",
        "--hostname",
        "--jq",
        "-q",
        "--template",
        "-t",
    }
    skip_next = False
    for part in parts[2:]:
        if skip_next:
            skip_next = False
            continue
        if part in flags_with_args:
            skip_next = True
            continue
        if part.startswith("-"):
            continue
        return part
    return None


def explicit_http_method(parts: Sequence[str]) -> str | None:
    """Return the HTTP method explicitly selected by a ``gh api`` command."""
    for index, part in enumerate(parts):
        if part in {"-X", "--method"} and index + 1 < len(parts):
            return parts[index + 1].upper()
        if part.startswith("--method="):
            return part.partition("=")[2].upper()
    return None


def check_for_dangerous_method(parts: list[str]) -> str | None:
    """Return an explicitly selected dangerous HTTP method, if present."""
    method = explicit_http_method(parts)
    return method if method in DANGEROUS_METHODS else None


def _field_values(parts: Sequence[str]) -> Iterator[str]:
    """Yield values supplied through GitHub API field flags."""
    for index, part in enumerate(parts):
        if part in FIELD_FLAGS and index + 1 < len(parts):
            yield parts[index + 1]
        elif any(part.startswith(f"{flag}=") for flag in FIELD_FLAGS):
            yield part.partition("=")[2]


def normalize_gh_invocation(parts: Sequence[str]) -> list[str]:
    """Remove supported global flags so the command group has a stable position."""
    normalized = [parts[0]]
    index = 1
    while index < len(parts):
        part = parts[index]
        if part in GH_GLOBAL_FLAGS_WITH_VALUES:
            index += 2
            continue
        if any(part.startswith(f"{flag}=") for flag in GH_GLOBAL_FLAGS_WITH_VALUES):
            index += 1
            continue
        break
    normalized.extend(parts[index:])
    return normalized


def effective_http_method(parts: Sequence[str]) -> str:
    """Return the method GitHub CLI will use for a REST API invocation."""
    explicit_method = explicit_http_method(parts)
    if explicit_method is not None:
        return explicit_method
    if any(part in FIELD_FLAGS or part in INPUT_FLAGS for part in parts):
        return "POST"
    if any(
        any(part.startswith(f"{flag}=") for flag in FIELD_FLAGS | INPUT_FLAGS)
        for part in parts
    ):
        return "POST"
    return "GET"


def graphql_has_mutation(document: str) -> bool:
    """Return whether a GraphQL document declares a top-level mutation."""
    index = 0
    brace_depth = 0
    while index < len(document):
        if document.startswith('"""', index):
            end = document.find('"""', index + 3)
            index = len(document) if end == -1 else end + 3
            continue
        character = document[index]
        if character == '"':
            index += 1
            while index < len(document):
                if document[index] == "\\":
                    index += 2
                    continue
                if document[index] == '"':
                    index += 1
                    break
                index += 1
            continue
        if character == "#":
            newline = document.find("\n", index + 1)
            index = len(document) if newline == -1 else newline + 1
            continue
        if character == "{":
            brace_depth += 1
            index += 1
            continue
        if character == "}":
            brace_depth = max(0, brace_depth - 1)
            index += 1
            continue
        if character.isalpha() or character == "_":
            end = index + 1
            while end < len(document) and (
                document[end].isalnum() or document[end] == "_"
            ):
                end += 1
            if brace_depth == 0 and document[index:end].lower() == "mutation":
                return True
            index = end
            continue
        index += 1
    return False


def graphql_mutation_reason(parts: Sequence[str]) -> str | None:
    """Return a block reason for GraphQL mutations or opaque query input."""
    if any(part in INPUT_FLAGS or part.startswith("--input=") for part in parts):
        return (
            "GraphQL input files require manual approval because their operation "
            "is opaque"
        )

    query_values = [
        value.partition("=")[2]
        for value in _field_values(parts)
        if value.startswith("query=")
    ]
    if not query_values:
        return "Could not determine whether the GraphQL operation is read-only"
    if any(query.startswith("@") for query in query_values):
        return (
            "GraphQL query files require manual approval because their operation "
            "is opaque"
        )
    if any(graphql_has_mutation(query) for query in query_values):
        return "GraphQL mutations require manual approval"
    return None


def blocked_invocation_reason(parts: list[str]) -> str | None:
    """Return why a parsed GitHub CLI invocation must be blocked."""
    parts = normalize_gh_invocation(parts)
    lowered = [part.lower() for part in parts]
    if len(lowered) >= 3:
        reason = BLOCKED_SUBCOMMANDS.get((lowered[1], lowered[2]))
        if reason is not None:
            return reason

    if len(lowered) < 2 or lowered[1] != "api":
        return None

    endpoint = extract_endpoint(parts)
    if endpoint == "graphql":
        return graphql_mutation_reason(parts)

    method = effective_http_method(parts)
    if method not in {"GET", "HEAD"}:
        return f"gh api with effective {method} method requires manual approval"
    return None


def check_blocked_subcommands(command: str) -> str | None:
    """Return why any actual ``gh`` invocation in a command is blocked."""
    try:
        invocations = iter_gh_invocations(command)
        for invocation in invocations:
            reason = blocked_invocation_reason(invocation)
            if reason is not None:
                return reason
    except ValueError:
        return "Could not safely parse GitHub CLI command"
    return None


def main() -> None:
    """Validate GitHub CLI invocations in a Claude Code Bash tool call."""
    context = create_context()
    if not isinstance(context, PreToolUseContext):
        context.output.exit_success()

    command = context.tool_input.get("command", "")
    if "gh" not in command.lower():
        context.output.exit_success()

    blocked_reason = check_blocked_subcommands(command)
    if blocked_reason is not None:
        context.output.exit_block(
            f"BLOCKED: {blocked_reason}\n"
            f"Command: {command}\n"
            "If this operation is truly needed, ask the user for explicit permission."
        )
    context.output.exit_success()


if __name__ == "__main__":
    main()
