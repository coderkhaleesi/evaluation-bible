# Research brief: state of the art in evaluating LLM agents

Compiled 2026-10-31 for the evaluation-bible repo (Python, Google ADK, cloud agnostic).

**Verification legend.**
- No tag means the claim was read on the primary page this session (WebFetch of the page, or the arXiv abstract).
- `[snippet]` means the claim came from a search-result snippet of the primary URL. The page itself was not opened.
- `[secondary]` means the claim came from a third-party summary. Check it against the primary source before citing it.
- `[inference]` means the brief's own synthesis, with no single source behind it.
- `[gap]` means no primary source turned up for that sub-topic.

---

## 1. Online vs offline eval divergence

**Findings.**
- Anthropic splits automated evals (pre-launch and CI) from production monitoring, A/B tests, user feedback, and transcript review. It says each layer catches what the others miss, such as drift and real-world failures, and that no single layer is enough. https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Hamel Husain's FAQ separates the two by purpose. CI uses small curated sets (often 100+ examples) and prefers deterministic assertions. Production monitoring samples live traces and runs reference-free LLM judges asynchronously. Track confidence intervals and investigate when the lower bound crosses a threshold. Representative production failures go back into the CI set. https://hamel.dev/blog/posts/evals-faq/
- Benchmark scores can be a weak proxy for real tasks. TerminalWorld reports Pearson r = 0.20 between Terminal-Bench 2.0 scores and scores on real-world terminal tasks (57.0 to 82.7% versus 49.0 to 62.5%). https://arxiv.org/pdf/2605.22535 `[snippet]`
- Data leakage and broken tasks distort offline numbers. OpenAI reportedly retired SWE-bench Verified in February 2026. It cited contamination: GPT-5.2, Claude Opus 4.5, and Gemini 3 Flash had seen the solutions. It also cited a 138-task audit that found 59.4% of the persistently failed tasks broken. https://decrypt.co/359012/openai-benchmark-measure-ai-coding-supremacy-contaminated `[secondary]`
- Proxy metrics and reward design mislead. The Agentic Benchmark Checklist found that tau-bench scored empty responses as successes. It estimates that task-setup and reward flaws misstate performance by up to 100% relative, and that 7 of 10 popular agent benchmarks had outcome-validity flaws. https://arxiv.org/abs/2507.02825 `[snippet]`
- Judge and criteria drift. Shankar et al. show that grading outputs changes the criteria graders hold ("criteria drift"), so an offline judge tuned once goes stale as the pipeline and the users change. https://arxiv.org/abs/2404.12272
- Harness and context differences. The same model reportedly scored 64.9% in one agent framework and 57.6% in another. https://kili-technology.com/blog/ai-benchmarks-guide-the-top-evaluations-in-2026-and-why-theyre-not-enough `[secondary]`
- Closing the gap means routing failing production traces into dataset items, reproducing each failure offline, fixing it, and keeping the item as a permanent regression test. Langfuse and LangChain describe this loop; both are vendor sources. https://langfuse.com/blog/2025-11-12-evals and https://www.langchain.com/resources/agent-evals `[snippet]`
- Shadow then A/B. Common practice runs a candidate on mirrored production traffic with no user impact, then A/B tests it on a small share of traffic. GitHub Copilot reportedly goes offline, then dogfood, then online A/B. https://www.datadoghq.com/blog/ab-testing.md `[secondary]`
- Interleaving (from search ranking) came up in no agent-eval source found this session. `[gap]`

**What the repo should teach or demo from this.** A "gap diagnosis" notebook. It compares offline pass rate with an online sampled-judge pass rate on the same agent, attributes the gap (unseen intents, judge disagreement, harness differences), and promotes failing traces into the ADK eval set as regression cases.

---

## 2. LLM-as-judge

