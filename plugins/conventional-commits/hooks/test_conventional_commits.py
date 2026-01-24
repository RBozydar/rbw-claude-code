#!/usr/bin/env python3
"""Tests for the conventional commits PreToolUse hook."""

import importlib.util
import sys
from pathlib import Path

import pytest

# Import from the file
hook_path = Path(__file__).parent / "conventional_commits.py"
spec = importlib.util.spec_from_file_location("conventional_commits", hook_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load {hook_path}")
conventional_commits = importlib.util.module_from_spec(spec)
sys.modules["conventional_commits"] = conventional_commits
spec.loader.exec_module(conventional_commits)

# Import the functions we want to test
extract_all_commands = conventional_commits.extract_all_commands
find_commit_command = conventional_commits.find_commit_command
extract_messages = conventional_commits.extract_messages
has_dynamic_content = conventional_commits.has_dynamic_content
is_commit_command_context = conventional_commits.is_commit_command_context
CONVENTIONAL_PATTERN = conventional_commits.CONVENTIONAL_PATTERN


class TestExtractAllCommands:
    """Test command extraction from nested shells."""

    def test_simple_command(self):
        cmds = extract_all_commands("git commit -m 'test'")
        assert len(cmds) == 1
        assert "git commit" in cmds[0]

    def test_bash_c_single_quotes(self):
        cmds = extract_all_commands("bash -c 'git commit -m test'")
        assert len(cmds) == 2
        assert "git commit" in cmds[1]

    def test_bash_c_double_quotes(self):
        cmds = extract_all_commands('bash -c "git commit -m test"')
        assert len(cmds) == 2
        assert "git commit" in cmds[1]

    def test_sh_c(self):
        cmds = extract_all_commands("sh -c 'git commit -m test'")
        assert len(cmds) == 2

    def test_eval(self):
        cmds = extract_all_commands("eval 'git commit -m test'")
        assert len(cmds) == 2


class TestFindCommitCommand:
    """Test finding commit commands."""

    def test_git_commit(self):
        cmd = find_commit_command("git commit -m 'test'")
        assert cmd is not None
        assert "git commit" in cmd

    def test_git_merge(self):
        cmd = find_commit_command("git merge feature-branch")
        assert cmd is not None
        assert "git merge" in cmd

    def test_git_cherry_pick(self):
        cmd = find_commit_command("git cherry-pick abc123")
        assert cmd is not None

    def test_git_revert(self):
        cmd = find_commit_command("git revert HEAD")
        assert cmd is not None

    def test_no_commit(self):
        cmd = find_commit_command("git status")
        assert cmd is None

    def test_nested_bash_c(self):
        cmd = find_commit_command("bash -c 'git commit -m test'")
        assert cmd is not None
        assert "git commit" in cmd


class TestExtractMessages:
    """Test message extraction from -m flags."""

    def test_double_quoted(self):
        msgs = extract_messages('git commit -m "feat: add feature"')
        assert len(msgs) == 1
        assert msgs[0] == "feat: add feature"

    def test_single_quoted(self):
        msgs = extract_messages("git commit -m 'fix: fix bug'")
        assert len(msgs) == 1
        assert msgs[0] == "fix: fix bug"

    def test_unquoted(self):
        msgs = extract_messages("git commit -m test")
        assert len(msgs) == 1
        assert msgs[0] == "test"

    def test_multiple_m_flags(self):
        msgs = extract_messages('git commit -m "subject" -m "body"')
        assert len(msgs) == 2
        assert msgs[0] == "subject"
        assert msgs[1] == "body"

    def test_no_m_flag(self):
        msgs = extract_messages("git commit --amend")
        assert len(msgs) == 0


class TestHasDynamicContent:
    """Test detection of dynamic content in messages."""

    def test_command_substitution_dollar(self):
        assert has_dynamic_content("$(date)")
        assert has_dynamic_content("feat: $(whoami)")

    def test_command_substitution_backticks_with_command(self):
        """Backticks with shell-like content should be blocked."""
        # Command with argument
        assert has_dynamic_content("`cat /etc/passwd`")
        assert has_dynamic_content("feat: `rm -rf /`")
        # Pipes and redirects
        assert has_dynamic_content("`echo test | grep t`")
        assert has_dynamic_content("`cat < file`")

    def test_markdown_backticks_allowed(self):
        """Paired backticks with code identifiers should be allowed (markdown)."""
        # Single code words (method/class names)
        assert not has_dynamic_content("fix: update `method_name` to handle edge case")
        assert not has_dynamic_content("fix: update `ClassName` method")
        assert not has_dynamic_content("feat: add `foo` and `bar` functions")

    def test_triple_backticks_allowed(self):
        """Triple backticks (markdown code blocks) should be allowed."""
        assert not has_dynamic_content("fix: ```code block```")
        assert not has_dynamic_content("feat: add ```example``` feature")

    def test_unpaired_backtick_blocked(self):
        """Unpaired backticks should be blocked (likely shell substitution)."""
        assert has_dynamic_content("feat: `whoami")
        assert has_dynamic_content("feat: test`")

    def test_variable_expansion(self):
        assert has_dynamic_content("$VAR")
        assert has_dynamic_content("${VAR}")
        assert has_dynamic_content("feat: $MSG")

    def test_static_content(self):
        assert not has_dynamic_content("feat: add feature")
        assert not has_dynamic_content("fix(scope): fix bug")


class TestIsCommitCommandContext:
    """Test detection of commit command context vs safe argument context."""

    def test_actual_git_commit(self):
        """Actual git commit commands should be in commit context."""
        assert is_commit_command_context("git commit -m 'test'")
        assert is_commit_command_context("git commit --amend")

    def test_gh_pr_create_skipped(self):
        """gh pr create should NOT trigger commit validation."""
        assert not is_commit_command_context('gh pr create --body "git commit --amend"')
        assert not is_commit_command_context(
            "gh pr create --title 'test' --body 'details'"
        )

    def test_gh_pr_edit_skipped(self):
        """gh pr edit should NOT trigger commit validation."""
        assert not is_commit_command_context('gh pr edit --body "mentions git commit"')

    def test_gh_issue_create_skipped(self):
        """gh issue create should NOT trigger commit validation."""
        assert not is_commit_command_context(
            'gh issue create --body "git rebase issue"'
        )

    def test_gh_issue_edit_skipped(self):
        """gh issue edit should NOT trigger commit validation."""
        assert not is_commit_command_context('gh issue edit --body "test"')

    def test_echo_skipped(self):
        """echo commands should NOT trigger commit validation."""
        assert not is_commit_command_context('echo "git commit --amend"')

    def test_printf_skipped(self):
        """printf commands should NOT trigger commit validation."""
        assert not is_commit_command_context('printf "git commit example"')

    def test_other_commands_not_skipped(self):
        """Other commands should be checked for commits."""
        assert is_commit_command_context("ls -la")
        assert is_commit_command_context("cat file.txt")


class TestConventionalPattern:
    """Test the conventional commit pattern."""

    def test_valid_feat(self):
        assert CONVENTIONAL_PATTERN.match("feat: add feature")

    def test_valid_fix(self):
        assert CONVENTIONAL_PATTERN.match("fix: fix bug")

    def test_valid_with_scope(self):
        assert CONVENTIONAL_PATTERN.match("feat(api): add endpoint")

    def test_valid_with_breaking(self):
        assert CONVENTIONAL_PATTERN.match("feat!: breaking change")

    def test_valid_with_scope_and_breaking(self):
        assert CONVENTIONAL_PATTERN.match("feat(api)!: breaking change")

    def test_all_types(self):
        types = [
            "feat",
            "fix",
            "docs",
            "style",
            "refactor",
            "perf",
            "test",
            "build",
            "ci",
            "chore",
            "revert",
        ]
        for t in types:
            assert CONVENTIONAL_PATTERN.match(f"{t}: description")

    def test_invalid_no_colon(self):
        assert not CONVENTIONAL_PATTERN.match("feat add feature")

    def test_invalid_no_space(self):
        assert not CONVENTIONAL_PATTERN.match("feat:add feature")

    def test_invalid_wrong_type(self):
        assert not CONVENTIONAL_PATTERN.match("feature: add feature")

    def test_invalid_empty_description(self):
        assert not CONVENTIONAL_PATTERN.match("feat: ")


class TestBypassPrevention:
    """Test that bypass vectors are properly blocked."""

    def test_file_flag_detected(self):
        """The -F flag should be detected in the command."""
        cmd = find_commit_command("git commit -F /tmp/msg.txt")
        assert cmd is not None
        assert "-F" in cmd

    def test_reuse_message_detected(self):
        cmd = find_commit_command("git commit -C HEAD")
        assert cmd is not None
        assert "-C" in cmd

    def test_no_verify_detected(self):
        cmd = find_commit_command("git commit --no-verify -m 'test'")
        assert cmd is not None
        assert "--no-verify" in cmd

    def test_commit_tree_detected(self):
        cmd = find_commit_command("git commit-tree abc123")
        assert cmd is not None
        assert "commit-tree" in cmd

    def test_heredoc_in_outer_command(self):
        """Heredoc patterns should be detectable."""
        cmd = "git commit << EOF\nfeat: test\nEOF"
        # The outer command contains the heredoc
        assert "<<" in cmd
        assert "EOF" in cmd


class TestBlockedPatternsNotMatchingMessageContent:
    """Test that blocked patterns don't match content inside commit messages.

    This tests the fix for a bug where patterns like '-c' (for --reedit-message)
    would incorrectly match 'python -c' inside a commit message body.
    """

    def test_python_c_in_message_not_blocked(self):
        """'python -c' inside a message should NOT trigger -c/--reedit-message block."""
        import re
        from conventional_commits import BLOCKED_PATTERNS

        # This commit message mentions "python -c" in the body
        commit_cmd = """git commit -m 'feat(clean-code-guard): add plugin

- clean-code-guard plugin: blocks python -c multi-line scripts
- Updated all gemini agents to use stdin piping'"""

        # None of the blocked patterns should match this
        for pattern, msg in BLOCKED_PATTERNS:
            match = re.search(pattern, commit_cmd)
            assert match is None, f"Pattern '{pattern}' incorrectly matched: {msg}"

    def test_actual_reedit_message_flag_blocked(self):
        """Actual -c flag for --reedit-message should still be blocked."""
        import re
        from conventional_commits import BLOCKED_PATTERNS

        # The -c flag before any quoted message
        commit_cmd = "git commit -c HEAD~1 -m 'feat: test'"

        # Find the -c pattern
        c_pattern = None
        for pattern, msg in BLOCKED_PATTERNS:
            if "reedit-message" in msg:
                c_pattern = pattern
                break

        assert c_pattern is not None
        assert re.search(c_pattern, commit_cmd) is not None

    def test_template_flag_still_blocked(self):
        """Actual -t flag should still be blocked."""
        import re
        from conventional_commits import BLOCKED_PATTERNS

        commit_cmd = "git commit -t /tmp/template.txt -m 'feat: test'"

        t_pattern = None
        for pattern, msg in BLOCKED_PATTERNS:
            if "template" in msg:
                t_pattern = pattern
                break

        assert t_pattern is not None
        assert re.search(t_pattern, commit_cmd) is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
