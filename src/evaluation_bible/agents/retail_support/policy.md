# retail_support policy

Rules the `retail_support` agent's tools enforce, independent of what the model
is asked to do:

1. A refund above 100 must be escalated to a human, never issued directly.
   `issue_refund` refuses any amount over the limit and names the limit in its
   refusal; the agent should call `escalate` instead.
2. A cancelled order cannot be refunded. `issue_refund` refuses on a
   cancelled order regardless of amount.
3. Every tool call that targets an order id that does not exist in the store
   refuses by naming that order id, and leaves the store unchanged.
