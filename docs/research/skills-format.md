# Packaging best practices as agent skills: research brief

Researched 2026-10-31. Every claim carries its source on the same line. "Unverified" marks a claim no fetched page confirmed.

## 1. The Agent Skills format

### Open spec (agentskills.io)

- Agent Skills is an open format that Anthropic first developed and then released as an open standard. The spec repo is github.com/agentskills/agentskills (Apache-2.0). Source: https://agentskills.io/home, https://github.com/agentskills/agentskills
- A skill is a directory with a required `SKILL.md` and optional `scripts/`, `references/`, and `assets/` folders. Source: https://agentskills.io/specification
- `name` is required, 1 to 64 chars, lowercase a-z, 0-9 and hyphens, no leading, trailing or doubled hyphen, and it must match the parent directory name. Source: https://agentskills.io/specification
- `description` is required, 1 to 1024 chars, and should say what the skill does and when to use it, with trigger keywords. Source: https://agentskills.io/specification
- Optional fields are `license`, `compatibility` (max 500 chars), `metadata` (string-to-string map), and `allowed-tools` (space-separated, experimental). Source: https://agentskills.io/specification
- Progressive disclosure has three levels. Name and description (about 100 tokens) load at startup. The body (under 5000 tokens recommended) loads on activation. Resources load when needed. Source: https://agentskills.io/specification
- Keep `SKILL.md` under 500 lines, and keep file references one level deep from `SKILL.md` using relative paths. Source: https://agentskills.io/specification
- `skills-ref validate ./my-skill` checks frontmatter and naming. This is a ready-made CI lint. Source: https://agentskills.io/specification, https://github.com/agentskills/agentskills/tree/main/skills-ref

### Anthropic / Claude Code specifics

- Claude Code discovers skills at `~/.claude/skills/<name>/SKILL.md` (personal), `.claude/skills/<name>/SKILL.md` (project), nested `<subdir>/.claude/skills/`, and `<plugin>/skills/<name>/SKILL.md` (plugin, invoked as `/plugin:skill`). Source: https://code.claude.com/docs/en/skills
- Claude Code adds fields beyond the spec, including `when_to_use`, `disable-model-invocation`, `user-invocable`, `disallowed-tools`, `model`, `effort`, `context: fork`, `paths`, and `hooks`. It ignores unknown fields. Source: https://code.claude.com/docs/en/skills
- claude.ai and the Skills API accept only `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`, and any other field fails upload. For portability, stick to these six. Source: https://code.claude.com/docs/en/skills
- Description plus `when_to_use` is truncated at 1,536 chars in the listing, so put the key use case first. Source: https://code.claude.com/docs/en/skills
- `claude plugin eval` evaluates a plugin skill against a no-plugin baseline. This fits an evaluation repo. Source: https://code.claude.com/docs/en/skills
- anthropics/skills has `skills/`, `spec/`, `template/` (a `template-skill`), and `.claude-plugin/` marketplace metadata. Most skills are Apache-2.0, and the docx, pdf, pptx and xlsx skills are source-available. Source: https://github.com/anthropics/skills
- Install a skills repo with `/plugin marketplace add anthropics/skills` and then `/plugin install <bundle>@anthropic-agent-skills`. Source: https://github.com/anthropics/skills

### Other tools that read the same format

| Tool | Project dirs | User dirs | Source |
|---|---|---|---|
| OpenAI Codex | `.agents/skills` (cwd, parents, repo root) | `~/.agents/skills`, admin `/etc/codex/skills` | https://learn.chatgpt.com/docs/build-skills |
| Gemini CLI | `.gemini/skills`, `.agents/skills` (the alias wins) | `~/.gemini/skills`, `~/.agents/skills` | https://geminicli.com/docs/cli/skills/ |
| Cursor | `.agents/skills`, `.cursor/skills`, plus `.claude/skills`, `.codex/skills` | `~/.agents/skills`, `~/.cursor/skills`, `~/.claude/skills`, `~/.codex/skills` | https://cursor.com/docs/context/skills |
| GitHub Copilot | `.github/skills`, `.claude/skills`, `.agents/skills` | `~/.copilot/skills`, `~/.agents/skills` | https://docs.github.com/en/copilot/concepts/agents/about-agent-skills |
| OpenCode | `.opencode/skills`, `.claude/skills`, `.agents/skills` | `~/.config/opencode/skills`, `~/.claude/skills`, `~/.agents/skills` | https://opencode.ai/docs/skills/ |

