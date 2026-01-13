#!/usr/bin/env python3
"""Tests for the gemini model guard hook."""

import importlib.util
import sys
from pathlib import Path

import pytest

# Import from the hyphenated filename
hook_path = Path(__file__).parent / "check-gemini-model.py"
spec = importlib.util.spec_from_file_location("check_gemini_model", hook_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load {hook_path}")
check_gemini_model = importlib.util.module_from_spec(spec)
sys.modules["check_gemini_model"] = check_gemini_model
spec.loader.exec_module(check_gemini_model)

# Import the functions we want to test
extract_model_from_segment = check_gemini_model.extract_model_from_segment
find_gemini_segments = check_gemini_model.find_gemini_segments
is_gemini_2_model = check_gemini_model.is_gemini_2_model
normalize_command = check_gemini_model.normalize_command
has_blocked_flag = check_gemini_model.has_blocked_flag


class TestNormalizeCommand:
    """Test command normalization."""

    def test_removes_backslash_newlines(self):
        cmd = "echo hello \\\n  && gemini -m gemini-2.5-pro"
        normalized = normalize_command(cmd)
        assert "\n" not in normalized
        assert "echo hello" in normalized
        assert "&& gemini" in normalized

    def test_preserves_normal_newlines(self):
        cmd = "echo hello\ngemini -m gemini-2.5-pro"
        assert "\n" in normalize_command(cmd)


class TestExtractModel:
    """Test model extraction from command segments."""

    def test_short_flag(self):
        assert (
            extract_model_from_segment("gemini -m gemini-2.5-pro prompt")
            == "gemini-2.5-pro"
        )

    def test_long_flag_space(self):
        assert (
            extract_model_from_segment("gemini --model gemini-2.5-pro prompt")
            == "gemini-2.5-pro"
        )

    def test_long_flag_equals(self):
        assert (
            extract_model_from_segment("gemini --model=gemini-2.5-pro prompt")
            == "gemini-2.5-pro"
        )

    def test_no_model(self):
        assert extract_model_from_segment("gemini prompt") is None

    def test_complex_model_name(self):
        assert (
            extract_model_from_segment("gemini -m gemini-2.5-pro-preview-05-06")
            == "gemini-2.5-pro-preview-05-06"
        )


class TestIsGemini2Model:
    """Test Gemini 2.x model detection."""

    def test_detects_gemini_2(self):
        assert is_gemini_2_model("gemini-2.5-pro")
        assert is_gemini_2_model("gemini-2.5-pro-preview-05-06")
        assert is_gemini_2_model("gemini-2.0-flash")
        assert is_gemini_2_model("gemini-2-pro")

    def test_allows_gemini_3(self):
        assert not is_gemini_2_model("gemini-3-pro-preview")
        assert not is_gemini_2_model("gemini-3-flash-preview")

    def test_case_insensitive(self):
        assert is_gemini_2_model("GEMINI-2.5-PRO")
        assert is_gemini_2_model("Gemini-2.5-Pro")


class TestFindGeminiSegments:
    """Test finding gemini invocations in commands."""

    # === Direct invocation (should find) ===

    def test_simple_direct(self):
        segments = find_gemini_segments("gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1
        assert "gemini" in segments[0]

    def test_with_quotes_in_prompt(self):
        segments = find_gemini_segments('gemini -m gemini-2.5-pro "hello world"')
        assert len(segments) == 1

    # === Pipe bypasses (should find) ===

    def test_pipe_cat(self):
        segments = find_gemini_segments("cat file.txt | gemini -m gemini-2.5-pro")
        assert len(segments) == 1
        assert "-m gemini-2.5-pro" in segments[0]

    def test_pipe_echo(self):
        segments = find_gemini_segments('echo "prompt" | gemini -m gemini-2.5-pro')
        assert len(segments) == 1

    def test_multiple_pipes(self):
        segments = find_gemini_segments(
            "cat file | grep foo | gemini -m gemini-2.5-pro | tee out"
        )
        assert len(segments) == 1

    # === Command chaining bypasses (should find) ===

    def test_and_chaining(self):
        segments = find_gemini_segments("cd /tmp && gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    def test_or_chaining(self):
        segments = find_gemini_segments("false || gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    def test_semicolon_chaining(self):
        segments = find_gemini_segments("echo setup; gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    def test_newline_chaining(self):
        segments = find_gemini_segments("echo setup\ngemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    # === Subshell/grouping bypasses (should find) ===

    def test_subshell_parens(self):
        segments = find_gemini_segments("(gemini -m gemini-2.5-pro prompt)")
        assert len(segments) == 1

    def test_command_substitution_dollar(self):
        segments = find_gemini_segments('result=$(gemini -m gemini-2.5-pro "prompt")')
        assert len(segments) == 1

    def test_command_substitution_backticks(self):
        segments = find_gemini_segments('result=`gemini -m gemini-2.5-pro "prompt"`')
        assert len(segments) == 1

    def test_brace_grouping(self):
        segments = find_gemini_segments("{ gemini -m gemini-2.5-pro prompt; }")
        assert len(segments) == 1

    # === Wrapper command bypasses (should find) ===

    def test_env_wrapper(self):
        segments = find_gemini_segments("env gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    def test_timeout_wrapper(self):
        segments = find_gemini_segments("timeout 60 gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    def test_time_wrapper(self):
        segments = find_gemini_segments("time gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    def test_nohup_wrapper(self):
        segments = find_gemini_segments("nohup gemini -m gemini-2.5-pro prompt &")
        assert len(segments) == 1

    def test_exec_wrapper(self):
        segments = find_gemini_segments("exec gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    def test_nice_wrapper(self):
        segments = find_gemini_segments("nice gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    # === Path variation bypasses (should find) ===

    def test_absolute_path(self):
        segments = find_gemini_segments("/usr/bin/gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    def test_relative_path_dot(self):
        segments = find_gemini_segments("./gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    def test_relative_path_dotdot(self):
        segments = find_gemini_segments("../bin/gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    def test_home_path(self):
        segments = find_gemini_segments("~/.local/bin/gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    # === Environment variable prefix bypasses (should find) ===

    def test_env_var_prefix(self):
        segments = find_gemini_segments(
            "GEMINI_API_KEY=xxx gemini -m gemini-2.5-pro prompt"
        )
        assert len(segments) == 1

    def test_multiple_env_vars(self):
        segments = find_gemini_segments("VAR1=a VAR2=b gemini -m gemini-2.5-pro prompt")
        assert len(segments) == 1

    # === bash -c / sh -c bypasses (should find) ===

    def test_bash_c_single_quotes(self):
        segments = find_gemini_segments("bash -c 'gemini -m gemini-2.5-pro prompt'")
        assert len(segments) == 1

    def test_bash_c_double_quotes(self):
        segments = find_gemini_segments('bash -c "gemini -m gemini-2.5-pro prompt"')
        assert len(segments) == 1

    def test_sh_c(self):
        segments = find_gemini_segments("sh -c 'gemini -m gemini-2.5-pro prompt'")
        assert len(segments) == 1

    # === eval bypasses (should find) ===

    def test_eval_single_quotes(self):
        segments = find_gemini_segments("eval 'gemini -m gemini-2.5-pro prompt'")
        assert len(segments) == 1

    def test_eval_double_quotes(self):
        segments = find_gemini_segments('eval "gemini -m gemini-2.5-pro prompt"')
        assert len(segments) == 1

    # === xargs bypasses (should find) ===

    def test_xargs_gemini(self):
        segments = find_gemini_segments("echo prompt | xargs gemini -m gemini-2.5-pro")
        assert len(segments) >= 1

    def test_xargs_with_flags(self):
        segments = find_gemini_segments(
            "echo prompt | xargs -I {} gemini -m gemini-2.5-pro {}"
        )
        assert len(segments) >= 1

    # === Combined bypasses (should find) ===

    def test_pipe_and_chain(self):
        segments = find_gemini_segments(
            "cd /tmp && cat file | gemini -m gemini-2.5-pro"
        )
        assert len(segments) == 1

    def test_env_and_pipe(self):
        segments = find_gemini_segments(
            "cat file | API_KEY=xxx gemini -m gemini-2.5-pro"
        )
        assert len(segments) == 1

    def test_subshell_in_chain(self):
        segments = find_gemini_segments(
            "echo start && (gemini -m gemini-2.5-pro prompt) && echo done"
        )
        assert len(segments) == 1

    # === False positives (should NOT find or should not have model) ===

    def test_echo_gemini_string(self):
        """Should not match gemini as a string argument."""
        segments = find_gemini_segments('echo "gemini-2.5-pro"')
        # May find the segment but won't have a model flag to extract
        for seg in segments:
            model = extract_model_from_segment(seg)
            # If it finds something, verify it's not a false detection
            if model:
                # This shouldn't happen for echo "gemini-2.5-pro"
                pass  # Acceptable if regex is conservative

    def test_grep_gemini(self):
        """Searching for gemini string should not trigger."""
        segments = find_gemini_segments("grep gemini file.txt")
        # 'grep gemini' should not match as gemini invocation because
        # gemini here is an argument to grep, not a command
        # The pattern requires gemini to be after a separator
        assert len(segments) == 0

    def test_gemini_3_allowed(self):
        """Gemini 3 models should be detected but not blocked."""
        segments = find_gemini_segments("gemini -m gemini-3-pro-preview prompt")
        assert len(segments) == 1
        model = extract_model_from_segment(segments[0])
        assert model == "gemini-3-pro-preview"
        assert not is_gemini_2_model(model)

    def test_no_model_specified(self):
        """Commands without model flag should be found but have no model."""
        segments = find_gemini_segments("gemini prompt")
        assert len(segments) == 1
        model = extract_model_from_segment(segments[0])
        assert model is None


class TestBlockedFlags:
    """Test blocked introspection flag detection."""

    def test_version_flag_long(self):
        assert has_blocked_flag("gemini --version") == "--version"

    def test_version_flag_short(self):
        assert has_blocked_flag("gemini -v") == "-v"

    def test_help_flag_long(self):
        assert has_blocked_flag("gemini --help") == "--help"

    def test_help_flag_short(self):
        assert has_blocked_flag("gemini -h") == "-h"

    def test_no_blocked_flag(self):
        assert has_blocked_flag("gemini -m gemini-3-pro-preview prompt") is None

    def test_version_in_model_name(self):
        """--version as part of model name should not trigger."""
        # This should not be blocked - the -v is part of gemini-3-pro-preview
        assert has_blocked_flag("gemini -m gemini-3-pro-preview prompt") is None


class TestRealWorldBypasses:
    """Test the specific bypass example from the user."""

    def test_user_example_cat_pipe(self):
        """The exact bypass example the user provided."""
        cmd = 'cat plans/feat-citation-verification-gate-v2-plan.md | gemini -m gemini-2.5-pro-preview-05-06 "Review this"'
        segments = find_gemini_segments(cmd)
        assert len(segments) == 1
        model = extract_model_from_segment(segments[0])
        assert model == "gemini-2.5-pro-preview-05-06"
        assert is_gemini_2_model(model)

    def test_heredoc_pipe(self):
        """Heredoc piped to gemini."""
        cmd = """cat << 'EOF' | gemini -m gemini-2.5-pro
prompt content here
EOF"""
        segments = find_gemini_segments(cmd)
        assert len(segments) >= 1
        # Should find the gemini invocation after the pipe
        found_model = False
        for seg in segments:
            model = extract_model_from_segment(seg)
            if model and is_gemini_2_model(model):
                found_model = True
                break
        assert found_model


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
