# Data Sources — Swing Trade Setup

This skill is chat-fast, so the data-gathering step needs to be lean. Use the priority list below and stop as soon as you have enough to populate the indicator dashboard. Do not over-fetch.

## Source priority by data point

### Current price, OHLC, volume, market cap, beta, 52W range, next earnings
1. **stockanalysis.com/stocks/[ticker]/** — single-page snapshot, easy to parse, refreshed each session.
2. **finance.yahoo.com/quote/[TICKER]/** — fallback if stockanalysis.com is rate-limited.
3. **stockinvest.us/stock/[TICKER]** — has Fibonacci and accumulated-volume S/R levels alongside price; useful when you want both at once.

### 50DMA, 200DMA, RSI(14), MACD posture
1. **stockinvest.us/stock/[TICKER]** — explicit S/R, recommended stop-loss, MA posture in plain language.
2. **altindex.com/ticker/[ticker]/technical-analysis** — exposes RSI numerically, plus a buy/sell signal count.
3. **tickeron.com/ticker/[TICKER]/** — backup; tends to surface multi-timeframe summaries.
4. **investtech.com** — useful for medium-term trend channel reads when other sources disagree.

### Recent material news (last 14 days)
1. **finance.yahoo.com/quote/[TICKER]/news/** — chronological, easy to skim headlines.
2. **stocktitan.net/news/[TICKER]/** — surfaces earnings releases, M&A, and 8-K-style updates with date stamps.
3. **WebSearch** — for company-specific catalysts (FDA decisions, regulator actions). Use the company name AND ticker to disambiguate.

### Analyst consensus (light touch — verdict line, not the deliverable)
1. **stockanalysis.com/stocks/[ticker]/forecast/** — consensus and PT range in one shot.
2. **MarketBeat** as fallback.

## Calling pattern

Two parallel calls is usually enough:
1. WebSearch for "[ticker] stock price RSI MACD moving average [current month year]" — gets the technical summary.
2. WebFetch the stockanalysis.com snapshot page — gets price/cap/beta/earnings/52W/volume in one structured pull.

If WebFetch returns a "result too large" error, use the local file Grep/Read pattern to extract just the snapshot keys (Price, Market Cap, Beta, 52-Week Range, Volume, Average Volume, Earnings Date). Do not load the full HTML into context.

## Disagreement between sources

Different screeners disagree on RSI and on which way the 50/200DMA cross is sitting because they use slightly different windows and refresh times. Resolve disagreement honestly:

- If two sources agree and one is the outlier, go with the two — note the disagreement only if it changes the verdict.
- If sources split on RSI by more than 15 points (e.g., one says 50, one says 72), surface it as "RSI mixed across screeners (50–72)" and lean on MACD and the volume tape instead.
- If 50DMA vs 200DMA cross direction is ambiguous, say so. A "near Golden Cross" or "near Death Cross" is itself a useful technical observation.

## Staleness rules

- Intraday is nice to have but not required — last close is the working baseline.
- A close more than 3 trading sessions stale: re-fetch before publishing the read. Markets move.
- Earnings date older than 90 days from "today" implies the next-earnings field is wrong. Re-fetch.

## When data simply isn't available

For thinly-traded names, smallcaps, or non-US listings:
- 50DMA and 200DMA may not be widely published — compute from the last 200 closes if you can pull them, or note "MA data not surfaced".
- RSI may not be on the screeners — say so rather than skip.
- Beta may be unstable for low-history names — note "beta unstable; use vol cone instead".

The reader would rather see "not surfaced" than a fabricated number.
