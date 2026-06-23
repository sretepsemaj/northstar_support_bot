# North Star Support Bot Demo Script

A short outline for the required 2-3 minute video demo.

## Opening

- Show the local demo page at `http://localhost:8000`.
- Open the support widget.
- Mention that the bot uses provided mock data and works without an API key.

## Scenario 1: Order Tracking

Suggested prompt:

```text
Track order #111
```

Show:

- Bot recognizes order tracking.
- Bot returns shipped status and arrival timing.

Optional invalid order prompt:

```text
Track order #999
```

Show:

- Bot handles invalid order numbers clearly.

## Scenario 2: Returns & Exchanges

Suggested prompt:

```text
I want to return this jacket
```

Show:

- Bot explains the 30-day return policy.
- Bot includes the returns link.

## Scenario 3: Product Recommendations

Suggested prompt:

```text
I need a recommendation
```

Show:

- Bot asks clarifying category question.
- Select a category such as `Camping Gear` or `Weather Protection`.
- Bot asks a category-specific follow-up.
- Bot recommends a product category without inventing specific products.

## Scenario 4: Human Handoff

Suggested prompt:

```text
I want to talk to a person
```

Show:

- Bot transitions to live agent / human support state.

## Scenario 5: Fallback Handling

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
