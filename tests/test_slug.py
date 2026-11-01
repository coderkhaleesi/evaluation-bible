from evaluation_bible.slug import kebab


def test_kebab_joins_words_with_hyphens() -> None:
    assert kebab("Rubric Grader Demo") == "rubric-grader-demo"
