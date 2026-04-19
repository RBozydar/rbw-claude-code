from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


HOOKS_DIR = Path(__file__).parent
HOOK_SCRIPT = HOOKS_DIR / "reminder_hook.py"
HOOKS_JSON = HOOKS_DIR / "hooks.json"


def load_hook_module():
    spec = importlib.util.spec_from_file_location("reminder_hook", HOOK_SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {HOOK_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["reminder_hook"] = module
    spec.loader.exec_module(module)
    return module


def test_hooks_json_points_to_non_test_named_hook_script() -> None:
    hooks_config = json.loads(HOOKS_JSON.read_text())
    command = hooks_config["hooks"]["PostToolUse"][0]["hooks"][0]["command"]

    assert command.endswith("/hooks/reminder_hook.py")
    assert "/hooks/test_" not in command


def test_reminder_hook_exposes_test_detection_helper() -> None:
    module = load_hook_module()

    assert module.should_remind_about_tests("src/service.py") is True
    assert module.should_remind_about_tests("tests/test_service.py") is False
    assert module.should_remind_about_tests("src/conftest.py") is False
