# PIF Shariah Screen — 4-Step Methodology

This is the methodology transmitted directly from Adel @ PIF (3/26/26). It is stricter than AAOIFI and is the standard the user wants applied.

## How PIF differs from AAOIFI / Musaffa / Zoya

| Dimension | AAOIFI (Zoya/Musaffa use this) | PIF |
|---|---|---|
| Leverage metric | Debt / Market Cap < 30% | Not used; replaced with interest-income and interest-expense P&L tests |
| Haram revenue threshold | 5% | 2.5% — stricter |
| Time frame | Single snapshot (latest annual) | **Four consecutive quarters** must all pass |
| Geopolitical overlay | None | Israel presence / human rights check (Step 2) |
| Core business check | Loose (industry class) | Explicit industry checklist (Step 1) |

A stock can pass AAOIFI cleanly and still be rated "Uncomfortable" under PIF if, say, a single quarter's interest income spiked above 2.5% of revenue.

## The four steps

All four must pass. One fail → **Uncomfortable**.

### Step 1 — Core business is halal and serves halal purposes

Check exposure to each excluded industry. Mark Y, N, or Partial. "Partial" means material but not the core business (e.g., a tech platform where <10% of revenue is from advertising to industries listed here; or a retailer with a music streaming subsidiary).

Industries to check (use the full list in the report):
Alcohol • Tobacco • Cannabis • Pork products • Conventional financial services • Defense / weapons • Gambling / casinos • Music • Hotels • Cinema • Adult entertainment • Online dating

**Any "Y" fails Step 1.** "Partial" is a judgment call — look at how material it is, whether it's growing or shrinking, and whether the company could divest. Default is to fail Partial unless <2% of revenue and clearly non-core.

### Step 2 — No material Israel presence or human rights violations

Check:
- Company operations in Israel (offices, factories, JVs) — material means revenue, employees, or strategic value
- Reporting — does the company publicly disclose Israeli operations? (opacity can be a flag by itself)
- Flagged controversies — news search for "<company> human rights", check HRW / Amnesty International / UN reports if material, BDS movement lists

"Material" is a judgment call. Small sales-office presence with no operational footprint is typically not material. Large R&D campuses, strategic suppliers, or defense contracts with the Israeli state are material. Err on the side of flagging — the user would rather see a flag explained than have it silently omitted.

### Step 3 — Interest income ≤ 2.5% of total revenue, four consecutive quarters

Pull the most recent four quarters of data from 10-Q / 10-K filings:

| Quarter | Interest Income (A) | Total Revenue (B) | Ratio A/B | Pass? |
|---|---|---|---|---|
| Q(t-3) | | | | |
| Q(t-2) | | | | |
| Q(t-1) | | | | |
| Q(t) | | | | |

Interest income is typically in the "Other income (expense), net" footnote. Some companies disclose it on the income statement directly (usually those with large cash piles — NVDA, MSFT, AAPL, GOOGL).

**If any quarter's ratio > 2.5%, Step 3 fails** — even if the average across four quarters is below 2.5%.

### Step 4 — Interest expense ≤ 2.5% of total expenses, four consecutive quarters

| Quarter | Interest Expense (A) | Total Expenses (B) | Ratio A/B | Pass? |
|---|---|---|---|---|

Total expenses = COGS + Opex + Interest expense + Other expense. Effectively all expenses below the revenue line except tax.

Interest expense is typically in the "Other income (expense), net" footnote or on a separate line on the income statement for companies with material debt.

Same rule: any single quarter over 2.5% → **fails**.

## Rating

- **Comfortable** — all four steps pass across four consecutive quarters.
- **Uncomfortable** — any step fails, OR any single quarter in Steps 3/4 breaches 2.5%.

### One documented exception

Companies clearly in transition — pre-revenue or early-stage ramping production (e.g., a biotech pre-FDA approval, a manufacturer in pre-commercial scale-up) — may be reviewed contextually rather than auto-flagged. In that case:
- Explicitly name the exception in the report
- Note why the name is "in transition" (no revenue, losses, ramp phase)
- Flag that the screen should be re-run once commercial revenue is normalized

Do not invoke this exception for mature companies having a single bad quarter — that's a normal fail.

## Presentation in the report

Section 3c must show:
- The industry exposure table (Step 1) with the full 12-row checklist
- A single paragraph on Step 2 with sources
- A 4-row table for Step 3 with actual quarterly numbers
- A 4-row table for Step 4 with actual quarterly numbers
- The final "Comfortable / Uncomfortable" rating with a one-sentence reason

Always cite the filings by date (e.g., "10-Q filed 2026-02-21 for quarter ended 2026-01-26").
