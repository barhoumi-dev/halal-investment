---
name: investment-research-report
description: Produce a standardized, halal-conscious investment research report as a polished HTML file for a stock ticker or crypto token. Use this skill whenever the user asks for investment research, equity research, a stock report, a crypto report, a halal/Shariah screen, a ticker writeup, a DCF, or anything resembling "put together a research report on NVDA" (or any other ticker) — even if they don't explicitly ask for a "report". The skill enforces a fixed 10-section structure (snapshot, business overview, Shariah compliance, fundamentals, valuation, analyst coverage, technicals, catalysts/risks, deep-dives, thesis), a parallel 7-section crypto template, the PIF 4-step Shariah methodology, AAOIFI ratio screens, consistent navy/amber HalalInvest styling, and HTML builder rules that ensure stat-card snapshots, compliance progress-bar tables, and SVG charts render cleanly. Do not freehand an investment report without this skill — it is the only way to stay faithful to the user's standard format.
---

# Investment Research Report

You are producing a research HTML report that will sit alongside every other report the user has ever generated with this skill. Consistency with the standard structure matters more than cleverness — the reader needs to be able to flip between reports and compare at a glance.

## The deliverable

**HTML only.** No long inline markdown responses, no summaries in chat. Write the HTML file to `<research_dir>/` (see Settings) and share a short `computer://` link plus a 2-3 sentence thesis. The HTML is self-contained (all CSS and SVG inline) — no server required. It opens offline with system fallback fonts; the Geist / Instrument Serif web fonts load from Google Fonts when online.

## Settings

Before starting, read `.claude/halal-investing.local.md` in the current working directory if it exists, and parse its YAML frontmatter. Fall back to these defaults for any missing field or a missing file:

