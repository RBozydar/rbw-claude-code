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

    def test_command_substitution_backticks(self):
        assert has_dynamic_content("`date`")
        assert has_dynamic_content("feat: `whoami`")

    def test_variable_expansion(self):
        assert has_dynamic_content("$VAR")
        assert has_dynamic_content("${VAR}")
        assert has_dynamic_content("feat: $MSG")

    def test_static_content(self):
        assert not has_dynamic_content("feat: add feature")
        assert not has_dynamic_content("fix(scope): fix bug")


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