**Findings.**
- Zheng et al. (MT-Bench) name position, verbosity, and self-enhancement bias. They report that GPT-4 judges reach over 80% agreement with humans, the same as human-human agreement. https://arxiv.org/abs/2306.05685
- Self-preference is measurable. Self-recognition ability correlates linearly with self-preference strength, and GPT-4 identifies its own outputs 73.5% of the time. Do not let the agent's model family judge itself without checking for this bias. https://arxiv.org/abs/2404.13076 `[snippet]`
- Verbosity bias can be corrected statistically. Length-Controlled AlpacaEval regresses length out and raises Spearman correlation with Chatbot Arena from 0.94 to 0.98. https://arxiv.org/abs/2404.04475 `[snippet]`
- Use chance-corrected agreement, not percent agreement. "Judging the Judges" shows that judges with high percent agreement can still diverge badly. Kappa (later Scott's pi) separates judges where raw agreement does not. GPT-4 Turbo reached kappa 0.84 against a human ceiling of 0.96. https://arxiv.org/abs/2406.12624 `[snippet]`
- Eugene Yan treats evaluators as classifiers. Measure precision and recall on the failure class. Use Cohen's kappa for categorical labels and Kendall's tau or Spearman for ordinal ones. Pairwise suits subjective qualities. Label 50 to 100 failures out of 200 or more samples, and build one evaluator per dimension. https://eugeneyan.com/writing/llm-evaluators/ and https://eugeneyan.com/writing/product-evals/ `[snippet]`
- Pairwise versus pointwise is contested. Pairwise does better on standard sets but worse under adversarial inputs, where pointwise is more robust. https://arxiv.org/html/2406.12319v2 `[snippet]`
- Hamel Husain's workflow. Use binary pass/fail, not Likert. One domain expert ("benevolent dictator") labels with written critiques ("critique shadowing"). Split labels into train, dev, and test. Report TPR and TNR of the judge against the human labels. Build one judge per failure mode. https://hamel.dev/blog/posts/evals-faq/ and https://simonwillison.net/2024/Oct/30/llm-as-a-judge `[secondary, summarizes Hamel's Oct 2024 judge post]`
- "Who Validates the Validators" (EvalGen). People grade a subset of outputs, and the system selects the candidate assertions or judge prompts that best agree with those grades. The finding is that criteria evolve while you grade, so judge alignment is iterative and never done once. https://arxiv.org/abs/2404.12272
- Krippendorff's alpha. No agent-eval primary source turned up that recommends it over kappa. It is the standard choice when there are more than two raters or labels are missing. `[gap]` `[inference]`

**What the repo should teach or demo from this.** A "judge the judge" module. It holds a labeled CSV, a binary judge per failure mode, and train/dev/test splits. A report gives TPR, TNR, Cohen's kappa, and a position-swap test, and CI fails when kappa drops below a threshold after a judge-prompt or judge-model change.

---

## 3. Agent-specific evals

**Findings.**
- Anthropic's anatomy: task, trial, grader, transcript, outcome, harness. The guidance is to grade outcomes (the final environment state, such as whether a booking exists) rather than rigid paths, and to give partial credit. Start with 20 to 50 tasks drawn from real failures, including cases where a behavior should not happen. Capability evals start with low pass rates. Regression evals stay near 100%. Read transcripts before trusting scores. https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- pass@k versus pass^k. pass@k is the chance of at least one success in k tries and rises with k. pass^k is the chance that all k tries succeed and falls with k. Use pass^k for customer-facing reliability. Same Anthropic URL; pass^k comes from tau-bench: https://arxiv.org/abs/2406.12045
- tau-bench uses LLM-simulated users plus domain APIs and policies, and it grades by comparing the final DB state to an annotated goal state. gpt-4o succeeded on fewer than 50% of tasks, and pass^8 on retail fell below 25%. https://arxiv.org/abs/2406.12045
- tau2-bench adds a dual-control Telecom domain (a Dec-POMDP) where the user also has tools, plus a compositional task generator. Agents drop sharply from no-user to dual-control mode. https://arxiv.org/abs/2506.07982 and https://github.com/sierra-research/tau2-bench
- OpenAI's guidance starts from trace grading while debugging (right tool? right handoff?), then moves to datasets and eval runs for repeatability. https://developers.openai.com/api/docs/guides/agent-evals and https://developers.openai.com/api/docs/guides/trace-grading `[snippet]`
- Benchmarks and what each one measures:
  - SWE-bench measures real GitHub issues, graded by repo tests. Verified is now considered contaminated, and Pro is the suggested successor. https://arxiv.org/abs/2310.06770 `[snippet]`
  - WebArena measures self-hosted realistic websites with functional task checks. https://arxiv.org/abs/2307.13854 `[unverified ID]`
  - GAIA measures questions that are easy for humans but need tools and multi-step reasoning. https://arxiv.org/abs/2311.12983 `[snippet]`
  - AgentBench measures 8 interactive environments (OS, DB, KG, web, and others). https://arxiv.org/abs/2308.03688 `[snippet]`
  - BFCL measures function-call correctness via AST matching (v1), multi-turn calling (v3), and agentic tasks (v4). https://gorilla.cs.berkeley.edu/leaderboard.html `[snippet]`
  - ToolBench / ToolLLM measures API selection and calling over 16k+ real APIs. https://arxiv.org/abs/2307.16789 `[unverified ID]`
- Trajectory matching modes. LangChain agentevals offers strict, unordered, subset, and superset modes, plus an LLM trajectory judge for reasonableness. ADK's `tool_trajectory_avg_score` offers EXACT, IN_ORDER, and ANY_ORDER. https://github.com/langchain-ai/agentevals and https://adk.dev/evaluate/criteria
- ADK ships multi-turn LLM-judged criteria: `multi_turn_task_success_v1`, `multi_turn_trajectory_quality_v1`, `multi_turn_tool_use_quality_v1`, the rubric-based tool-use, response, and trajectory criteria, `hallucinations_v1`, and `safety_v1`. It also has non-gating efficiency counters (tool calls, inference calls, tokens, duration). A reported bug says `tool_trajectory_avg_score` returns 0.0 on identical calls, status unknown: https://github.com/google/adk-python/issues/5410. https://adk.dev/evaluate/criteria
- Agent-as-a-Judge gives the judge agentic access to the trajectory and workspace. It reached about 90% agreement with human consensus, against about 70% for LLM-as-a-Judge, on DevAI (55 tasks, 365 requirements). https://arxiv.org/abs/2410.10934 `[snippet]`
- Hamel Husain's agent advice. Phase 1 is black-box end-to-end success. Phase 2 is step diagnostics: tool name, arguments, result, resulting state, and authorization or preconditions. A transition failure matrix (last good state by first failing state) locates hotspots. https://hamel.dev/blog/posts/evals-faq/

**What the repo should teach or demo from this.** An ADK agent with a stateful mock backend, graded on final DB state. It reports pass^k for k in {1, 4, 8} alongside pass@k, places trajectory checks (IN_ORDER only where policy demands order) next to outcome checks, and generates a transition failure matrix from traces.

---

## 4. User simulation

**Findings.**
- tau-bench uses an LLM user that holds a hidden instruction (goal plus persona). It converses with the agent, and grading ignores the conversation and checks the DB state. https://arxiv.org/abs/2406.12045
- tau2-bench constrains the simulator with its own tools and observable state. The paper says this coupling improves fidelity, and ablations separate reasoning errors from communication and coordination errors. https://arxiv.org/abs/2506.07982
- Sierra runs persona-based simulations as release gates "just like unit tests", repeats each conversation many times because outputs vary, and reports customers running more than 35,000 simulated tests per day (company-stated). https://sierra.ai/blog/simulations-the-secret-behind-every-great-agent `[snippet]`
- A stochastic simulator confounds pass^k, because variance across trials mixes agent inconsistency with simulator inconsistency. https://beancount.io/bean-labs/research-logs/2026/06/12/tau-bench-tool-agent-user-interaction-real-world-domains `[secondary]`
- Failure mode 1, over-cooperation. Default simulators are excessively cooperative and stylistically uniform, and they lack frustration and ambiguity, which inflates agent scores. https://arxiv.org/html/2605.12894v1 `[snippet]`. Simulated customers "never walk away" and miss real willingness decay. https://arxiv.org/html/2606.20708v1 `[snippet]`
- Failure mode 2, goal misalignment. Simulators confuse goal details, misprioritize, or stop after the first sub-goal, failing 10 to 40% of the time across LLMs. The proposed fix is User Goal State Tracking. https://www.alphaxiv.org/abs/2507.20152 `[snippet]`
- Failure mode 3, goal and information leakage. The simulator holds private goal and persona data. Leakage controls appear in grounded-simulation work, but no paper found here validates leakage as a failure mode. https://arxiv.org/html/2605.20204v1 `[snippet]` `[gap]`
- Validating a simulator. SimulatorArena (909 human conversations) scores how well simulator behavior matches human behavior and how well simulator-derived ratings track human ratings. Profile-conditioned simulators reach about rho 0.7. https://arxiv.org/abs/2510.05444 `[snippet]`. ADK ships `per_turn_user_simulator_quality_v1` to judge whether the simulator follows its `ConversationScenario` (starting_prompt, conversation_plan, user_persona). https://adk.dev/evaluate/criteria

**What the repo should teach or demo from this.** An ADK `LlmBackedUserSimulator` with a persona matrix (cooperative, terse, frustrated, adversarial). The demo validates the simulator before trusting it: per-turn simulator quality, a leak check that the agent never sees the hidden goal, and a small human-replay comparison. It reports agent pass^k per persona.

---

## 5. Hill climbing and eval-driven development

**Findings.**
- Error analysis comes first. Use open coding (free-text notes per trace), then axial coding (cluster the notes into a failure taxonomy and count each category). Note the first upstream failure, and review at least 100 diverse traces until saturation. https://hamel.dev/blog/posts/evals-faq/
- Build an eval only for failures error analysis surfaced. Use code assertions for objective failures and an aligned LLM judge for subjective ones. Re-run on every change, and retire or harden saturated evals. https://hamel.dev/blog/posts/evals-faq/ and https://hamel.dev/notes/llm/evals/ `[snippet]`
- Eugene Yan's three steps: label a small balanced set, align one evaluator per criterion, then run the harness on every change. https://eugeneyan.com/writing/product-evals/ `[snippet]`
- Capability evals are the hill to climb. They graduate into regression suites once they pass consistently. https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- CI regression gating. Braintrust labels each experiment row as improvement, regression, tradeoff, or tie against a baseline and gates GitHub Actions. This is vendor-described. https://www.braintrust.dev/articles/langsmith-vs-braintrust `[secondary]`
- Gating on non-deterministic evals needs repeated trials and confidence intervals, not a single run. https://hamel.dev/blog/posts/evals-faq/ (CI intervals) and https://sierra.ai/blog/simulations-the-secret-behind-every-great-agent (repeated runs) `[inference that combines both]`
- Segment before fixing. Jason Liu's RAG playbook targets high-impact query segments. https://maven.com/applied-llms/rag-playbook `[snippet]`

**What the repo should teach or demo from this.** A worked hill-climb log with these stages: trace review, then open and axial codes, then a failure-taxonomy count table, then one fix, then a re-run with CIs, then promotion of the fixed cases into a regression set gated by `adk eval` in GitHub Actions.

---

## 6. Self-healing and self-improving agent systems

**Findings.**
- Prompt optimizers are research tools that some teams use in production. DSPy optimizers (MIPROv2, GEPA) and TextGrad treat prompts as parameters tuned against a metric. https://arxiv.org/abs/2406.07496 (TextGrad; Nature 2025 version reported) `[snippet]`
- GEPA reflects on full execution traces in natural language and keeps a Pareto set of prompts. It reports beating GRPO by 10% on average with up to 35x fewer rollouts, and MIPROv2 by more than 10%. It is an ICLR 2026 poster and integrated into DSPy. https://arxiv.org/abs/2507.19457 `[snippet]`
- Practitioner caveat. Decagon reports that with GPT-4o-mini as the reflection model, GEPA left the seed prompt essentially unchanged. https://decagon.ai/blog/optimizing-gepa-for-production `[snippet]`
- Arize "prompt learning" optimizes prompts from English judge critiques. It reports +5% (Claude Code) and +15% (Cline) on SWE-bench with 150 examples. These are vendor-reported figures. https://arize.com/blog/prompt-learning-using-english-feedback-to-optimize-llm-systems/ `[snippet]`
- Automatic failure detection from traces is shipping in products. LangSmith Insights clusters production traces into usage patterns and failure modes (GA for Plus and Enterprise). https://docs.langchain.com/langsmith/insights `[snippet]`
- Hamel Husain's skepticism. Optimizers hill-climb a fixed metric, so they refine known failures but cannot discover new ones. Use them for the final stretch, after the evals are trustworthy. https://hamel.dev/blog/posts/evals-faq/
- Guardrails versus evaluators. Guardrails are inline, fast, and mostly deterministic, and they block, redact, or regenerate. LLM judges are rarely suitable as synchronous guardrails because of latency. https://hamel.dev/blog/posts/evals-faq/. NeMo Guardrails input and output rails can rewrite or refuse messages. https://docs.nvidia.com/nemo/guardrails/0.15.0/user-guides/configuration-guide/guardrails-configuration.html `[snippet]`
- Real today versus research. In production: trace clustering, trace-to-dataset promotion, and inline guardrails with fallbacks. Still early: closed-loop prompt auto-repair deployed without a human gate. No source reviewed here shows that safely. `[inference]`

**What the repo should teach or demo from this.** A "propose, never auto-merge" loop. Failing traces are clustered and become candidate test cases. GEPA (DSPy) proposes a prompt patch. The patch must pass the regression gate and pass^k before a human approves it. An inline guardrail with a deterministic fallback runs alongside.

---

## 7. Monitoring traces at scale

**Findings.**
- OpenTelemetry GenAI semantic conventions define `invoke_agent {agent.name}` parent spans with `chat` and `execute_tool {tool_name}` children. They are still in Development status, and the spec moved to a separate semconv-genai repo around v1.42, so pin the version you emit. https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans `[snippet]`
- OTel defines a `gen_ai.evaluation.result` event (score, label, explanation, response correlation), so judge output can travel on the trace. Metrics include token usage, operation duration, and time to first chunk. https://www.truefoundry.com/blog/opentelemetry-genai-semantic-conventions `[secondary]`
- Open-source backends: Langfuse (OTel-based SDKs, online evaluators with a sampling percentage, 5% in the docs example) https://langfuse.com/docs/evaluation/overview `[snippet]`; Arize Phoenix (OTel-native, self-hostable) `[secondary]`; OpenLLMetry (Apache-2.0 OTel instrumentations that export to any OTel backend) https://github.com/traceloop/openllmetry `[snippet]`
- Sampling strategy. Mix random sampling with clustering, classifier-flagged, and feedback-flagged traces, and always keep a random slice in each batch. https://hamel.dev/blog/posts/evals-faq/
- Tier evaluators by cost. Run cheap checks on 100% of traces and an expensive judge on a sample (for example, nightly). LangChain suggests starting at about 10%. https://hamel.dev/blog/posts/evals-faq/ and https://www.langchain.com/resources/llm-evals `[snippet for the second URL]`
- Alert on the lower confidence bound of a sampled metric crossing its threshold, not on the point estimate. https://hamel.dev/blog/posts/evals-faq/
- Adoption is uneven. One LangChain survey reports 89% of organizations have observability, 52% run offline evals, and 37% run online evals. https://www.langchain.com/resources/llm-evals `[snippet]`
- What breaks at 10x to 100x. `[inference]`, with no single source:
  - Judge spend grows linearly with the sample rate. Fix the sample count per segment instead of a percentage.
  - Trace storage and PII exposure grow, because the semconv makes prompt and tool content capture opt-in. Default to off and capture on a sample.
  - The human label backlog outruns reviewers. Route by classifier and uncertainty, and keep the random slice small but fixed.
  - Rare failures still need targeted sampling, because a random sample at 100x volume still misses them.

**What the repo should teach or demo from this.** An OTel-instrumented ADK agent exporting to a pluggable backend (Phoenix or Langfuse). It runs tiered online evaluators (deterministic on all traces, judge on a stratified sample) that emit `gen_ai.evaluation.result`, with a cost and latency SLO dashboard and CI-bound alerts. A load script shows the judge cost at 1x, 10x, and 100x.

---

## 8. Safety, security, and compliance evals

**Findings.**
- Prompt injection is LLM01 in the OWASP LLM Top 10 (2025; a 2026 edition is reported for August 2026). OWASP frames it as an ongoing risk to manage, not a vulnerability to fully fix. https://genai.owasp.org/llm-top-10/ `[secondary; URL not opened]`
- The OWASP Top 10 for Agentic Applications (ASI01 to ASI10, first edition dated 2026) covers goal hijack, tool misuse, privilege abuse, memory poisoning, and rogue agents. https://www.cybersaint.io/cybersecurity-frameworks-and-standards/glossary/what-is-the-owasp-top-10-for-llm-and-agentic-ai `[secondary]`
- AgentDojo has 97 user tasks, 629 injection cases, and 4 environments. It scores utility and security with deterministic state checks, not an LLM judge, which is the right model for indirect injection through tool outputs. https://github.com/ACAI-Security/agentdojo `[snippet]`
- Red-team tooling: garak (NVIDIA, probe-based scanner), PyRIT (Microsoft, multi-turn orchestrated attacks such as Crescendo), and promptfoo (CLI red-team plus evals; one unverified report says OpenAI acquired it in 2026). https://www.braintrust.dev/articles/best-llm-red-teaming-tools-2026 `[secondary; tool repos not opened]`
- Policy adherence is part of the core task metric in tau-bench, where agents must follow domain policy. ADK ships `safety_v1` and `hallucinations_v1`, plus rubric criteria for custom policy checks. https://arxiv.org/abs/2406.12045 and https://adk.dev/evaluate/criteria
- Authorization checks. A valid tool call can still be wrong if preconditions or authorization fail, so test them explicitly. https://hamel.dev/blog/posts/evals-faq/
- PII leakage and the NIST AI 600-1 GenAI profile were not covered by any source fetched this session. `[gap]`

**What the repo should teach or demo from this.** A security eval suite for the ADK agent. It runs AgentDojo-style injected tool outputs with state-based attack-success checks, a PII-leak detector on outputs and traces, policy rubrics, and a scheduled garak or PyRIT run whose results are reported as attack success rate alongside utility.

---

## Cross-cutting recommendations for the repo `[inference]`

1. Grade on state and outcomes first, trajectories second, and prose last.
2. Report pass^k with confidence intervals, never a single-run pass rate.
3. Treat every LLM judge and every user simulator as a model that needs its own labeled validation set and drift check.
4. Run one loop end to end: production trace, sample, error analysis, failure taxonomy, dataset, fix, regression gate, deploy, monitor.
5. Emit OTel GenAI spans and evaluation events, so the repo stays cloud agnostic and backend agnostic.