| Field | Default | Effect here |
|---|---|---|
| `research_dir` | `research-reports` | Output folder (relative to the agent's working directory unless absolute). Create it if absent. |
| `pif_strict` | `true` | When `false`, all four PIF steps are reported for information only and AAOIFI alone drives `shariah_status`. |

Save the report to `<research_dir>/<TICKER>_research_report_<YYYY-MM-DD>.html` (date = as-of close) under the directory the agent is running from, keeping the repo's `research-reports/` structure. If no settings file exists and you cannot determine where the user wants the output saved, ask once before writing the file.

## The workflow

1. **Decide: equity or crypto.** If the user names a stock ticker, use the 10-section equity template (`references/report_structure.md`). If a crypto token, use the 7-section crypto template (`references/crypto_template.md`).
2. **Pull the data.** Use WebSearch + WebFetch against the source priority list in `references/data_sources.md`. Pull *real numbers* from filings/IR pages/screeners — do not estimate if actual figures are available. Shariah inputs (four quarters of interest income/expense, balance-sheet ratios) are pulled by the agent in step 3 — fetch them here only if the agent is unavailable.
3. **Run the four Shariah lenses via the `shariah-screener` agent.** For equities, dispatch the `halal-investing:shariah-screener` agent **in the background** with the ticker, company name, and `pif_strict` value. It pulls four consecutive quarters of filings and returns Zoya, Musaffa, AAOIFI ratios, PIF 4-step results, and purification cents/share as a structured block — use those numbers for Section 3 (3a–3d), and pass its `shariah_status:` line straight to the `HtmlReportBuilder` constructor. Continue pulling non-Shariah data while it runs. If the agent is unavailable, run the lenses inline per `references/aaoifi_screen.md` and `references/pif_screen.md`. Crypto tokens skip the agent and follow `references/crypto_template.md`. Don't skip a lens because a free screener didn't have the name.
4. **Build the HTML report.** Use the builder at `skills/investment-research-report/scripts/build_report_html.py` (relative to the agent's working directory, the repo root) — it renders stat-card snapshot grids, AAOIFI compliance rows with progress bars and PASS/FAIL badges, standard data tables with zebra striping, and inline SVG charts. Do not write the HTML from scratch; the helpers exist to ensure consistent design across all reports.
5. **Deliver.** Save to `<research_dir>/<TICKER>_research_report_<YYYY-MM-DD>.html` (date = as-of close), share the `computer://` link, and add a 2-3 sentence plain-language thesis. Close with the disclaimer.

## Report structure (equity)

Always these 10 sections in this order. Full template with example tables is in `references/report_structure.md`.

1. **Snapshot** (table) — price, market cap, shares out, 52W high/low, div yield TTM, beta, next earnings, sector/industry.
2. **Business Overview** — prose: what they do, model, revenue streams, moat. Segment/geo revenue breakdown table. Ownership structure (founder/insider %, recent insider txns). Recent strategic developments.
3. **Shariah Compliance** — four lenses stacked. Subsections 3a summary table, 3b AAOIFI ratios with real numbers, 3c PIF 4-step, 3d purification cents/share.
4. **Financial Fundamentals** — 3-yr historicals + forward estimate table with YoY %. Revenue + NPAT growth bar chart. Balance sheet & returns table. Prose on cash flow quality (FCF vs NI, CapEx intensity).
5. **Valuation** — multiples table (P/E TTM, Fwd P/E, PEG, EV/EBITDA, P/S, P/FCF, div yield) with sector median, 5-yr avg, signal. DCF base/bear/bull + reverse DCF.
6. **Analyst Coverage** — one row per analyst: Firm | Date | Rating | Prev Rating (↑↓=) | Target | Prev Target | Upside %. Sort newest first. Consensus + range at bottom. Analyst target range dot plot. Key commentary prose.
7. **Technical Analysis** — price chart with 50DMA + 200DMA. Indicators table (price, 50DMA, 200DMA, RSI, MACD, support, resistance, beta, weekly vol).
8. **Catalysts & Risks** — bulleted. Catalysts = specific events/data points. Risks = named mechanism of loss, not vague fears.
9. **Optional Deep-Dives** — judgment call per stock; use the checklist in `references/report_structure.md` (founder-led → insider detail + capital allocation; small cap → short interest; contested → auditor flags; etc.).
10. **Summary & Thesis** — one-paragraph bull, one-paragraph bear, 2-3 observable "what to watch next" data points, disclaimer.

For crypto reports, use the parallel 7-section structure in `references/crypto_template.md`.

## HTML build rules (the single most important section)

Use `build_report_html.py` exclusively — do not write raw HTML from scratch. The builder enforces the HalalInvest design system (navy `#0B3C5D` / amber `#C69214` palette, sidebar TOC, stat-card snapshot grid, compliance rows with progress bars) and keeps all reports visually consistent.

Import the builder by putting its folder on `sys.path` (the skill lives under `<repo-root>/skills`):

```python
import os, sys
root = os.getcwd()   # the agent runs from the repo root; the skill lives under <root>/skills
sys.path.insert(0, os.path.join(root, "skills", "investment-research-report", "scripts"))
from build_report_html import HtmlReportBuilder, svg_revenue_chart, svg_price_chart, svg_analyst_dotplot
```

If the import fails, Glob `**/investment-research-report/scripts/build_report_html.py` from the working directory and use the folder that contains it.

Key rules:

- **Pass `ticker` and `shariah_status` to the constructor.** They populate the header badge and TOC logo. `shariah_status` is `"halal"`, `"haram"`, or `"review"`.
- **Use `b.snapshot(dict)` for Section 1** — it renders as a responsive stat-card grid, not a flat table. Short values like `"$142.5M"` are fine; the grid handles layout automatically.
- **Use `b.aaoifi(rows)` for the AAOIFI screen** — it renders each ratio as a card row with a pass/fail badge and a visual progress bar showing the ratio vs. its threshold. Each row is `(ratio_name, threshold_str, actual_str, passed: bool)` — e.g. `("Interest-bearing debt / Market cap", "< 30%", "0.3%", True)`. `passed` must be a real bool: the string `"FAIL"` is truthy and would render a green PASS badge.
- **SVG charts are inserted with `b.html(svg_fn(...))`** — call `svg_revenue_chart(years, revenue, npat)`, `svg_price_chart(prices, dates, ma50, ma200)`, or `svg_analyst_dotplot(low, median, current, high)` and pass the returned string to `b.html()`. All three functions are importable from `build_report_html`.
- **No verification step needed.** The HTML file is the deliverable. Open it in any browser to review; no rendering pipeline required.
- **Output path:** `<research_dir>/<TICKER>_research_report_<YYYY-MM-DD>.html` (date = as-of close).

## Data sourcing rules

- **Cite actual figures.** Every number in a table traces to a source — filing, IR deck, screener. Put the source in the footer of the relevant table or a "Sources" appendix.
- **State when data isn't available** — "Analyst-level target data not publicly available for this small cap" is fine and expected. Silently omitting or making up granularity is not.
- **For the PIF screen, pull four consecutive quarters.** Steps 3 and 4 explicitly require a quarterly series; a single annual snapshot fails the methodology even if the annual number passes.
- **The PIF Israel / human rights overlay is unique to PIF** — AAOIFI and mainstream screeners do not apply it. Check operations, reporting, and flagged controversies separately (news search, company sustainability reports, HRW/Amnesty references if material).

See `references/data_sources.md` for the ordered source list by data point.

## Style

- Prose is concise and argument-driven, not padded. Narrative sections (Business Overview, analyst commentary, Summary) are prose; catalysts/risks are bullets; everything else is tables.
- No emojis. No flourishes. The report looks like a sellside note, not a blog post.
- Section numbering stays identical across every report (1-10 equity, 1-7 crypto) so a reader can jump to "section 3c" in any report and find the PIF screen.
- Close every report with: *"This is research, not financial advice. Do your own due diligence."*

## When not to use this skill

- The user is asking a one-off question about a stock ("is NVDA overvalued?") and doesn't want a report. Answer in chat.
- The user wants a spreadsheet model, not a narrative report. Use `xlsx` instead.
- The user is asking to *read* an existing research PDF. Use `pdf` instead.
