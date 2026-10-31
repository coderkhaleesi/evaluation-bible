"""Check that every skill has a demo of the same name and a portable SKILL.md.

Usage: python tools/validate_structure.py [--root DIR]

Exit 1 with one line per problem, or exit 0 with the count of skills checked. The rules come
from PLAN.md Phase 0 step 5: a skill directory needs a demo directory of the same name and the
reverse, the frontmatter `name` must equal the directory name, SKILL.md may not exceed 500
lines, and the frontmatter may use only the six portable fields.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PORTABLE_FIELDS = frozenset(
    {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
)
MAX_SKILL_LINES = 500
TEMPLATE_DIR = "_template"
FIELD = re.compile(r"^([A-Za-z][A-Za-z0-9-]*):")


def frontmatter_fields(text: str) -> tuple[dict[str, str], str | None]:
    """Top-level keys and raw values of the frontmatter between the leading `---` fences, or a problem."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "SKILL.md does not start with a '---' frontmatter fence"
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields, None
        match = FIELD.match(line)
        if match:
            fields[match.group(1)] = line[match.end() :].strip()
    return fields, "frontmatter has no closing '---' fence"


def skill_problems(skill_dir: Path, demos: Path) -> list[str]:
    name = skill_dir.name
    problems: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"skills/{name}: no SKILL.md"]
    text = skill_md.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    if line_count > MAX_SKILL_LINES:
        problems.append(
            f"skills/{name}/SKILL.md: {line_count} lines, the limit is {MAX_SKILL_LINES}"
        )
    fields, fence_problem = frontmatter_fields(text)
    if fence_problem is not None:
        return [*problems, f"skills/{name}/SKILL.md: {fence_problem}"]
    declared = fields.get("name")
    if declared is None:
        problems.append(f"skills/{name}/SKILL.md: frontmatter has no name")
    elif declared != name:
        problems.append(
            f"skills/{name}/SKILL.md: frontmatter name {declared!r} differs from the directory name"
        )
    if "description" not in fields:
        problems.append(f"skills/{name}/SKILL.md: frontmatter has no description")
    for field in sorted(set(fields) - PORTABLE_FIELDS):
        problems.append(
            f"skills/{name}/SKILL.md: frontmatter field {field!r} is not one of the portable six"
        )
    if not (demos / name).is_dir():
        problems.append(f"skills/{name}: no demo at demos/{name}/")
    return problems


def validate(root: Path) -> list[str]:
    """Every problem in the skills and demos trees under root, in path order."""
    skills = root / "skills"
    demos = root / "demos"
    skill_dirs = (
        sorted(p for p in skills.iterdir() if p.is_dir() and p.name != TEMPLATE_DIR)
        if skills.is_dir()
        else []
    )
    demo_dirs = sorted(p for p in demos.iterdir() if p.is_dir()) if demos.is_dir() else []
    problems: list[str] = []
    for skill_dir in skill_dirs:
        problems.extend(skill_problems(skill_dir, demos))
    skill_names = {p.name for p in skill_dirs}
    for demo_dir in demo_dirs:
        if demo_dir.name not in skill_names:
            problems.append(f"demos/{demo_dir.name}: no skill at skills/{demo_dir.name}/")
    return problems


def count_skills(root: Path) -> int:
    skills = root / "skills"
    if not skills.is_dir():
        return 0
    return sum(1 for p in skills.iterdir() if p.is_dir() and p.name != TEMPLATE_DIR)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root (default: current directory)",
    )
    args = parser.parse_args(argv)
    problems = validate(args.root)
    for problem in problems:
        sys.stderr.write(f"{problem}\n")
    if problems:
        return 1
    sys.stdout.write(f"ok: {count_skills(args.root)} skills, each with a demo\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
