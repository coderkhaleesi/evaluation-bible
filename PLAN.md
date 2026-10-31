# evaluation-bible plan

This repo collects agent-evaluation best practices for enterprises as agent skills (`SKILL.md` files that Claude Code, Codex, Gemini CLI, Cursor, and Copilot can load), with runnable Python demos built on Google ADK. It covers the whole eval cycle, from the first eval set to online monitoring, A/B tests, and self-healing loops. The core stays cloud agnostic. Cloud adapters come later as optional extras.

The plan has seven phases. Phase 0 scaffolds the repo. Phases 1 to 6 each add one chapter of skills and demos. Every skill ships with a demo of the same name, and CI rejects a skill without one.

Status on 2026-10-31: plan only. No skills or demos exist yet.

## How to read this

The body is a how-to for whoever builds the repo. Each phase lists the skills and demos it adds and the condition that closes it. The catalogue after the phases describes each skill and demo in one block. Appendices hold the research summary, decisions, open questions, risks, and the reading list.

The research behind this plan lives in `docs/research/`. Each claim there carries its source URL, and unverified claims are labeled.

## Repository layout

```
evaluation-bible/
  README.md
  PLAN.md                      this file
  CONTRIBUTING.md
  LICENSE                      Apache-2.0, see decisions
  pyproject.toml               one uv project, [dependency-groups] dev
  uv.lock
  justfile                     lint, test, smoke, validate
  .github/workflows/           keyless CI on every PR, keyed evals on dispatch
  .claude-plugin/              marketplace and plugin manifest for Claude Code
  .agents/skills -> ../skills  symlink so Codex, Gemini CLI, Cursor, and Copilot find the skills
  skills/<name>/SKILL.md       one skill per practice, spec fields only
  skills/<name>/references/    long material the skill points to
  skills/<name>/scripts/       helpers the skill tells the agent to run
  demos/<name>/                one runnable demo per skill, same name
  demos/<name>/README.md       what to run and what you should see
  demos/<name>/evals/          *.evalset.json and test_config.json
  demos/<name>/tests/          pytest, keyless where possible
  src/evaluation_bible/        shared library the demos import
  src/evaluation_bible/agents/ the reference agent every demo uses
  docs/research/               the research briefs behind this plan
  docs/lifecycle.md            the end-to-end cycle, one page
  tools/validate_structure.py  the CI check for skill and demo pairing
```

## The lifecycle the repo teaches

The chapters follow the order an enterprise team meets the work. Each stage names the skills that cover it. The skill names are the directory names under `skills/`.

| Stage | Question the team asks | Skills |
|---|---|---|
| 1. Define | What does good look like, and how do we score it? | `define-agent-evals`, `write-rubrics`, `custom-metrics`, `grade-final-state` |
| 2. Grade | Can we trust the grader? | `calibrate-judge` |
| 3. Run offline | Does this change pass, and is the difference real? | `run-evals-in-ci`, `compare-eval-runs` |
| 4. Build data | Where do eval cases come from? | `build-eval-sets-from-traces`, `simulate-users`, `simulate-environment`, `version-eval-data` |
| 5. Observe | What is the agent doing in production? | `trace-agents-with-otel`, `sample-and-judge-online` |
| 6. Diagnose | Why do offline and online numbers disagree? | `error-analysis`, `transition-failure-matrix`, `diagnose-offline-online-gap` |
| 7. Experiment | Is variant B better for real users? | `ab-testing` |
| 8. Improve | How do we climb, and when do we let the system fix itself? | `hill-climb`, `optimize-prompts-with-gate`, `self-heal`, `scale-monitoring` |
| 9. Protect | Is the agent safe under attack and policy? | `security-evals` |

## Phases

### Phase 0. Scaffold the repo

Build the skeleton that every later phase drops into.

