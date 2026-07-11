#!/usr/bin/env python3
"""
Skill evaluation helper.

This script provides a lightweight eval harness for skill authors:
- load a trigger/negative-trigger eval spec from evals/skill-evals.yaml
- summarize repeated trial outcomes
- print a compact report for iteration

The script does not attempt to invoke Claude Code directly. Instead, it gives skill
authors a stable spec format and summary tool so repeated manual or agent-driven
runs can be scored consistently.

Usage:
    uv run python plugins/core/skills/skill-creator/scripts/evaluate_skill.py <eval-spec> --results <results-json>

Results JSON format:
{
  "should_trigger": {
    "prompt text": [true, true, false]
  },
  "should_not_trigger": {
    "other prompt": [true, true, true]
  }
}
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def load_eval_spec(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Eval spec must be a mapping")

    skill = data.get("skill")
    if not isinstance(skill, str) or not skill.strip():
        raise ValueError("Eval spec must define a non-empty 'skill' field")

    for section in ("should_trigger", "should_not_trigger"):
        cases = data.get(section, [])
        if cases is None:
            cases = []
            data[section] = cases
        if not isinstance(cases, list):
            raise ValueError(f"Section '{section}' must be a list")
        for idx, case in enumerate(cases):
            if not isinstance(case, dict):
                raise ValueError(f"Section '{section}' case {idx} must be a mapping")
            prompt = case.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError(f"Section '{section}' case {idx} must define a non-empty prompt")
            trials = case.get("trials", 3)
            if not isinstance(trials, int) or trials < 1:
                raise ValueError(f"Section '{section}' case {idx} must define trials >= 1")
    return data


def load_results(path: str | Path) -> dict[str, dict[str, list[bool]]]:
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError("Results JSON must be an object")
    normalized: dict[str, dict[str, list[bool]]] = {}
    for section, prompts in data.items():
        if not isinstance(prompts, dict):
            raise ValueError(f"Results section '{section}' must be an object")
        normalized[section] = {}
        for prompt, values in prompts.items():
            if not isinstance(prompt, str):
                raise ValueError("Prompt keys must be strings")
            if not isinstance(values, list) or not all(isinstance(v, bool) for v in values):
                raise ValueError(
                    f"Results for prompt '{prompt}' in section '{section}' must be a list of booleans"
                )
            normalized[section][prompt] = values
    return normalized


def summarize_cases(
    spec: dict[str, Any], results: dict[str, dict[str, list[bool]]]
) -> dict[str, list[dict[str, Any]]]:
    summary: dict[str, list[dict[str, Any]]] = {"should_trigger": [], "should_not_trigger": []}
    for section in summary:
        case_results = results.get(section, {})
        for case in spec.get(section, []):
            prompt = case["prompt"]
            observed = case_results.get(prompt, [])
            passed_trials = sum(1 for value in observed if value)
            failed_trials = sum(1 for value in observed if not value)
            total_trials = len(observed)
            pass_rate = (passed_trials / total_trials) if total_trials else 0.0
            summary[section].append(
                {
                    "id": case.get("id"),
                    "prompt": prompt,
                    "expected_trials": case.get("trials", 3),
                    "observed_trials": total_trials,
                    "passed_trials": passed_trials,
                    "failed_trials": failed_trials,
                    "pass_rate": pass_rate,
                    "success_criteria": case.get("success_criteria", []),
                }
            )
    return summary


def render_summary(skill: str, summary: dict[str, list[dict[str, Any]]]) -> str:
    lines = [f"Skill eval summary: {skill}", ""]
    for section in ("should_trigger", "should_not_trigger"):
        title = "Should trigger" if section == "should_trigger" else "Should NOT trigger"
        lines.append(title)
        lines.append("-" * len(title))
        cases = summary.get(section, [])
        if not cases:
            lines.append("(no cases)")
            lines.append("")
            continue
        for case in cases:
            lines.append(
                f"- {case['prompt']} | pass_rate={case['pass_rate']:.0%} | "
                f"passed={case['passed_trials']} failed={case['failed_trials']} "
                f"observed={case['observed_trials']}/{case['expected_trials']}"
            )
        lines.append("")
    return "\n".join(lines).rstrip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize repeated skill eval runs")
    parser.add_argument("eval_spec", help="Path to evals/skill-evals.yaml")
    parser.add_argument("--results", required=True, help="Path to JSON file with boolean trial outcomes")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary")
    args = parser.parse_args()

    spec = load_eval_spec(args.eval_spec)
    results = load_results(args.results)
    summary = summarize_cases(spec, results)

    if args.json:
        print(json.dumps({"skill": spec["skill"], "summary": summary}, indent=2))
    else:
        print(render_summary(spec["skill"], summary))


if __name__ == "__main__":
    main()
