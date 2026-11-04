---
name: verify
description: Drive evaluation-bible the way a contributor does, through the uv CLI, the structure check, the retail_support library surface, and each demo README's command block. Use it to prove a change on the real surface before claiming a task done, or when the acceptance lane fails.
---

# Verify evaluation-bible

The surface is a Python library plus CLI tools under uv. There is no server. Every drive is a short-lived process started from the repository root.

## Launch

```bash
uv sync
```

Ready when it exits 0: `.venv/` holds google-adk and the dev tools. There is nothing to tear down.

## Doctor

```bash
uv run python -c 'import evaluation_bible, google.adk; print("ok")' && uv run adk --version
```

Expect `ok` and `adk, version 2.<minor>.<patch>`. If this fails, nothing else is worth driving.

## Drive

The feature map at `tests/acceptance/features/` is the recipe. Its README states the contract. The map lives under `tests/`, not in this skill's directory, because `.claude/` is protected from factory workflows and the builder must add a feature whenever it adds a demo.

- One feature: `FACTORY_TIER=fast uv run pytest tests/acceptance -k <feature-id>`
- Every keyless feature: `FACTORY_TIER=fast uv run pytest tests/acceptance`
- Every feature, keyed ones included: `FACTORY_TIER=full uv run pytest tests/acceptance` with `EVAL_BIBLE_AGENT_MODEL`, `EVAL_BIBLE_JUDGE_MODEL`, and the provider key from `.env.example` set in the shell

A keyed feature carries `- Tier: full`, and the secrets it needs are named in `factory.json` under `lanes.acceptance.full.secrets`. The nightly workflow runs that tier under the `nightly` environment. A pull request runs the fast tier only.

To drive by hand, run a feature's bash fences from the repository root exactly as written. They check their own result.

## Evidence

`reports/acceptance/<feature-id>.log` holds the script, stdout, stderr, and the exit code. `reports/` is gitignored, so paste the lines that matter into the pull request's Evidence section. Proof means the real import or CLI path, the observable result checked inside the script, and the side effect checked too: after a refused refund, the order's status is read back and is unchanged.

## Cleanup

Features that need scratch state create it with `mktemp -d` and remove it before they exit, on the failure path as well. Nothing listens on a port. Never delete `reports/acceptance/`.

## Helpers

`tests/acceptance/test_features.py` is the runner, seeded by the factory and owned by this project. To add a feature, copy a file in `tests/acceptance/features/`, keep the four H2 sections, one `- Tier:` line, and bash fences that check their result, then add a line to the README's Features list. Every `demos/<name>/README.md` needs `demo-<name>.md`, and the runner fails until it exists.

## Maintenance

`/maintain-verification-skill` re-reads the map against the code and the demos.
