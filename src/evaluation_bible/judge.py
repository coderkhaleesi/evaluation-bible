"""A judge call that needs a provider key."""

import os


def judge_endpoint() -> str:
    """The judge provider's endpoint, authorised by ``OPENAI_API_KEY`` from the environment."""
    key = os.environ["OPENAI_API_KEY"]
    return f"https://api.openai.com/v1/responses?key_prefix={key[:3]}"
