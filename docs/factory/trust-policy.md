# Factory trust policy

What the software factory may do in this repository without a person, and where a person must act. Every rule here names the mechanism that enforces it. A rule with no mechanism is a wish, and this file does not keep wishes.

Owner: Tanya Dixit (`coderkhaleesi`). The owner is the only person who approves plans, reviews factory pull requests, and edits this file.

Written 2026-10-31 for plan revision 3 of the factory. Starting values are marked. They change after the first measured trial, not before.

## Change classes

The planner reads the issue's risk class and the diff it expects. The classifier in CI reads the real diff. The stricter of the two wins.

| Class | Criteria, all must hold | Plan approval | Merge |
|---|---|---|---|
| light | Docs, tests, or one source file. Under 20 changed lines. No new dependency. Nothing under `.github/`, `ci/`, `scripts/`, or the protected files. | Automatic. The planner applies `factory:light`; a deterministic step applies `factory:approved`. | Owner's approving review, then auto-merge. |
| full | Anything that is not light and not shared. | Owner applies `factory:approved` after reading the plan comment. | Owner's approving review, then auto-merge. |
| shared | Touches `.github/`, `ci/`, `scripts/`, the protected files, `pyproject.toml` dependencies, secrets, or a GitHub environment. | Owner applies `factory:approved`. The builder's protected-files policy is `request_review`, never `allowed`. | Owner's approving review. Auto-merge stays off for this class until the end of the trial. |

Protected files are `AGENTS.md`, `CLAUDE.md`, `no-fakes.allow`, `no-fakes.profile`, `scripts/check.sh`, `scripts/check_no_fakes.py`, `ruff.toml`, `.claude/`, `.github/`, and `ci/`.

## Mutation score

The nightly sweep (`Mutation sweep`, mutmut) scores killed mutants over all judged mutants, with mutants no test reaches counted against the project. The threshold is 0.8, recorded in `factory.json` under `mutation.threshold`. Below it, the sweep files one issue "Strengthen tests in <module>" labelled `factory:suggested`; the owner promotes it to `factory:ready` or closes it. The score never blocks a merge.

## Human touches

Per change, two. Per release, one.

1. Labelling the issue. `factory:ready` starts the planner. `factory:approved` starts the builder. For a full or shared change the owner applies both after reading the plan, so this counts as one touch.
2. The approving review on the pull request. Its body carries the owner line and the three readiness declarations. Readiness is checked by `ci/pr-readiness.mjs` from the default branch, and an agent never fills those lines.
3. Merging the release pull request that release-please opens. Once per release.

Nothing else needs a person. If a run needs one, it stops and labels `factory:needs-input` or `factory:stuck`. It never guesses.

## Budgets

The spend ceiling is USD 50 per month on the Anthropic account. It is set as a monthly spend limit in the Anthropic console, which is the hard stop. gh-aw caps bound single runs and single days so one bad day cannot use the month. In gh-aw one AI credit is USD 0.01, computed from token counts with catalog prices, so the figures below are estimates of the bill, not the bill.

| Workflow | `timeout-minutes` | `max-turns` | `max-ai-credits` per run | `max-daily-ai-credits` |
|---|---|---|---|---|
| factory-plan | 15 | 40 | 100 | 300 |
| factory-build | 45 | 200 | 800 | 1200 |
| factory-pr-fix | 30 | 100 | 400 | 800 |
| factory-review | 15 | 30 | 150 | 300 |
| factory-ci-doctor | 10 | 20 | 50 | 100 |
| factory-cost, factory-hello | 5 | 10 | 20 | 50 |

Starting values. The daily caps add up to USD 28, so the console limit is reached only after several heavy days in a row. After the trial in the factory plan's T14, the owner replaces these with measured numbers.

Other bounds, each enforced by gh-aw frontmatter:

- The fixer gets three attempts per pull request, counted by the factory's gate script from the commits the factory App has pushed to the branch since the pull request opened. The fourth failure applies `factory:stuck` and starts no agent.
- One planner run per issue and one builder run per issue. A pre-step exits when the plan comment or the branch already exists.
- No schedule starts an agent that writes code. The nightly mutation sweep files issues with `factory:suggested`, and only the owner promotes one to `factory:ready`.

Actions minutes. The repository is public, so standard runners are free. The ceiling is still 3,000 minutes per month, checked monthly in the usage page, so a runaway matrix is noticed. Each workflow carries its own `timeout-minutes`.

## Merge rule

A pull request merges when all of these hold:

- the `required` check is green, with every selected lane reporting success, not skipped;
- the `PR readiness` check is green;
- one approving review from the owner, with stale reviews dismissed on push;
- a Conventional Commits title;
- linear history, no force push.

Enforced by branch protection on `main`. Auto-merge is on, so the approving review is the last click. Agents never merge. The `merge-pull-request` safe output is not enabled in any workflow. Enabling it for the light class is a change to this file and needs ten merged factory pull requests with zero reverts first.

## Dependencies

Every external system the repository will talk to, sorted into one of three kinds. The kind decides where the factory tests against it. There is no fourth kind and no label that turns a lane off.

- Container. Runs as a GitHub Actions service container on every pull request that touches code using it.
- Vendor sandbox. The vendor offers a test endpoint. Runs on every pull request with a key from a GitHub environment.
- No sandbox. Only the real thing exists. Runs in the nightly full tier with keys from the `nightly` environment, never on a pull request lane.

| Dependency | Used by | Kind | Where tested | Credential |
|---|---|---|---|---|
| Gemini API, the default ADK model | reference agent, judges, user simulator | no sandbox | nightly | `GOOGLE_API_KEY` in the `nightly` environment |
| Any other model via LiteLLM strings | optional judge from a second model family | no sandbox | nightly | that provider's key in `nightly` |
| Phoenix, trace backend | `trace-agents-with-otel`, online sampling demos | container | PR lanes when tracing code changes | none |
| OpenTelemetry collector | tracing demos | container | PR lanes when tracing code changes | none |
| Langfuse, second trace backend | `trace-agents-with-otel` demo | container | nightly only, because its compose stack has four services | none |
| garak and PyRIT red-team runs | `security-evals` | no sandbox | nightly, scheduled, because they call a model | model key in `nightly` |

Two systems are reached but not tested against, so they have no row. PyPI is a network allowlist entry in the builder for `uv sync`. The GitHub API is used by the factory itself through safe outputs on the App token, whose id and private key are repository secrets. Vertex AI metrics are out of the repository's scope and have no row. Recorded model sessions from `adk conformance record` are teaching material for the `run-evals-in-ci` skill. They are not evidence in any lane, and no pull-request test replays one.

The container rows are from the vendors' published images and are confirmed when the lane is wired in the factory plan's T8. If one turns out not to run as a service container, its row moves to nightly, and this file records the move.

## The `nightly` environment

A GitHub environment named `nightly` holds every model key. Only the scheduled full-tier workflow and `workflow_dispatch` by the owner may read it. No workflow that runs on `pull_request`, `issues`, or `workflow_run` references it, and the factory's CI check fails any workflow file that does.

## Changing this file

Only the owner edits it, in a pull request titled `docs(factory): ...`. The builder's protected-files policy flags any agent edit for review. Each change adds a line below.

- 2026-10-31. First version. Starting budgets, two touches per change, no agent merges.
- 2026-10-31. Attempts are counted from App commits on the branch, not from labels, per the factory's `docs/design.md`.
