# Equity Report Structure — Full Template

Read this when you're actually building an equity report. SKILL.md covers the overview; this file has the exact tables, columns, and rendering guidance section by section.

## 1. Snapshot

One-row table (or two-column key/value if that fits better). Columns:

| Price | Market Cap | Shares Out | 52W High | 52W Low | Div Yield (TTM) | Beta | Next Earnings | Sector / Industry |

All numeric cells as strings (e.g., "$142.50", "$3.5T", "1.23"). Long values (e.g. sector/industry) wrap automatically in the HTML stat cards.

## 2. Business Overview

**Prose, 3-5 short paragraphs.** Cover:
- What the company does in plain language
- Revenue model (product, subscription, ad, transaction, etc.)
- Revenue streams — where the money actually comes from, ranked
- Competitive moat — named mechanism (network effect, switching cost, IP, cost advantage, brand)

**Segment / geographic revenue breakdown** — table:

| Segment | % Revenue | YoY Growth | EBIT Margin | Notes |

If the company doesn't disclose segment margins, put "n/d" and say so in the narrative.

**Ownership structure** — short paragraph or mini-table:
- Founder / insider ownership %
- Top institutional holders (if concentrated)
- Recent insider transactions — only surface if material (>$1M or >1% of holdings in last 90 days)

**Recent strategic developments** — bullet list. M&A announcements, pivots, major contracts, regulatory changes. Last 12 months max.

## 3. Shariah Compliance

### 3a. Summary table

| Lens | Rating | Key driver |
|---|---|---|
| Zoya | Compliant / Non-compliant / Questionable | Brief reason |
| Musaffa | Halal / Not Halal / Doubtful | Brief reason |
| AAOIFI (manual calc) | Pass / Fail | Which ratio drove it |
| PIF 4-step | Comfortable / Uncomfortable | Which step drove it |
| **Overall assessment** | Your synthesized view | 1 sentence |

If Zoya or Musaffa doesn't cover the name, write "Not covered" — don't fabricate a rating.

### 3b. AAOIFI Financial Ratio Screen

See `aaoifi_screen.md` for the methodology. Present as a table with real numbers:

| Ratio | Threshold | Actual | Pass? |
|---|---|---|---|
| Haram revenue / Total revenue | < 5% | 0.8% | ✓ |
| Interest-bearing debt / Market Cap | < 30% | 4.2% | ✓ |
| Interest-bearing securities / Market Cap | < 30% | 1.1% | ✓ |
| Accounts Receivable / Market Cap | < 49% | 7.3% | ✓ |

Show the input numbers (total revenue, debt, securities, AR, market cap) in a short paragraph below the table so the calc is auditable.

### 3c. PIF 4-step screen

See `pif_screen.md` for full methodology. Four subsections:

**Step 1 — Core business halal.** Use the industry exposure checklist:

| Excluded Industry | Exposure? | Notes |
|---|---|---|
| Alcohol | N | — |
| Tobacco | N | — |
| Cannabis | N | — |
| Pork products | N | — |
| Conventional financial services | N / Partial | e.g. "Stripe partnership for payments" |
| Defense / weapons | N | — |
| Gambling / casinos | N | — |
| Music | N / Partial | e.g. "Apple Music is ~6% of services" |
| Hotels | N | — |
| Cinema | N | — |
| Adult entertainment | N | — |
| Online dating | N | — |


**Step 2 — Israel presence / human rights.** One paragraph. Check company operations in Israel, human rights controversies, supply chain flags. Cite sources (news, company sustainability report, HRW/Amnesty if material).

**Step 3 — Interest income ≤ 2.5% of total revenue, four consecutive quarters.** Table:

| Quarter | Interest Income | Total Revenue | Ratio | Pass? |
|---|---|---|---|---|

Pull from 10-Q / 10-K filings.

**Step 4 — Interest expense ≤ 2.5% of total expenses, four consecutive quarters.** Table:

| Quarter | Interest Expense | Total Expenses | Ratio | Pass? |
|---|---|---|---|---|

**Rating.** If any step fails, rate "Uncomfortable". The one documented exception: pre-revenue or early-stage ramp companies may be reviewed contextually — note this explicitly if you invoke it.

### 3d. Purification

If the name generates any interest income (cash on balance sheet, treasury holdings) or any non-permissible revenue, calculate the purification amount:

- Purification per share = (Interest income + Non-permissible revenue, TTM) / Shares outstanding
- Round to cents/share

State: "Purification required: $0.04/share (TTM interest income $420M + haram revenue $90M = $510M / 14B shares)".

## 4. Financial Fundamentals

**Historicals + forward table:**

| Line | FY-3 | FY-2 | FY-1 | FY-0 (est) | YoY % |
|---|---|---|---|---|---|
| Revenue | | | | | |
| Gross Profit | | | | | |
| EBIT | | | | | |
| NPAT | | | | | |
| EPS | | | | | |
| Gross margin | | | | | |
| EBIT margin | | | | | |
| Net margin | | | | | |
| DPS | | | | | |

