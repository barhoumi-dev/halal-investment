# halal-investing

A Claude Code plugin for halal-conscious investing: research reports, swing-trade setup decks, and a filing-backed Shariah screening agent.

## Components

| Type | Name | Trigger |
|---|---|---|
| Skill (auto) | `investment-research-report` | "research report on NVDA", "equity research", "halal screen", "DCF on…" |
| Skill (auto) | `swing-trade-setup` | "should I buy TSLA", "levels on AMD", "swing setup on PLTR" |
| Skill (slash) | `/halal-investing:research <TICKER> [crypto]` | Explicit report request |
| Skill (slash) | `/halal-investing:swing <TICKER> [weeks]` | Explicit swing deck request |
| Agent | `shariah-screener` | Dispatched by the research skill for Section 3, or for "is X halal?" |

Outputs are self-contained HTML files (inline CSS + SVG) written into the current project. Swing decks make no network requests; research reports render offline but load Google Fonts when online.

## Examples

Sample output in `examples/`, laid out exactly as the plugin writes it (download and open in a browser) — the same ticker as a full report and a swing deck:

| Ticker | Research report | Swing deck |
|---|---|---|
| TSM | `research-reports/TSM_research_report.html` | `swing-setups/TSM_swing_setup_2026-06-15.html` |
| IREN | `research-reports/IREN_research_report.html` | `swing-setups/IREN_swing_setup_2026-06-15.html` |

Samples are illustrative snapshots, not current recommendations.

## Install

From GitHub (the repo doubles as its own marketplace):

```
/plugin marketplace add barhoumi-dev/halal-investment
/plugin install halal-investing@barhoumi-dev
```

For local development, load the working copy in place with `claude --plugin-dir .` — don't `marketplace add` a local path: that copies the whole folder (ignoring `.gitignore`) into the plugin cache.

Prerequisites: Python 3.10+ on `PATH`. The builders are pure stdlib; the legacy PDF builder (`build_report.py`) additionally needs `reportlab` and `matplotlib`.

## Settings

Optional. Copy `examples/halal-investing.local.md` to `<project>/.claude/halal-investing.local.md`:

| Field | Default | Purpose |
|---|---|---|
| `research_dir` | `research-reports` | Report output folder |
| `swing_dir` | `swing-setups` | Deck output folder |
| `halal_mandate` | `true` | Non-compliance overrides BUY → AVOID in swing decks |
| `pif_strict` | `true` | Require PIF "Comfortable" for a `halal` status |
| `default_horizon_weeks` | `2-8` | Swing horizon |

Settings are read at the start of each run; no restart needed. Keep the file out of git (`.claude/*.local.md`).

## Layout

```
.claude-plugin/plugin.json        manifest
.claude-plugin/marketplace.json   local marketplace entry
agents/shariah-screener.md
skills/investment-research-report/  SKILL.md, references/, scripts/build_report_html.py
skills/swing-trade-setup/           SKILL.md, references/, scripts/build_slides.py
skills/research/  skills/swing/     slash-command entry points
examples/halal-investing.local.md   settings template
examples/research-reports/          sample reports (mirrors research_dir)
examples/swing-setups/              sample decks (mirrors swing_dir)
```

Disclaimer: research and technical reads only, not financial advice.