- Codex requires `name` and `description`. An optional `agents/openai.yaml` sets UI metadata and invocation policy. The Codex page does not list `.codex/skills`, so treat `.codex/skills` as unverified for Codex itself, though Cursor reads it. Source: https://learn.chatgpt.com/docs/build-skills, https://cursor.com/docs/context/skills
- Gemini CLI says it is "based on" agentskills.io. Codex says it "builds on" it. Cursor and Copilot link the standard. OpenCode lists the same fields without naming the site. None of these pages claims full conformance. Source: the five URLs in the table above.
- Cursor adds `paths`, `icon`, and `color`. Copilot covers its CLI, its app, the cloud agent, and agent mode in VS Code, Visual Studio, and JetBrains. Source: https://cursor.com/docs/context/skills, https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
- **Recommendation (inferred).** Put the canonical tree in `skills/<name>/` for plugin and marketplace installs. Codex, Gemini, Cursor, Copilot and OpenCode all read `.agents/skills/`, so point it at that tree with a symlink or a copy step. Claude Code reads `.claude/skills` and plugins. Inferred from the table above.

## 2. Local conventions (pstack 0.9.93 install)

- Skill directory names are kebab-case verbs or nouns (`unslop`, `blast-radius`, `fix-ci`). Families share a prefix (`principle-*`, `thermo-nuclear-*`). Source: local `ls` of <locally installed pstack plugin>/skills/
- `unslop/SKILL.md` has only the `name` and `description` frontmatter. Its description is one sentence ("Cut AI tells from any writing."). The rules are numbered with stable ids that other skills cite, and a removed rule leaves a gap. Source: <locally installed pstack plugin>/skills/unslop/SKILL.md
- Larger skills keep `references/`, `playbooks/`, and `scripts/` next to `SKILL.md` (for example `poteto-mode/references/codex-tools.md`). The plugin root has `skills/`, `agents/`, `hooks/`, `assets/`, and `models.json`. Source: <locally installed pstack plugin>/skills/poteto-mode/SKILL.md and a local `ls` of the plugin root
- Per-runtime tool mappings live in `references/<runtime>-tools.md`, so the main SKILL.md stays runtime-neutral. evaluation-bible could copy this. Source: <locally installed pstack plugin>/skills/poteto-mode/SKILL.md

## 3. Reference repos

1. https://github.com/anthropics/skills. It has one folder per skill under `skills/`, a `template/` to copy, a `spec/`, and `.claude-plugin/` so one repo works as both a marketplace and plugins. Copy the template folder and the marketplace file.
2. https://github.com/hamelsmu/evals-skills (MIT, about 1.7k stars). This is the closest prior art, an eval-practice skill set: `error-analysis`, `write-judge-prompt`, `validate-evaluator`, `eval-audit`, `evaluate-rag`, `generate-synthetic-data`, `build-review-interface`. Each is a bare `SKILL.md`, with `.claude-plugin/` for install. Source: GitHub API listing. Credit it, and differentiate with runnable ADK demos.
3. https://github.com/obra/superpowers (MIT). It has `skills/` grouped by purpose, with a meta `writing-skills` skill that has `references/`. It keeps a per-harness plugin dir for each of 16 agents (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/`, `gemini-extension.json`) and runs skill-behavior evals in `evals/`. Copy the multi-harness packaging and the "writing skills" meta-skill.
4. https://github.com/google/adk-samples (Apache-2.0). It has `core/<lang>/` and `contrib/<lang>/<recipe>/`, and each recipe has `app/`, `tests/`, `eval/`, `deployment/`, `pyproject.toml`, `uv.lock`, `.env.example`, `README.md`, and `manifest.yaml`. Repo-maintenance skills live in `.agents/skills/` (`scaffold-python-recipe`, `generate-python-runnability-test`). `tools/validate_*.py` enforces structure. Source: GitHub API listing. Copy the per-demo manifest and the structure validator.
5. https://github.com/agentskills/agentskills (Apache-2.0). It holds the spec, docs, the `skills-ref` validator, and `AGENTS.md` and `CLAUDE.md` at the root. Copy the validator into CI.
6. https://github.com/onejune2018/Awesome-LLM-Eval (MIT, data under a separate `LICENSE-DATA.txt`). It is a curated list of eval tools, benchmarks and papers. Copy the split code and data license. I found no dedicated "awesome agent evals" list, so this is the nearest one (WebSearch, unverified beyond the GitHub API description).

