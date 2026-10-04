# AGENT.md

This file provides guidance to AI coding agents (Claude Code, Pi, or similar) when working with code in this repository.

## What this repo is

This directory is **the user's "Investment folder"** — both the source of the `halal-investing` plugin and the delivery folder where its generated HTML reports and decks accumulate. It is not a typical software project: there is no package manifest, no build system, no tests.

The repo root is also the **`halal-investing` plugin** — distributed as a Claude Code plugin (manifest `.claude-plugin/plugin.json`, local marketplace `.claude-plugin/marketplace.json`, user docs in `README.md`), with the skills also runnable by other agents directly from this folder. Its two model-invoked skills live under `skills/`:

- `skills/investment-research-report/` — produces a 10-section equity (or 7-section crypto) research **HTML report** via `scripts/build_report_html.py` (self-contained, no external deps). The legacy `scripts/build_report.py` (ReportLab PDF) is preserved for reference.
- `skills/swing-trade-setup/` — produces a 6-slide self-contained **HTML deck** (inline SVG, arrow-key navigable) for a 2-to-8-week swing trade via `scripts/build_slides.py`.

Each skill folder contains `SKILL.md` (the prompt that drives the agent), `references/*.md` (templates + methodology), and `scripts/*.py` (the deterministic builders). The matching `.skill` zip archives in `cowork-skills/` are **portable, version-pinned distributables** — useful for sharing or re-installing, but the copies under `skills/` are the live ones the plugin ships.

Other plugin components:
- `skills/research/`, `skills/swing/` — thin slash-command entry points (`/halal-investing:research <TICKER>`, `/halal-investing:swing <TICKER>`), `disable-model-invocation: true` so they never compete with the two skills above.
- `agents/shariah-screener.md` — runs PIF 4-step + AAOIFI on four quarters of filings; the research skill dispatches it for Section 3.
- `examples/research-reports/`, `examples/swing-setups/` — curated, committed sample report/deck pairs (TSM, IREN), mirroring the real output folders. The root `research-reports/` and `swing-setups/` are gitignored; copy a file into the matching `examples/` subfolder deliberately to publish it.
- `examples/halal-investing.local.md` — settings template (`research_dir`, `swing_dir`, `halal_mandate`, `pif_strict`, `default_horizon_weeks`). Live copy goes in `.claude/halal-investing.local.md` (gitignored).

## Where deliverables go

Per-ticker outputs are organized into two subdirectories — write new artifacts to the matching folder, **not** to the repo root:

- `swing-setups/` — every `<TICKER>_swing_setup_<YYYY-MM-DD>.html` produced by the swing-trade-setup skill goes here.
- `research-reports/` — every `<TICKER>_research_report_<YYYY-MM-DD>.html` produced by the investment-research-report skill goes here.

Each skill's `SKILL.md` says generically "write to the user's Investment folder" — in this workspace, that resolves to the appropriate subfolder above. When you call the builders, set `--out` (or `b.build(...)`) to the subfolder path:

```bash
# swing
python skills/swing-trade-setup/scripts/build_slides.py \
    --spec /tmp/setup_spec.json \
    --out "swing-setups/<TICKER>_swing_setup_<YYYY-MM-DD>.html"

# research (Python API)
b.build("research-reports/<TICKER>_research_report_<YYYY-MM-DD>.html")
# No verify step needed — open the HTML in any browser to review
```

Artifacts left at the repo root are intentionally **not** per-ticker: `AGENT.md`, `README.md`, the plugin dirs (`.claude-plugin/`, `skills/`, `agents/`, `examples/`), `cowork-skills/`, and the two skill-tooling HTMLs (`swing-trade-setup-eval-viewer.html`, `swing-trade-setup-results-slides.html` — these are skill-development/evaluation aids, not deliverables for a specific ticker).

## Working on the skills

Edit files directly under `skills/<skill-name>/`. Inside skills and agents, reference bundled files relative to the agent's working directory (the repo root), e.g. `skills/<skill-name>/...` — the skills run from this folder with cwd-relative paths, so any agent launched from the repo root resolves them correctly. The internal layout each skill expects is fixed:

```
skills/<skill-name>/
  SKILL.md                  # frontmatter + workflow prompt
  references/*.md           # templates the SKILL.md cites by relative path
  scripts/*.py              # deterministic builders SKILL.md invokes
```

Do not rename `references/` or `scripts/` — `SKILL.md` references them by exact path.

Distribution (Claude Code) is via GitHub (`/plugin marketplace add barhoumi-dev/halal-investment`), which clones the repo, so `.gitignore` keeps deliverables out. For local development use `claude --plugin-dir .` (reads in place). **Never** `/plugin marketplace add .` on this folder: a local-path marketplace copies the whole directory into `~/.claude/plugins/cache`, ignoring `.gitignore` — that's ~155 MB including `halal-investment-site/`, every report, and `.claude/settings.local.json`. After a release, bump `version` in `plugin.json`.

Other agents load the same skills directly from the repo root: `.pi/settings.json` points its `skills` resource at the `skills/` folder. Because the skills use cwd-relative paths, any agent launched from the repo root works without plugin installation.

Do **not** recreate `.claude/skills/` or `.pi/skills/` — a project-local copy would load alongside the repo-root `skills/` folder and double-trigger. Point agents at the repo-root `skills/` folder instead (`.pi/settings.json` already does this).

To re-pack a skill into a portable `.skill` archive (archives contain a top-level `<skill-name>/` folder):

```bash
cd skills
zip -r ../cowork-skills/investment-research-report.skill investment-research-report -x '*__pycache__*'
zip -r ../cowork-skills/swing-trade-setup.skill swing-trade-setup -x '*__pycache__*'
```

## Running the builders

