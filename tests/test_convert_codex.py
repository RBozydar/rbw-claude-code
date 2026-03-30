from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.convert.converters.codex import convert_claude_to_codex
from src.convert.converters.content import transform_content_for_codex
from src.convert.types import (
    ClaudeAgent,
    ClaudeManifest,
    ClaudeMcpServer,
    ClaudePlugin,
    CodexAgentFile,
    CodexBundle,
)
from src.convert.writers.codex import render_codex_agent_file, write_codex_bundle


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
    assert "/review" in transformed
    assert "/deep-research" in transformed
    assert "`code-simplicity-reviewer` agent" in transformed
    assert "ask the user directly" in transformed
    assert "~/.codex/config" in transformed
    assert ".codex/settings.json" in transformed


def test_convert_claude_to_codex_generates_custom_agents() -> None:
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
                body="Task repo-research-analyst(find simpler patterns)",
                source_path="/tmp/plugin/agents/code-simplicity-reviewer.md",
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

    rendered = render_codex_agent_file(reviewer, "/tmp")
    assert 'name = "code-simplicity-reviewer"' in rendered
    assert 'description = "Review code for unnecessary complexity"' in rendered
    assert "[mcp_servers.context7]" in rendered
    assert 'url = "https://mcp.context7.com/mcp"' in rendered


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


def test_write_codex_bundle_writes_custom_agent_files(tmp_path: Path) -> None:
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
        ]
    )

    write_codex_bundle(str(tmp_path), bundle)

    generated = (tmp_path / ".codex" / "agents" / "reviewer.toml").read_text(
        encoding="utf-8"
    )
    assert generated.startswith("# Generated from ")
    assert 'name = "reviewer"' in generated
    assert "developer_instructions = '''" in generated
    assert "[mcp_servers.docs]" in generated


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
