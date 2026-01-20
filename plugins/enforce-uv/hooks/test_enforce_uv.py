#!/usr/bin/env python3
"""Tests for the enforce-uv PreToolUse hook."""

import re

import pytest

# Define patterns directly for testing (mirrors the hook's patterns)
SEP = r"(?:^|&&|\|\||;)\s*"

patterns = {
    "python": (rf"{SEP}python(?:\d+(?:\.\d+)?)?(?:\s|$)", "uv run python"),
    "python3": (rf"{SEP}python3(?:\.\d+)?(?:\s|$)", "uv run python"),
    "pip install": (rf"{SEP}pip\s+install", "uv add"),
    "python -m pip": (rf"{SEP}python(?:\d+(?:\.\d+)?)?\s+-m\s+pip\s+install", "uv add"),
    "pypy": (rf"{SEP}pypy[3]?(?:\s|$)", "uv run python"),
    "ipython": (rf"{SEP}ipython[3]?(?:\s|$)", "uv run ipython"),
    "/usr/bin/python": (
        rf"{SEP}/usr/bin/python[23]?(?:\.\d+)?(?:\s|$)",
        "uv run python",
    ),
    "/usr/local/bin/python": (
        rf"{SEP}/usr/local/bin/python[23]?(?:\.\d+)?(?:\s|$)",
        "uv run python",
    ),
    "conda install": (rf"{SEP}conda\s+install", "uv add"),
    "poetry add": (rf"{SEP}poetry\s+add", "uv add"),
    "pipenv install": (rf"{SEP}pipenv\s+install", "uv add"),
    "pytest": (rf"{SEP}pytest(?:\s|$)", "uv run pytest"),
    "ruff": (rf"{SEP}ruff(?:\s|$)", "uvx ruff"),
    "mypy": (rf"{SEP}mypy(?:\s|$)", "uvx mypy"),
}

SHELL_WRAPPER_PATTERNS = [
    (
        r"""(?:ba)?sh\s+-c\s+['"](?:[^'"]*(?:^|[;&|]\s*))?python(?:\d+(?:\.\d+)?)?(?:\s|$)""",
        "python command inside bash -c",
    ),
    (
        r"""eval\s+['"](?:[^'"]*(?:^|[;&|]\s*))?python(?:\d+(?:\.\d+)?)?(?:\s|$)""",
        "python command inside eval",
    ),
    (
        r"""(?:ba)?sh\s+-c\s+['"][^'"]*\bpip[3]?\s+install\b""",
        "pip install inside bash -c",
    ),
    (r"""eval\s+['"][^'"]*\bpip[3]?\s+install\b""", "pip install inside eval"),
    (r"""(?:ba)?sh\s+-c\s+['"][^'"]*\bpytest\b""", "pytest inside bash -c"),
    (r"""eval\s+['"][^'"]*\bpytest\b""", "pytest inside eval"),
]


class TestBasicPatterns:
    """Test basic Python command patterns."""

    def test_python_detected(self):
        pattern = patterns["python"][0]
        assert re.search(pattern, "python script.py")
        assert re.search(pattern, "cd /tmp && python script.py")

    def test_python3_detected(self):
        pattern = patterns["python3"][0]
        assert re.search(pattern, "python3 script.py")

    def test_pip_install_detected(self):
        pattern = patterns["pip install"][0]
        assert re.search(pattern, "pip install requests")
        assert re.search(pattern, "cd /tmp && pip install requests")

    def test_uv_allowed(self):
        """Commands starting with uv should not match patterns."""
        for cmd, (pattern, _) in patterns.items():
            assert not re.search(pattern, "uv run python script.py")
            assert not re.search(pattern, "uvx pytest")


class TestVersionSpecificPython:
    """Test detection of version-specific Python invocations."""

    def test_python3_with_minor_version(self):
        """python3.11, python3.8, etc. should be detected."""
        pattern = patterns["python"][0]
        assert re.search(pattern, "python3.11 script.py")
        assert re.search(pattern, "python3.8 script.py")
        assert re.search(pattern, "python3.12 script.py")
        assert re.search(pattern, "cd /app && python3.11 manage.py")

    def test_python2_with_minor_version(self):
        """python2.7 should be detected."""
        pattern = patterns["python"][0]
        assert re.search(pattern, "python2.7 script.py")
        assert re.search(pattern, "cd /legacy && python2.7 old_script.py")

    def test_python3_pattern_with_minor_version(self):
        """python3 pattern should catch python3.X."""
        pattern = patterns["python3"][0]
        assert re.search(pattern, "python3.11 script.py")
        assert re.search(pattern, "python3.8 -m pip install requests")

    def test_absolute_path_with_version(self):
        """/usr/bin/python3.11 and /usr/local/bin/python3.11 should be detected."""
        # Test /usr/bin patterns
        usr_bin_pattern = patterns["/usr/bin/python"][0]
        assert re.search(usr_bin_pattern, "/usr/bin/python3.11 script.py")
        assert re.search(usr_bin_pattern, "/usr/bin/python3.8 script.py")
        assert re.search(usr_bin_pattern, "/usr/bin/python2.7 legacy.py")

        # Test /usr/local/bin patterns
        usr_local_bin_pattern = patterns["/usr/local/bin/python"][0]
        assert re.search(usr_local_bin_pattern, "/usr/local/bin/python3.11 script.py")
        assert re.search(usr_local_bin_pattern, "/usr/local/bin/python3.8 script.py")
        assert re.search(usr_local_bin_pattern, "/usr/local/bin/python2.7 legacy.py")

    def test_python_m_pip_with_version(self):
        """python3.11 -m pip install should be detected."""
        # Use the "python -m pip" pattern which handles versioned python
        pattern = (
            patterns["python -m pip"][0]
            if "python -m pip" in patterns
            else patterns["python"][0]
        )
        assert re.search(pattern, "python3.11 -m pip install requests")
        assert re.search(pattern, "python3.8 -m pip install numpy")