1. Create `pyproject.toml` with uv, `google-adk>=2.13`, and a dev group with pytest, ruff, and mypy. Commit `uv.lock`.
2. Write the reference agent in `src/evaluation_bible/agents/retail_support/`. It is an ADK `LlmAgent` over an in-memory order store with tools `lookup_order`, `cancel_order`, `issue_refund`, and `escalate`, and a written policy (for example, refunds over a limit need escalation). One agent serves every demo, so each demo can grade the final store state, the tool trajectory, and policy adherence.
3. Read the agent model and the judge model from `EVAL_BIBLE_AGENT_MODEL` and `EVAL_BIBLE_JUDGE_MODEL`. Accept any string the ADK `LLMRegistry` resolves, including LiteLLM prefixes, so no provider is hard-wired. Ship `.env.example`.
4. Copy a skill template into `skills/_template/` with the six portable frontmatter fields only.
5. Write `tools/validate_structure.py`. It fails when a skill has no demo of the same name, when `name` differs from the directory, when `SKILL.md` exceeds 500 lines, or when a frontmatter field is outside the portable six.
6. Add CI. On every PR run `ruff check`, `ruff format --check`, `skills-ref validate skills/*`, `tools/validate_structure.py`, and keyless pytest. Run live-model evals only on `workflow_dispatch` with secrets.
7. Settle the open questions in Appendix C that block Phase 1, and record each answer in `docs/research/decisions.md`.
8. Write `CONTRIBUTING.md`, `LICENSE`, and `docs/lifecycle.md`.

Done when CI is green on an empty skills tree and `uv run pytest` runs the reference agent against a recorded session with no API key.

### Phase 1. Offline foundations

Add the skills a team needs to write and trust its first eval set.

Skills and demos. `define-agent-evals`, `write-rubrics`, `custom-metrics`, `grade-final-state`, `calibrate-judge`, `run-evals-in-ci`, `compare-eval-runs`.

