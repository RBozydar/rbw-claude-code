from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.convert.converters.codex import convert_claude_to_codex
from src.convert.converters.content import transform_content_for_codex
from src.convert.types import (
    ClaudeAgent,
    ClaudeCommand,
    ClaudeManifest,
    ClaudeMcpServer,
    ClaudePlugin,
    CodexAgentFile,
    CodexBundle,
    CodexPromptFile,
)
from src.convert.writers.codex import (
    render_codex_agent_file,
    render_codex_prompt_file,
    write_codex_bundle,
)


def test_transform_content_for_codex_rewrites_claude_specific_syntax() -> None:
    body = "\n".join(
        [
            "Task core:review:code-simplicity-reviewer(check the diff)",
            'Task 1: research-worker → "Topic A"',
            'Task(subagent_type: "deep_research:gap-detector", prompt: "check the draft")',
            "Run /review and /deep-research and @code-simplicity-reviewer.",
            "If blocked, AskUserQuestion for clarification.",
            "Config lives in ~/.claude/config and .claude/settings.json.",
        ]
    )

    transformed = transform_content_for_codex(
        body,
        prompt_targets={"review": "review", "deep-research": "deep-research"},
        agent_targets={"code-simplicity-reviewer": "code-simplicity-reviewer"},
    )

    assert (
        "Spawn the `code-simplicity-reviewer` agent with this task: check the diff."
        in transformed
    )
    assert "Spawn the `research-worker` agent with this task: Topic A." in transformed
    assert (
        "Spawn the `gap-detector` agent with this task: check the draft."
        in transformed
    )
    assert "/prompts:review" in transformed
    assert "/prompts:deep-research" in transformed
    assert "`code-simplicity-reviewer` agent" in transformed
    assert "ask the user directly" in transformed
    assert "~/.codex/config" in transformed
    assert ".codex/settings.json" in transformed


def test_convert_claude_to_codex_generates_custom_agents_and_prompts() -> None:
    plugin = ClaudePlugin(
        root="/tmp/plugin",
        manifest=ClaudeManifest(name="example", version="1.0.0"),
        agents=[
            ClaudeAgent(
                name="repo-research-analyst",
                description="Map relevant code paths",
                body="Read the relevant files and summarize the findings.",
                source_path="/tmp/plugin/agents/repo-research-analyst.md",
            ),
            ClaudeAgent(
                name="code-simplicity-reviewer",
                description="Review code for unnecessary complexity",
                body=(
                    "Task repo-research-analyst(find simpler patterns)\n"
                    "Then run /workflows:review."
                ),
                source_path="/tmp/plugin/agents/code-simplicity-reviewer.md",
            ),
        ],
        commands=[
            ClaudeCommand(
                name="workflows:review",
                description="Perform a deep review",
                argument_hint="[PR]",
                body=(
                    "Task repo-research-analyst(map the changed code)\n"
                    "If needed, run /plan_review."
                ),
                source_path="/tmp/plugin/commands/workflows/review.md",
            ),
            ClaudeCommand(
                name="plan_review",
                description="Review the implementation plan",
                body="Read the plan and summarize the risks.",
                source_path="/tmp/plugin/commands/plan_review.md",
            ),
        ],
        mcp_servers={
            "context7": ClaudeMcpServer(url="https://mcp.context7.com/mcp"),
        },
    )

    bundle = convert_claude_to_codex(plugin)

    assert [agent.name for agent in bundle.agents] == [
        "repo-research-analyst",
        "code-simplicity-reviewer",
    ]
    reviewer = bundle.agents[1]
    assert reviewer.description == "Review code for unnecessary complexity"
    assert (
        "Spawn the `repo-research-analyst` agent with this task: find simpler patterns."
        in reviewer.developer_instructions
    )
    assert "/prompts:workflows-review" in reviewer.developer_instructions

    rendered = render_codex_agent_file(reviewer, "/tmp")
    assert 'name = "code-simplicity-reviewer"' in rendered
    assert 'description = "Review code for unnecessary complexity"' in rendered
    assert "[mcp_servers.context7]" in rendered
    assert 'url = "https://mcp.context7.com/mcp"' in rendered

    assert [prompt.name for prompt in bundle.prompts] == [
        "workflows-review",
        "plan_review",
    ]
    review_prompt = bundle.prompts[0]
    assert review_prompt.description == "Perform a deep review"
    assert review_prompt.argument_hint == "[PR]"
    assert (
        "Spawn the `repo-research-analyst` agent with this task: map the changed code."
        in review_prompt.body
    )
    assert "/prompts:plan_review" in review_prompt.body

    rendered_prompt = render_codex_prompt_file(review_prompt, "/tmp")
    assert 'description: "Perform a deep review"' in rendered_prompt
    assert 'argument-hint: "[PR]"' in rendered_prompt
    assert "<!-- Generated from plugin/commands/workflows/review.md -->" in rendered_prompt


