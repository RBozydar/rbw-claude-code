#!/usr/bin/env python3
"""Tests for the gh-api-guard PreToolUse hook."""

import importlib.util
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
SHELL_WRAPPER_PATTERN = check_gh_api_module.SHELL_WRAPPER_PATTERN


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


class TestShellWrapperPattern:
    """Test detection of shell wrapper bypass attempts."""

    def test_bash_c_with_gh(self):
        cmd = "bash -c 'gh repo delete owner/repo'"
        assert SHELL_WRAPPER_PATTERN.search(cmd)

    def test_sh_c_with_gh(self):
        cmd = "sh -c 'gh pr merge 123'"
        assert SHELL_WRAPPER_PATTERN.search(cmd)

    def test_eval_with_gh(self):
        cmd = 'eval "gh secret set KEY"'
        assert SHELL_WRAPPER_PATTERN.search(cmd)

    def test_no_wrapper(self):
        cmd = "gh pr view 123"
        assert not SHELL_WRAPPER_PATTERN.search(cmd)


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
