---
name: define-agent-evals
description: Pick the right metric for an agent eval — grade final state and outcome first, trajectory second, prose last, report pass^k next to pass@k, and build the first 20-50 task eval set from real failures. Use when starting evals for a new agent, choosing between ADK criteria, or deciding what an eval set should contain.
license: Apache-2.0
metadata:
  category: evals
allowed-tools: Read Write
---

# Define agent evals

How to pick what an agent eval grades, and how to build the first eval set.
This is the starting skill: every other eval skill in this repository (rubrics,
custom metrics, final-state grading, CI gating) assumes the eval set this skill
produces already exists.

## Grade in this order: state, then trajectory, then prose

An agent's conversation text is the least reliable thing to grade, because two
very different responses can both satisfy the user, and one fluent response can
still leave the system in the wrong state. Grade in this order:

1. **Final state and outcome.** Did the thing the user asked for actually
   happen? For `retail_support`, that is the order's status in the store after
   the conversation ends — `refunded`, `cancelled`, or still `placed` — not
   what the agent said about it. tau-bench grades this way: it ignores the
   conversation and diffs the database against an annotated goal state.
2. **Trajectory.** Did the agent call the right tools, in the order policy
   requires? Use ADK's `tool_trajectory_avg_score` for this. Pick its match
   mode by what the policy actually demands:
   - `EXACT` when the case has one correct path and nothing else should run.
   - `IN_ORDER` when policy requires a sequence (look up before you act) but
     tolerates extra calls around it.
   - `ANY_ORDER` when several calls must happen but their order doesn't matter.
   Don't default to `EXACT` everywhere — it fails cases the policy never
   actually constrained.
3. **Prose.** Only grade the natural-language response last, with
   `final_response_match_v2` or a rubric-based criterion. Prose quality is
   real, but it's the weakest signal: a judge can be fooled by a well-written
   response that got the state or the trajectory wrong.

Source: Anthropic, "Demystifying evals for AI agents" —
https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

## Report pass^k next to pass@k

A single pass rate hides how often the agent is reliable under repetition.
Run every case `k` times (`k` of 3 or more) and report both numbers next to
each other:

- **pass@k** — the chance of at least one success in `k` tries. Rises with
  `k`. Answers "can this agent ever do it."
- **pass^k** — the chance that *all* `k` tries succeed. Falls with `k`.
  Answers "can I trust this agent every time," which is what a customer-facing
  deployment actually needs.

A case with pass@3 = 100% and pass^3 = 20% looks fine on the first number and
is not fine at all on the second. Report both, always, not just whichever one
looks better. `tau-bench` introduced pass^k for exactly this reason: on its
retail domain, `pass^8` fell below 25% for agents that looked strong on a
single run.

Source: tau-bench — https://arxiv.org/abs/2406.12045

## Start with 20 to 50 tasks drawn from real failures

Don't start an eval set from imagination. Start from traces of things that
actually went wrong (support tickets, logged failures, bug reports), and
write 20 to 50 cases that reproduce them. A handful of synthetic happy-path
cases tells you almost nothing about where the agent actually breaks.

Within that set, deliberately include **must-not-happen cases**: tasks where
the correct behavior is for the agent to refuse or escalate, not to act. For
`retail_support`, the sharpest one is a refund request over `REFUND_LIMIT` —
the only correct trajectory calls `escalate` and never calls `issue_refund`,
regardless of how reasonable the user's request sounds. Grade a must-not-happen
case the same way as any other: by trajectory (the forbidden tool call never
appears) and by final state (the order was never refunded), not only by
whether the prose sounds appropriately cautious.

Source: Hamel Husain, evals FAQ — https://hamel.dev/blog/posts/evals-faq/

## Keep capability evals apart from regression evals

An eval set has two different jobs, and conflating them hides both signals:

- **Capability evals** are the hill you're climbing. A low pass rate here is
  expected and informative — it's the gap between what the agent can do today
  and what it needs to do. These evals change often as you add tasks.
- **Regression evals** are cases that already pass reliably. They exist to
  catch the agent getting *worse*, not to measure how much better it could
  get. Keep this set near 100% passing; a drop here blocks a change.

A capability eval graduates into the regression set once it passes
consistently (every run, over several runs, not just once). Don't mix the two
sets: a capability eval sitting in your regression suite makes every run look
like a real regression even when nothing broke, and a regression case sitting
in your capability suite hides an actual capability gap behind a number that
never moves.

Source: Anthropic, "Demystifying evals for AI agents" —
https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

## What this looks like for `retail_support`

The demo at `demos/define-agent-evals/` is a first eval set built this way:

- Six cases that come from reading `policy.md`, not imagination: a lookup, a
  cancel, a refund within the limit, a refund over the limit (must-not-happen:
  `escalate`, never `issue_refund`), a refund attempt on an already-cancelled
  order, and a lookup on an order id that doesn't exist.
- `evals/test_config.json` configures `tool_trajectory_avg_score` in `IN_ORDER`
  mode — `policy.md` demands that the agent look an order up before acting on
  it, but tolerates nothing stronger — next to `final_response_match_v2` for
  the prose.
- `evals/retail_support.evalset.json` is an ADK `EvalSet`: see
  `demos/define-agent-evals/README.md` for what to run and what you should
  see, including pass^k and pass@k once it runs against a live judge.

This set is a capability eval today — it is small and untested against a live
model. It graduates into a regression set once it passes consistently across
several runs.
