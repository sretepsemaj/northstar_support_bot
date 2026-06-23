# North Star Support Bot Demo Script

A short outline for the required 2-3 minute video demo.

## Opening

- Show the local demo page at `http://localhost:8000`.
- Open the support widget.
- Mention that the bot uses provided mock data and works without an API key.

## Scenario 1: Order Tracking

Suggested prompts:

```text
Track order #111
Where is order 222?
Order status 333
Track order #999
```

Show:

- Bot recognizes order tracking variations.
- `#111` returns shipped / arriving tomorrow.
- `#222` returns processing / ships in 24 hours.
- `#333` returns delivered with a follow-up.
- Invalid order numbers are handled clearly.

## Scenario 2: Returns & Exchanges

Suggested prompt:

```text
I want to return this jacket
```

Show:

- Bot explains the 30-day return policy.
- Bot includes the returns link.

## Scenario 3: Shipping Policy

Suggested prompt:

```text
How long is shipping?
```

Show:

- Bot answers from provided shipping data.
- Standard shipping is `3-5 days`.
- Expedited shipping is `1-2 days`.
- Bot does not ask for an order number for a generic shipping-policy question.

## Scenario 4: Product Recommendations

Suggested prompt:

```text
I need a recommendation
```

Show:

- Bot asks clarifying category question.
- Select a category such as `Camping Gear` or `Weather Protection`.
- Bot asks a category-specific follow-up.
- Bot recommends a product category without inventing specific products.

## Scenario 5: Human Handoff

Suggested prompt:

```text
I want to talk to a person
```

Show:

- Bot transitions to live agent / human support state.

## Scenario 6: Fallback Handling

Suggested prompt:

```text
What is the weather today?
```

Show:

- Bot gives a clear fallback response.
- Bot offers supported options and mentions live agent escalation.

## Optional: LLM Assist

If `USE_LLM=true` is configured locally, show `Response details` after an ambiguous product message.

Suggested prompt:

```text
I need rainwear for a wet trail day
```

Show:

- `llm_attempted` and `intent_reviewed` metadata when LLM assists.
- Final response still uses controlled app categories and mock data.

## Closing

- Show the demo tracker with completed scenarios.
- Mention tests can be run with:

```bash
make test
```

- Mention no deployment is required for this assignment.
