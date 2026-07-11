#!/usr/bin/env python3
"""Tests for the gh-api-guard PreToolUse hook."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

# Import from the file
hook_path = Path(__file__).parent / "check-gh-api.py"
spec = importlib.util.spec_from_file_location("check_gh_api", hook_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load {hook_path}")
check_gh_api_module = importlib.util.module_from_spec(spec)
sys.modules["check_gh_api"] = check_gh_api_module
spec.loader.exec_module(check_gh_api_module)

# Import functions to test
extract_endpoint = check_gh_api_module.extract_endpoint
check_for_dangerous_method = check_gh_api_module.check_for_dangerous_method
check_blocked_subcommands = check_gh_api_module.check_blocked_subcommands


def run_hook(command: str) -> subprocess.CompletedProcess[str]:
    """Run the hook with a complete Claude Code PreToolUse payload."""
    payload = {
        "session_id": "test-session",
        "transcript_path": "/tmp/test-transcript.jsonl",
        "cwd": str(Path.cwd()),
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }
    return subprocess.run(
        [str(hook_path)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


class TestHookBoundary:
    """Test behavior through the real hook process."""

    def test_user_reported_compound_read_commands_are_allowed(self) -> None:
        command = (
            "gh pr view 5 --json comments --jq '.comments | length' 2>&1; "
            "gh api repos/RBozydar/cat_tracker/pulls/5/comments "
            "--jq 'length' 2>&1"
        )

        result = run_hook(command)

        assert result.returncode == 0, result.stdout + result.stderr

    @pytest.mark.parametrize(
        "command",
        [
            "gh api repos/owner/repo/issues/1/comments -f body=write",
            "gh api repos/owner/repo/issues/1/comments --method POST -f body=write",
            "gh api --method=DELETE repos/owner/repo/issues/1/comments",
            "gh api graphql -f 'query=mutation { closeIssue(input: {}) { clientMutationId } }'",
            "gh api graphql -f query=@mutation.graphql",
            "bash -c 'gh pr merge 123'",
            "bash -lc 'gh pr merge 123'",
            "gh pr view 123; gh pr merge 123",
            "gh --repo owner/repo pr merge 123",
            "gh --hostname github.example api repos/owner/repo/issues -f title=write",
        ],
    )
    def test_mutations_are_blocked(self, command: str) -> None:
        result = run_hook(command)

        assert result.returncode == 2

    @pytest.mark.parametrize(
        "command",
        [
            "gh api graphql -f 'query=query { viewer { login } }'",
            "gh api graphql -f 'query=query { repository(name: \"mutation\") { id } }'",
            "gh api 'repos/owner/repo/pulls/1/comments?per_page=100'",
            "gh api repos/owner/repo/issues -X GET -f state=open",
            "cd /tmp && gh api repos/owner/repo/pulls/1/comments",
            "bash -c 'gh pr view 123'",
            "gh ruleset view 1",
            "printf 'example: gh pr merge 123'",
        ],
    )
    def test_safe_github_commands_are_allowed(self, command: str) -> None:
        result = run_hook(command)

        assert result.returncode == 0, result.stdout + result.stderr


class TestExtractEndpoint:
    """Test API endpoint extraction from command parts."""

    def test_simple_endpoint(self):
        parts = ["gh", "api", "repos/owner/repo/pulls/123/comments"]
        assert extract_endpoint(parts) == "repos/owner/repo/pulls/123/comments"

    def test_with_method_flag(self):
        parts = ["gh", "api", "-X", "GET", "repos/owner/repo"]
        assert extract_endpoint(parts) == "repos/owner/repo"

    def test_with_jq_flag(self):
        parts = ["gh", "api", "--jq", ".[] | .body", "repos/owner/repo/pulls"]
        assert extract_endpoint(parts) == "repos/owner/repo/pulls"

    def test_with_multiple_flags(self):
        parts = [
            "gh",
            "api",
            "-H",
            "Accept: application/json",
            "-q",
            ".data",
            "repos/owner/repo",
        ]
        assert extract_endpoint(parts) == "repos/owner/repo"

    def test_no_endpoint(self):
        parts = ["gh", "api", "-X", "GET"]
        assert extract_endpoint(parts) is None


class TestCheckForDangerousMethod:
    """Test detection of dangerous HTTP methods."""

    def test_get_allowed(self):
        parts = ["gh", "api", "-X", "GET", "repos/owner/repo"]
        assert check_for_dangerous_method(parts) is None

    def test_post_blocked(self):
        parts = ["gh", "api", "-X", "POST", "repos/owner/repo"]
        assert check_for_dangerous_method(parts) == "POST"

    def test_delete_blocked(self):
        parts = ["gh", "api", "-X", "DELETE", "repos/owner/repo"]
        assert check_for_dangerous_method(parts) == "DELETE"

    def test_patch_blocked(self):
        parts = ["gh", "api", "-X", "PATCH", "repos/owner/repo"]
        assert check_for_dangerous_method(parts) == "PATCH"

    def test_put_blocked(self):
        parts = ["gh", "api", "-X", "PUT", "repos/owner/repo"]
        assert check_for_dangerous_method(parts) == "PUT"

    def test_case_insensitive(self):
        parts = ["gh", "api", "-X", "post", "repos/owner/repo"]
        assert check_for_dangerous_method(parts) == "POST"


class TestCheckBlockedSubcommands:
    """Test detection of blocked gh subcommands."""

    def test_repo_delete_blocked(self):
        reason = check_blocked_subcommands("gh repo delete owner/repo")
        assert reason is not None
        assert "delete" in reason.lower()

    def test_pr_merge_blocked(self):
        reason = check_blocked_subcommands("gh pr merge 123")
        assert reason is not None
        assert "merge" in reason.lower()

    def test_secret_set_blocked(self):
        reason = check_blocked_subcommands("gh secret set MY_SECRET")
        assert reason is not None
        assert "secret" in reason.lower()

    def test_graphql_mutation_blocked(self):
        reason = check_blocked_subcommands("gh api graphql -f query='mutation { ... }'")
        assert reason is not None
        assert "mutation" in reason.lower()

    def test_pr_view_allowed(self):
        reason = check_blocked_subcommands("gh pr view 123")
        assert reason is None

    def test_issue_list_allowed(self):
        reason = check_blocked_subcommands("gh issue list")
        assert reason is None


class TestJqPipeHandling:
    """Test that jq pipes inside arguments don't break parsing."""

    def test_jq_with_pipe_extracts_correctly(self):
        """gh api --jq '.[] | .body' should parse correctly."""
        # The pipe inside jq should NOT be treated as command separator
        parts = ["gh", "api", "--jq", ".[] | .body", "repos/owner/repo/pulls"]
        endpoint = extract_endpoint(parts)
        assert endpoint == "repos/owner/repo/pulls"

    def test_complex_jq_filter(self):
        """Complex jq filters with multiple pipes should work."""
        parts = [
            "gh",
            "api",
            "--jq",
            '.[] | select(.state == "open") | .title',
            "repos/owner/repo/issues",
        ]
        endpoint = extract_endpoint(parts)
        assert endpoint == "repos/owner/repo/issues"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
