# Crypto Report Structure (7 sections)

Parallel to the equity template but adapted for tokens. Same HTML builder (`build_report_html.py`) and navy/amber palette; no verification step needed.

## 1. Project Snapshot

Table:

| Token | Category | Price | Market Cap | FDV | Circulating Supply | Max Supply | 24h Volume | Primary Exchanges |

- **Category**: L1 / L2 / DeFi (DEX, lending, perps, etc.) / Infra (oracles, bridges, DA layers) / Stablecoin / Meme / RWA / Other
- **FDV** = fully diluted valuation = price × max supply
- "Primary Exchanges" = top 3-5 by volume (Binance, Coinbase, Kraken, Uniswap, etc.)

## 2. Shariah Compliance

Apply PIF's 4-step methodology adapted for crypto.

### Step 1 — Utility vs speculation

Replace the "core business halal" check with a utility assessment:

| Dimension | Halal / Doubtful / Haram | Notes |
|---|---|---|
| Primary use case | | e.g. "Compute coordination (L1 settlement)" vs "Pure speculation / memetic" |
| Real economic activity | | Is there on-chain activity driven by real demand? |
| Project funding model | | ICO? Airdrop? VC allocation? Fair launch? |
| Incentive structure | | Does the tokenomics reward productive activity or pure holding/speculation? |

Most pure meme coins fail here. Utility tokens with real on-chain activity (ETH, SOL, Chainlink, Arbitrum) tend to pass.

### Step 2 — Staking / yield mechanics

Replace Step 2 (Israel overlay still applies — check the team's country of operation and any Israeli VC/foundation backers for names where that matters to the user) with a yield mechanics check:

| Yield type | Shariah character |
|---|---|
| Native staking (PoS validator rewards from block rewards + tx fees) | Generally acceptable — reward is for securing the network; scholars compare to mudarabah/musharakah |
| Restaking (EigenLayer, etc.) | Case-by-case — look at what's being secured and the reward mechanism |
| Lending protocols (Aave, Compound) | Typically riba-like in structure — avoid |
| LP / AMM yield | Case-by-case — fee-sharing (Uniswap v3) generally acceptable; impermanent loss is a gharar concern |
| Bridges, wrapped assets | Review structure; wrapped BTC on Ethereum usually OK, synthetic derivatives (sBTC, etc.) not |

### Step 3 & 4 — Interest ratios

For protocol-level tokens (i.e., tokens that represent ownership of a protocol that generates revenue), check protocol revenue vs any interest-like income/expense. Most L1/L2 tokens don't have interest-bearing balance sheets in the same sense, so this often collapses to "N/A — no balance sheet".

### Scholar consensus overlay

Quick note on where mainstream scholars stand on the specific token:
- AMJA (US): often conservative
- Mufti Taqi Usmani (Pakistan): generally skeptical of pure crypto
- Shaikh Yusuf DeLorenzo, Amanie Advisors: more permissive for utility tokens
- Recent fatwas on specific tokens (ETH, BTC, SOL) — cite if available

Rating: **Comfortable / Uncomfortable / Discuss with scholar** — the last bucket exists because crypto lacks AAOIFI-level settled methodology.

## 3. On-Chain Fundamentals

Table with 90-day trend arrows:

| Metric | Current | 30d avg | 90d avg | Trend |
|---|---|---|---|---|
| Active addresses (daily) | | | | ↑ / → / ↓ |
| Transaction volume (USD) | | | | |
| Fees (USD, daily) | | | | |
| Staking ratio (% of supply staked) | | | | (PoS only) |
| TVL (if DeFi) | | | | |
| Developer activity (commits/mo) | | | | |

## 4. Token Distribution & Unlocks

**Always include this.** Unlock schedules are where most crypto writeups go stale.

| Allocation | % of Supply | Unlock Schedule | Notes |
|---|---|---|---|
| Team | | e.g. "4yr linear, 1yr cliff (to Jun 2026)" | |
| Investors | | | VCs / seed / private |
| Foundation / Treasury | | | |
| Public / circulating | | | |
| Airdrops / future incentives | | | |

Add a mini-table of the **next 90 days of unlocks** with dollar value at current price — this is the near-term sell pressure map.

Also: **top-wallet concentration** — % of supply held by top 10 / top 100 non-exchange wallets (use Etherscan/Solscan/equivalent).

## 5. Valuation & Market Metrics

| Metric | Value | Peer median (category) | Signal |
|---|---|---|---|
| Mcap / FDV | | | Lower = more dilution ahead |
| NVT (Market Cap / daily tx volume, USD) | | | Like a P/E for networks |
| MVRV (Market Value / Realized Value) | | | Cycle-position indicator |
| P/F (Mcap / annualized fees) | | | Revenue-like multiple |
| P/S (Mcap / annualized revenue, if applicable) | | | DeFi protocols with fee-sharing |

**Peer comp within category** — 2-3 closest peers with the same metrics. Categorize before comparing (don't compare SOL to UNI).

## 6. Technicals & Cycle Context

Same as equity plus:
- **BTC dominance** (% of total crypto mcap in BTC) — where are we in the cycle?
- **Funding rates** (for perpetual futures on major exchanges) — positive = leveraged long crowded; negative = crowded short
- **Halving cycle position** — weeks since / until next BTC halving. Historical pattern: BTC tops ~12-18 months post-halving.

## 7. Catalysts & Risks

Same structure as equity — specific events and named mechanisms.

Crypto-specific categories to consider:
- **Protocol upgrades** with specific mainnet date (e.g., "Pectra upgrade on Ethereum — targeted Q2 2026")
- **Exchange listings** (Coinbase, Binance, Upbit spot listings move price)
- **Unlock events** in next 90 days (covered in section 4)
- **Smart contract risk** — audits, recent exploits, bug bounty size
- **Regulatory risk** — named jurisdiction (SEC action, MiCA enforcement, Korean regulator stance)
- **Narrative risk** — for category-dependent names (DePIN cooling, AI narrative fading)

## Disclaimer

Same as equity: *"This is research, not financial advice. Do your own due diligence."*