## 4. Python project conventions

- Commit `uv.lock` and never commit `.venv`. uv needs `pyproject.toml` to find the project root. Source: https://docs.astral.sh/uv/concepts/projects/layout/
- adk-samples' root `pyproject.toml` uses `[dependency-groups] dev = [pytest>=8, ruff>=0.14, mypy>=1.10]`, a hatchling build backend, and `[tool.uv] required-version = ">=0.5"` so `astral-sh/setup-uv` does not call the GitHub API. Source: https://github.com/google/adk-samples/blob/main/pyproject.toml
- One lesson in that file is to keep `ruff` in the dev group. CI used `uvx ruff`, the docs told contributors `uv run ruff format`, and that command failed until ruff was added. Source: https://github.com/google/adk-samples/blob/main/pyproject.toml
- adk-samples CI has `python-format.yml`, `python-tests.yml`, `python-validate-recipe.yml`, and `python-dependency-policy.yml`. The test job finds the changed recipes and runs pytest per recipe in a matrix, filtered by paths, with `permissions: contents: read` and concurrency cancel. Source: https://github.com/google/adk-samples/tree/main/.github/workflows
- adk-python has a root `.pre-commit-config.yaml`, `AGENTS.md`, `CONTRIBUTING.md`, and `src/` + `tests/` layout. Source: https://github.com/google/adk-python
- ADK eval uses `.test.json` (one session, unit-style), evalsets (many sessions, integration), and a `test_config.json` per folder. You run it with `adk eval <agent> <evalset>`, `AgentEvaluator.evaluate(...)` under pytest, or `adk web`. Source: https://adk.dev/evaluate/
- The default ADK criteria are `tool_trajectory_avg_score` 1.0 and `response_match_score` 0.8. Rubric, hallucination, safety and multi-turn criteria call the Vertex Gen AI Evaluation Service, which needs `GOOGLE_API_KEY` or GCP ADC. Source: https://adk.dev/evaluate/
- **Proposed layout (inferred, not sourced).** `skills/<name>/SKILL.md`, `demos/<name>/{agent/, evals/*.test.json, test_config.json, README.md}`, `src/evaluation_bible/` for shared scripts, `tests/`, `pyproject.toml` with one uv workspace, `justfile` or `Makefile` targets `lint`, `test`, `smoke`, `validate-skills`.
- **Keyless smoke test (inferred).** CI runs `ruff check`, `ruff format --check`, `skills-ref validate skills/*`, and pytest. Those tests import every demo, load each evalset, and score recorded or stubbed agent outputs with non-LLM criteria (trajectory match). Live-model evals run only on `workflow_dispatch` with secrets. Whether ADK's trajectory scorer runs offline against a canned session is unverified. Check it in adk-python before relying on it.

## 5. Licensing and contributing

- MIT allows commercial use, modification, distribution and private use. Its only condition is keeping the notice. Source: https://choosealicense.com/licenses/
- Apache-2.0 adds an express patent grant from contributors, a "state changes" condition, and a trademark limitation. Source: https://choosealicense.com/licenses/
- Licenses in the ecosystem: the spec (agentskills), anthropics/skills (most skills), adk-samples and adk-python use Apache-2.0. superpowers and hamelsmu/evals-skills use MIT. Source: GitHub API `license.spdx_id` for each repo and https://github.com/anthropics/skills
- **Recommendation (judgment).** Use Apache-2.0. It matches ADK and the spec, and it has the patent grant for contributed scripts. Set `license: Apache-2.0` in each SKILL.md frontmatter, which the spec allows. Source for the field: https://agentskills.io/specification
- adk-samples requires a Google CLA and routes contributors through a contributor guide and a recipe handbook. A PR is ready for review only after every check passes. Source: https://github.com/google/adk-samples/blob/main/CONTRIBUTING.md
- **CONTRIBUTING pattern (proposed, inferred from adk-samples and anthropics/skills).** One PR adds exactly one `skills/<name>/` and one `demos/<name>/` with the same name. A required `manifest.yaml` or frontmatter `metadata` links the two. CI fails if a skill has no demo, if `skills-ref validate` fails, if `name` differs from the directory, if SKILL.md is over 500 lines, or if the keyless smoke test fails. The PR template asks for the description's trigger phrases and one before/after eval result. Have a script enforce this, as adk-samples' `tools/validate_structure.py` does, rather than prose alone. Source for that precedent: https://github.com/google/adk-samples/tree/main/tools
