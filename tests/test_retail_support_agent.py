import pytest

from evaluation_bible.agents.retail_support.agent import AGENT_MODEL_ENV_VAR, build_agent


def test_build_agent_without_the_env_var_raises_naming_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(AGENT_MODEL_ENV_VAR, raising=False)
    with pytest.raises(RuntimeError, match=AGENT_MODEL_ENV_VAR):
        build_agent()


def test_build_agent_with_the_env_var_set_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(AGENT_MODEL_ENV_VAR, "test-model-name")
    agent = build_agent()
    assert agent.model == "test-model-name"
    assert agent.name == "retail_support"
    assert len(agent.tools) == 4


def test_build_agent_with_an_empty_env_var_raises_naming_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(AGENT_MODEL_ENV_VAR, "")
    with pytest.raises(RuntimeError, match=AGENT_MODEL_ENV_VAR):
        build_agent()