YoY % column is FY-0 vs FY-1.

**Revenue + NPAT growth bar chart.** Two colored bars per year — revenue in navy, NPAT in amber. Helper: `svg_revenue_chart(years, revenue, npat)` in build_report_html.py, inserted via `b.html(...)`.

**Balance sheet & returns table:**

| Metric | Value | Notes |
|---|---|---|
| Cash & equivalents | | |
| Total debt | | |
| Net debt | | |
| Net debt / EBITDA | | |
| ROE | | |
| ROIC | | |
| Current ratio | | |

**Cash flow quality** — prose (2-3 short paragraphs):
- FCF generation vs net income (divergence? why?)
- CapEx intensity — maintenance vs growth split if disclosable
- Working capital swings worth flagging

## 5. Valuation

**Multiples table:**

| Multiple | Current | Sector Median | 5-yr Avg | Signal |
|---|---|---|---|---|
| P/E (TTM) | | | | ↑ / → / ↓ |
| Forward P/E | | | | |
| PEG | | | | |
| EV/EBITDA | | | | |
| P/S | | | | |
| P/FCF | | | | |
| Dividend yield | | | | |

**Intrinsic valuation table (DCF):**

| Scenario | Implied / Share | % vs Current | Key assumption |
|---|---|---|---|
| Bear | | | e.g. "Rev CAGR 4%, terminal 2%, WACC 10%" |
| Base | | | |
| Bull | | | |
| **Reverse DCF** | What growth is priced in? | | |


## 6. Analyst Coverage

**Analyst table** — sorted most-recent date at top:

| Analyst / Firm | Date | Rating | Prev. Rating | Target | Prev. Target | Upside % |
|---|---|---|---|---|---|---|

Use ↑ / ↓ / = arrows in Prev. Rating column to show change. Two summary rows at bottom:
- **Consensus** — median target, consensus rating, count of analysts
- **Range** — low / high target, spread %

**If analyst-level data is not publicly available** (common for small caps), show a single summary row with consensus from Yahoo/Stockanalysis and a note: "Analyst-level granularity not publicly available; consensus only."

**Analyst target range dot plot** — horizontal line with four points: Low / Median / Current / High. Helper: `svg_analyst_dotplot(low, median, current, high)`.

**Key Analyst Commentary** — prose section. For each analyst with a notable call in the last 60 days, pull the one-sentence statement from their note that drove the target. Cite source.

## 7. Technical Analysis

**Price chart** — 12-month daily price with 50DMA and 200DMA overlay. Helper: `svg_price_chart(prices, dates, ma50, ma200)`. Use navy for price, amber for 50DMA, gray for 200DMA.

**Indicators table:**

| Indicator | Value | Read |
|---|---|---|
| Current price | | |
| 50DMA | | Above / below price |
| 200DMA | | |
| RSI (14) | | Overbought / neutral / oversold |
| MACD | | Bullish / bearish crossover |
| Key support | | |
| Key resistance | | |
| Beta | | |
| Weekly volatility | | |

Wrap "Read" column.

## 8. Catalysts & Risks

Two bulleted lists. 3-6 items each.

**Catalysts** — each one names a specific event or data point:
- "Q2 earnings on 2026-05-15 — watch data center segment YoY growth; consensus 58%"
- "Blackwell ramp contribution to gross margin by Q3"

Not: "strong earnings", "AI demand" (vague; not a catalyst).

**Risks** — each one names the actual mechanism of loss:
- "Export controls on China-bound AI chips → ~15% of revenue at risk"
- "Hyperscaler CapEx normalization after 2026 → multiple compression"

Not: "macro risk", "competition" (not actionable).

## 9. Optional Deep-Dives

Pick based on what the name actually needs. Don't include all of these in every report.

- **Insider & institutional ownership detail** — always for founder-led or serial acquirer names. Show top 10 institutions, insider holdings over time.
- **Short interest** — include for contested, small-cap, or high-SI names. Pull from NYSE/Nasdaq short interest report or Ortex.
- **Capital allocation track record** — always for serial acquirers. Show M&A ROIC calc, buyback yield, dividend growth.
- **Scenario analysis** — for binary-event names (FDA approvals, key trial readouts, regulatory decisions) or highly assumption-sensitive DCFs.
- **Competitive positioning matrix** — 2x2 or feature matrix when there's a clear peer group.
- **Management compensation** — when alignment is questionable (e.g., options-heavy pay vs TSR, disclosed concerns).
- **Auditor / accounting flags** — only when something warrants attention. Auditor changes, going-concern language, restatements, unusual non-GAAP adjustments.

## 10. Summary & Thesis

- **Bull case** — one paragraph. The reason this works.
- **Bear case** — one paragraph. The reason this breaks.
- **What to watch next** — 2-3 bullets, each naming a specific observable data point or event with a date or frequency.
- **Disclaimer** — verbatim: *"This is research, not financial advice. Do your own due diligence."*
