# Data Sources — Where to Fetch Each Data Point

Use WebSearch first to locate the right page, then WebFetch to pull content. Prefer primary sources (SEC filings, IR pages, exchange data) over secondary aggregators when there's any chance of divergence. Always show the source in the report.

## Equity data

| Data point | Primary source | Backup | Notes |
|---|---|---|---|
| Current price, market cap, shares out, 52W H/L, beta, div yield | `stockanalysis.com/stocks/<ticker>/` | `finance.yahoo.com/quote/<TICKER>` | Stockanalysis tends to be the cleanest layout; Yahoo as fallback |
| Next earnings date | `stockanalysis.com/stocks/<ticker>/earnings/` | Company IR page | IR page most authoritative |
| Sector / industry | Stockanalysis snapshot | Company 10-K (ITEM 1 Business) | |
| 10-K, 10-Q filings | `sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=<ticker>` | Company IR page "SEC Filings" | Use EDGAR full-text search when you need a specific number |
| Segment revenue | 10-K Note on Segments | Latest investor day deck | |
| Historical financials (3-yr) | `stockanalysis.com/stocks/<ticker>/financials/` | `macrotrends.net/stocks/charts/<ticker>/…` | Stockanalysis is more consistent; Macrotrends is deeper on history |
| Forward estimates (revenue, EPS) | Stockanalysis Forecast tab | Yahoo Analysis tab | Both show consensus |
| Analyst targets & ratings | `stockanalysis.com/stocks/<ticker>/ratings/` | Yahoo Analysis tab; MarketBeat | For analyst-level granularity, Stockanalysis ratings page or TipRanks (often paywalled — fall back to Yahoo consensus) |
| Insider transactions | SEC Form 4 filings via EDGAR | `openinsider.com/screener?s=<TICKER>` | OpenInsider is readable; EDGAR is authoritative |
| Institutional holdings | `stockanalysis.com/stocks/<ticker>/institutional/` | 13F filings on EDGAR | |
| Short interest | `fintel.io/ss/us/<ticker>` or Nasdaq short interest page | | For small caps that don't show up elsewhere |
| Price chart + moving averages | `finance.yahoo.com/quote/<TICKER>/history` for raw data | Stockanalysis chart | Pull daily closes for ~260 trading days to compute 50DMA and 200DMA |
| RSI, MACD read | Can compute from daily closes | TradingView / StockCharts for visual | |

## Shariah screening

| Check | Source |
|---|---|
| Zoya rating | `zoya.finance` (free tier has per-stock lookup) — search for the ticker |
| Musaffa rating | `musaffa.com/stock/<ticker>` or search the app |
| AAOIFI inputs | Pull from 10-K directly — see `aaoifi_screen.md` for each input |
| PIF Steps 3 & 4 quarterly data | Pull from last four 10-Q / 10-K filings — see `pif_screen.md` |
| Israel operations / human rights flags | News search ("<company> Israel", "<company> human rights"), company sustainability/ESG report, `hrw.org` or `amnesty.org` if material, BDS movement lists if relevant |

## Crypto

| Data point | Primary source | Backup |
|---|---|---|
| Price, market cap, FDV, circulating/max supply, 24h volume | `coingecko.com/en/coins/<slug>` | `coinmarketcap.com/currencies/<slug>` |
| On-chain: active addresses, tx volume, fees | `glassnode.com` (requires account for deeper metrics) | `tokenterminal.com` / project's explorer |
| TVL (DeFi) | `defillama.com/protocol/<slug>` | |
| Token distribution & vesting | Project's tokenomics page | `cryptorank.io/price/<slug>/vesting` |
| Developer activity | `cryptomiso.com` or `santiment.net` | GitHub directly |
| BTC dominance, funding rates | `coinglass.com`, `tradingview.com/symbols/BTC.D/` | |
| Halving cycle context | `bitcoinmagazine.com` / any halving tracker | |

## General rules when sourcing

- **Prefer a filing over a screener** when the number is load-bearing (AAOIFI ratios, PIF quarterly ratios, debt figures). Screeners can be stale.
- **Show your source** in a small footer line under each table or in a Sources appendix. Don't hide it.
- **When a number conflicts across sources**, pick the filing if possible, note the discrepancy, and say why you chose what you chose.
- **When a number truly isn't available** (small caps often have no analyst coverage, for example), say so explicitly. "Not publicly disclosed" is a valid answer; a fabricated precise number is not.
- **WebFetch returns summarized content.** For dense financial pages, use a specific prompt: "Extract the revenue, gross profit, EBIT, and net income for the last 3 fiscal years plus the most recent quarter. Return as a table."
