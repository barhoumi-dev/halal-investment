# AAOIFI Financial Ratio Screen

AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions) sets the mainstream quantitative standard used by Zoya, Musaffa, S&P Shariah, and most retail screeners. Its Shariah Standard No. 21 governs equity screening.

You should calculate these ratios yourself from filings rather than just trusting a screener's final rating, for two reasons:
1. Screeners sometimes lag by a reporting cycle
2. The user's standard is to show the raw numbers and the math

## The four ratios

All four must pass. If any fails, the name is non-compliant under AAOIFI.

| # | Ratio | Threshold | What it captures |
|---|-------|-----------|------------------|
| 1 | Non-permissible (haram) revenue / Total revenue | < 5% | Revenue from alcohol, pork, gambling, conventional finance, etc. |
| 2 | Interest-bearing debt / Market Cap | < 30% | Leverage test — how much of the equity value is propped up by interest-bearing borrowing |
| 3 | Interest-bearing securities / Market Cap | < 30% | Asset-side riba exposure — bonds, money market holdings, etc. |
| 4 | Accounts Receivable / Market Cap | < 49% | Liquidity / monetary asset test (a diluted form of the classical "cash + receivables < 49% of assets" rule) |

## Where to get each input

| Input | Source | Line |
|-------|--------|------|
| Total revenue (TTM) | 10-K / 10-Q | Top of income statement |
| Non-permissible revenue | Segment disclosures, 10-K risk factors, investor day slides | Often requires estimate if not broken out — be conservative |
| Interest-bearing debt | 10-K balance sheet | Short-term + long-term debt (not operating leases under ASC 842 — those aren't interest-bearing in the AAOIFI sense; some scholars include, the conservative default is to exclude operating-lease liabilities) |
| Interest-bearing securities | 10-K / 10-Q investments footnote | Available-for-sale debt securities, held-to-maturity debt, short-term treasuries, money market funds, commercial paper |
| Accounts receivable | 10-Q balance sheet | AR, net of allowance |
| Market cap | Yahoo/Stockanalysis | Shares outstanding × current price — use **current**, not average |

## Denominator choice

AAOIFI allows either market cap or total assets as denominator for ratios 2, 3, 4. The **market cap** version is stricter (market cap moves with sentiment, total assets don't), which is why most modern implementations use it. Stay with market cap unless there's a specific reason.

## Worked example (illustrative, NVDA-style)

Suppose:
- Total revenue TTM: $130.5B
- Non-permissible revenue: ~0 (no meaningful haram exposure)
- Interest-bearing debt: $11.0B (short-term $1B + long-term $10B)
- Interest-bearing securities: $39.0B (treasuries + corp debt in cash & investments)
- Accounts receivable: $23.1B
- Market cap: $3,500B

Ratios:
1. 0 / $130.5B = **0.0%** ✓ (< 5%)
2. $11.0B / $3,500B = **0.3%** ✓ (< 30%)
3. $39.0B / $3,500B = **1.1%** ✓ (< 30%)
4. $23.1B / $3,500B = **0.7%** ✓ (< 49%)

→ **Pass** all four. AAOIFI-compliant.

## Presentation

In the report, show the **input numbers** in a short paragraph under the ratio table, then the calculated ratios. The reader should be able to audit your math without opening the filing.

## Edge cases to flag explicitly

- **Interest income on cash** — not a ratio failure but relevant for **purification** (section 3d), together with any non-permissible revenue. Always disclose.
- **Mixed-use revenue** — e.g., Apple Services includes Apple Music. Estimate pro-rata or flag as "Partial" in the PIF industry checklist.
- **M&A target recently closed** — ratios may not yet reflect the combined balance sheet. Note pro-forma if material.
- **Share buybacks mid-quarter** — market cap uses current shares, but balance sheet items are at period end. Small divergence; flag only if >5%.