Shared code. `src/evaluation_bible/metrics/final_state.py` (a custom metric that reads `EvalCase.final_session_state`, which ADK declares but no evaluator uses), `src/evaluation_bible/judge/calibration.py` (TPR, TNR, Cohen's kappa, position-swap test), `src/evaluation_bible/compare/runs.py` (paired and clustered standard errors over two `EvalSetResult` files).

Done when a PR to the reference agent's prompt runs `adk eval` in CI, reports pass^k with a confidence interval, and fails on a regression against the stored baseline.

### Phase 2. Build data

Add the ways eval cases come into being.

Skills and demos. `build-eval-sets-from-traces`, `simulate-users`, `simulate-environment`, `version-eval-data`.

Shared code. `src/evaluation_bible/traces/to_eval_case.py` (an OTLP or Phoenix or Langfuse export to `EvalCase`), a persona matrix for `LlmBackedUserSimulator` (cooperative, terse, frustrated, adversarial), and a leak check that asserts the agent never saw the hidden goal.

Done when a simulated conversation over the reference agent passes `per_turn_user_simulator_quality_v1`, the leak check, and a small replay against human transcripts, and the demo reports pass^k per persona.

### Phase 3. Observe and diagnose

Add tracing, online sampling, and the process for closing the offline-online gap.

Skills and demos. `trace-agents-with-otel`, `sample-and-judge-online`, `error-analysis`, `transition-failure-matrix`, `diagnose-offline-online-gap`.

Shared code. `src/evaluation_bible/online/sampler.py` (stratified sampling, tiered evaluators, and emission of the OpenTelemetry `gen_ai.evaluation.result` event), `src/evaluation_bible/analysis/transition_matrix.py`.

Done when the reference agent runs under load with traces in Phoenix or Langfuse, a cheap check runs on every trace, a judge runs on a stratified sample, and a notebook attributes an offline-online gap and promotes the failing traces into the eval set.

### Phase 4. Experiment

Add A/B testing for agents, grounded in Evan Miller's articles and his "Adding Error Bars to Evals" paper.

Skills and demos. `ab-testing`, with one reference file per article under `skills/ab-testing/references/` and these scripts in `src/evaluation_bible/stats/`.

| Script | Formula | Source |
|---|---|---|
| `sample_size.py` | `n = 16 p(1-p) / delta^2`, exact z form, the low-base-rate table, and the lazy-assignment efficiency `E = (1-p1)/(1-p2)` | How Not To Run An A/B Test, The Low Base Rate Problem, Lazy Assignment and A/B Testing |
| `sequential.py` | stop with a winner when `T - C >= 2 sqrt(N)`, with no winner when `T + C >= N`, and warn when `1.5p + delta >= 0.36` | Simple Sequential A/B Testing |
| `bayes_ab.py` | closed-form `Pr(p_B > p_A)` in log-beta, the Gamma-Poisson rate form, and the three-arm form | Formulas for Bayesian A/B Testing |
| `peeking_simulator.py` | A/A simulation with daily peeks that reproduces the ~26% false-positive figure | How Not To Run An A/B Test |
| `error_bars.py` | paired SE, clustered SE, K resamples per question, and the power formula | Adding Error Bars to Evals (arXiv 2411.00640) |
| `cuped.py` | `Y ~ arm + pre-period covariates + concurrent arms` with robust SEs | You Can't Spell CUPED Without Frisch-Waugh-Lovell |
| `leaderboard.py` | Wilson lower bound and the star-rating lower bound | How Not To Sort By Average Rating, Ranking Items With Star Ratings |

Done when the demo runs an A/B test between two prompts for the reference agent on simulated traffic, the peeking simulator reproduces Miller's figure within a tolerance, and `bayes_ab.py` matches a Monte Carlo check.

### Phase 5. Improve and scale

Add the hill-climb loop, gated prompt optimization, self-healing, and the cost model for scale.

Skills and demos. `hill-climb`, `optimize-prompts-with-gate`, `self-heal`, `scale-monitoring`.

Done when a worked hill-climb log exists for the reference agent (trace review, open and axial codes, a taxonomy count, one fix, a re-run with intervals, promotion to the regression set), `adk optimize` proposes a prompt patch that must pass the regression gate before a human approves it, and a load script reports judge cost at 1x, 10x, and 100x traffic.

### Phase 6. Protect

Add the safety and security suite.

Skills and demos. `security-evals`.

Done when the reference agent is scored on injected tool outputs with state-based attack-success checks, a PII-leak detector runs on outputs and traces, policy rubrics run as `rubric_based_*` metrics, and a scheduled red-team run reports attack success rate next to utility.

### Later, out of scope for now

Cloud adapters (Vertex AI Evaluation Service, Bedrock, Azure AI Foundry) as optional extras that swap in for the cloud-agnostic metrics. Non-Python ADK. Frameworks other than ADK.

## Skill and demo catalogue

Each block names the skill, what it teaches, what the demo shows, the ADK features it uses, and the sources it draws on. Sources are in `docs/research/`.

### define-agent-evals

Teaches how to pick the metric for an agent. Grade the final state and the outcome first, the trajectory second, and the prose last. Report pass^k for reliability next to pass@k. Start with 20 to 50 tasks drawn from real failures, including tasks where a behavior must not happen. Keep capability evals (low pass rate, the hill to climb) apart from regression evals (near 100%).
Demo. The first eval set for the reference agent, with `tool_trajectory_avg_score` in `IN_ORDER` mode only where policy demands order, `final_response_match_v2`, and the final-state metric. Runs under `adk eval` and under pytest.
ADK. `EvalSet`, `EvalCase`, `test_config.json`, `MultiRunConfig` with `pass_rate`.
Sources. Anthropic, Demystifying evals for AI agents. tau-bench (pass^k). Hamel Husain, evals FAQ.

### write-rubrics

Teaches how to write rubrics the three `rubric_based_*` metrics can grade. Binary per failure mode, not Likert. One rubric per failure, worded so two readers agree.
Demo. Rubrics for the reference agent's policy, graded with a non-Gemini judge to show the judge is pluggable.
ADK. `Rubric`, `RubricsBasedCriterion`, `JudgeModelOptions.num_samples`.
Sources. Hamel Husain, evals FAQ. Eugene Yan, LLM evaluators.

### custom-metrics

Teaches both routes for a custom metric, the `custom_metrics` config entry and the `Evaluator` subclass registered through `MetricEvaluatorRegistry`.
Demo. A metric that counts policy violations from tool arguments.
ADK. `custom_metric_evaluator`, `MetricEvaluatorRegistry.register_evaluator`.

### grade-final-state

Teaches outcome grading. Compare the store state after the conversation with the annotated goal state, the way tau-bench grades, and ignore the conversation text.
Demo. The final-state metric over the reference agent's order store.
ADK. `EvalCase.final_session_state`, which exists in the schema but no built-in evaluator reads.
Sources. tau-bench. Anthropic, Demystifying evals for AI agents.

### calibrate-judge

Teaches how to validate an LLM judge before trusting it. Label 50 to 100 failures from 200 or more samples with one domain expert writing critiques. Split into train, dev, and test. Report TPR, TNR, and Cohen's kappa against the human labels, run a position-swap test for pairwise judges, and fail CI when kappa drops after a judge prompt or model change. Do not let the agent's model family judge itself without checking self-preference.
Demo. A labeled CSV, one binary judge per failure mode, and the calibration report.
ADK. `LlmAsJudge` subclass, judge model resolved through `LLMRegistry`.
Sources. Shankar et al., Who Validates the Validators. Zheng et al., MT-Bench. Judging the Judges (kappa). Panickssery et al. (self-preference). Hamel Husain.

### run-evals-in-ci

Teaches the CI setup. `adk eval` exit codes are reliable only from 2.13.0. Use `MultiRunConfig` with `pass_rate` for a stochastic agent. Keep keyless checks on every PR and keyed evals behind `workflow_dispatch`. Record sessions with `adk conformance record` so replay tests need no key.
Demo. The GitHub Actions workflow, plus a recorded session replay.
ADK. `adk eval`, `AgentEvaluator.evaluate`, `adk conformance`.

### compare-eval-runs

Teaches how to say a difference is real. ADK stores one `EvalSetResult` per run and has no compare command. Compare paired per-task differences, cluster by task family, add K trials per task, and report the minimum detectable effect at the current n.
Demo. `compare/runs.py` over two stored runs of the reference agent.
Sources. Adding Error Bars to Evals (arXiv 2411.00640).

### build-eval-sets-from-traces

Teaches the loop that keeps the eval set honest. Sample production traces, convert the failing ones into eval cases, reproduce offline, fix, and keep the case as a regression test. ADK converts a session in `adk web` only, so the demo adds a converter from OTLP exports.
Demo. `traces/to_eval_case.py` run against a Phoenix or Langfuse export.
ADK. `EvalCase`, `Invocation`, `IntermediateData`, `adk eval_set add_eval_case`.
Sources. Hamel Husain. Langfuse and LangChain write-ups (vendor sources).

### simulate-users

Teaches ADK user simulation and how to validate the simulator. Write a `ConversationScenario`, pick or define a `UserPersona`, cap turns, and grade with `per_turn_user_simulator_quality_v1`. Known simulator failures are over-cooperation, goal confusion, and simulator randomness that inflates the spread of pass^k. Only the rubric, hallucination, user-sim-quality, and multi-turn metrics support simulated conversations.
Demo. The persona matrix, the leak check, and pass^k per persona for the reference agent.
ADK. `LlmBackedUserSimulator`, `ConversationScenario`, `UserPersonaRegistry`, `per_turn_user_simulator_quality_v1`.
Sources. tau-bench, tau2-bench. Sierra on simulations. SimulatorArena. ADK user-sim docs.

### simulate-environment

Teaches tool mocking and fault injection so the agent is tested under errors and latency.
Demo. `EnvironmentSimulationPlugin` injecting HTTP errors and latency into `lookup_order` with a probability and a seed.
ADK. `EnvironmentSimulationConfig`, `ToolSimulationConfig`, `InjectionConfig`.

### version-eval-data

Teaches dataset versioning and lineage with git, because `EvalSet` has no version or hash field. Record the trace id each case came from, the labeler, and the date.
Demo. A convention file and a script that stamps a content hash into `metadata`.

### trace-agents-with-otel

Teaches vendor-neutral tracing. Export through `OTEL_EXPORTER_OTLP_*`, pin the semantic-convention schema (2.13.0 moved to the 1.44 schema and dropped the `call_llm` span), keep content capture off by default and turn it on for a sample, and use `BasePlugin` hooks for per-call capture.
Demo. The reference agent exporting to Phoenix and to Langfuse through OpenInference, switched by one environment variable.
ADK. `maybe_set_otel_providers`, `BasePlugin`, `AutoTracingPlugin`, `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`.
Sources. ADK observability docs. OpenTelemetry GenAI semantic conventions.

### sample-and-judge-online

Teaches online evaluation, which ADK does not provide. Run cheap checks on every trace and a judge on a stratified sample. Keep a fixed random slice per batch. Alert when the lower confidence bound crosses the threshold, not the point estimate. Emit judge results as `gen_ai.evaluation.result` events so they travel with the trace.
Demo. `online/sampler.py` over the traced reference agent, with a dashboard of pass rate, cost, and latency.
Sources. Hamel Husain. OpenTelemetry GenAI conventions. LangChain and Langfuse online-eval docs (vendor sources).

### error-analysis

Teaches open coding, then axial coding, over at least 100 traces until the failure categories stop growing. Note the first upstream failure in each trace. Count each category before fixing anything. This skill credits and builds on `hamelsmu/evals-skills`.
Demo. A coded sample of reference-agent traces and the resulting taxonomy table.
Sources. Hamel Husain, evals FAQ.

### transition-failure-matrix

Teaches step diagnostics for agents. For each failed trace record the last good state and the first failing state, and tabulate the pairs to find hotspots.
Demo. `analysis/transition_matrix.py` over reference-agent traces.
Sources. Hamel Husain, evals FAQ.

### diagnose-offline-online-gap

Teaches the process when offline and online numbers disagree. Check the known causes in order. Unseen intents, judge disagreement, harness and context differences, proxy metrics that reward the wrong thing, contaminated or broken tasks, and criteria drift. Measure offline pass rate and online sampled-judge pass rate on the same agent version, attribute the gap, and promote the failing traces into the eval set.
Demo. A notebook over the reference agent that compares the two numbers and attributes the gap.
Sources. Anthropic. Hamel Husain. Agentic Benchmark Checklist (arXiv 2507.02825). Shankar et al. (criteria drift).

### ab-testing

Teaches online experiments for agents. Fix n before launch and show the detectable effect at the current n instead of a live p-value. Use the sequential rule when the success event is rare and the fixed-n test when it is common. Report `Pr(B > A)` from counts. Rare failures need very large n, so measure a common precursor, test offline on an adversarial set, or assign lazily at the hand-off to the agent. Log the exposure time apart from the session start. Adjust for pre-period covariates and concurrent experiments. Use quantile tests for latency and cost.
Demo. The seven scripts in the Phase 4 table, run against simulated traffic between two prompts.
Sources. Evan Miller's articles and calculators, and Adding Error Bars to Evals.

### hill-climb

Teaches sustained improvement of one metric. Loop over hypothesis, before-and-after measurement with intervals, a decision log, and one commit per accepted win. Graduate a capability eval into the regression set when it passes consistently. Retire or harden a saturated eval.
Demo. The worked log for one reference-agent metric.
Sources. Anthropic. Hamel Husain. Eugene Yan.

### optimize-prompts-with-gate

Teaches prompt optimization as the last step, after the evals are trusted. Run `adk optimize` with the GEPA optimizer, and let a patch through only after it passes the regression gate and pass^k and a human approves it. Note the practitioner caveat that a weak reflection model leaves the seed prompt unchanged.
Demo. `adk optimize` on the reference agent with the gate in front.
ADK. `GEPARootAgentPromptOptimizer`.
Sources. GEPA (arXiv 2507.19457). Decagon on GEPA in production. Hamel Husain.

### self-heal

Teaches what is safe to automate today. Cluster failing traces, turn clusters into candidate eval cases, propose a fix, and never merge without the gate. Run inline guardrails with deterministic fallbacks apart from the evaluators, because a judge is too slow to sit in the request path.
Demo. The propose-never-auto-merge loop over the reference agent, with one guardrail and fallback.
Sources. Hamel Husain. LangSmith Insights (vendor). NeMo Guardrails docs.

### scale-monitoring

Teaches what breaks when traffic grows 10x to 100x. Judge spend grows with the sample rate, so fix the sample count per segment. Trace storage and PII exposure grow, so keep content capture off and capture on a sample. The label backlog outruns reviewers, so route by classifier and uncertainty. Rare failures still need targeted sampling.
Demo. A load script that reports judge cost and trace volume at 1x, 10x, and 100x.

### security-evals

Teaches the safety suite. Prompt injection through tool outputs, scored by state-based attack-success checks rather than a judge. A PII-leak detector on outputs and traces. Policy adherence as rubrics. Authorization and precondition checks on tool calls. A scheduled red-team run with garak or PyRIT, reported as attack success rate next to utility. `safety_v1` in ADK is Vertex-only, so the demo reimplements a safety rubric.
Demo. Injected product descriptions in the reference agent's order store, and the full suite.
Sources. AgentDojo. OWASP LLM Top 10 and Agentic Top 10. tau-bench policy adherence.

## Appendix A. What the research found

Full briefs with sources are in `docs/research/`.

ADK (brief `adk.md`). The current release is google-adk 2.13.0. The eval data model is `EvalSet` to `EvalCase`, where a case holds either a static conversation or a `ConversationScenario`. Thirteen quality metrics and four always-on efficiency metrics exist. Four need Vertex and a GCP project (`response_evaluation_score`, `safety_v1`, and the three `multi_turn_*_v1`). The rest run locally, and the LLM judge resolves any `LLMRegistry` model string. User simulation, environment simulation, multi-run pass rates, custom metrics, conformance record and replay, and `adk optimize` are built in. Spans follow the OpenTelemetry GenAI conventions and export to any OTLP backend. ADK has no online sampling, no A/B routing, no run comparison, no judge calibration, no annotation queue, no dataset versioning, no baseline-relative CI gate, and no final-state assertion. Those gaps are what this repo builds.

Evaluation practice (brief `agent-evals.md`). The consensus is to grade state and outcomes first, report pass^k with intervals, treat every judge and simulator as a model with its own validation set, and run one loop from production trace to regression gate. Judge calibration uses binary labels, TPR and TNR, and chance-corrected agreement. User simulators fail by over-cooperation and goal confusion. Online evals run tiered. Closed-loop prompt auto-repair without a human gate has no documented safe deployment.

A/B testing (brief `evan-miller.md`). Evan Miller's site holds twelve A/B and statistics pieces, seven calculators, and the eval-specific paper Adding Error Bars to Evals. Peeking at a dashboard raises the false-positive rate from 5% to about 26% in his simulation. The sequential test suits rare events and is a poor fit when success is around 70%. A 10% relative change on a 0.1% failure rate needs about 1.6 million sessions per arm. He has no article on bandits, so the repo will not attribute bandit claims to him.

Skills format (brief `skills-format.md`). The Agent Skills spec requires only `name` and `description`, and `name` must match the directory. claude.ai and the Skills API reject fields outside `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`. Codex, Gemini CLI, Cursor, Copilot, and OpenCode all read `.agents/skills/`. The closest prior art is `hamelsmu/evals-skills`, which packages eval practice as bare skills without runnable demos.

## Appendix B. Decisions

- Skills use the six portable frontmatter fields only, so one tree uploads to every tool. The canonical tree is `skills/`, with `.agents/skills` as a symlink and `.claude-plugin/` for Claude Code.
- One skill and one demo per PR, with the same name, enforced by `tools/validate_structure.py`, not by prose.
- The cloud-agnostic metric set excludes the four Vertex-only metrics. Safety and multi-turn task success are reimplemented as rubric or custom metrics.
- The judge model is a configurable `LLMRegistry` string, pinned per metric, and by default from a different model family than the agent.
- Every reported number is pass^k with a confidence interval, never a single run.
- Pin `google-adk>=2.13` for the exit code and the 1.44 telemetry schema.
- One reference agent, the retail support agent, serves every demo.
- The license is Apache-2.0, matching ADK, the Agent Skills spec, and `anthropics/skills`, with its patent grant for contributed scripts. This is a recommendation for the repo owner to confirm.
- The repo credits `hamelsmu/evals-skills` and differs by shipping runnable ADK demos and the online half of the cycle.

## Appendix C. Open questions to settle in Phase 0

Each one is a fact to check by running code, not a preference.

1. Does `google-adk` need the `eval` extra for the local metrics? The extra pulls `google-cloud-aiplatform` even for local use. Find the smallest install that runs `tool_trajectory_avg_score`, ROUGE, and the rubric metrics.
2. Is ADK issue 5410 fixed? It reports `tool_trajectory_avg_score` returning 0.0 on identical tool calls, which would break the first demo.
3. Does `JudgeModelOptions.judge_model` accept a `BaseLlm` instance? The 2.13.0 changelog says yes, but the field is typed `str` on main.
4. Does `adk conformance record` give a keyless replay path for pytest, or does the keyless smoke test need canned sessions?
5. Does a non-Gemini judge work end to end through `LLMRegistry`? The code path exists, and nobody on this research pass ran it.
6. What release introduced `MultiRunConfig`? It is on main with no changelog entry.
7. The user simulator's default model is `gemini-flash-latest` in the docs and `gemini-2.5-flash` in the code. Pin it explicitly in every demo.

## Appendix D. Risks

- ADK moves fast. Twelve releases shipped in 2026, with a breaking telemetry change in 2.13.0. Pin the version in `pyproject.toml` and test the upgrade in its own PR.
- Four ADK metrics are Vertex-only. Reimplementing them as rubrics changes what they measure, so the demo must say so.
- Judge cost. Rubric metrics sample five times per invocation by default. The demos pin `num_samples` and report cost.
- Simulated users inflate scores. The simulator validation step in `simulate-users` is mandatory before any pass^k per persona is reported.
- Two arXiv identifiers in the research (WebArena, ToolBench) are from memory. Verify before citing them in a skill.
- No Miller article on bandits exists. Bandit claims must cite other sources.

## Appendix E. Reading list

The briefs in `docs/research/` carry the full URL list. The entries below are the ones to read before writing any skill.

- Anthropic, Demystifying evals for AI agents, https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Hamel Husain, evals FAQ, https://hamel.dev/blog/posts/evals-faq/
- ADK evaluate docs, https://adk.dev/evaluate/ and criteria at https://adk.dev/evaluate/criteria/
- ADK user simulation, https://adk.dev/evaluate/user-sim/
- ADK observability, https://adk.dev/observability/traces/
- tau-bench, https://arxiv.org/abs/2406.12045 and tau2-bench, https://arxiv.org/abs/2506.07982
- Shankar et al., Who Validates the Validators, https://arxiv.org/abs/2404.12272
- Evan Miller, How Not To Run An A/B Test, https://www.evanmiller.org/how-not-to-run-an-ab-test.html
- Evan Miller, Simple Sequential A/B Testing, https://www.evanmiller.org/sequential-ab-testing.html
- Evan Miller, Formulas for Bayesian A/B Testing, https://www.evanmiller.org/bayesian-ab-testing.html
- Evan Miller, The Low Base Rate Problem, https://www.evanmiller.org/the-low-base-rate-problem.html
- Adding Error Bars to Evals, https://arxiv.org/abs/2411.00640
- Agent Skills specification, https://agentskills.io/specification
- hamelsmu/evals-skills, https://github.com/hamelsmu/evals-skills
- OpenTelemetry GenAI agent spans, https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans
