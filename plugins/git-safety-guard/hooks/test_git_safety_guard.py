#!/usr/bin/env python3
"""Tests for the git-safety-guard PreToolUse hook."""

import re

import pytest

# Define patterns directly for testing (mirrors the hook's patterns)
SAFE_PATTERNS = [
    r"git\s+checkout\s+-b\s",  # Creating a new branch
    r"git\s+checkout\s+--orphan\s",  # Creating orphan branch
    r"git\s+restore\s+--staged",  # Unstaging files (safe)
    r"git\s+clean\s+.*(-n|--dry-run)",  # Dry run mode
]

BLOCKED_PATTERNS = [
    # Working directory destruction
    (
        r"git\s+checkout\s+--\s",
        "git checkout -- discards uncommitted changes permanently",
    ),
    (r"git\s+reset\s+--hard", "git reset --hard destroys all uncommitted work"),
    (r"git\s+clean\s+-[a-zA-Z]*f", "git clean -f permanently deletes untracked files"),
    # Remote/history destruction
    (
        r"git\s+push\s+.*--force",
        "git push --force rewrites remote history (use new commits instead)",
    ),
    (
        r"git\s+push\s+(?:.*\s)?-[a-zA-Z]*f(?:\s|$)",
        "git push -f destroys remote history",
    ),
    (r"git\s+push\s+.*--delete", "git push --delete removes remote branches/tags"),
    (r"git\s+branch\s+-D", "git branch -D force-deletes without merge check"),
    # Saved work destruction
    (
        r"git\s+stash\s+(drop|clear)",
        "git stash drop/clear permanently deletes saved work",
    ),
    # Rebase (rewrites history)
    (
        r"git\s+rebase\b(?!\s+--(abort|continue|skip))",
        "git rebase rewrites commit history",
    ),
]

SHELL_WRAPPER_PATTERN = re.compile(
    r"""(?:(?:ba)?sh\s+-c|eval)\s+['"].*\bgit\s+""",
    re.IGNORECASE,
)

HEREDOC_PATTERN = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?")


class TestSafePatterns:
    """Test that safe patterns are allowed."""

    def test_checkout_new_branch_allowed(self):
        """git checkout -b should be allowed."""
        cmd = "git checkout -b new-feature"
        for pattern in SAFE_PATTERNS:
            if re.search(pattern, cmd):
                return
        pytest.fail("git checkout -b should match a safe pattern")

    def test_restore_staged_allowed(self):
        """git restore --staged should be allowed."""
        cmd = "git restore --staged file.txt"
        for pattern in SAFE_PATTERNS:
            if re.search(pattern, cmd):
                return
        pytest.fail("git restore --staged should match a safe pattern")

    def test_clean_dry_run_allowed(self):
        """git clean -n should be allowed."""
        cmd = "git clean -n"
        for pattern in SAFE_PATTERNS:
            if re.search(pattern, cmd):
                return
        pytest.fail("git clean -n should match a safe pattern")


class TestResetPatterns:
    """Test git reset blocking."""

    def test_reset_hard_blocked(self):
        """git reset --hard should be blocked."""
        cmd = "git reset --hard HEAD~1"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert blocked, "git reset --hard should be blocked"

    def test_reset_soft_allowed(self):
        """git reset --soft should NOT be blocked."""
        cmd = "git reset --soft HEAD~1"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert not blocked, "git reset --soft should NOT be blocked"


class TestPushPatterns:
    """Test git push blocking."""

    def test_push_force_blocked(self):
        """git push --force should be blocked."""
        cmd = "git push --force origin main"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert blocked, "git push --force should be blocked"

    def test_push_f_blocked(self):
        """git push -f should be blocked."""
        cmd = "git push -f origin main"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert blocked, "git push -f should be blocked"

    def test_push_delete_blocked(self):
        """git push --delete should be blocked."""
        cmd = "git push origin --delete feature-branch"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert blocked, "git push --delete should be blocked"

    def test_push_normal_allowed(self):
        """Regular git push should be allowed."""
        cmd = "git push origin main"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert not blocked, "git push should NOT be blocked"


class TestCleanPatterns:
    """Test git clean blocking."""

    def test_clean_f_blocked(self):
        """git clean -f should be blocked."""
        cmd = "git clean -f"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert blocked, "git clean -f should be blocked"

    def test_clean_fd_blocked(self):
        """git clean -fd should be blocked."""
        cmd = "git clean -fd"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert blocked, "git clean -fd should be blocked"


