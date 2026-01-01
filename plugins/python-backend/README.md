# Python Backend Plugin

Python-specific development tools for backend codebases, including specialized reviewers and commands for testing and type checking.

## What it does

This plugin extends the core plugin with Python-specific capabilities:
- Specialized code reviewers for Python idioms and patterns
- ML/DS/LLM code review expertise
- Commands for pytest and type checking workflows

## Installation

```bash
claude plugin add ./plugins/python-backend
```

**Recommended:** Also install the core plugin for full functionality:
```bash
claude plugin add ./plugins/core
```

## Components

### Agents (6)

**Review Agents:**

- `kieran-python-reviewer` - Reviews Python code with high quality bar
  - Type hints and modern Python patterns
  - Pythonic idioms and best practices
  - Testability and maintainability focus

- `skeptical-simplicity-reviewer` - Anti-overengineering critique
  - Questions every abstraction
  - Detects Java/C# patterns in Python
  - Champions "simple is better than complex"

- `ml-expert-reviewer` - ML/DS/LLM specialized review
  - Data leakage detection
  - Reproducibility checks
  - LLM integration patterns
  - Model deployment readiness

**External LLM Agents:**

- `gemini-brainstorm` - Second opinion from Gemini
  - Architecture and design decisions
  - Surfaces blind spots through model diversity
  - Compares findings with Claude

- `gemini-reviewer` - Alternative code review from Gemini
  - Different perspective on code quality
  - Highlights consensus and differences
  - Requires Gemini CLI installed

- `gemini-plan-reviewer` - Alternative plan review from Gemini
  - Reviews plans and specifications
  - Surfaces blind spots through model diversity
  - Requires Gemini CLI installed

### Commands (2)

- `/pytest-runner` - Smart pytest execution
  - Automatic configuration detection
  - Parallel execution support
  - Git-aware test discovery
  - Failure analysis with suggestions

- `/type-check` - Intelligent type checking
  - Auto-detect mypy/pyright
  - Incremental checking
  - Error categorization
  - Quick fix suggestions

## Usage

### Code Review

The reviewers are automatically invoked by the core plugin's `/workflows:review` command when Python files are detected.

You can also invoke them directly:

```bash
# Via Task tool
Task kieran-python-reviewer: "Review the user service implementation"
Task skeptical-simplicity-reviewer: "Check this code for over-engineering"
Task ml-expert-reviewer: "Review the training pipeline for data leakage"
```

### Testing

```bash
/pytest-runner                    # Run all tests
/pytest-runner tests/unit/        # Run specific tests
/pytest-runner affected           # Run tests for changed files
/pytest-runner --coverage         # Include coverage report
```

### Type Checking

```bash
/type-check                       # Check all files
/type-check src/services/         # Check specific module
/type-check affected              # Check changed files only
/type-check --strict              # Enable strict mode
```

## Integration with Core Plugin

When used with the core plugin:

1. `/workflows:review` automatically includes Python reviewers for `.py` files
2. `/workflows:work` uses pytest and type checking for quality gates
3. `/plan_review` includes Python-specific perspectives

## Requirements

- Python 3.10+ (for modern type syntax)
- pytest (for `/pytest-runner`)
- mypy or pyright (for `/type-check`)
- uv, poetry, or pip for package management
- Gemini CLI (optional, for Gemini agents)
