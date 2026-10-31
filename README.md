# evaluation-bible

Agent-evaluation best practices for enterprises, packaged as agent skills with runnable demos on Google ADK (Python).

The repo covers the whole eval cycle. Defining metrics, calibrating judges, running evals in CI, building eval sets from traces, simulating users, tracing in production, sampling online, diagnosing offline-online divergence, A/B testing, hill climbing, self-healing with a human gate, scaling monitoring, and security evals.

The core is cloud agnostic. Any model the ADK registry resolves can be the agent or the judge, and traces export to any OpenTelemetry backend. Cloud-specific adapters come later as optional extras.

## Status

Planning. Read [PLAN.md](PLAN.md) for the phases, the skill and demo catalogue, decisions, open questions, and risks. The research behind the plan is in [docs/research/](docs/research/), with a source URL on every claim.

## How the repo will be organized

- `skills/<name>/SKILL.md` is one practice in the [Agent Skills](https://agentskills.io/specification) format, loadable by Claude Code, Codex, Gemini CLI, Cursor, and Copilot.
- `demos/<name>/` is the runnable demo for that skill, with eval sets and tests.
- `src/evaluation_bible/` is the shared library and the reference agent every demo uses.

Every skill ships with a demo of the same name, and CI rejects one without the other.

## Prior art

[hamelsmu/evals-skills](https://github.com/hamelsmu/evals-skills) packages eval practice as skills. This repo builds on that idea and adds runnable ADK demos and the online half of the cycle.
