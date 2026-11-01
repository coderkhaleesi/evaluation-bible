from evaluation_bible.judge import judge_endpoint


def test_judge_endpoint_uses_the_provider_key() -> None:
    assert judge_endpoint().startswith("https://api.openai.com/v1/responses?key_prefix=sk-")
