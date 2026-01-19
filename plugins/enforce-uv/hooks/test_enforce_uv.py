#!/usr/bin/env python3
"""Tests for the enforce-uv PreToolUse hook."""

import re

import pytest

# Define patterns directly for testing (mirrors the hook's patterns)
SEP = r"(?:^|&&|\|\||;)\s*"

patterns = {
    "python": (rf"{SEP}python\s", "uv run python"),
    "python3": (rf"{SEP}python3\s", "uv run python"),
    "pip install": (rf"{SEP}pip\s+install", "uv add"),
    "pypy": (rf"{SEP}pypy[3]?\s", "uv run python"),
    "ipython": (rf"{SEP}ipython[3]?\s", "uv run ipython"),
    "/usr/bin/python": (rf"{SEP}/usr/bin/python[23]?\s", "uv run python"),
    "conda install": (rf"{SEP}conda\s+install", "uv add"),
    "poetry add": (rf"{SEP}poetry\s+add", "uv add"),
    "pipenv install": (rf"{SEP}pipenv\s+install", "uv add"),
    "pytest": (rf"{SEP}pytest(?:\s|$)", "uv run pytest"),
    "ruff": (rf"{SEP}ruff\s", "uvx ruff"),
    "mypy": (rf"{SEP}mypy\s", "uvx mypy"),
}

SHELL_WRAPPER_PATTERNS = [
    (
        r"""(?:ba)?sh\s+-c\s+['"](?:[^'"]*(?:^|[;&|]\s*))?python[23]?\s""",
        "python command inside bash -c",
    ),
    (
        r"""eval\s+['"](?:[^'"]*(?:^|[;&|]\s*))?python[23]?\s""",
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
