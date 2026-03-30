from __future__ import annotations

from pathlib import Path

from src.convert.converters.codex import convert_claude_to_codex
from src.convert.converters.content import transform_content_for_codex
from src.convert.types import (
    ClaudeAgent,
    ClaudeCommand,
    ClaudeManifest,
    ClaudeMcpServer,
    ClaudePlugin,
    ClaudeSkill,
    CodexBundle,
    CodexGeneratedSkill,
    CodexInvocationTargets,
    CodexPrompt,
    SkillDir,
)
from src.convert.writers.codex import render_codex_config, write_codex_bundle


def test_transform_content_for_codex_rewrites_claude_specific_syntax() -> None:
    body = "\n".join(
        [
            "Task core:review:code-simplicity-reviewer(check the diff)",
            "Run /review and /deep-research and @code-simplicity-reviewer.",
            "Config lives in ~/.claude/config and .claude/settings.json.",
        ]
    )

    transformed = transform_content_for_codex(
        body,
        prompt_targets={"review": "review"},
        skill_targets={"deep-research": "deep-research"},
        agent_targets={"code-simplicity-reviewer": "code-simplicity-reviewer"},
    )

    assert (
        "Use the $code-simplicity-reviewer skill to: check the diff" in transformed
    )
    assert "/prompts:review" in transformed
    assert "the deep-research skill" in transformed
    assert "$code-simplicity-reviewer skill" in transformed
    assert "~/.codex/config" in transformed
    assert ".codex/settings.json" in transformed


def test_convert_claude_to_codex_generates_prompts_and_skills() -> None:
    plugin = ClaudePlugin(
        root="/tmp/plugin",
        manifest=ClaudeManifest(name="example", version="1.0.0"),
        agents=[
            ClaudeAgent(
                name="code-simplicity-reviewer",
                description="Review code for unnecessary complexity",
                body="Task repo-research-analyst(find simpler patterns)",
                source_path="/tmp/plugin/agents/code-simplicity-reviewer.md",
            )
        ],
        commands=[
            ClaudeCommand(
                name="review",
                description="Review the current change",
                argument_hint="[scope]",
                body="Use /deep-research before Task code-simplicity-reviewer(review it)",
                source_path="/tmp/plugin/commands/review.md",
            )
        ],
        skills=[
            ClaudeSkill(
                name="deep-research",
                description="Research workflow",
                source_dir="/tmp/plugin/skills/deep-research",
                skill_path="/tmp/plugin/skills/deep-research/SKILL.md",
            )
        ],
    )

    bundle = convert_claude_to_codex(plugin)

    assert [prompt.name for prompt in bundle.prompts] == ["review"]
    assert bundle.skill_dirs == [
        SkillDir(name="deep-research", source_dir="/tmp/plugin/skills/deep-research")
    ]
    generated_names = [skill.name for skill in bundle.generated_skills]
    assert generated_names == ["review", "code-simplicity-reviewer"]

    prompt_content = bundle.prompts[0].content
    assert "Use the $review skill for this command" in prompt_content
    assert "Use the $code-simplicity-reviewer skill to: review it" in prompt_content
    assert "the deep-research skill" in prompt_content

    agent_skill = bundle.generated_skills[1].content
    assert "name: code-simplicity-reviewer" in agent_skill
    assert "Use the $repo-research-analyst skill to: find simpler patterns" in agent_skill


def test_write_codex_bundle_writes_generated_files_and_config(tmp_path: Path) -> None:
    source_skill_dir = tmp_path / "source-skill"
    source_skill_dir.mkdir()
    (source_skill_dir / "SKILL.md").write_text(
        "Run /review and Task code-simplicity-reviewer(check it)\n",
        encoding="utf-8",
    )

    bundle = CodexBundle(
        prompts=[CodexPrompt(name="review", content="prompt body")],
        skill_dirs=[SkillDir(name="deep-research", source_dir=str(source_skill_dir))],
        generated_skills=[
            CodexGeneratedSkill(name="code-simplicity-reviewer", content="generated body")
        ],
        invocation_targets=CodexInvocationTargets(
            prompt_targets={"review": "review"},
            skill_targets={"deep-research": "deep-research"},
            agent_targets={"code-simplicity-reviewer": "code-simplicity-reviewer"},
        ),
        mcp_servers={
            "context7": ClaudeMcpServer(url="https://mcp.context7.com/mcp"),
            "gdelt": ClaudeMcpServer(
                command="uv",
                cwd="./mcp-server",
                args=["run", "python", "-m", "py_gdelt.mcp_server.server"],
            ),
        },
    )

    write_codex_bundle(str(tmp_path), bundle)

    assert (tmp_path / ".codex" / "prompts" / "review.md").read_text(
        encoding="utf-8"
    ) == "prompt body\n"
    copied_skill = (tmp_path / ".codex" / "skills" / "deep-research" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "/prompts:review" in copied_skill
    assert "Use the $code-simplicity-reviewer skill to: check it" in copied_skill
    assert (
        tmp_path / ".codex" / "skills" / "code-simplicity-reviewer" / "SKILL.md"
    ).read_text(encoding="utf-8") == "generated body\n"

    config = (tmp_path / ".codex" / "config.toml").read_text(encoding="utf-8")
    assert '[mcp_servers.context7]' in config
    assert 'url = "https://mcp.context7.com/mcp"' in config
    assert '[mcp_servers.gdelt]' in config
    assert 'cwd = "./mcp-server"' in config


def test_render_codex_config_returns_none_for_empty_servers() -> None:
    assert render_codex_config(None) is None
