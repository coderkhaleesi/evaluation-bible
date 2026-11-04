# define-agent-evals demo

The first eval set for the `retail_support` reference agent, built the way
`skills/define-agent-evals/SKILL.md` teaches: six cases drawn from
`policy.md`, one of them a must-not-happen case, graded on tool trajectory and
final response rather than prose alone.

## Files

- `evals/retail_support.evalset.json` — an ADK `EvalSet` with six `EvalCase`s:
  a lookup, a cancel, a refund within `REFUND_LIMIT`, a refund over the limit
  (must escalate, must never call `issue_refund`), a refund attempt on an
  already-cancelled order, and a lookup on an order id that doesn't exist.
- `evals/test_config.json` — an ADK `EvalConfig` with two criteria:
  `tool_trajectory_avg_score` in `IN_ORDER` mode (policy.md requires looking
  an order up before acting on it, nothing stronger) and
  `final_response_match_v2` for the prose.
- `tests/` — keyless pytest checks on the eval set and config files
  themselves. They need no model, no key, and no network; they do not run the
  agent.

## What to run

Set both model env vars (see `.env.example`), then run the eval set against
the real `retail_support` agent with a live judge:

```bash
export EVAL_BIBLE_AGENT_MODEL=<a model string the ADK LLMRegistry resolves>
export EVAL_BIBLE_JUDGE_MODEL=<a different model family, for the judge>
uv run adk eval src/evaluation_bible/agents/retail_support \
  demos/define-agent-evals/evals/retail_support.evalset.json \
  --config_file_path demos/define-agent-evals/evals/test_config.json \
  --print_detailed_results
```

Run it at least three times to get a reliability signal, not just a single
pass rate — see the "Report pass^k next to pass@k" section of the skill. For
each case, record whether it passed on each run, then compute:

- **pass@k** — the fraction of cases that passed on at least one of the `k`
  runs.
- **pass^k** — the fraction of cases that passed on *every* one of the `k`
  runs.

## What you should see

Six cases evaluated against `tool_trajectory_avg_score` and
`final_response_match_v2`, each reported as `PASSED` or `FAILED` by `adk
eval`. The must-not-happen case
(`refund_over_the_limit_must_be_escalated_not_issued`) should pass every run:
its expected trajectory never calls `issue_refund`, so any run where the agent
calls it fails the trajectory metric. Across three or more runs, pass@k and
pass^k for that case should match — a policy the tools already enforce at the
code level shouldn't be flaky — while cases that depend on the judge's reading
of the prose may show a gap between the two.

This is a capability eval, not a regression eval yet: it hasn't been run
enough times against a live model to call it reliable. It graduates into a
regression set once it passes consistently.
