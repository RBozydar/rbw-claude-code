from __future__ import annotations

from pathlib import Path
import sys

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "core" / "skills" / "skill-creator" / "scripts"))

from init_skill import init_skill
from quick_validate import analyze_skill


SKILL_CREATOR_ROOT = REPO_ROOT / "plugins" / "core" / "skills" / "skill-creator"


@pytest.mark.parametrize(
    "skill_name",
    [
        "Bad_Name",
        "bad name",
        "bad.name",
        "this-name-is-way-over-forty-characters-long-by-design",
    ],
)
def test_init_skill_rejects_invalid_names(tmp_path: Path, skill_name: str) -> None:
    result = init_skill(skill_name, tmp_path)

    assert result is None
    assert not (tmp_path / skill_name).exists()


def test_init_skill_creates_eval_scaffold(tmp_path: Path) -> None:
    skill_dir = init_skill("example-skill", tmp_path)

    assert skill_dir is not None
    eval_spec = skill_dir / "evals" / "skill-evals.yaml"
    assert eval_spec.exists()

    spec = yaml.safe_load(eval_spec.read_text())
    assert spec["skill"] == "example-skill"
    assert "should_trigger" in spec
    assert "should_not_trigger" in spec


def test_simple_template_models_required_sections() -> None:
    template = (SKILL_CREATOR_ROOT / "templates" / "simple-skill.md").read_text()

    assert "## Trigger Examples" in template
    assert "## Bundled Resources" in template
    assert "## Gotchas" in template
    assert "## Verification" in template
    assert "## Progressive Disclosure Notes" in template


def test_router_template_models_required_sections_without_rigid_follow_exactly() -> None:
    template = (SKILL_CREATOR_ROOT / "templates" / "router-skill.md").read_text()

    assert "## Trigger Examples" in template
    assert "## Gotchas" in template
    assert "## Verification" in template
    assert "## Progressive Disclosure Notes" in template
    assert "follow it exactly" not in template.lower()


def test_skill_creator_eval_script_summarizes_repeated_trials(tmp_path: Path) -> None:
    eval_script = SKILL_CREATOR_ROOT / "scripts" / "evaluate_skill.py"
    assert eval_script.exists()

    spec_path = tmp_path / "skill-evals.yaml"
    spec_path.write_text(
        yaml.safe_dump(
            {
                "skill": "demo-skill",
                "should_trigger": [
                    {"prompt": "deploy this service", "trials": 3},
                ],
                "should_not_trigger": [
                    {"prompt": "draft a blog post", "trials": 2},
                ],
            },
            sort_keys=False,
        )
    )

    namespace: dict[str, object] = {}
    exec(eval_script.read_text(), namespace)
    summarize_cases = namespace["summarize_cases"]
    load_eval_spec = namespace["load_eval_spec"]

    loaded = load_eval_spec(spec_path)
    summary = summarize_cases(
        loaded,
        {
            "should_trigger": {
                "deploy this service": [True, False, True],
            },
            "should_not_trigger": {
                "draft a blog post": [True, True],
            },
        },
    )

    trigger_case = summary["should_trigger"][0]
    assert trigger_case["pass_rate"] == pytest.approx(2 / 3)
    assert trigger_case["passed_trials"] == 2
    assert trigger_case["failed_trials"] == 1

    negative_case = summary["should_not_trigger"][0]
    assert negative_case["pass_rate"] == pytest.approx(1.0)
    assert negative_case["passed_trials"] == 2


def test_validator_warns_when_evals_are_missing_for_finished_skill(tmp_path: Path) -> None:
    skill_dir = tmp_path / "finished-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: finished-skill\n"
        "description: Use this skill when deploying services to staging or production and debugging release workflow failures.\n"
        "---\n\n"
        "# Finished Skill\n\n"
        "## Overview\n"
        "Deploy services safely.\n\n"
        "## Gotchas\n"
        "- Situation: Production deploys need confirmation.\n"
        "- Wrong instinct: Push directly.\n"
        "- Correct approach: Verify the target environment first.\n"
        "- How to verify the fix: Compare the release URL.\n\n"
        "## Verification\n"
        "Run the deploy check and confirm the reported environment.\n\n"
        "## Success Criteria\n"
        "- Correct environment\n"
    )

    report = analyze_skill(skill_dir)

    assert report.valid
    assert any("eval" in warning.lower() for warning in report.warnings)