class TestRebasePatterns:
    """Test git rebase blocking."""

    def test_rebase_blocked(self):
        """git rebase should be blocked."""
        cmd = "git rebase main"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert blocked, "git rebase should be blocked"

    def test_rebase_abort_allowed(self):
        """git rebase --abort should be allowed."""
        cmd = "git rebase --abort"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert not blocked, "git rebase --abort should NOT be blocked"

    def test_rebase_continue_allowed(self):
        """git rebase --continue should be allowed."""
        cmd = "git rebase --continue"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert not blocked, "git rebase --continue should NOT be blocked"

    def test_rebase_skip_allowed(self):
        """git rebase --skip should be allowed."""
        cmd = "git rebase --skip"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert not blocked, "git rebase --skip should NOT be blocked"


class TestStashPatterns:
    """Test git stash blocking."""

    def test_stash_drop_blocked(self):
        """git stash drop should be blocked."""
        cmd = "git stash drop"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert blocked, "git stash drop should be blocked"

    def test_stash_clear_blocked(self):
        """git stash clear should be blocked."""
        cmd = "git stash clear"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert blocked, "git stash clear should be blocked"

    def test_stash_push_allowed(self):
        """git stash (push) should be allowed."""
        cmd = "git stash"
        blocked = False
        for pattern, _ in BLOCKED_PATTERNS:
            if re.search(pattern, cmd):
                blocked = True
                break
        assert not blocked, "git stash should NOT be blocked"


class TestShellWrapperPattern:
    """Test shell wrapper bypass detection."""

    def test_bash_c_with_git_detected(self):
        """bash -c with git should be detected."""
        cmd = "bash -c 'git reset --hard'"
        assert SHELL_WRAPPER_PATTERN.search(cmd)

    def test_eval_with_git_detected(self):
        """eval with git should be detected."""
        cmd = "eval 'git push --force'"
        assert SHELL_WRAPPER_PATTERN.search(cmd)

    def test_no_wrapper(self):
        """Command without wrapper should not match."""
        cmd = "git status"
        assert not SHELL_WRAPPER_PATTERN.search(cmd)


class TestHeredocPatterns:
    """Test heredoc bypass detection."""

    def test_heredoc_with_git_detected(self):
        """Heredoc with git commands should be detected."""
        cmd = "bash <<EOF\ngit reset --hard\nEOF"
        assert HEREDOC_PATTERN.search(cmd)

    def test_heredoc_quoted_delimiter(self):
        """Heredoc with quoted delimiter should be detected."""
        cmd = "bash <<'EOF'\ngit push --force\nEOF"
        assert HEREDOC_PATTERN.search(cmd)

    def test_heredoc_double_quoted(self):
        """Heredoc with double-quoted delimiter should be detected."""
        cmd = 'bash <<"EOF"\ngit stash clear\nEOF'
        assert HEREDOC_PATTERN.search(cmd)

    def test_heredoc_with_dash(self):
        """Heredoc with dash (tab stripping) should be detected."""
        cmd = "bash <<-EOF\n\tgit reset --hard\nEOF"
        assert HEREDOC_PATTERN.search(cmd)

    def test_no_heredoc(self):
        """Commands without heredoc should not match."""
        cmd = "git status"
        assert not HEREDOC_PATTERN.search(cmd)

    def test_heredoc_without_git_allowed(self):
        """Heredoc without git commands should be allowed."""
        cmd = "cat <<EOF\nhello world\nEOF"
        assert HEREDOC_PATTERN.search(cmd)
        assert not re.search(r"(ba)?sh\s+.*<<.*git\s+", cmd, re.DOTALL | re.IGNORECASE)

    def test_heredoc_with_bash_and_git(self):
        """Heredoc with bash and git should match blocking pattern."""
        cmd = "bash <<EOF\ngit reset --hard\nEOF"
        assert HEREDOC_PATTERN.search(cmd)
        assert re.search(r"(ba)?sh\s+.*<<.*git\s+", cmd, re.DOTALL | re.IGNORECASE)

    def test_heredoc_multiline_git_detection(self):
        """Heredoc with git on separate line should be detected."""
        cmd = "bash <<EOF\necho 'starting'\ngit push --force origin main\nEOF"
        assert HEREDOC_PATTERN.search(cmd)
        assert re.search(r"<<.*\n.*\bgit\s+", cmd, re.DOTALL | re.IGNORECASE)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