Both builders are standalone Python scripts. There is no shared dependency manifest; install per-script as needed.

### investment-research-report — `scripts/build_report_html.py`

Library-style API (not a CLI), pure stdlib. Imported by the agent inside the skill workflow:

```python
import sys; sys.path.insert(0, "skills/investment-research-report/scripts")
from build_report_html import HtmlReportBuilder, svg_revenue_chart, svg_price_chart, svg_analyst_dotplot

b = HtmlReportBuilder("NVIDIA Corp (NVDA)", subtitle="As of 2026-04-21", ticker="NVDA", shariah_status="halal")
b.section("1. Snapshot")
b.snapshot({...})
# ... sections 2–10 ...
b.disclaimer()
b.build("research-reports/NVDA_research_report_2026-04-21.html")
```

The legacy `scripts/build_report.py` (ReportLab PDF + `verify_pdf()`) is kept for reference only; do not use it for new reports.

### swing-trade-setup — `scripts/build_slides.py`

CLI: takes a JSON spec (schema in `references/output_template.md`) and emits a single self-contained HTML file.

```bash
python skills/swing-trade-setup/scripts/build_slides.py \
    --spec /tmp/setup_spec.json \
    --out "swing-setups/<TICKER>_swing_setup_<YYYY-MM-DD>.html"
```

No external runtime deps — pure stdlib (`argparse`, `html`, `json`). All graphics are inline SVG generated in-script. The output renders offline, no CDN.

`scripts/make_levels_chart.py` is a legacy standalone PNG chart helper kept for compatibility; the slide deck embeds its own SVG version.

## Architecture: how the two skills share design DNA

Read these together — they are deliberately consistent so a reader can flip between a research report and a swing deck on the same ticker without visual whiplash.

- **Shared palette**: navy `#0B3C5D` for headers/structure, amber `#C69214` for accents, `#2E7D32` / `#C62828` for pass/fail. Both builders hardcode the same hexes.
- **Shared Shariah lens**: `swing-trade-setup` uses a lean 3-lens quick screen (`shariah_quick_screen.md`); `investment-research-report` uses the full 4-lens stack (Zoya + Musaffa + AAOIFI + PIF 4-step) per `aaoifi_screen.md` and `pif_screen.md`. **The swing skill should reuse the deeper verdict if a prior research-report HTML on the same ticker exists in this folder** (this is explicit in `swing-trade-setup/SKILL.md` line 105–107).
- **Shared sourcing priority**: both `references/data_sources.md` files lead with `stockanalysis.com` for snapshot data, falling back to Yahoo Finance, with `stockinvest.us` for technicals on the swing side. Primary filings (SEC EDGAR, IR pages) outrank screeners whenever a number is load-bearing.
- **Brief chat reply, file-based deliverable**: both skills explicitly forbid pasting tables into chat. The chat response is verdict + 2-3 sentence rationale + `computer://` link. The deliverable IS the file.

## Critical correctness rules (these are the bug-prone spots)

These are the failure modes the user has called out — each one is enforced inside the skill's prompts and builder code. Don't relax them.

1. **HTML report uses `build_report_html.py`, not `build_report.py`.** The HTML builder has no ReportLab overflow issues — word-wrap is handled by the browser. Never write raw HTML for the report from scratch; use the builder helpers.
2. **Pass `ticker` and `shariah_status` to `HtmlReportBuilder(...)`.** These populate the header badge and the sidebar logo. Missing them produces a blank header.
3. **PIF Shariah Step 3 and Step 4 require four consecutive quarters.** A single annual snapshot fails the methodology even if the annual ratio passes — any one quarter > 2.5% fails the step. Always pull 4× 10-Q (or 10-K + 3× 10-Q) for these inputs.
4. **PIF haram-revenue threshold is 2.5%, not AAOIFI's 5%.** A name can pass AAOIFI cleanly and still fail PIF. Don't conflate them — the report shows both.
5. **PIF Step 2 (Israel presence / human rights) is unique to PIF.** Mainstream screeners do not apply it. Run a separate news/sustainability-report check.
6. **No verification pipeline for HTML reports.** The HTML is the deliverable — open it in a browser to verify. No `verify_pdf()` call needed.
7. **For swing setups, never fabricate precise levels.** Zones (`"$197–$200"`) are correct; fake-precise pinpoints (`$198.37`) are not. If a number genuinely isn't available, the JSON spec accepts `null` and the slide renders `"n/d"`.
8. **If a binary catalyst (earnings, FDA, regulator, M&A close) sits inside the 2-to-8-week swing horizon, the trade is an event bet, not a technical trade.** The earnings-window flag on slide 4 fires red and the position-sizing field defaults to "half-size" or "WAIT until print". Don't override this silently.
9. **Halal-mandate non-compliance overrides BUY into AVOID** in the swing verdict — say so explicitly when it bites.
10. **Disclaimer wording is fixed.** Research report: *"This is research, not financial advice. Do your own due diligence."* Swing deck: *"Technical read, not financial advice — do your own due diligence."* The builders insert these automatically — do not duplicate.

## Output naming conventions (so files sort cleanly)

- Research HTML reports: `research-reports/<TICKER>_research_report_<YYYY-MM-DD>.html` (date = as-of close; e.g., `research-reports/NVDA_research_report_2026-04-21.html`, `research-reports/BTDR_research_report_2026-10-04.html`).
- Swing decks: `swing-setups/<TICKER>_swing_setup_<YYYY-MM-DD>.html` (date is the as-of close).

## Playwright MCP screenshots

All screenshots taken via the Playwright MCP tool must use a `filename` inside the `halal-investment-site/.playwright-mcp/` directory (e.g., `filename: ".playwright-mcp/my-screenshot.png"`). Never save Playwright screenshots to the project root or any other location.
