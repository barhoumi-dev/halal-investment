---
name: swing-trade-setup
description: Produce a self-contained HTML slide deck (inline SVG, navy/amber palette) for a swing-trade setup on a single ticker, 2-to-8-week horizon. The 6-slide deck covers verdict, Halal/Shariah flag, key levels chart, indicator dashboard with gauges, entry/stop/targets with a risk-reward visualization, and catalysts. Use whenever the user asks for a swing-trade setup, a short-term technical read, "is this a good buy", entry/stop/target on a ticker, key levels for a stock, or anything that sounds like a trader sizing up a setup over the next few weeks — even without the words "swing trade". Triggers include "should I buy NVDA", "what's the setup on TSLA", "give me levels on AMD", "where would I get in on PLTR", "is KEEL a buy here". The deliverable is always one HTML file navigated by arrow keys — the chat reply is just a brief verdict line plus the file link. Do NOT use for full fundamental reports (use investment-research-report) or long-term investment thesis.
---

# Swing-Trade Setup — Slide Deck

You are producing a self-contained HTML slide deck for a swing trader. The horizon is 2 to 8 weeks. The reader opens the file in a browser, navigates with arrow keys, and walks away with a verdict and concrete trade levels.

## When to use this skill

Trigger on any prompt where the user is sizing up a single ticker over a short horizon. Common phrasings:

- "Should I buy [ticker]?"
- "What's the technical setup on [ticker]?"
- "Give me levels on [ticker]"
- "Where would I get in on [ticker]?"
- "Is [ticker] a buy here?"
- "Quick technical read on [ticker]"

Do not use this skill if the user wants a full research report (fundamentals, valuation, DCF, multi-section report) — that's `investment-research-report`. Do not use this skill for crypto tokens unless the user explicitly asks for a swing setup on a token.

## The deliverable

A single self-contained HTML file written to `<swing_dir>/` (see Settings). The file:

- Contains 6–7 slides navigable with `←` `→` arrow keys
- Has all graphics inline as SVG (no external image files, no CDN dependencies)
- Renders correctly when opened directly in a browser, even offline
- Uses the navy `#0B3C5D` / amber `#C69214` palette consistent with the user's investment-research-report HTML reports

The chat reply that accompanies the file is **brief**: one verdict line, a one-sentence rationale, and the `computer://` link. Do NOT paste the full setup tables in chat — that defeats the point of the deck.

Example chat reply shape:

