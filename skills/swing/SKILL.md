---
name: swing
description: Generate a 6-slide swing-trade setup deck for a ticker. Invoked explicitly as /halal-investing:swing <TICKER> [horizon-weeks].
argument-hint: <TICKER> [horizon e.g. 2-8]
disable-model-invocation: true
---

Produce a swing-trade setup deck for: $ARGUMENTS

1. Take the first token of the arguments as the ticker, uppercased. If no ticker was given, ask for one and stop.
2. If a second argument looks like a week range (`3-6`) or a single number (`4`), use it as the horizon in weeks, overriding `default_horizon_weeks` from settings.
3. Follow the `swing-trade-setup` skill end to end — its Settings, workflow, slide structure, honesty rules, and builder invocation all apply unchanged.
4. Reply in chat with only the verdict line, a one-sentence rationale, and the link to the deck.
