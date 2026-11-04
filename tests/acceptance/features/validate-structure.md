# Validate the skills tree

The structure check is the first thing a contributor runs after adding a skill. It pairs every `skills/<name>/` with `demos/<name>/`, checks the frontmatter, and prints a one-line verdict.

## Sub-features

- `structure-ok` prints `ok: <n> skills, each with a demo` and exits 0 on a well-formed tree.
- `structure-orphan` names a skill that has no demo and exits non-zero.

## How to get to it (user POV)

- Run `uv run python tools/validate_structure.py` from the repository root.
- Run it on another tree with `--root <dir>`.

## Driving it with bash

Preconditions:

- Tier: fast
- `uv sync` has run.

```bash
out="$(uv run python tools/validate_structure.py)"
printf '%s\n' "$out"
printf '%s\n' "$out" | grep -Eq '^ok: [0-9]+ skills, each with a demo$'
```

```bash
scratch="$(mktemp -d)"
mkdir -p "$scratch/skills/orphan"
printf -- '---\nname: orphan\ndescription: a skill with no demo\n---\n# Orphan\n' > "$scratch/skills/orphan/SKILL.md"
if out="$(uv run python tools/validate_structure.py --root "$scratch" 2>&1)"; then
  echo "expected a non-zero exit for a skill without a demo"
  rm -rf "$scratch"
  exit 1
fi
rm -rf "$scratch"
printf '%s\n' "$out"
printf '%s\n' "$out" | grep -q 'orphan'
```

## Gotchas

- `skills/_template/` is exempt from the pairing rule and is not counted.
- The verdict goes to stdout. Problems go to stderr, one per line, each naming the skill.
