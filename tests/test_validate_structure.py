"""Behavior of tools/validate_structure.py on small skill and demo trees."""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from validate_structure import validate

TOOL = Path(__file__).resolve().parents[1] / "tools" / "validate_structure.py"

GOOD = "---\nname: {name}\ndescription: One practice.\n---\n\n# {name}\n"


def make_skill(
    root: Path, name: str, text: str | None = None, demo: bool = True
) -> None:
    skill = root / "skills" / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(GOOD.format(name=name) if text is None else text)
    if demo:
        (root / "demos" / name).mkdir(parents=True)


def test_empty_tree_and_a_valid_pair_pass(tmp_path: Path) -> None:
    assert validate(tmp_path) == []
    make_skill(tmp_path, "define-agent-evals")
    (tmp_path / "skills" / "_template").mkdir()
    assert validate(tmp_path) == []


def test_a_skill_without_a_demo_and_a_demo_without_a_skill_fail(tmp_path: Path) -> None:
    make_skill(tmp_path, "write-rubrics", demo=False)
    (tmp_path / "demos" / "orphan").mkdir(parents=True)
    assert validate(tmp_path) == [
        "skills/write-rubrics: no demo at demos/write-rubrics/",
        "demos/orphan: no skill at skills/orphan/",
    ]


def test_frontmatter_name_must_equal_the_directory(tmp_path: Path) -> None:
    make_skill(tmp_path, "hill-climb", text=GOOD.format(name="hillclimb"))
    assert validate(tmp_path) == [
        "skills/hill-climb/SKILL.md: frontmatter name 'hillclimb' differs from the directory name"
    ]


def test_skill_md_over_500_lines_fails(tmp_path: Path) -> None:
    text = GOOD.format(name="self-heal") + "line\n" * 500
    make_skill(tmp_path, "self-heal", text=text)
    assert validate(tmp_path) == [
        "skills/self-heal/SKILL.md: 506 lines, the limit is 500"
    ]


def test_frontmatter_fields_outside_the_portable_six_fail(tmp_path: Path) -> None:
    text = "---\nname: ab-testing\ndescription: x\nversion: 2\nauthor: me\n---\n"
    make_skill(tmp_path, "ab-testing", text=text)
    assert validate(tmp_path) == [
        "skills/ab-testing/SKILL.md: frontmatter field 'author' is not one of the portable six",
        "skills/ab-testing/SKILL.md: frontmatter field 'version' is not one of the portable six",
    ]


def test_missing_fences_or_description_are_reported(tmp_path: Path) -> None:
    make_skill(tmp_path, "error-analysis", text="# no frontmatter\n")
    make_skill(tmp_path, "calibrate-judge", text="---\nname: calibrate-judge\n---\n")
    assert validate(tmp_path) == [
        "skills/calibrate-judge/SKILL.md: frontmatter has no description",
        "skills/error-analysis/SKILL.md: SKILL.md does not start with a '---' frontmatter fence",
    ]


@pytest.mark.parametrize(("make_bad", "expected"), [(False, 0), (True, 1)])
def test_cli_exit_code_follows_the_problems(
    tmp_path: Path, make_bad: bool, expected: int
) -> None:
    make_skill(tmp_path, "trace-agents-with-otel", demo=not make_bad)
    result = subprocess.run(
        [sys.executable, str(TOOL), "--root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == expected, result.stderr
    if expected == 0:
        assert result.stdout == "ok: 1 skills, each with a demo\n"
    else:
        assert "no demo at demos/trace-agents-with-otel/" in result.stderr
