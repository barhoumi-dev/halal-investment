# Output Template — Swing Trade Setup Slide Deck

This skill always emits a 6-slide HTML deck via `scripts/build_slides.py`. The script consumes a JSON spec; this file documents the spec schema and what each slide contains.

## The JSON spec

`build_slides.py` accepts a single JSON file with this top-level shape:

```json
{
  "ticker": "NVDA",
  "name": "NVIDIA Corporation",
  "as_of": "2026-05-03",
  "verdict": "WAIT",
  "verdict_reason": "Earnings 17 days out and price mid-range with bearish MACD; best entry is a pullback or post-earnings breakout.",
  "halal": {
    "status": "Compliant",
    "summary": "GPUs / accelerated computing — clean. Debt/MC <1%, interest income immaterial."
  },
  "trend": "Primary uptrend intact and pressing toward all-time highs ($216.83 set within the last 52 weeks); price reclaimed the 200DMA in April but is now stalling just below the 50DMA (~$206) with bearish near-term MACD — classic mid-range coil heading into the May 20 print.",
  "price": 198.45,
  "supports":   [{"price": 200, "label": "Fib pivot / last week's lows"},
                 {"price": 188, "label": "200DMA / long-term cluster"},
                 {"price": 165, "label": "March swing low / major demand"}],
  "resistances":[{"price": 207, "label": "50DMA"},
                 {"price": 217, "label": "52W / ATH"},
                 {"price": 225, "label": "measured-move extension"}],
  "ma50": 206.40,
  "ma200": 189.06,
  "indicators": {
    "rsi": 52,
    "rsi_note": "Mixed across screeners (51–71); lean neutral.",
    "macd": "bearish",
    "macd_note": "Line below signal; mild negative momentum.",
    "beta": 1.7,
    "daily_vol_pct": 3.0,
    "next_earnings": "2026-05-20",
    "earnings_in_horizon": true,
    "earnings_days_away": 17
  },
  "trade": {
    "direction": "Long",
    "entry_low": 188,
    "entry_high": 192,
    "entry_b_label": "Break > $217 on >1.5x volume",
    "stop": 182,
    "t1": 216,
    "t2": 232,
    "rr_t1": 3.3,
    "rr_t2": 5.4,
    "sizing": "Half-size — earnings inside horizon",
    "invalidation": "Daily close < $182 — trend break"
  },
  "catalysts": [
    "Q1 FY27 earnings 2026-05-20 (after close) — guidance is the swing factor",
    "Blackwell Ultra ramp updates — gross margin commentary",
    "China export-control headlines — H20 / B30 chip variants"
  ],
  "sources": [
    {"label": "stockinvest.us — NVDA", "url": "https://stockinvest.us/stock/NVDA"},
    {"label": "altindex — NVDA technical", "url": "https://altindex.com/ticker/nvda/technical-analysis"},
    {"label": "Wall Street Horizon earnings", "url": "https://www.wallstreethorizon.com/nvidia-earnings-calendar"}
  ]
}
```

### Required fields

- `ticker`, `name`, `as_of`, `verdict`, `verdict_reason`
- `halal.status` (one of `Compliant`, `Doubtful`, `Non-compliant`), `halal.summary`
- `trend`, `price`
- `supports` (≥1), `resistances` (≥1)
- `trade.direction`, `trade.stop`, `trade.t1`
- At least one entry zone — `entry_low`+`entry_high` OR `entry_b_label` (or both)

### Optional fields

- `ma50`, `ma200` — drawn on the levels chart if present
- `indicators.*` — each renders a small visual on slide 4; missing fields render as `n/d`
- `trade.t2`, `trade.rr_t1`, `trade.rr_t2`
- `catalysts` (list of strings)
- `sources` (list of `{label, url}`)

## Slide-by-slide content

### Slide 1 — Title

- Large ticker symbol and company name
- Date ("As of YYYY-MM-DD")
- Big verdict pill — colour-coded (BUY = green, WAIT = amber, AVOID = red)
- Current price callout
- One-line verdict reason
- Halal status pill (small but unmissable)

### Slide 2 — Trend & Halal

- Trend paragraph (the `trend` field, rendered as is)
- Halal flag block — status pill + the `halal.summary` line
- For Halal-mandate readers, this slide is the early-exit gate. If status is "Non-compliant", a callout box says "This trade is not yours to take" and the verdict pill on slide 1 was already AVOID.

### Slide 3 — Key levels chart

- Inline SVG showing a vertical price ladder
- Horizontal bands for support (gray dashed), resistance (gray dashed)
- 50DMA (amber line), 200DMA (gray dashed-dot)
- Entry zone (amber tinted band)
- Stop (red line)
- T1 (green dashed), T2 (green dotted)
- Current price (navy bold line, labelled)
- Each level is labelled to the right with its tag (e.g., "S $188 — 200DMA cluster")

### Slide 4 — Indicator dashboard

- RSI gauge — semicircular arc, 0–100, current RSI as a needle. Zones: 0–30 oversold (green tint), 30–70 neutral (white), 70–100 overbought (red tint). Outlier-spread note shown below if `rsi_note` mentions disagreement.
- MACD posture indicator — bullish (green) or bearish (red) tile with the `macd_note` underneath.
- Moving-average position bar — horizontal stack showing where price sits relative to 50DMA and 200DMA (above or below, by what %).
- Earnings-window flag — large green tile if outside horizon, large red tile if inside (`earnings_in_horizon: true`).
- Beta and daily volatility shown as small stat callouts.

### Slide 5 — Trade setup

- Two-column layout
  - Left: entry/stop/T1/T2 table with the `direction`, `sizing`, `invalidation` rows
  - Right: SVG bar showing risk vs reward — risk bar (red, downward from entry-mid to stop), T1 bar (green, upward to T1), T2 bar (lighter green, upward to T2). Overlaid with R:R ratios.
- The bar visualization is what makes the slide instantly scannable: a long red and a short green = bad trade; a short red and tall greens = good trade.

### Slide 6 — Catalysts, verdict, sources

- Catalysts list (bulleted, with dates / triggers)
- Verdict restated, larger
- Sources (1–3 links)
- Closing disclaimer: "Technical read, not financial advice — do your own due diligence."

## Style

The deck inherits the navy/amber palette from the investment-research-report skill so it sits comfortably alongside any research report the user has previously generated. Title bar uses a subtle navy gradient; body slides are white with the amber accent rule under the section headline. Inline SVG only — no external CDN, no fonts beyond system stack.

## What NOT to put in the deck

- Walls of prose. Each slide should fit on one screen at 720p without scrolling.
- Multiple charts per slide — one focal graphic per slide, max.
- The full text of analyst notes or news articles. Headlines / dates only.
- Tracking pixels, telemetry, anything that calls out to the network when opened.

## Why slides instead of chat

A trader scanning a setup doesn't need 400 words of prose. They need: verdict, levels, a chart, sized entry/stop. The deck format puts each of those on its own slide with one focal graphic. It's also shareable — the trader can drop the HTML file into a watchlist folder, mail it, or open it later without rerunning anything.

The chat reply is one verdict line plus a link, deliberately. The deck carries the substance.
