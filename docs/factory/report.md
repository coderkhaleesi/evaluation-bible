# Factory trial report

Two change requests ran end to end through the factory on this repository
between 2026-11-01 and 2026-11-04. The first was meant to merge. The second
was meant to get stuck, because its last task needs a live judge and the
build sandbox has no key. Both did what they were meant to do.

## The two requests

| Request | Issue | Pull request | Outcome |
|---|---|---|---|
| Add the `retail_support` reference agent | #31 | #32 | Merged by the App at `7f28695` after the attesting review |
| Add the `define-agent-evals` skill and its demo | #33 | #34 | Open, `factory:stuck`; T3 marked `[!]` in the body, no stub in the diff |

## Agent runs

Cost is the figure the engine reported in each run's log. One AI credit is
USD 0.01. Wall time is the whole workflow run, from trigger to conclusion.
Agent time is the agent job alone.

| Request | Run | Wall time | Agent time | Cost (USD) | Result |
|---|---|---|---|---|---|
| #31 | Planner | 6m 19s | 3m 21s | 0.38 | Plan comment, 4 tasks, 0 open questions |
| #31 | Builder | 9m 24s | 6m 02s | 1.42 | Draft PR #32, 12 files, 26 tests, every task `[x]` |
| #31 | Reviewer | 6m 07s | 3m 22s | 0.45 | COMMENT review, 2 Medium findings, both real |
| #33 | Planner | 9m 38s | 6m 41s | 0.73 | Plan comment, 3 tasks; predicted T3 blocked |
| #33 | Builder | 16m 28s | 12m 47s | 3.82 | Draft PR #34, T1 and T2 `[x]`, T3 `[!]`, `factory:stuck` |
| #33 | Reviewer | 8m 44s | 5m 15s | 0.86 | Stopped at max-turns (30); 3 inline findings posted, no summary review |

Totals: USD 2.25 for #31 and USD 5.41 for #33. The fixer never ran, because
CI never failed. `gh aw forecast` on 2026-11-04 projected 317 AI credits a
month (USD 3.17) over the planner, builder, and hello workflows, from fewer
than ten samples each, against the USD 50 ceiling in `trust-policy.md`. The
forecast does not sample the reviewer or fixer workflows.

## Human touches

`trust-policy.md` allows two human touches per change: the labels on the
issue and the attesting review on the pull request.

| Request | Touch | When (UTC) | By |
|---|---|---|---|
| #31 | `factory:ready` | 2026-11-01 06:08 | the repository owner |
| #31 | `factory:approved` | 2026-11-01 06:22 | the repository owner |
| #31 | Attesting review on `cbfcde9` | 2026-11-04 06:38 | the repository owner |
| #33 | `factory:ready` | 2026-11-04 06:41 | the session agent, on the owner's instruction to run autonomously |
| #33 | `factory:approved` | 2026-11-04 06:51 | the session agent, on the owner's instruction |

#31 counted two touches, as the policy allows: the labels, then the review.
#33 ended stuck before any review, so its touches were the labels only, and
those were applied by the session agent rather than the owner. The factory
does not measure human minutes. The only bounded interval is the owner's
reading of the #31 plan, which took under eight minutes between the plan
comment and the approval label.

One commit on #32 came from neither a human nor a factory run. The session
agent pushed `cbfcde9` to close the reviewer's two findings test-first,
because CI was green and the fixer only runs on a CI failure. See "Gaps".

## Gates that fired

- Readiness status failed on every head until the attesting review landed,
  then reported "ready; attested by coderkhaleesi" and auto-merge landed #32
  within a minute.
- The readiness workflow marked both drafts ready once CI passed.
- CI ran the changes, static, unit, and artifact lanes on both PRs. The
  artifact lane's dependency check judged `uv.lock` on #32 and passed because
  the issue named `google-adk`. The secret scan found nothing.
- gh-aw's own protected-files banner fired on `pyproject.toml` and `uv.lock`
  (#32) and on `README.md` and `pyproject.toml` (#34), putting both PRs in
  request-review mode. The factory's `request_review` rule did not fire, since
  neither diff touched a factory-protected file.
- The builder on #33 stopped at the task it could not do for real, named the
  two missing things (the `google-adk[eval]` extra and a model key with a
  network route), and refused the recorded-output shortcut the issue forbade.
  It tried the extra, saw the dependency surface it pulled in, and reverted.
- The planner on #33 predicted that block in its assumptions and told the
  builder how to report it.

## Gaps found

Each becomes a correction in the factory's T13a pass.

1. **No path from a reviewer finding to the fixer.** The fixer triggers on a
   CI failure only. A human either fixes a finding by hand or breaks CI with a
   regression test to wake the fixer. On #32 the session agent did the former.
2. **`uv add` is not in the builder's bash allowlist**, though the plan told
   the builder to use it. The builder edited `pyproject.toml` by hand and ran
   `uv sync`, which produced the same lock. The allowlist or the planner's
   vocabulary should agree.
3. **The reviewer's turn budget is too small for a data-heavy diff.** A
   681-line diff with a 421-line JSON eval set exhausted 30 turns before the
   summary review was submitted. The inline findings were posted, the summary
   and the evidence check were not.
4. **The builder on #33 cost 2.7 times the builder on #31.** Installing and
   reverting the `eval` extra and investigating the blocked run took the
   turns. A planner assumption that is checkable before the build (does the
   base install run `adk eval`) would have saved most of it.
5. **gh-aw redacts URLs in plan comments.** The #33 plan's source links came
   out as `redacted`, so the builder had to take them from `PLAN.md`. The issue
   happened to say so.
6. **`EVAL_BIBLE_JUDGE_MODEL` is documented but not wired** in the #34 demo.
   The reviewer's High finding stands until T3 is unblocked.

## What unblocks #34

A run with the `google-adk[eval]` extra, both model variables set, and a
network route to the model vendor. That is the acceptance lane the factory's
T8 adds, with the key entered as a repository secret by the owner.