> **NVDA — WAIT.** Earnings 17 days out and price mid-range with bearish MACD; best entry is a $188–$192 pullback or a confirmed >$217 break post-earnings.
>
> [Open the deck](computer://...path...)

## Settings

Before starting, read `.claude/halal-investing.local.md` in the current working directory if it exists, and parse its YAML frontmatter. Fall back to these defaults for any missing field or a missing file:

| Field | Default | Effect here |
|---|---|---|
| `swing_dir` | `swing-setups` | Output folder (relative to the agent's working directory unless absolute). Create it if absent. |
| `research_dir` | `research-reports` | Where to look for a prior report on the same ticker. |
| `halal_mandate` | `true` | When `true`, a non-compliant Halal flag overrides BUY into AVOID. When `false`, show the flag but let the technicals drive the verdict. |
| `default_horizon_weeks` | `2-8` | Horizon used for the earnings-window check and catalyst slide unless the user names one. |

Save the deck to `<swing_dir>/<TICKER>_swing_setup_<YYYY-MM-DD>.html` under the directory the agent is running from, keeping the repo's `swing-setups/` structure. If no settings file exists and you cannot determine where the user wants the output saved, ask once before writing the file.

## The workflow

1. **Resolve the ticker.** If the user gave a casual name ("Nvidia", "Apple"), confirm the ticker before pulling data. If the ticker is ambiguous, ask once.

2. **Pull current data.** Use the source priority list in `references/data_sources.md`. The minimum set you need:
   - Current price, day's range, previous close, volume vs average volume
   - 50-day moving average, 200-day moving average
   - RSI(14), MACD posture
   - 52-week high / low
   - Beta, average daily volatility
   - Next earnings date (critical — if it's inside the swing horizon, the trade is an earnings bet)
   - Recent material news in the last 14 days

   Do not invent figures. If a number is genuinely unavailable, the spec accepts `null` and the slide will render with a "n/d" placeholder.

3. **Run the Halal quick-flag.** See `references/shariah_quick_screen.md`. The flag is mandatory and prominent. If the user has a prior fundamental report on the ticker, reuse the verdict.

4. **Identify levels.** Pull at least three support and three resistance levels. Cluster nearby levels into zones — the trader cares about zones, not pinpoints.

5. **Build the trade-setup spec.** Decide on:
   - Direction (long / short / neutral)
   - Entry zone A (preferred — pullback or breakout)
   - Entry zone B (alternative — confirmation entry)
   - Stop-loss anchored to a named level
   - Two targets (T1 = first measured-move objective, T2 = swing high / extension)
   - Risk/reward to T1
   - Position sizing language (full / half-size / wait)
   - Invalidation level

6. **Take a stand.** One verdict: BUY, WAIT, or AVOID. "WAIT" must name the trigger (specific price level + volume condition, or a specific event). When `halal_mandate` is `true`, non-compliance overrides BUY into AVOID — say so when it bites.

7. **Generate the deck.** Build a JSON spec following the schema in `references/output_template.md`, write it to a temp path, then run:

   ```
   python skills/swing-trade-setup/scripts/build_slides.py --spec <tmp>/setup_spec.json --out "<swing_dir>/<TICKER>_swing_setup_<YYYY-MM-DD>.html"
   ```

   `skills/` resolves from the agent's working directory (the repo root). If the script isn't there, Glob `**/swing-trade-setup/scripts/build_slides.py` from the working directory to locate it.

   The script writes a single self-contained HTML file. It draws the levels chart, indicator gauges, and risk/reward bar as inline SVG — there are no external dependencies and the file works offline.

8. **Reply briefly in chat.** One verdict line, one-sentence rationale, the `computer://` link. That's it.

## Slide structure

The deck is always 6 slides in this order. The user can flip through them in 30 seconds and walk away with the setup.

1. **Title slide** — Ticker, name, date, large verdict (BUY/WAIT/AVOID), price, halal status pill.
2. **Trend & Halal** — One-paragraph trend read, the three-lens Halal flag with the verdict prominent.
3. **Key levels chart** — SVG horizontal-band visualization showing supports, resistances, MAs, current price, entry zone, stop, and targets in one view.
4. **Indicator dashboard** — RSI gauge, MACD posture indicator, MA-position bars, earnings-window flag.
5. **Trade setup** — Entry/stop/target table plus a risk/reward visualization (one-bar chart showing risk vs T1 reward vs T2 reward).
6. **Catalysts, verdict, sources** — Catalysts inside the horizon, the verdict line restated, two-three source links, disclaimer.

Why six slides: enough to separate concerns visually but few enough that a trader on a phone can flip through in seconds.

## Honesty rules

- **Don't bury bad signals.** If RSI is 75 (overbought) and you're recommending BUY, say so on the indicator slide.
- **Don't anchor on the user's apparent bias.** "Should I buy?" does not mean "convince me." If the right call is WAIT or AVOID, the verdict pill on slide 1 reflects that.
- **Don't fabricate precise levels.** Zones are fine ("$197–$200"); fake-precise pinpoints ($198.37) are not.
- **State staleness.** If the most recent close is two days old, the title slide says "as of [date]". Don't fake intraday precision.

## When the news matters more than the chart

If a binary catalyst (earnings, FDA decision, regulator ruling, M&A close) sits inside the swing horizon, slide 4's earnings-window flag fires red, and the trade-setup slide's position-sizing field defaults to "half-size" or "WAIT until print". A swing trade three days into earnings is an earnings bet, not a technical trade.

## Reading the user's portfolio context

Glob `<research_dir>/<TICKER>_*_report.html` to check whether a fundamental report on this ticker already exists. If one does, reuse the Shariah verdict and the bull/bear context for the Halal flag and the catalysts slide. Map the report's header status to the quick-flag vocabulary: `halal` → Compliant, `haram` → Non-compliant, `review` → Doubtful. The technical levels still need to be pulled fresh.

## Reference files

- `references/output_template.md` — slide-by-slide structure and the JSON spec schema for `build_slides.py`
- `references/data_sources.md` — ordered source list for price, indicators, news
- `references/shariah_quick_screen.md` — lean Halal flag heuristic
- `scripts/build_slides.py` — the deck generator (HTML + inline SVG, single-file output)
- `scripts/make_levels_chart.py` — older standalone PNG chart helper, kept for compatibility but the slide deck embeds its own SVG version

## Disclaimer

Every deck closes slide 6 with: *"Technical read, not financial advice — do your own due diligence."* The script handles this automatically; don't add it manually.