class TestAlternativeInterpreters:
    """Test detection of alternative Python interpreters."""

    def test_pypy_detected(self):
        pattern = patterns["pypy"][0]
        assert re.search(pattern, "pypy script.py")
        assert re.search(pattern, "pypy3 script.py")

    def test_ipython_detected(self):
        pattern = patterns["ipython"][0]
        assert re.search(pattern, "ipython script.py")

    def test_absolute_path_python_detected(self):
        pattern = patterns["/usr/bin/python"][0]
        assert re.search(pattern, "/usr/bin/python script.py")
        assert re.search(pattern, "/usr/bin/python3 script.py")


class TestPackageManagers:
    """Test detection of alternative package managers."""

    def test_conda_detected(self):
        pattern = patterns["conda install"][0]
        assert re.search(pattern, "conda install numpy")

    def test_poetry_detected(self):
        pattern = patterns["poetry add"][0]
        assert re.search(pattern, "poetry add requests")

    def test_pipenv_detected(self):
        pattern = patterns["pipenv install"][0]
        assert re.search(pattern, "pipenv install requests")


class TestToolPatterns:
    """Test detection of Python tools."""

    def test_pytest_detected(self):
        pattern = patterns["pytest"][0]
        assert re.search(pattern, "pytest tests/")
        assert re.search(pattern, "pytest")  # No args

    def test_ruff_detected(self):
        pattern = patterns["ruff"][0]
        assert re.search(pattern, "ruff check .")

    def test_mypy_detected(self):
        pattern = patterns["mypy"][0]
        assert re.search(pattern, "mypy src/")


class TestShellWrapperPatterns:
    """Test detection of shell wrapper bypass attempts."""

    def test_bash_c_python_detected(self):
        """bash -c 'python ...' should be detected."""
        pattern = SHELL_WRAPPER_PATTERNS[0][0]  # python inside bash -c
        assert re.search(pattern, "bash -c 'python script.py'", re.IGNORECASE)
        assert re.search(pattern, "sh -c 'python script.py'", re.IGNORECASE)

    def test_bash_c_python_versioned(self):
        """bash -c 'python3.11 ...' should be detected."""
        pattern = SHELL_WRAPPER_PATTERNS[0][0]  # python inside bash -c
        assert re.search(pattern, "bash -c 'python3.11 script.py'", re.IGNORECASE)
        assert re.search(pattern, "bash -c 'python3.8 script.py'", re.IGNORECASE)
        assert re.search(pattern, "bash -c 'python2.7 script.py'", re.IGNORECASE)

    def test_eval_python_versioned(self):
        """eval 'python3.11 ...' should be detected."""
        pattern = SHELL_WRAPPER_PATTERNS[1][0]  # python inside eval
        assert re.search(pattern, "eval 'python3.11 script.py'", re.IGNORECASE)
        assert re.search(pattern, "eval 'python3.8 script.py'", re.IGNORECASE)

    def test_bash_c_pip_detected(self):
        """bash -c 'pip install ...' should be detected."""
        pattern = SHELL_WRAPPER_PATTERNS[2][0]  # pip install inside bash -c
        assert re.search(pattern, "bash -c 'pip install requests'", re.IGNORECASE)

    def test_eval_python_detected(self):
        """eval 'python ...' should be detected."""
        pattern = SHELL_WRAPPER_PATTERNS[1][0]  # python inside eval
        assert re.search(pattern, "eval 'python script.py'", re.IGNORECASE)

    def test_echo_python_not_command(self):
        """echo 'python is great' should not trigger shell wrapper patterns."""
        cmd = "echo 'python is a great language'"
        matches = []
        for pattern, desc in SHELL_WRAPPER_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                matches.append(desc)
        assert len(matches) == 0


class TestChainedCommands:
    """Test detection in chained commands."""

    def test_chained_with_and(self):
        pattern = patterns["python"][0]
        assert re.search(pattern, "cd /app && python manage.py runserver")

    def test_chained_with_or(self):
        pattern = patterns["python"][0]
        assert re.search(pattern, "test -f file || python fallback.py")

    def test_chained_with_semicolon(self):
        pattern = patterns["python"][0]
        assert re.search(pattern, "echo hello; python script.py")


class TestEndOfStringCommands:
    """Test that commands at the end of the input (no trailing space) are detected."""

    def test_python_at_end(self):
        """python at end of string should be detected."""
        pattern = patterns["python"][0]
        assert re.search(pattern, "cd /tmp && python")

    def test_python3_at_end(self):
        """python3 at end of string should be detected."""
        pattern = patterns["python3"][0]
        assert re.search(pattern, "ls && python3")

    def test_pytest_at_end(self):
        """pytest at end of string should be detected."""
        pattern = patterns["pytest"][0]
        assert re.search(pattern, "cd /tests && pytest")
        assert re.search(pattern, "pytest")  # Just the command itself

    def test_ruff_at_end(self):
        """ruff at end of string should be detected."""
        pattern = patterns["ruff"][0]
        assert re.search(pattern, "cd /src && ruff")

    def test_mypy_at_end(self):
        """mypy at end of string should be detected."""
        pattern = patterns["mypy"][0]
        assert re.search(pattern, "cd /src && mypy")

    def test_ipython_at_end(self):
        """ipython at end of string should be detected."""
        pattern = patterns["ipython"][0]
        assert re.search(pattern, "cd /notebook && ipython")

    def test_pypy_at_end(self):
        """pypy at end of string should be detected."""
        pattern = patterns["pypy"][0]
        assert re.search(pattern, "cd /app && pypy")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
