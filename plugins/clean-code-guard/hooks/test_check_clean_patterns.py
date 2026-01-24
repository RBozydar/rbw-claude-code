#!/usr/bin/env python3
"""Tests for the clean-code-guard PreToolUse hook."""

import importlib.util
import sys
from pathlib import Path

import pytest

# Import from the file
hook_path = Path(__file__).parent / "check-clean-patterns.py"
spec = importlib.util.spec_from_file_location("check_clean_patterns", hook_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load {hook_path}")
check_clean_patterns = importlib.util.module_from_spec(spec)
sys.modules["check_clean_patterns"] = check_clean_patterns
spec.loader.exec_module(check_clean_patterns)

# Import the functions and constants we want to test
check_python_c_pattern = check_clean_patterns.check_python_c_pattern
check_gemini_heredoc_pattern = check_clean_patterns.check_gemini_heredoc_pattern
DISABLE_PATTERN = check_clean_patterns.DISABLE_PATTERN
PYTHON_C_LENGTH_THRESHOLD = check_clean_patterns.PYTHON_C_LENGTH_THRESHOLD
MAX_COMMAND_LENGTH = check_clean_patterns.MAX_COMMAND_LENGTH


class TestPythonCPattern:
    """Test detection of python -c patterns."""

    def test_simple_oneliner_allowed(self):
        """Short one-liners without newlines should be allowed."""
        cmd = 'python -c "print(1+1)"'
        assert check_python_c_pattern(cmd) is None

    def test_uv_run_simple_oneliner_allowed(self):
        """uv run python -c with short one-liner should be allowed."""
        cmd = 'uv run python -c "import sys; print(sys.version)"'
        assert check_python_c_pattern(cmd) is None

    def test_multiline_blocked(self):
        """Multi-line scripts should be blocked."""
        cmd = '''python -c "
import os
print(os.getcwd())
"'''
        result = check_python_c_pattern(cmd)
        assert result is not None
        assert "blocked" in result.lower()

    def test_uv_run_multiline_blocked(self):
        """uv run python -c with multi-line should be blocked."""
        cmd = '''uv run python -c "
from mymodule import Foo
obj = Foo()
print(obj)
"'''
        result = check_python_c_pattern(cmd)
        assert result is not None
        assert "blocked" in result.lower()

    def test_long_oneliner_blocked(self):
        """One-liners exceeding threshold should be blocked."""
        # Create a command longer than PYTHON_C_LENGTH_THRESHOLD
        long_code = "x" * (PYTHON_C_LENGTH_THRESHOLD + 10)
        cmd = f'python -c "{long_code}"'
        result = check_python_c_pattern(cmd)
        assert result is not None

    def test_single_quotes_work(self):
        """Single-quoted code should be detected."""
        cmd = "python -c 'print(1)'"
        assert check_python_c_pattern(cmd) is None

    def test_python3_detected(self):
        """python3 should be detected."""
        cmd = '''python3 -c "
import sys
print(sys.path)
"'''
        result = check_python_c_pattern(cmd)
        assert result is not None

    def test_no_python_c_passes(self):
        """Commands without python -c should pass."""
        assert check_python_c_pattern("python script.py") is None
        assert check_python_c_pattern("uv run pytest") is None
        assert check_python_c_pattern("echo hello") is None

    def test_error_message_has_alternatives(self):
        """Error message should include alternatives."""
        cmd = '''python -c "
import foo
foo.bar()
"'''
        result = check_python_c_pattern(cmd)
        assert "test" in result.lower()
        assert "pytest" in result.lower()
        assert "escape hatch" in result.lower()


class TestGeminiHeredocPattern:
    """Test detection of gemini heredoc/variable patterns."""

    def test_stdin_piping_allowed(self):
        """Stdin piping should be allowed."""
        cmd = 'cat file.md | gemini --sandbox "Review this"'
        assert check_gemini_heredoc_pattern(cmd) is None

    def test_at_syntax_allowed(self):
        """@ file reference syntax should be allowed."""
        cmd = 'gemini --sandbox "Review this" @file.md'
        assert check_gemini_heredoc_pattern(cmd) is None

    def test_git_diff_pipe_allowed(self):
        """Git diff piping should be allowed."""
        cmd = 'git diff | gemini --sandbox -o text "Review this diff"'
        assert check_gemini_heredoc_pattern(cmd) is None

    def test_heredoc_blocked(self):
        """Heredoc pattern should be blocked."""
        cmd = '''gemini --sandbox "$(cat <<EOF
Review this content
EOF
)"'''
        result = check_gemini_heredoc_pattern(cmd)
        assert result is not None
        assert "heredoc" in result.lower()

    def test_variable_assignment_blocked(self):
        """Variable assignment pattern should be blocked."""
        cmd = 'CONTENT=$(cat file.md); gemini --sandbox "$CONTENT"'
        result = check_gemini_heredoc_pattern(cmd)
        assert result is not None
        assert "variable" in result.lower()

    def test_variable_with_braces_blocked(self):
        """Variable with braces should be blocked."""
        cmd = 'PLAN=$(cat plan.md); gemini --sandbox "${PLAN}"'
        result = check_gemini_heredoc_pattern(cmd)
        assert result is not None

    def test_direct_heredoc_in_args_blocked(self):
        """Direct heredoc in gemini args should be blocked."""
        cmd = '''gemini --sandbox "$(cat <<'EOF'
content here
EOF
)"'''
        result = check_gemini_heredoc_pattern(cmd)
        assert result is not None

    def test_no_gemini_passes(self):
        """Commands without gemini should pass."""
        assert check_gemini_heredoc_pattern("cat file.md") is None
        assert check_gemini_heredoc_pattern("echo hello") is None
        assert check_gemini_heredoc_pattern("python script.py") is None

    def test_error_message_has_alternatives(self):
        """Error message should include alternatives."""
        cmd = 'CONTENT=$(cat file.md); gemini "$CONTENT"'
        result = check_gemini_heredoc_pattern(cmd)
        assert "stdin" in result.lower() or "pipe" in result.lower()
        assert "@" in result
        assert "escape hatch" in result.lower()

    def test_case_insensitive(self):
        """Pattern should be case insensitive for gemini."""
        cmd = 'CONTENT=$(cat file); GEMINI "$CONTENT"'
        # Note: uppercase GEMINI is unlikely but pattern should handle it
        result = check_gemini_heredoc_pattern(cmd)
        assert result is not None


class TestEscapeHatch:
    """Test the escape hatch mechanism."""

    def test_disable_comment_matches(self):
        """Disable comment should be detected."""
        cmd = "# clean-code-guard: disable\nsome command"
        assert DISABLE_PATTERN.search(cmd) is not None

    def test_disable_comment_case_insensitive(self):
        """Disable comment should be case insensitive."""
        cmd = "# CLEAN-CODE-GUARD: DISABLE\nsome command"
        assert DISABLE_PATTERN.search(cmd) is not None

    def test_disable_comment_with_spaces(self):
        """Disable comment with varying spaces should match."""
        cmd = "#  clean-code-guard:  disable\nsome command"
        assert DISABLE_PATTERN.search(cmd) is not None

    def test_no_disable_comment(self):
        """Commands without disable comment should not match."""
        cmd = "python -c 'print(1)'"
        assert DISABLE_PATTERN.search(cmd) is None


class TestReDoSProtection:
    """Test ReDoS protection mechanisms."""

    def test_max_command_length_constant(self):
        """MAX_COMMAND_LENGTH should be defined and reasonable."""
        assert MAX_COMMAND_LENGTH > 1000
        assert MAX_COMMAND_LENGTH <= 100000

    def test_long_command_handling(self):
        """Very long commands should not cause issues."""
        # Create a command longer than MAX_COMMAND_LENGTH
        # The actual protection is in main(), but we verify the constant exists
        long_cmd = "x" * (MAX_COMMAND_LENGTH + 100)
        # These functions should handle long input without hanging
        # (actual protection is length check in main before calling these)
        # Just verify they don't crash
        check_python_c_pattern(long_cmd[:1000])  # Truncated for safety
        check_gemini_heredoc_pattern(long_cmd[:1000])


class TestEdgeCases:
    """Test edge cases and potential false positives/negatives."""

    def test_python_c_in_path_not_blocked(self):
        """'python -c' in a file path should not be blocked."""
        cmd = "cat /path/to/python-config.txt"
        assert check_python_c_pattern(cmd) is None

    def test_gemini_in_variable_name_not_blocked(self):
        """'gemini' as part of variable name should be handled."""
        cmd = "GEMINI_API_KEY=xxx python script.py"
        assert check_gemini_heredoc_pattern(cmd) is None

    def test_empty_command(self):
        """Empty command should pass."""
        assert check_python_c_pattern("") is None
        assert check_gemini_heredoc_pattern("") is None

    def test_whitespace_only(self):
        """Whitespace-only command should pass."""
        assert check_python_c_pattern("   ") is None
        assert check_gemini_heredoc_pattern("   ") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
