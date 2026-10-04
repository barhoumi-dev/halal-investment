# Shariah Quick Screen — for the Halal Flag

This is **not** a substitute for a full AAOIFI / PIF / Zoya / Musaffa screen. The point of this lean heuristic is to put a one-to-three-sentence flag at the top of the swing-trade setup so a halal-mandate reader knows immediately whether the trade is theirs to take.

If the user has a deeper prior screen on file (e.g., a previous investment-research-report), reuse that verdict and say so. If not, run this:

## The flag has three possible verdicts

- **Compliant** — passes the lean check on all three lenses below.
- **Non-compliant** — fails clearly on at least one lens.
- **Doubtful** — borderline on one or more lenses, or insufficient data.

## The three quick lenses

### Lens 1 — Core business (industry exposure)

Hard-no industries (any one fails the screen):
- Conventional banks, insurance, brokers (interest-based finance)
- Alcohol, tobacco, cannabis, pork
- Gambling, casinos, lottery
- Adult entertainment, online dating
- Defense / weapons (primary contractor)
- Cinema, music labels
- Hotels (depends on revenue mix from alcohol; flag as doubtful unless disclosed)

Crypto-mining names (BTDR, MARA, RIOT, CIFR, CLSK, IREN, HUT) are **doubtful at best** — classical scholars are split. Default to "Doubtful" and explain.

### Lens 2 — Debt (single ratio: total interest-bearing debt / market cap)

Threshold: < 30% (AAOIFI-style).

Pull total debt from the most recent stockanalysis.com snapshot or 10-Q. Pull market cap from the same source. Compute. If the ratio is:
- < 30%: pass
- 30–35%: borderline — flag as "borderline on AAOIFI debt ratio (X%)"
- > 35%: clear fail

### Lens 3 — Income mix (single ratio: interest income / total revenue)

Threshold: < 5% (Zoya-style; this is looser than the PIF 2.5% step but adequate for a quick flag).

For most operating companies, interest income is a tiny fraction of revenue (think Apple, Nvidia, Microsoft — all sub-1% even with large cash piles). For names with large treasuries or financial-services adjacency, this matters. If you can't find the figure quickly, default to a one-line note: "Interest income mix not publicly broken out at quick-look; if the company holds a material treasury, flag for full screen."

## Putting it together

Run all three lenses. If all three pass cleanly: **Compliant**.
If any one is a clear fail: **Non-compliant**, name the lens.
If anything is borderline or genuinely unknown: **Doubtful**, name the issue.

## Output format

The Halal flag is a single line, sometimes two for borderline / non-compliant:

**Compliant example:**
> *Halal flag:* **Compliant.** Hardware/software revenue, debt/MC ~5%, interest income <0.5% of revenue.

**Non-compliant example:**
> *Halal flag:* **Non-compliant.** Failed PIF Step 4 (interest expense ~9–11% of total expenses every quarter of FY25 due to ~$1B convertible note stack); business activity also doubtful on a strict reading (Bitcoin mining contested). Halal-mandate readers: this trade is not yours to take.

**Doubtful example:**
> *Halal flag:* **Doubtful.** Core business is conventional payment processing; AAOIFI debt ratio passes but income mix not broken out. Recommend full screen before sizing.

## When to escalate to the full screen

- Reader explicitly asks "is this halal?" — refer them to investment-research-report skill for the full AAOIFI + PIF.
- Result of this lean check is "Doubtful" and the reader is sizing more than a small position — escalate.
- Material change since the prior screen (large debt raise, M&A into a doubtful business) — re-screen.

## Why this is at the top, not the bottom

A halal-mandate reader who sees "Non-compliant" can stop reading immediately. That is more respectful of their time than burying the flag at the bottom. Non-mandate readers can read past the flag in two seconds — it costs them nothing.