def test_convert_claude_to_codex_rejects_reserved_and_colliding_names() -> None:
    reserved = ClaudePlugin(
        root="/tmp/plugin",
        manifest=ClaudeManifest(name="example", version="1.0.0"),
        agents=[
            ClaudeAgent(
                name="worker",
                description="Reserved name",
                body="Do work.",
                source_path="/tmp/plugin/agents/worker.md",
            )
        ],
    )
    with pytest.raises(ValueError, match='reserved Codex agent name "worker"'):
        convert_claude_to_codex(reserved)

    colliding = ClaudePlugin(
        root="/tmp/plugin",
        manifest=ClaudeManifest(name="example", version="1.0.0"),
        agents=[
            ClaudeAgent(
                name="Reviewer",
                description="First",
                body="First body.",
                source_path="/tmp/plugin/agents/reviewer-1.md",
            ),
            ClaudeAgent(
                name="reviewer",
                description="Second",
                body="Second body.",
                source_path="/tmp/plugin/agents/reviewer-2.md",
            ),
        ],
    )
    with pytest.raises(ValueError, match='same Codex agent name "reviewer"'):
        convert_claude_to_codex(colliding)

    prompt_collision = ClaudePlugin(
        root="/tmp/plugin",
        manifest=ClaudeManifest(name="example", version="1.0.0"),
        commands=[
            ClaudeCommand(
                name="workflows:review",
                description="First",
                body="First body.",
                source_path="/tmp/plugin/commands/review-1.md",
            ),
            ClaudeCommand(
                name="workflows review",
                description="Second",
                body="Second body.",
                source_path="/tmp/plugin/commands/review-2.md",
            ),
        ],
    )
    with pytest.raises(ValueError, match='same Codex prompt name "workflows-review"'):
        convert_claude_to_codex(prompt_collision)


def test_convert_claude_to_codex_stringifies_structured_argument_hints() -> None:
    plugin = ClaudePlugin(
        root="/tmp/plugin",
        manifest=ClaudeManifest(name="example", version="1.0.0"),
        commands=[
            ClaudeCommand(
                name="heal-skill",
                description="Heal a skill",
                argument_hint=[{"optional": "specific issue to fix"}],
                body="Inspect the target skill and fix it.",
                source_path="/tmp/plugin/commands/heal-skill.md",
            )
        ],
    )

    bundle = convert_claude_to_codex(plugin)

    assert bundle.prompts[0].argument_hint == "optional: specific issue to fix"
    rendered = render_codex_prompt_file(bundle.prompts[0], "/tmp")
    assert 'argument-hint: "optional: specific issue to fix"' in rendered


def test_write_codex_bundle_writes_custom_agent_and_prompt_files(tmp_path: Path) -> None:
    bundle = CodexBundle(
        agents=[
            CodexAgentFile(
                name="reviewer",
                description="Review code changes",
                developer_instructions="Review code like an owner.",
                source_path="/tmp/plugin/agents/reviewer.md",
                mcp_servers={
                    "docs": ClaudeMcpServer(url="https://developers.openai.com/mcp")
                },
            )
        ],
        prompts=[
            CodexPromptFile(
                name="workflows-review",
                description="Review a pull request",
                argument_hint="[PR]",
                body="Review the target thoroughly.",
                source_path="/tmp/plugin/commands/workflows/review.md",
            )
        ],
    )

    write_codex_bundle(str(tmp_path), bundle)

    generated = (tmp_path / ".codex" / "agents" / "reviewer.toml").read_text(
        encoding="utf-8"
    )
    assert generated.startswith("# Generated from ")
    assert 'name = "reviewer"' in generated
    assert "developer_instructions = '''" in generated
    assert "[mcp_servers.docs]" in generated

    prompt = (tmp_path / ".codex" / "prompts" / "workflows-review.md").read_text(
        encoding="utf-8"
    )
    assert prompt.startswith("---\n")
    assert 'description: "Review a pull request"' in prompt
    assert 'argument-hint: "[PR]"' in prompt
    assert "<!-- Generated from " in prompt


def test_write_codex_bundle_rejects_unmanaged_overwrite(tmp_path: Path) -> None:
    target = tmp_path / ".codex" / "agents"
    target.mkdir(parents=True)
    (target / "reviewer.toml").write_text('name = "reviewer"\n', encoding="utf-8")

    bundle = CodexBundle(
        agents=[
            CodexAgentFile(
                name="reviewer",
                description="Review code changes",
                developer_instructions="Review code like an owner.",
                source_path="/tmp/plugin/agents/reviewer.md",
            )
        ]
    )

    with pytest.raises(FileExistsError, match="unmanaged Codex agent file"):
        write_codex_bundle(str(tmp_path), bundle)


def test_write_codex_bundle_rejects_unmanaged_prompt_overwrite(tmp_path: Path) -> None:
    target = tmp_path / ".codex" / "prompts"
    target.mkdir(parents=True)
    (target / "workflows-review.md").write_text(
        "---\ndescription: test\n---\n",
        encoding="utf-8",
    )

    bundle = CodexBundle(
        prompts=[
            CodexPromptFile(
                name="workflows-review",
                description="Review a pull request",
                argument_hint="[PR]",
                body="Review the target thoroughly.",
                source_path="/tmp/plugin/commands/workflows/review.md",
            )
        ]
    )

    with pytest.raises(FileExistsError, match="unmanaged Codex prompt file"):
        write_codex_bundle(str(tmp_path), bundle)
