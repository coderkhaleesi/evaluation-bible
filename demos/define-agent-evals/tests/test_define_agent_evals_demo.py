"""Keyless checks on the define-agent-evals demo's data files.

These load the eval set and config as real ADK models and assert on their
structure. They run no agent and reach no model: eval scores need
EVAL_BIBLE_AGENT_MODEL/EVAL_BIBLE_JUDGE_MODEL and a live judge, which is a
separate, non-keyless run of `uv run adk eval`.
"""

from __future__ import annotations

from pathlib import Path

from google.adk.evaluation.eval_case import get_all_tool_calls
from google.adk.evaluation.eval_config import EvalConfig, get_eval_metrics_from_config
from google.adk.evaluation.eval_metrics import ToolTrajectoryCriterion
from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.trajectory_evaluator import TrajectoryEvaluator

DEMO_DIR = Path(__file__).resolve().parent.parent
EVAL_SET_PATH = DEMO_DIR / "evals" / "retail_support.evalset.json"
TEST_CONFIG_PATH = DEMO_DIR / "evals" / "test_config.json"
MUST_NOT_HAPPEN_EVAL_ID = "refund_over_the_limit_must_be_escalated_not_issued"


def load_eval_set() -> EvalSet:
    return EvalSet.model_validate_json(EVAL_SET_PATH.read_text(encoding="utf-8"))


def load_eval_config() -> EvalConfig:
    return EvalConfig.model_validate_json(TEST_CONFIG_PATH.read_text(encoding="utf-8"))


def test_eval_set_has_at_least_five_cases() -> None:
    eval_set = load_eval_set()
    assert len(eval_set.eval_cases) >= 5


def test_every_case_targets_retail_support() -> None:
    eval_set = load_eval_set()
    for case in eval_set.eval_cases:
        assert case.session_input is not None, case.eval_id
        assert case.session_input.app_name == "retail_support", case.eval_id


def test_must_not_happen_case_escalates_and_never_issues_a_refund() -> None:
    eval_set = load_eval_set()
    case = next(c for c in eval_set.eval_cases if c.eval_id == MUST_NOT_HAPPEN_EVAL_ID)
    assert case.conversation is not None
    tool_names = [
        call.name
        for invocation in case.conversation
        for call in get_all_tool_calls(invocation.intermediate_data)
    ]
    assert "escalate" in tool_names
    assert "issue_refund" not in tool_names


def test_config_parses_with_exactly_the_two_criteria() -> None:
    eval_config = load_eval_config()
    assert set(eval_config.criteria) == {"tool_trajectory_avg_score", "final_response_match_v2"}


def test_config_runs_tool_trajectory_in_order_mode() -> None:
    eval_config = load_eval_config()
    metrics = {metric.metric_name: metric for metric in get_eval_metrics_from_config(eval_config)}
    trajectory_evaluator = TrajectoryEvaluator(eval_metric=metrics["tool_trajectory_avg_score"])
    assert trajectory_evaluator._match_type == ToolTrajectoryCriterion.MatchType.IN_ORDER
