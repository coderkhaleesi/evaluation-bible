# Research brief: ADK Python evaluation, user simulation, observability (as of 2026-10-31)

Method. Source read from a shallow clone of `google/adk-python` at commit `8cd3b12` (2026-10-30) and `google/adk-docs` (2026-10-30). Docs moved from google.github.io/adk-docs to adk.dev (301 redirect observed); doc URLs below use adk.dev and were spot-checked live (criteria, user-sim, custom_metrics, observability/traces). Code URLs point at `main`; line content was read at `8cd3b12`.
Labels. "observed" means read in source or docs. "unverified" means stated but not confirmed in code. "inferred" means my reading, not a stated fact.

## 0. Version and 2026 timeline

- Current release is `google-adk` 2.13.0, released 2026-10-22 (CHANGELOG) / 2026-10-23 (PyPI). https://pypi.org/project/google-adk/ , https://github.com/google/adk-python/blob/main/CHANGELOG.md
- `__version__ = "2.13.0"` on main. https://github.com/google/adk-python/blob/main/src/google/adk/version.py
- 2026 releases: 1.22.0 (Jan 8) through 1.34.0 (May 18), 2.0.0 (May 19), then 2.1.0 to 2.13.0 (Oct 22). https://github.com/google/adk-python/blob/main/CHANGELOG.md
- Eval and telemetry features new in 2026 (all from CHANGELOG, https://github.com/google/adk-python/blob/main/CHANGELOG.md):
  - 1.22.0: `MetricInfoProvider` interface; `ToolTrajectoryCriterion.match_type` accepts strings.
  - 1.28.0: multi-turn task-success, trajectory and tool-use metrics added; "agent simulator" renamed to environment simulation, with tracing.
  - 1.29.0: sub-agent intermediate final responses included in eval intermediate data.
  - 1.32.0: native OpenTelemetry agentic metrics; OTel tracing for event compaction; `gen_ai.tool_definitions` renamed to `gen_ai.tool.definitions`.
  - 1.34.0: Gemini Live API support in evaluate; option to pass tool calls/responses to the user simulator.
  - 2.2.0: `RubricBasedMultiTurnTrajectoryEvaluator`; `AutoTracingPlugin`; native OTel `gen_ai.client.*` metrics.
  - 2.3.0: per-request OpenTelemetry configuration; `user_simulator_config` exposed in `generate_responses`; custom eval metadata preserved.
  - 2.6.0: audio user simulator; invocation-level rubrics; `get_agent_async` in `adk eval`; eval samples (basic_criteria, custom_metric, llm_judge_match, rubric_criteria, user_simulation).
  - 2.7.0: judge metrics graded against the criterion threshold; eval fails when the agent crashes before any metric runs; optional eval-set result persistence in `AgentEvaluator`; `test_config.json` auto-discovery in `adk eval`.
  - 2.8.0: custom metrics supported in `AgentEvaluator`; per-invocation and per-workflow token metrics.
  - 2.9.0: `ignore_args` on tool trajectory; a metric that never ran reports NOT_EVALUATED instead of FAILED.
  - 2.10.0: efficiency metrics (duration, tokens, model-call counts); `evaluate`/`evaluate_eval_set` raise `ValueError` when zero cases are evaluated; `safety_v1` pinned to a specific Vertex spec version.
  - 2.12.0: efficiency metrics in Dev UI evals; AFC disabled in all `LlmAsJudge` judge requests; grounding metadata in hallucinations judge context.
  - 2.13.0: duration split into model/tool/framework time; `adk eval` exit code now reflects pass/fail; "support BaseLlm instances in evaluation and user simulation"; telemetry defaults to OTel GenAI semconv v2 (`otel_semconv_1_44`) and drops the `call_llm` span (breaking).
- Multi-run config (`MultiRunConfig`, pass-rate aggregation) exists on main; I did not find its CHANGELOG entry, so its release version is unverified. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py

## 1. Eval data model

All Pydantic models in `google.adk.evaluation`. JSON uses camelCase aliases (`alias_generators.to_camel`). https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py

- `EvalSet`: `eval_set_id`, `name`, `description`, `eval_cases: list[EvalCase]`, `creation_timestamp`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py
- `EvalCase`: `eval_id`, `conversation: Optional[StaticConversation]`, `conversation_scenario: Optional[ConversationScenario]`, `session_input: Optional[SessionInput]`, `creation_timestamp`, `rubrics: Optional[list[Rubric]]`, `final_session_state`. A validator enforces exactly one of `conversation` or `conversation_scenario`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py
- `StaticConversation` is a type alias for `list[Invocation]`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py
- `Invocation`: `invocation_id`, `user_content: genai_types.Content`, `final_response: Optional[Content]`, `intermediate_data: Optional[IntermediateDataType]`, `creation_timestamp`, `duration`, `model_duration`, `tool_duration`, `rubrics` (invocation-level), `app_details: Optional[AppDetails]`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py
- `IntermediateDataType = Union[IntermediateData, InvocationEvents]`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py
- Tool trajectories are stored in `IntermediateData.tool_uses: list[genai_types.FunctionCall]` and `tool_responses: list[genai_types.FunctionResponse]`, chronological; `intermediate_responses: list[tuple[author, list[Part]]]` holds sub-agent progress text. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py
- `InvocationEvents.invocation_events: list[InvocationEvent]`, where `InvocationEvent` has `author`, `content`, `grounding_metadata`, `usage_metadata`, `model_version`. This is the richer, event-level form. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py
- `SessionInput`: `app_name`, `user_id`, `session_id`, `state` (initial session state). https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py
- `AppDetails.agent_details: dict[str, AgentDetails]`, each with `name`, `instructions`, `tool_declarations`. Used to give judges the agent's tools and instructions (inferred from field docs). https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/app_details.py
- `Rubric`: `rubric_id`, `rubric_content: RubricContent(text_property)`, `description`, `type`. `RubricScore`: `rubric_id`, `rationale`, `score`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_rubrics.py
- Results: `EvalCaseResult` (`eval_set_id`, `eval_id`, `final_eval_status`, `overall_eval_metric_results`, `eval_metric_result_per_invocation`, `session_id`, `session_details`, `user_id`, `repetition_index`) and `EvalSetResult` (`eval_set_result_id`, `eval_set_id`, `eval_case_results`). https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_result.py
- `EvalStatus` enum includes `INFORMATIONAL` (value 4) for efficiency metrics. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py
- `EvalCase.final_session_state` is declared but no evaluator reads it; `grep` finds it only in `eval_case.py` (observed). Expected-state checking needs a custom metric. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py
- Two file formats: legacy `.test.json` test files and `.evalset.json` eval set files, with `AgentEvaluator.migrate_eval_data_to_new_schema` for migration. https://adk.dev/evaluate/ , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/agent_evaluator.py
- Storage backends: `LocalEvalSetsManager`, `InMemoryEvalSetsManager`, `GcsEvalSetsManager`, and matching results managers. `--eval_storage_uri` accepts `gs://` or `file://`. https://github.com/google/adk-python/tree/main/src/google/adk/evaluation , https://github.com/google/adk-python/blob/main/src/google/adk/cli/cli_tools_click.py

## 2. Built-in metrics (`PrebuiltMetrics` enum)

Enum and criteria classes: https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py . Registry: https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/metric_evaluator_registry.py . Docs table: https://adk.dev/evaluate/criteria/

Judge defaults. `JudgeModelOptions`: `judge_model="gemini-2.5-flash"`, `judge_model_config`, `num_samples=5`, `parallelism_limit=1`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py
Judge resolution. `LlmAsJudge._setup_auto_rater` resolves the model string through `LLMRegistry`, so any registered provider can judge: `gemini-*`, `claude-*` (AnthropicLlm), `gpt-*`/`o\d+-*` (OpenAILlm), and LiteLlm prefixes such as `openai/`, `azure/`, `anthropic/`, `bedrock/`, `ollama_chat/`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/llm_as_judge.py , https://github.com/google/adk-python/blob/main/src/google/adk/models/__init__.py
Cloud-agnostic judging with non-Gemini models works by registry resolution (observed in code). I have not run it, so end-to-end success is unverified.

| Metric | Evaluator class | Measures | Reference? | Judge / backend |
|---|---|---|---|---|
| `tool_trajectory_avg_score` | `TrajectoryEvaluator` | Tool-call trajectory vs expected; `ToolTrajectoryCriterion.match_type` EXACT / IN_ORDER / ANY_ORDER, `ignore_args` | Yes | None, local deterministic |
| `response_match_score` | `ResponseEvaluator` -> `RougeEvaluator` | ROUGE-1 F-measure vs reference, Unicode-aware tokenizer | Yes | None, local |
| `response_evaluation_score` | `ResponseEvaluator` | Coherence, 1 to 5 | Yes | Vertex Gen AI Eval SDK (`PrebuiltMetric.COHERENCE`) |
| `final_response_match_v2` | `FinalResponseMatchV2Evaluator` | Semantic match to reference, 0 to 1 | Yes | Local LLM judge via `LlmAsAJudgeCriterion` |
| `rubric_based_final_response_quality_v1` | `RubricBasedFinalResponseQualityV1Evaluator` | Final response vs user rubrics | No | Local LLM judge, `RubricsBasedCriterion` |
| `rubric_based_tool_use_quality_v1` | `RubricBasedToolUseV1Evaluator` | Tool use vs user rubrics | No | Local LLM judge |
| `rubric_based_multi_turn_trajectory_quality_v1` | `RubricBasedMultiTurnTrajectoryEvaluator` | Multi-turn trajectory vs rubrics | No | Local LLM judge |
| `hallucinations_v1` | `HallucinationsV1Evaluator` | Unsupported or contradictory claims; segments response then validates each sentence; `evaluate_intermediate_nl_responses` | No | Local LLM judge, `HallucinationsCriterion` |
| `safety_v1` | `SafetyEvaluatorV1` | Harmlessness, 0 to 1 | No | Vertex Gen AI Eval SDK; needs `GOOGLE_CLOUD_PROJECT`/`LOCATION` |
| `per_turn_user_simulator_quality_v1` | `PerTurnUserSimulatorQualityV1` | Whether each simulated user turn follows the scenario | No | Local LLM judge, `LlmBackedUserSimulatorCriterion(stop_signal="</finished>")` |
| `multi_turn_task_success_v1` | `MultiTurnTaskSuccessV1Evaluator` | Goal achieved across the conversation | No | Vertex (`RubricMetric.MULTI_TURN_TASK_SUCCESS`) |
| `multi_turn_trajectory_quality_v1` | `MultiTurnTrajectoryQualityV1Evaluator` | Overall conversation trajectory | No | Vertex (`RubricMetric.MULTI_TURN_TRAJECTORY_QUALITY`) |
| `multi_turn_tool_use_quality_v1` | `MultiTurnToolUseQualityV1Evaluator` | Function calls in a conversation | No | Vertex (`RubricMetric.MULTI_TURN_TOOL_USE_QUALITY`) |
| `tool_call_count_v1` | `_ToolCallCountV1Evaluator` | Tool calls per invocation | n/a | Local, INFORMATIONAL |
| `inference_call_count_v1` | `_InferenceCallCountV1Evaluator` | Model calls per invocation | n/a | Local, INFORMATIONAL |
| `token_usage_v1` | `_TokenUsageV1Evaluator` | Tokens per invocation with per-type breakdown | n/a | Local, INFORMATIONAL |
| `invocation_duration_v1` | `_InvocationDurationV1Evaluator` | Wall-clock seconds, split model/tool/framework | n/a | Local, INFORMATIONAL |

Row sources: Vertex delegation is in https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/safety_evaluator.py , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/response_evaluator.py , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/multi_turn_task_success_evaluator.py , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/multi_turn_trajectory_quality_evaluator.py , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/multi_turn_tool_use_quality_evaluator.py . Efficiency metrics are in https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/_efficiency_evaluators.py .

Notes:
- Cloud-agnostic set (no Vertex): `tool_trajectory_avg_score`, `response_match_score`, `final_response_match_v2`, all three `rubric_based_*`, `hallucinations_v1`, `per_turn_user_simulator_quality_v1`, and the four efficiency metrics (observed from imports). Vertex-only: `response_evaluation_score`, `safety_v1`, `multi_turn_*_v1`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/metric_evaluator_registry.py
- The `eval` extra pulls `google-cloud-aiplatform[evaluation]>=2.2,<3` even for local-only use. https://github.com/google/adk-python/blob/main/pyproject.toml
- Default criteria when no config is given: `{"tool_trajectory_avg_score": 1.0, "response_match_score": 0.8}`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py
- Efficiency metrics are always on, cannot be disabled, and reject a threshold. https://adk.dev/evaluate/criteria/
- `BaseCriterion.include_intermediate_responses_in_final` concatenates pre-tool text with the final response for judging. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py
- Rubric judging: `RubricBasedEvaluator` samples `num_samples` times, aggregates per invocation with `MajorityVotePerInvocationResultsAggregator`, then summarizes with `MeanInvocationResultsSummarizer`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/rubric_based_evaluator.py
- Docs recommend `tool_trajectory_avg_score` and `response_match_score` for CI because they are fast and predictable. https://adk.dev/evaluate/

## 3. User simulation and environment simulation

User simulation is built in (Python since v1.18.0). https://adk.dev/evaluate/user-sim/

- Scenario: `ConversationScenario(starting_prompt: str, conversation_plan: str, user_persona: Optional[UserPersona])`; a string persona id resolves from the default registry. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/conversation_scenarios.py
- Simulator classes: abstract `UserSimulator`; `StaticUserSimulator` (replays a fixed conversation); `LlmBackedUserSimulator`; `_LlmAudioUserSimulator` (private class, public via config `type: "llm_audio"`); factory `UserSimulatorProvider`. https://github.com/google/adk-python/tree/main/src/google/adk/evaluation/simulation
- `LlmBackedUserSimulatorConfig` (`type: "llm_backed"`): `model` (code default `gemini-2.5-flash`; docs show `gemini-flash-latest`), `model_configuration`, `max_allowed_invocations=20` (the starting prompt counts; `-1` disables), `custom_instructions` (Jinja template that must contain `{{ stop_signal }}`, `{{ conversation_plan }}`, `{{ conversation_history }}`, and `{{ persona }}` when used), `include_function_calls=False`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/simulation/llm_backed_user_simulator.py , https://adk.dev/evaluate/user-sim/
- Configured through `EvalConfig.user_simulator_config`, a union discriminated on `type`. Legacy configs without `type` default to `llm_backed`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py
- Termination: `Status` = `SUCCESS`, `TURN_LIMIT_REACHED`, `STOP_SIGNAL_DETECTED`, `NO_MESSAGE_GENERATED`; default stop signal is `</finished>`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/simulation/user_simulator.py , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py
- Personas: `UserPersona(id, description, behaviors: Sequence[UserBehavior])`, where `UserBehavior` has `name`, `description`, `behavior_instructions`, `violation_rubrics`. Pre-built ids are `EXPERT`, `NOVICE`, `EVALUATOR`; `UserPersonaRegistry` holds custom personas. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/simulation/user_simulator_personas.py , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/simulation/pre_built_personas.py
- Scenario generation: `adk eval_set generate_eval_cases <agent> <eval_set_id> --user_simulation_config_file=...` with `ConversationGenerationConfig(count, generation_instruction, environment_context, model_name)`. It requires the Vertex Gen AI Evaluation Service and a GCP project, so it is not cloud agnostic. https://adk.dev/evaluate/user-sim/ , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/_vertex_ai_scenario_generation_facade.py
- Limits (observed): only the rubric, hallucination, safety, user-sim-quality and multi-turn metrics support simulated conversations; `tool_trajectory_avg_score`, `response_match_score`, `final_response_match_v2` and `response_evaluation_score` do not, because they need a reference. The simulator is text plus optional TTS only; no tool-level user actions. https://adk.dev/evaluate/criteria/
- Environment simulation (tool mocking and fault injection): `EnvironmentSimulationPlugin` or a callback, configured by `EnvironmentSimulationConfig(tool_simulation_configs, simulation_model="gemini-2.5-flash", tracing, environment_data)`. `ToolSimulationConfig(tool_name, injection_configs, mock_strategy_type)`. `InjectionConfig(injection_probability, match_args, injected_latency_seconds<=120, random_seed, injected_error: InjectedError(injected_http_error_code, error_message), injected_response)`. https://github.com/google/adk-python/blob/main/src/google/adk/tools/environment_simulation/environment_simulation_config.py , https://adk.dev/evaluate/environment_simulation/

## 4. Running evals and extending them

- CLI: `adk eval AGENT_MODULE_FILE_PATH EVAL_SET_FILE_PATH_OR_ID... [--config_file_path] [--num_runs] [--parallelism] [--print_detailed_results] [--eval_storage_uri] [--log_level]`. A `file.json:eval_1,eval_2` suffix selects cases. `--parallelism` defaults to 4. https://github.com/google/adk-python/blob/main/src/google/adk/cli/cli_tools_click.py , https://adk.dev/evaluate/
- The `adk eval` exit code reflects pass/fail only since 2.13.0. Before that, CI gating on the exit code was unreliable. https://github.com/google/adk-python/blob/main/CHANGELOG.md
- Eval-set management: `adk eval_set create`, `adk eval_set add_eval_case`, `adk eval_set generate_eval_cases`. https://github.com/google/adk-python/blob/main/src/google/adk/cli/cli_tools_click.py
- Config file: `test_config.json` holds an `EvalConfig` with `criteria`, `custom_metrics`, `user_simulator_config`, `live_model_config`, `multi_run_config`, `parallelism`. It is auto-discovered next to a single eval file since 2.7.0. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py
- Multi-run: `MultiRunConfig(num_runs, max_crashed_runs=0, cross_run_scoring="mean_over_invocations", cross_run_scoring_by_metric, cross_run_criteria, custom_methods)`. Built-in methods are `mean_over_invocations`, `mean_of_runs`, `min_over_runs` and `pass_rate` (for example `{"method": "pass_rate", "threshold": 0.8}`). Each run uses a fresh session. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/_multi_run_aggregation_methods.py
- pytest: `await AgentEvaluator.evaluate(agent_module, eval_dataset_file_path_or_dir, num_runs=2, agent_name=None, initial_session_file=None, print_detailed_results=True, artifact_service=None, output_file=None, app_name=None, eval_set_results_manager=None, parallelism=None)`. It fails by `assert not failures`, and raises `ValueError` when zero cases run. `agent_module` may be a module path (looks for `root_agent` or `get_agent_async`), a `BaseNode`, or an `App`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/agent_evaluator.py , https://adk.dev/evaluate/
- Also `AgentEvaluator.evaluate_eval_set(...)` for an in-memory `EvalSet`. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/agent_evaluator.py
- Programmatic API: `LocalEvalService(root_agent, eval_sets_manager, metric_evaluator_registry, session_service, artifact_service, eval_set_results_manager, session_id_supplier, user_simulator_provider, memory_service, app)`, with `perform_inference(InferenceRequest)` then `evaluate(EvaluateRequest)`. Inference and scoring are separate steps, so you can re-score stored inferences (inferred). https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/local_eval_service.py , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/base_eval_service.py
- Custom metric, route 1 (config): add `custom_metrics: {name: {code_config: {name: "pkg.mod.fn"}, metric_info, description}}` and reference `name` in `criteria`. The function signature is `fn(eval_metric, actual_invocations, expected_invocations, conversation_scenario) -> EvaluationResult` and may be async. https://adk.dev/evaluate/custom_metrics/ , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/custom_metric_evaluator.py
- Custom metric, route 2 (class): subclass `Evaluator` (`evaluate_invocations(actual_invocations, expected_invocations, conversation_scenario) -> EvaluationResult`, with `criterion_type` ClassVar) and call `MetricEvaluatorRegistry.register_evaluator(metric_info, evaluator)`. Subclass `LlmAsJudge` or `RubricBasedEvaluator` for judge metrics. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/evaluator.py , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/metric_evaluator_registry.py
- Web UI: `adk web` has an Eval tab to save sessions as eval cases, edit them, run with chosen metrics, and a Trace tab (Event, Request, Response, Graph). https://adk.dev/evaluate/
- Conformance (record and replay regression): `adk conformance record <dir> none|sse` with `RecordingsPlugin`, then `adk conformance test [paths] [--generate_report --report_dir]`. The layout is `tests/<category>/<case>/spec.yaml` plus `generated-recordings.yaml` and `generated-session.yaml`. https://adk.dev/evaluate/
- Optimization: `adk optimize` with sampler and optimizer configs; `GEPARootAgentPromptOptimizer` and `SimplePromptOptimizer` use eval results to tune prompts. https://github.com/google/adk-python/tree/main/src/google/adk/optimization

## 5. Observability

- ADK emits OTel spans following the GenAI semantic conventions: `invoke_agent {agent.name}`, `invoke_workflow {workflow.name}`, `execute_tool {tool.name}`, `generate_content {model.name}`. https://adk.dev/observability/traces/
- Other spans seen in source: `execute_tool (merged)` (parallel calls), `compact_events {trigger}`, `send_data`, `create_cache`, `handle_context_caching`, and skill spans `execute_tool {tool} {skill} [{resource}]`. https://github.com/google/adk-python/tree/main/src/google/adk/telemetry
- Schema (breaking in 2.13.0): the default is now `otel_semconv_1_44` and the legacy `call_llm` span is gone. Set `ADK_TELEMETRY_SCHEMA_VERSION_OPT_IN=otel_semconv_1_36` to keep v1. https://github.com/google/adk-python/blob/main/CHANGELOG.md
- Vendor-neutral export: `google.adk.telemetry.setup.maybe_set_otel_providers()` reads `OTEL_EXPORTER_OTLP_ENDPOINT` and the `_TRACES_`, `_METRICS_` and `_LOGS_ENDPOINT` variants, plus `OTEL_SERVICE_NAME` and `OTEL_RESOURCE_ATTRIBUTES`. `adk web` and `adk api_server` honor the same variables. https://github.com/google/adk-python/blob/main/src/google/adk/telemetry/setup.py , https://adk.dev/observability/traces/
- `--otel_to_cloud` and `--trace_to_cloud` are the GCP-specific paths (Cloud Trace, `telemetry.googleapis.com`); a cloud-agnostic repo should avoid them. https://adk.dev/observability/traces/
- Content capture is off by default. `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` takes `NO_CONTENT`, `EVENT_ONLY`, `SPAN_ONLY` or `SPAN_AND_EVENT`; the span modes also need `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`. Per-run scoping uses `RunConfig.telemetry` with `capture_message_content=ContentCapturingMode...`. https://adk.dev/observability/logging/
- Metrics (native OTel). Stable: `gen_ai.client.inference.operation.*`, `gen_ai.client.inference.usage.{input,output,cache_read.input,cache_write.input,reasoning.output}_tokens`, `gen_ai.client.inference.time_to_first_chunk`, `time_per_output_chunk`, `gen_ai.invoke_agent.duration`, `gen_ai.execute_tool.duration`, `gen_ai.invoke_workflow.duration`, `gen_ai.invoke_agent.{inference_calls,tool_calls}`. Experimental: `adk.experimental.invoke_workflow.{inference_calls,tool_calls,total_tokens,compactions,...}`. https://github.com/google/adk-python/blob/main/src/google/adk/telemetry/_metrics.py , https://adk.dev/observability/metrics/
- Local trace store: `SqliteSpanExporter(db_path=...)` backs `adk web` trace reloads. https://github.com/google/adk-python/blob/main/src/google/adk/telemetry/sqlite_span_exporter.py
- Phoenix: `openinference-instrumentation-google-adk` plus `phoenix.otel.register(...)`. https://adk.dev/integrations/phoenix/
- Langfuse: `GoogleADKInstrumentor().instrument()` from OpenInference, exporting OTLP to Langfuse. https://adk.dev/integrations/langfuse/
- Other listed integrations: AgentOps, Arize AX, Datadog, Freeplay, Galileo, LangWatch, MLflow (tracing and scorers), Monocle, Weave. https://github.com/google/adk-docs/tree/main/docs/integrations
- Callbacks on agents: `before_agent_callback`/`after_agent_callback`, `before_model_callback`/`after_model_callback`, `before_tool_callback`/`after_tool_callback`. A non-None return short-circuits the step. https://adk.dev/callbacks/types-of-callbacks/
- `BasePlugin` hooks apply globally through the Runner: `on_user_message_callback`, `before_run_callback`, `on_event_callback`, `after_run_callback`, `before_agent_callback`, `after_agent_callback`, `before_model_callback`, `after_model_callback`, `on_model_error_callback`, `before_tool_callback`, `after_tool_callback`, `on_tool_error_callback`, `on_agent_error_callback`, `on_run_error_callback`, `close`. These hooks are the main point for per-LLM-call and per-tool instrumentation. https://github.com/google/adk-python/blob/main/src/google/adk/plugins/base_plugin.py , https://adk.dev/plugins/
- Built-in plugins usable for eval capture: `LoggingPlugin`, `DebugLoggingPlugin` (full capture to file), `AutoTracingPlugin` (OTel auto-instrumentation of custom code), `ReflectRetryToolPlugin`, `BigQueryAgentAnalyticsPlugin` (GCP-only, and as of 2.13 has "agent evaluation session and turn trace views"). The eval harness itself uses a private `_RequestIntercepterPlugin` to cache LLM requests. https://github.com/google/adk-python/tree/main/src/google/adk/plugins , https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/request_intercepter_plugin.py
- Plugins are passed with `Runner(..., plugins=[...])` or, for the CLI, `adk web --extra_plugins=module.Class`. https://adk.dev/plugins/ , https://adk.dev/evaluate/

## 6. Gaps for an enterprise eval program

Each gap is labeled observed-missing (searched the source and docs and found nothing) or unsure.

- Online eval sampling of production traffic. Observed-missing. No sampler or evaluator attaches to live traffic. Eval runs only offline over `EvalSet`s, and the `optimization/sampler.py` sampler draws training examples for the prompt optimizer. https://github.com/google/adk-python/tree/main/src/google/adk/evaluation
- Trace-to-eval-case conversion from OTLP or a third-party backend. Observed-missing in core. Only `adk web` "save session as eval case" and `adk eval_set add_eval_case` exist. https://adk.dev/evaluate/
- A/B or canary routing between agent versions. Observed-missing. No traffic-splitting primitive exists. The 2.13 `ClassifierNode` routes workflow steps, not experiments. https://github.com/google/adk-python/blob/main/CHANGELOG.md
- Paired comparison of two eval runs (diff, significance test). Observed-missing. `EvalSetResult` is stored per run, with no compare API or CLI. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_result.py
- Judge calibration against human labels (agreement, kappa, confusion matrix). Observed-missing. Judge reliability is handled only by `num_samples` majority vote. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/rubric_based_evaluator.py
- Human annotation or labeling queue. Observed-missing in core. Vendors such as Langfuse and Phoenix provide it. https://adk.dev/integrations/langfuse/
- Dataset versioning or lineage. Observed-missing. `EvalSet` has only `eval_set_id` and `creation_timestamp`, with no version or hash field. Git on the JSON files is the default answer (inferred). https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py
- Regression gating in CI. Partial. Since 2.13 there is a pass/fail exit code with per-metric thresholds, and `pass_rate` multi-run handles flakiness. There is no baseline-relative gate ("no worse than main by X") (observed-missing). `adk conformance test` is replay-based exact matching, not a score gate. https://github.com/google/adk-python/blob/main/CHANGELOG.md , https://adk.dev/evaluate/
- Expected final-state assertion. Observed-missing. `final_session_state` is declared but unused by any evaluator. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py
- Cloud-agnostic safety, multi-turn task success, coherence and scenario generation. Observed-missing. All four are Vertex-only, so a cloud-agnostic repo must reimplement them as rubric or custom metrics. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/safety_evaluator.py
- Cost in currency. Unsure. `token_usage_v1` reports tokens only. The 2.13 changelog mentions "measure model consultation escalations, tokens, and cost", but that applies to a tools feature, not eval. https://github.com/google/adk-python/blob/main/CHANGELOG.md
- Passing a `BaseLlm` instance as the judge. Unsure. The 2.13 changelog claims "support BaseLlm instances in evaluation and user simulation", but `JudgeModelOptions.judge_model` is typed `str` on main. Mechanism unverified. https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py
- Red-teaming or adversarial scenario generation. Observed-missing beyond personas and environment-simulation fault injection. https://adk.dev/evaluate/environment_simulation/
- Eval result export to OTel or third-party backends. Unsure. Eval runs execute the agent under the normal Runner, so spans are emitted if a provider is configured (inferred). No built-in links metric scores to trace ids (observed-missing). https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/local_eval_service.py
- PII redaction in traces. Observed-missing beyond content capture being off by default. https://adk.dev/observability/logging/

## 7. Implications for a cloud-agnostic best-practices repo (inferred)

- Core metric set without GCP: trajectory (`IN_ORDER` or `ANY_ORDER` plus `ignore_args`), ROUGE, `final_response_match_v2`, the three rubric metrics, `hallucinations_v1`, the four efficiency metrics, and custom metrics for state and safety.
- Point the judge at a non-Gemini model through the LLMRegistry strings, and pin the judge model per metric.
- Use `multi_run_config` with `pass_rate` for non-determinism. Use `adk eval` (>=2.13) or pytest `AgentEvaluator` for CI.
- Export traces through `OTEL_EXPORTER_OTLP_*` to a collector, with Phoenix or Langfuse as reference backends. Use `BasePlugin` for per-call capture.
- Build in the repo what ADK lacks: baseline diffing, judge calibration, dataset versioning, and online sampling.
- Caveat: installing the `eval` extra still pulls `google-cloud-aiplatform`, even when it is never called. https://github.com/google/adk-python/blob/main/pyproject.toml
