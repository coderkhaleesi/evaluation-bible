# Build the retail_support agent

The reference agent is a library. A demo imports `build_agent`, sets the model name in the environment, and gets an ADK `LlmAgent` wired to four tools that refuse what `policy.md` forbids.

## Sub-features

- `agent-builds` returns an agent named `retail_support` with four tools when `EVAL_BIBLE_AGENT_MODEL` is set.
- `agent-missing-model` fails and names `EVAL_BIBLE_AGENT_MODEL` when it is unset.
- `policy-refund-limit` refuses a refund over the limit, names the limit, and leaves the order unchanged.

## How to get to it (user POV)

- `from evaluation_bible.agents.retail_support import build_agent`, with `EVAL_BIBLE_AGENT_MODEL` set as `.env.example` shows.
- `from evaluation_bible.agents.retail_support import OrderStore, RetailSupportTools`, to drive the tools without a model.

## Driving it with bash

Preconditions:

- Tier: fast
- `uv sync` has run.

```bash
out="$(EVAL_BIBLE_AGENT_MODEL=verify-model uv run python -c '
from evaluation_bible.agents.retail_support import build_agent
agent = build_agent()
print(agent.name, len(agent.tools))
')"
printf '%s\n' "$out"
[ "$out" = "retail_support 4" ]
```

```bash
if out="$(env -u EVAL_BIBLE_AGENT_MODEL uv run python -c 'from evaluation_bible.agents.retail_support import build_agent; build_agent()' 2>&1)"; then
  echo "expected build_agent() to fail without EVAL_BIBLE_AGENT_MODEL"
  exit 1
fi
printf '%s\n' "$out" | tail -1
printf '%s\n' "$out" | grep -q 'EVAL_BIBLE_AGENT_MODEL'
```

```bash
uv run python -c '
from evaluation_bible.agents.retail_support import OrderStore, RetailSupportTools
tools = RetailSupportTools(OrderStore())
result = tools.issue_refund("ORD-1002", 250.0)
assert result["status"] == "error" and "100.0" in result["message"], result
assert tools.lookup_order("ORD-1002")["order_status"] == "placed"
print("refund over the limit refused:", result["message"])
'
```

## Gotchas

- Building the agent makes no model call. Only running it does, so a fast-tier feature must never run it.
- The first block needs the exact line `retail_support 4`. A changed tool count is a real change to the agent's surface.
