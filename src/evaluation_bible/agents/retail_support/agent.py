"""The retail_support reference agent: an ADK LlmAgent over the order store."""

from __future__ import annotations

import os

from google.adk.agents import LlmAgent

from evaluation_bible.agents.retail_support.store import OrderStore
from evaluation_bible.agents.retail_support.tools import RetailSupportTools

AGENT_MODEL_ENV_VAR = "EVAL_BIBLE_AGENT_MODEL"

INSTRUCTION = (
    "You are retail_support, a customer support agent for order management. "
    "Follow the rules in policy.md: refunds over the limit must be escalated, "
    "not issued, and a cancelled order cannot be refunded."
)


def _require_model_name() -> str:
    model = os.environ.get(AGENT_MODEL_ENV_VAR)
    if not model:
        raise RuntimeError(f"{AGENT_MODEL_ENV_VAR} is not set or is empty")
    return model


def build_agent(store: OrderStore | None = None) -> LlmAgent:
    """Build the retail_support LlmAgent wired to the four policy tools."""
    model = _require_model_name()
    tools = RetailSupportTools(store if store is not None else OrderStore())
    return LlmAgent(
        name="retail_support",
        model=model,
        description="Retail order support: lookup, cancel, refund, and escalate.",
        instruction=INSTRUCTION,
        tools=[
            tools.lookup_order,
            tools.cancel_order,
            tools.issue_refund,
            tools.escalate,
        ],
    )
