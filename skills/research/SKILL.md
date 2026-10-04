---
name: research
description: Generate a halal-conscious research report for a stock ticker or crypto token. Invoked explicitly as /halal-investing:research <TICKER>.
argument-hint: <TICKER> [crypto]
disable-model-invocation: true
---

Produce a research report for: $ARGUMENTS

1. Take the first token of the arguments as the ticker, uppercased. If no ticker was given, ask for one and stop.
2. Treat the asset as crypto if the second argument is `crypto` or the ticker is an obvious token (BTC, ETH, SOL, …); otherwise treat it as an equity.
3. Follow the `investment-research-report` skill end to end — its Settings, workflow, section structure, builder rules, and delivery format all apply unchanged. For equities, that includes dispatching the `shariah-screener` agent for Section 3.
4. Reply in chat with only the `shariah_status`, a 2–3 sentence thesis, and the link to the HTML file.
