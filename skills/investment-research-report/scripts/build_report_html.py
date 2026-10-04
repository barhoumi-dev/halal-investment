"""
Self-contained HTML investment research report builder.
Produces a styled, responsive HTML file using the HalalInvest design system
adapted for the navy/amber palette.

No external dependencies — pure Python stdlib only.

Usage:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from build_report_html import HtmlReportBuilder, svg_revenue_chart, svg_analyst_dotplot, svg_price_chart

    b = HtmlReportBuilder("NVIDIA Corp (NVDA)", subtitle="As of 2026-05-10",
                          ticker="NVDA", shariah_status="halal")
    b.section("1. Snapshot")
    b.snapshot({"Price": "$142.50", "Market Cap": "$3.5T", ...})
    b.section("2. Business Overview")
    b.prose("NVIDIA designs...")
    b.bullets(["item 1", "item 2"])
    b.section("4. Financial Fundamentals")
    b.html(svg_revenue_chart(["FY22","FY23","FY24"], [26.9,44.9,60.9], [4.37,9.76,16.7]))
    b.fundamentals(["Line","FY22","FY23","FY24","YoY%"], [...])
    b.section("6. Analyst Coverage")
    b.html(svg_analyst_dotplot(120, 175, 142, 220))
    b.analysts([...])
    b.disclaimer()
    b.build("research-reports/NVDA_research_report_2026-05-10.html")
"""
from __future__ import annotations

import html as _html_lib
import math
import os
import re
from typing import Iterable

# ---------------------------------------------------------------------------
# Palette — Verdant theme (forest green / bronze, warm-editorial)
# ---------------------------------------------------------------------------
NAVY = "#0f3d2e"       # --primary (forest green; name kept for SVG chart compat)
AMBER = "#b8835a"      # --accent  (warm bronze)
PASS_GREEN = "#2d6b4f" # --halal
FAIL_RED = "#b54a3a"   # --haram


def _e(text) -> str:
    """HTML-escape a value."""
    if text is None:
        return "—"
    return _html_lib.escape(str(text))


# ---------------------------------------------------------------------------
# CSS — HalalInvest Verdant design system (light-default, warm editorial)
# ---------------------------------------------------------------------------
_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Verdant light (default) ── */
:root {
  --primary:        #0f3d2e;
  --primary-fg:     #faf6eb;
  --accent:         #b8835a;

  --halal:          #2d6b4f;
  --halal-bg:       rgba(45,107,79,0.08);
  --haram:          #b54a3a;
  --haram-bg:       rgba(181,74,58,0.08);
  --review:         #b8835a;
  --review-bg:      rgba(184,131,90,0.10);

  --bg:             #f7f4ec;
  --bg-soft:        #efeadd;
  --panel:          #fffdf7;
  --panel-2:        #faf6eb;

  --fg:             #15211b;
  --fg-soft:        #3c4a40;
  --fg-muted:       #7a7368;
  --fg-faint:       #a89e8c;

  --border:         rgba(15,33,27,0.10);
  --border-strong:  rgba(15,33,27,0.18);
  --grid-line:      rgba(15,33,27,0.05);

  --shadow-sm: 0 1px 2px rgba(15,33,27,.04), 0 1px 0 rgba(255,255,255,.6) inset;
  --shadow-md: 0 1px 3px rgba(15,33,27,.06), 0 8px 24px rgba(15,33,27,.05);

  --font-display: "Instrument Serif","Source Serif 4",Georgia,serif;
  --font-body:    "Geist",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --font-mono:    "Geist Mono",ui-monospace,"SF Mono",Menlo,monospace;
  --display-tracking: -0.01em;

  --sidebar-w: 220px;
  --content-max: 960px;
}

/* ── Verdant dark ── */
@media (prefers-color-scheme: dark) {
  :root {
    --primary:       #d8b893;
    --primary-fg:    #0e1612;
    --accent:        #d8b893;

    --bg:            #0e1612;
    --bg-soft:       #131c17;
    --panel:         #16201a;
    --panel-2:       #1b261f;
    --fg:            #ece6d4;
    --fg-soft:       #c9c2af;
    --fg-muted:      #8c8676;
    --fg-faint:      #5e5b50;
    --border:        rgba(236,230,212,0.08);
    --border-strong: rgba(236,230,212,0.16);
    --grid-line:     rgba(236,230,212,0.04);
    --shadow-sm:     0 1px 2px rgba(0,0,0,.4);
    --shadow-md:     0 1px 3px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.3);
    --halal:         #76c79b;
    --halal-bg:      rgba(118,199,155,0.10);
    --haram:         #ec8474;
    --haram-bg:      rgba(236,132,116,0.10);
    --review:        #d8b893;
    --review-bg:     rgba(216,184,147,0.10);
  }
}

html { scroll-behavior: smooth; font-size: 15px; }
body {
  font-family: var(--font-body);
  color: var(--fg);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  line-height: 1.55;
}

/* ── App shell ── */
.report-app {
  display: grid;
  grid-template-columns: var(--sidebar-w) 1fr;
  min-height: 100vh;
}
@media (max-width: 800px) {
  .report-app { grid-template-columns: 1fr; }
  .report-sidebar { display: none; }
}

/* ── Sidebar ── */
.report-sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  padding: 22px 14px 24px;
  background: var(--panel);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
}
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  padding: 0 4px;
}
.sidebar-logomark { flex-shrink: 0; }
.sidebar-wordmark {
  font-family: var(--font-display);
  font-size: 17px;
  letter-spacing: var(--display-tracking);
  line-height: 1;
  color: var(--fg);
  font-weight: 400;
}
.sidebar-wordmark em { font-style: normal; color: var(--accent); }
.toc-label {
  font-size: 10px;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--fg-faint);
  font-weight: 600;
  padding: 0 10px 8px;
}
.toc-item {
  display: block;
  padding: 7px 10px;
  border-radius: 8px;
  color: var(--fg-muted);
  font-size: 12.5px;
  font-weight: 500;
  text-decoration: none;
  border: 0;
  border-left: 2px solid transparent;
  transition: background .15s, color .15s, border-color .15s;
  margin-bottom: 1px;
  cursor: pointer;
  background: transparent;
  width: 100%;
  text-align: left;
  font-family: inherit;
}
.toc-item:hover { background: var(--bg-soft); color: var(--fg); }
.toc-item.active {
  background: var(--bg-soft);
  color: var(--primary);
  border-left-color: var(--accent);
  font-weight: 600;
}

/* ── Main ── */
.report-main {
  min-width: 0;
  padding: 48px 56px 80px;
}
@media (max-width: 960px) { .report-main { padding: 32px 24px 64px; } }
@media (max-width: 600px) { .report-main { padding: 20px 16px 48px; } }
.report-body { max-width: var(--content-max); margin: 0 auto; }

/* ── Header ── */
.report-header {
  padding-bottom: 28px;
  margin-bottom: 0;
  border-bottom: 2px solid var(--accent);
}
.header-badges {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}
.ticker-badge {
  padding: 5px 11px;
  background: var(--primary);
  color: var(--primary-fg);
  border-radius: 7px;
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: .02em;
}
.report-title {
  font-family: var(--font-display);
  font-size: clamp(28px, 4vw, 44px);
  line-height: 1.08;
  letter-spacing: var(--display-tracking);
  color: var(--primary);
  margin-bottom: 10px;
  font-weight: 400;
}
.report-subtitle {
  font-size: 13px;
  color: var(--fg-muted);
  font-family: var(--font-mono);
}

/* ── Sections ── */
.section-block { padding-top: 44px; }
.section-heading {
  display: flex;
  align-items: baseline;
  gap: 11px;
  margin-bottom: 18px;
}
.section-num {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--fg-faint);
  min-width: 20px;
}
.section-title {
  font-family: var(--font-display);
  font-size: 24px;
  line-height: 1.15;
  letter-spacing: var(--display-tracking);
  color: var(--primary);
  font-weight: 400;
}
.subsection-heading {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--fg);
  margin-top: 22px;
  margin-bottom: 10px;
  letter-spacing: -.01em;
}
.section-divider {
  height: 1px;
  background: var(--border);
  margin-top: 44px;
}

/* ── Prose ── */
.prose p {
  color: var(--fg-soft);
  line-height: 1.65;
  font-size: 14px;
  margin-bottom: 11px;
  max-width: 70ch;
}
.prose ul { padding-left: 20px; margin-bottom: 12px; }
.prose li {
  color: var(--fg-soft);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 4px;
}

/* ── Stat cards ── */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill,minmax(148px,1fr));
  gap: 10px;
  margin-bottom: 18px;
}
.stat-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px 16px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border-color .15s, box-shadow .15s;
}
.stat-label {
  font-size: 10px;
  letter-spacing: .09em;
  text-transform: uppercase;
  color: var(--fg-muted);
  font-weight: 600;
  font-family: var(--font-mono);
}
.stat-value {
  font-family: var(--font-display);
  font-size: 22px;
  line-height: 1;
  letter-spacing: var(--display-tracking);
  color: var(--fg);
  font-weight: 400;
  font-feature-settings: "lnum";
}

/* ── Badges ── */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .04em;
  font-family: var(--font-mono);
  text-transform: uppercase;
  border: 1px solid transparent;
}
.badge-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: currentColor;
  display: inline-block;
  flex-shrink: 0;
}
.badge-halal  { color: var(--halal);  background: var(--halal-bg);  border-color: color-mix(in oklab,var(--halal) 28%,transparent); }
.badge-haram  { color: var(--haram);  background: var(--haram-bg);  border-color: color-mix(in oklab,var(--haram) 28%,transparent); }
.badge-review { color: var(--review); background: var(--review-bg); border-color: color-mix(in oklab,var(--review) 28%,transparent); }
.badge-pass   { color: var(--halal);  background: var(--halal-bg);  border-color: color-mix(in oklab,var(--halal) 28%,transparent); }
.badge-fail   { color: var(--haram);  background: var(--haram-bg);  border-color: color-mix(in oklab,var(--haram) 28%,transparent); }

/* ── Card ── */
.card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 14px;
  transition: border-color .15s, box-shadow .15s;
}
.card-inset { padding: 0 !important; overflow: hidden; }

/* ── Tables ── */
.tbl-wrap {
  overflow-x: auto;
  margin-bottom: 14px;
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}
.tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 12.5px;
  background: var(--panel);
}
.tbl thead tr { background: var(--primary); color: var(--primary-fg); }
.tbl th {
  padding: 9px 11px;
  text-align: center;
  font-weight: 600;
  font-size: 11px;
  letter-spacing: .04em;
  white-space: nowrap;
  font-family: var(--font-mono);
}
.tbl th:first-child { text-align: left; padding-left: 14px; }
.tbl td {
  padding: 8px 11px;
  border-bottom: 1px solid var(--border);
  color: var(--fg-soft);
  vertical-align: middle;
  text-align: center;
}
.tbl td:first-child { text-align: left; padding-left: 14px; font-weight: 500; color: var(--fg); }
.tbl tbody tr:last-child td { border-bottom: 0; }
.tbl tbody tr:nth-child(even) td { background: var(--bg-soft); }
.tbl tbody tr.hl td { background: color-mix(in oklab,var(--accent) 10%,transparent) !important; font-weight: 600; }
.mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }

/* ── Compliance rows ── */
.compliance-card { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-sm); margin-bottom: 14px; }
.compliance-row {
  display: flex;
  align-items: center;
  padding: 13px 18px;
  border-bottom: 1px solid var(--border);
  gap: 14px;
  flex-wrap: wrap;
}
.compliance-row:last-child { border-bottom: 0; }
.compliance-info { flex: 1; min-width: 160px; }
.compliance-name { font-size: 13px; font-weight: 500; color: var(--fg); margin-bottom: 2px; }
.compliance-threshold { font-size: 11px; color: var(--fg-muted); font-family: var(--font-mono); }
.compliance-bar { margin-top: 7px; height: 4px; background: var(--bg-soft); border-radius: 2px; overflow: hidden; }
.compliance-bar-fill { height: 100%; border-radius: 2px; }
.bar-pass { background: var(--halal); }
.bar-fail { background: var(--haram); }
.compliance-value { font-family: var(--font-mono); font-size: 16px; font-weight: 600; color: var(--fg); min-width: 65px; text-align: right; }
.compliance-verdict { min-width: 58px; text-align: right; }

/* ── Source note / Disclaimer ── */
.source-note { font-size: 11px; color: var(--fg-faint); font-style: italic; margin-bottom: 14px; }
.disclaimer-block {
  margin-top: 52px;
  padding: 16px 20px;
  background: var(--panel-2);
  border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 12px;
  color: var(--fg-muted);
  line-height: 1.6;
}
.disclaimer-block strong { color: var(--fg); }

/* ── Chart containers ── */
.chart-wrap { margin-bottom: 16px; background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 18px; box-shadow: var(--shadow-sm); }

/* ── Print ── */
@media print {
  .report-sidebar { display: none !important; }
  .report-app { grid-template-columns: 1fr !important; }
  .report-main { padding: 0 !important; }
  .section-block { page-break-inside: avoid; }
}
"""

# ---------------------------------------------------------------------------
# Scroll-spy JS
# ---------------------------------------------------------------------------
_JS = """
(function() {
  var sections = document.querySelectorAll('.section-block[id]');
  var items    = document.querySelectorAll('.toc-item[data-target]');
  if (!sections.length || !items.length) return;

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        items.forEach(function(it) {
          it.classList.toggle('active', it.dataset.target === entry.target.id);
        });
      }
    });
  }, { rootMargin: '-15% 0px -72% 0px', threshold: 0 });

  sections.forEach(function(s) { observer.observe(s); });

  items.forEach(function(item) {
    item.addEventListener('click', function(ev) {
      ev.preventDefault();
      var t = document.getElementById(item.dataset.target);
      if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
})();
"""


# ---------------------------------------------------------------------------
# SVG chart helpers
# ---------------------------------------------------------------------------

def svg_revenue_chart(
    years: list[str],
    revenue: list[float],
    npat: list[float],
    title: str = "Revenue & NPAT ($B)",
) -> str:
    """Grouped bar chart as a self-contained SVG wrapped in a card div."""
    W, H = 620, 270
    PL, PR, PT, PB = 54, 16, 38, 40
    cw = W - PL - PR
    ch = H - PT - PB

    n = max(len(years), 1)
    max_v = max(max(revenue or [1]), max(npat or [0.01])) * 1.18
    if max_v == 0:
        max_v = 1

    gw = cw / n
    bw = gw * 0.30
    bgap = gw * 0.05

    def bh(v): return max(2, (v / max_v) * ch)
    def by(v): return PT + ch - bh(v)
    def gx(i): return PL + i * gw + gw * 0.12

    parts: list[str] = []

    # Grid lines + Y labels
    for gi in range(5):
        gy = PT + (gi / 4) * ch
        gv = max_v * (1 - gi / 4)
        lbl = f"{gv:.0f}" if gv >= 10 else f"{gv:.1f}"
        parts.append(
            f'<line x1="{PL}" y1="{gy:.1f}" x2="{W-PR}" y2="{gy:.1f}" '
            f'stroke="var(--grid-line)" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{PL-5}" y="{gy+4:.1f}" text-anchor="end" font-size="9.5" '
            f'fill="var(--fg-faint)" font-family="var(--font-mono)">{lbl}</text>'
        )

    # Bars + X labels
    for i in range(n):
        x0 = gx(i)
        rv = revenue[i] if i < len(revenue) else 0
        nv = npat[i] if i < len(npat) else 0
        parts.append(
            f'<rect x="{x0:.1f}" y="{by(rv):.1f}" width="{bw:.1f}" '
            f'height="{bh(rv):.1f}" fill="{NAVY}" rx="2" opacity="0.88"/>'
        )
        x1 = x0 + bw + bgap
        parts.append(
            f'<rect x="{x1:.1f}" y="{by(nv):.1f}" width="{bw:.1f}" '
            f'height="{bh(nv):.1f}" fill="{AMBER}" rx="2" opacity="0.90"/>'
        )
        lx = x0 + bw + bgap / 2
        yr_lbl = years[i] if i < len(years) else ""
        parts.append(
            f'<text x="{lx:.1f}" y="{PT+ch+16}" text-anchor="middle" font-size="10.5" '
            f'fill="var(--fg-muted)" font-family="var(--font-mono)">{_e(yr_lbl)}</text>'
        )

    # Baseline
    parts.append(
        f'<line x1="{PL}" y1="{PT+ch}" x2="{W-PR}" y2="{PT+ch}" '
        f'stroke="var(--border-strong)" stroke-width="1"/>'
    )

    # Legend
    parts += [
        f'<rect x="{PL}" y="{PT-22}" width="11" height="9" fill="{NAVY}" rx="2" opacity="0.88"/>',
        f'<text x="{PL+15}" y="{PT-14}" font-size="10" fill="var(--fg-muted)" font-family="var(--font-body)">Revenue</text>',
        f'<rect x="{PL+76}" y="{PT-22}" width="11" height="9" fill="{AMBER}" rx="2"/>',
        f'<text x="{PL+91}" y="{PT-14}" font-size="10" fill="var(--fg-muted)" font-family="var(--font-body)">NPAT</text>',
        f'<text x="{PL}" y="13" font-size="11.5" font-weight="600" fill="{NAVY}" font-family="var(--font-body)">{_e(title)}</text>',
    ]

    inner = "\n  ".join(parts)
    return (
        f'<div class="chart-wrap">'
        f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block" '
        f'xmlns="http://www.w3.org/2000/svg">\n  {inner}\n</svg></div>\n'
    )


def svg_analyst_dotplot(
    low: float,
    median: float,
    current: float,
    high: float,
    title: str = "Analyst Target Range",
) -> str:
    """Horizontal dot-plot with Low / Median / Current / High."""
    W, H = 620, 100
    PL, PR, CY = 44, 44, 62

    vals = [low, median, current, high]
    mn, mx = min(vals), max(vals)
    span = mx - mn or 1

    def xp(v): return PL + (v - mn) / span * (W - PL - PR)

    pts_data = [
        ("Low",     low,     "#9ca3af", -26),
        ("Median",  median,  NAVY,       22),
        ("Current", current, AMBER,     -26),
        ("High",    high,    "#9ca3af",  22),
    ]

    parts: list[str] = [
        f'<text x="{PL}" y="13" font-size="11.5" font-weight="600" fill="{NAVY}" '
        f'font-family="var(--font-body)">{_e(title)}</text>',
        f'<line x1="{PL}" y1="{CY}" x2="{W-PR}" y2="{CY}" '
        f'stroke="var(--border-strong)" stroke-width="2.5"/>',
    ]

    for label, val, color, dy in pts_data:
        x = xp(val)
        parts.append(f'<circle cx="{x:.1f}" cy="{CY}" r="7" fill="{color}"/>')
        lbl_y = CY + dy
        val_y = CY + (dy + (-12 if dy < 0 else 13))
        parts.append(
            f'<text x="{x:.1f}" y="{lbl_y}" text-anchor="middle" font-size="9.5" '
            f'fill="var(--fg-muted)" font-family="var(--font-mono)">{_e(label)}</text>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{val_y}" text-anchor="middle" font-size="10.5" '
            f'font-weight="600" fill="{color}" font-family="var(--font-mono)">${val:,.2f}</text>'
        )

    inner = "\n  ".join(parts)
    return (
        f'<div class="chart-wrap">'
        f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block" '
        f'xmlns="http://www.w3.org/2000/svg">\n  {inner}\n</svg></div>\n'
    )


def svg_price_chart(
    prices: list[float],
    dates: list[str] | None = None,
    ma50: list[float] | None = None,
    ma200: list[float] | None = None,
    title: str = "Price · 1Y",
) -> str:
    """Price line chart with optional MAs."""
    if not prices:
        return ""
    W, H = 620, 200
    PL, PR, PT, PB = 52, 16, 36, 34
    cw = W - PL - PR
    ch = H - PT - PB
    n = len(prices)

    lo = min(p for p in prices if p is not None)
    hi = max(p for p in prices if p is not None)
    pad = (hi - lo) * 0.10 or 1
    lo -= pad
    hi += pad

    def px(i): return PL + (i / max(n - 1, 1)) * cw
    def py(v): return PT + ch - (v - lo) / (hi - lo) * ch

    is_up = prices[-1] >= prices[0]
    line_col = PASS_GREEN if is_up else FAIL_RED
    grad_col = line_col

    def polyline(data, color, width=1.8, dash=""):
        pts = " ".join(
            f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(data) if v is not None
        )
        da = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{da}/>'
        )

    # Fill area
    fill_pts = (
        f"{PL},{PT+ch} "
        + " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(prices) if v is not None)
        + f" {PL+cw},{PT+ch}"
    )

    gid = "pg"
    parts: list[str] = [
        f'<defs><linearGradient id="{gid}" x1="0" x2="0" y1="0" y2="1">'
        f'<stop offset="0%" stop-color="{grad_col}" stop-opacity="0.16"/>'
        f'<stop offset="100%" stop-color="{grad_col}" stop-opacity="0"/>'
        f'</linearGradient></defs>',
        f'<polygon points="{fill_pts}" fill="url(#{gid})"/>',
        polyline(prices, line_col, 2.0),
    ]
    if ma50:
        parts.append(polyline(ma50, AMBER, 1.3))
    if ma200:
        parts.append(polyline(ma200, "#888888", 1.3, "4,3"))

    # Grid
    for gi in range(4):
        gy = PT + (gi / 3) * ch
        gv = hi - (gi / 3) * (hi - lo)
        parts += [
            f'<line x1="{PL}" y1="{gy:.1f}" x2="{W-PR}" y2="{gy:.1f}" '
            f'stroke="var(--grid-line)" stroke-width="1"/>',
            f'<text x="{PL-5}" y="{gy+4:.1f}" text-anchor="end" font-size="9.5" '
            f'fill="var(--fg-faint)" font-family="var(--font-mono)">${gv:.0f}</text>',
        ]

    # X date labels
    if dates and len(dates) >= 2:
        for idx in [0, len(dates) // 2, len(dates) - 1]:
            parts.append(
                f'<text x="{px(idx):.1f}" y="{PT+ch+15}" text-anchor="middle" font-size="9.5" '
                f'fill="var(--fg-muted)" font-family="var(--font-mono)">{_e(dates[idx])}</text>'
            )

    # Baseline + title
    parts += [
        f'<line x1="{PL}" y1="{PT+ch}" x2="{W-PR}" y2="{PT+ch}" '
        f'stroke="var(--border-strong)" stroke-width="1"/>',
        f'<text x="{PL}" y="13" font-size="11.5" font-weight="600" fill="{NAVY}" '
        f'font-family="var(--font-body)">{_e(title)}</text>',
    ]

    inner = "\n  ".join(parts)
    return (
        f'<div class="chart-wrap">'
        f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block" '
        f'xmlns="http://www.w3.org/2000/svg">\n  {inner}\n</svg></div>\n'
    )


# ---------------------------------------------------------------------------
# Section HTML builders
# ---------------------------------------------------------------------------

def _snapshot_html(data: dict) -> str:
    cards = "".join(
        f'<div class="stat-card">'
        f'<div class="stat-label">{_e(k)}</div>'
        f'<div class="stat-value">{_e(v)}</div>'
        f'</div>'
        for k, v in data.items()
    )
    return f'<div class="stat-grid">{cards}</div>\n'


def _parse_bar_pct(actual: str, threshold: str) -> float | None:
    """Return fill% for the progress bar, or None if unparseable."""
    try:
        pct_v = float(str(actual).rstrip("%").strip())
        m = re.search(r"[\d.]+", str(threshold))
        thresh_v = float(m.group()) if m else 100
        return min(100.0, (pct_v / thresh_v) * 100)
    except Exception:
        return None


def _aaoifi_html(rows) -> str:
    parts = ['<div class="compliance-card">']
    for i, row in enumerate(rows):
        name, threshold, actual, passed = row
        bar_pct = _parse_bar_pct(actual, threshold)
        badge = ("badge-pass", "PASS") if passed else ("badge-fail", "FAIL")
        bar_cls = "bar-pass" if passed else "bar-fail"

        bar_html = ""
        if bar_pct is not None:
            bar_html = (
                f'<div class="compliance-bar">'
                f'<div class="compliance-bar-fill {bar_cls}" style="width:{bar_pct:.1f}%"></div>'
                f'</div>'
            )

        parts.append(
            f'<div class="compliance-row">'
            f'<div class="compliance-info">'
            f'<div class="compliance-name">{_e(name)}</div>'
            f'<div class="compliance-threshold">Threshold: {_e(threshold)}</div>'
            f'{bar_html}'
            f'</div>'
            f'<div class="compliance-value mono">{_e(actual)}</div>'
            f'<div class="compliance-verdict">'
            f'<span class="badge {badge[0]}">{badge[1]}</span>'
            f'</div>'
            f'</div>'
        )
    parts.append("</div>\n")
    return "\n".join(parts)


def _std_table_html(header: list, rows: list, highlights: list[int] | None = None) -> str:
    hl = set(highlights or [])
    th = "".join(f"<th>{_e(h)}</th>" for h in header)
    trs = []
    for i, row in enumerate(rows):
        cls = ' class="hl"' if i in hl else ""
        tds = "".join(f"<td>{_e(c) if c is not None else '—'}</td>" for c in row)
        trs.append(f"<tr{cls}>{tds}</tr>")
    return (
        f'<div class="tbl-wrap"><table class="tbl">'
        f'<thead><tr>{th}</tr></thead>'
        f'<tbody>{"".join(trs)}</tbody>'
        f'</table></div>\n'
    )


def _quarterly_table_html(header: list, rows: list) -> str:
    th = "".join(f"<th>{_e(h)}</th>" for h in header)
    trs = []
    for row in rows:
        cells = list(row)
        passed = cells[-1]
        display = cells[:-1]
        badge = (
            '<span class="badge badge-pass">✓ PASS</span>'
            if passed
            else '<span class="badge badge-fail">✗ FAIL</span>'
        )
        tds = "".join(f"<td>{_e(c)}</td>" for c in display) + f"<td>{badge}</td>"
        cls = "" if passed else ' class="hl"'
        trs.append(f"<tr{cls}>{tds}</tr>")
    return (
        f'<div class="tbl-wrap"><table class="tbl">'
        f'<thead><tr>{th}</tr></thead>'
        f'<tbody>{"".join(trs)}</tbody>'
        f'</table></div>\n'
    )


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class HtmlReportBuilder:
    """
    Builds a self-contained HTML research report using the HalalInvest design
    system. API mirrors build_report.ReportBuilder so SKILL.md workflows need
    only s/ReportBuilder/HtmlReportBuilder/ and minor param additions.
    """

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        ticker: str = "",
        shariah_status: str = "halal",
    ):
        self.title = title
        self.subtitle = subtitle
        self.ticker = ticker.upper()
        self.shariah_status = shariah_status.lower()

        self._sections: list[tuple[str, str, str]] = []
        self._cur_id: str | None = None
        self._cur_label: str | None = None
        self._cur_parts: list[str] = []
        self._disclaimer_html = ""

    # ── internal ──────────────────────────────────────────────────────────

    def _flush(self):
        if self._cur_id is not None:
            self._sections.append(
                (self._cur_id, self._cur_label, "\n".join(self._cur_parts))
            )
            self._cur_id = None
            self._cur_label = None
            self._cur_parts = []

    def _slugify(self, text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

    def _push(self, fragment: str):
        if self._cur_id is None:
            self._cur_id = "preamble"
            self._cur_label = "Overview"
        self._cur_parts.append(fragment)

    # ── structural ────────────────────────────────────────────────────────

    def section(self, heading: str):
        self._flush()
        m = re.match(r"^(\d+[a-z]?)\.\s+(.+)", heading)
        num, title_text = (m.group(1), m.group(2)) if m else ("", heading)
        self._cur_id = f"s-{self._slugify(heading)}"
        self._cur_label = heading
        num_html = f'<span class="section-num">{_e(num)}.</span>' if num else ""
        self._cur_parts = [
            f'<div class="section-heading">'
            f'{num_html}<h2 class="section-title">{_e(title_text)}</h2>'
            f"</div>\n"
        ]

    def subsection(self, heading: str):
        self._push(f'<h3 class="subsection-heading">{_e(heading)}</h3>\n')

    def prose(self, *paragraphs: str):
        ps = "".join(f"<p>{_e(p)}</p>" for p in paragraphs)
        self._push(f'<div class="prose">{ps}</div>\n')

    def bullets(self, items: Iterable[str]):
        lis = "".join(f"<li>{_e(i)}</li>" for i in items)
        self._push(f'<div class="prose"><ul>{lis}</ul></div>\n')

    def html(self, raw: str):
        """Insert pre-built HTML / SVG (e.g. svg_revenue_chart output)."""
        self._push(raw)

    def source_note(self, text: str):
        self._push(f'<p class="source-note">Source: {_e(text)}</p>\n')

    def spacer(self, _height=None):
        self._push('<div style="height:10px"></div>\n')

    # ── section tables ────────────────────────────────────────────────────

    def snapshot(self, data: dict):
        self._push(_snapshot_html(data))

    def aaoifi(self, ratio_rows: list[tuple]):
        self._push(_aaoifi_html(ratio_rows))

    def pif_industries(self, entries: list[tuple]):
        hl = [i for i, (_, e, _) in enumerate(entries)
              if str(e).strip().lower() in ("y", "yes", "partial")]
        self._push(_std_table_html(
            ["Excluded Industry", "Exposure?", "Notes"],
            [list(r) for r in entries],
            highlights=hl,
        ))

    def pif_income(self, rows: list[tuple]):
        self._push(_quarterly_table_html(
            ["Quarter", "Interest Income", "Total Revenue", "Ratio", "Pass?"], rows
        ))

    def pif_expense(self, rows: list[tuple]):
        self._push(_quarterly_table_html(
            ["Quarter", "Interest Expense", "Total Expenses", "Ratio", "Pass?"], rows
        ))

    def fundamentals(self, columns: list[str], rows: list[tuple]):
        self._push(_std_table_html(list(columns), [list(r) for r in rows]))

    def multiples(self, rows: list[tuple]):
        self._push(_std_table_html(
            ["Multiple", "Current", "Sector Median", "5-yr Avg", "Signal"],
            [list(r) for r in rows],
        ))

    def dcf(self, rows: list[tuple]):
        self._push(_std_table_html(
            ["Scenario", "Implied / Share", "% vs Current", "Key assumption"],
            [list(r) for r in rows],
        ))

    def analysts(self, rows: list[tuple]):
        self._push(_std_table_html(
            ["Analyst / Firm", "Date", "Rating", "Prev.", "Target", "Prev. Tgt", "Upside %"],
            [list(r) for r in rows],
        ))

    def indicators(self, rows: list[tuple]):
        self._push(_std_table_html(
            ["Indicator", "Value", "Read"],
            [list(r) for r in rows],
        ))

    def table(self, _ignored):
        """Compatibility stub — silently ignores ReportLab Table objects."""
        pass

    # ── disclaimer ────────────────────────────────────────────────────────

    def disclaimer(self):
        self._disclaimer_html = (
            '<div class="disclaimer-block">'
            "<strong>Disclaimer:</strong> This is research, not financial advice. "
            "Do your own due diligence."
            "</div>\n"
        )

    # ── build ─────────────────────────────────────────────────────────────

    def build(self, out_path: str) -> str:
        self._flush()

        # TOC
        toc_parts = []
        for sid, slabel, _ in self._sections:
            m = re.match(r"^(\d+[a-z]?)\.\s+(.+)", slabel)
            label = m.group(2) if m else slabel
            toc_parts.append(
                f'<a class="toc-item" data-target="{_e(sid)}" href="#{_e(sid)}">'
                f'{_e(label)}</a>'
            )
        toc_html = "\n    ".join(toc_parts)

        # Sections
        sec_parts = []
        for idx, (sid, _, body) in enumerate(self._sections):
            sec_parts.append(f'<section class="section-block" id="{_e(sid)}">\n{body}\n</section>')
            if idx < len(self._sections) - 1:
                sec_parts.append('<div class="section-divider"></div>')
        sections_html = "\n".join(sec_parts)

        # Header badges
        ticker_html = (
            f'<div class="ticker-badge">{_e(self.ticker)}</div>'
            if self.ticker
            else ""
        )
        _status = {
            "halal":  ("badge-halal",  "Halal"),
            "haram":  ("badge-haram",  "Haram"),
            "review": ("badge-review", "Under Review"),
        }
        bcls, blbl = _status.get(self.shariah_status, ("badge-review", "Under Review"))
        status_badge = (
            f'<span class="badge {bcls}">'
            f'<span class="badge-dot"></span>{_e(blbl)}</span>'
        )

        subtitle_html = (
            f'<p class="report-subtitle">{_e(self.subtitle)}</p>'
            if self.subtitle
            else ""
        )

        doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{_e(self.title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap">
  <style>{_CSS}</style>
</head>
<body>
<div class="report-app">

  <aside class="report-sidebar">
    <div class="sidebar-logo">
      <span class="sidebar-logomark">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="28" height="28" rx="7" fill="var(--primary)"/>
          <path d="M8 7v14M20 7v14M8 14h8" stroke="var(--primary-fg)" stroke-width="2" stroke-linecap="round"/>
          <circle cx="20" cy="14" r="3.2" fill="none" stroke="var(--primary-fg)" stroke-width="1.6"/>
          <circle cx="21" cy="13.4" r="2.6" fill="var(--primary)"/>
        </svg>
      </span>
      <span class="sidebar-wordmark">Halal<em>Invest</em></span>
    </div>
    <div class="toc-label">Contents</div>
    {toc_html}
  </aside>

  <main class="report-main">
    <div class="report-body">

      <header class="report-header">
        <div class="header-badges">
          {ticker_html}
          {status_badge}
        </div>
        <h1 class="report-title">{_e(self.title)}</h1>
        {subtitle_html}
      </header>

      {sections_html}
      {self._disclaimer_html}
    </div>
  </main>

</div>
<script>{_JS}</script>
</body>
</html>"""

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"[build_report_html] wrote {out_path} ({os.path.getsize(out_path):,} bytes)")
        return out_path


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "_sanity_report.html")
    b = HtmlReportBuilder(
        "Sanity Check Corp (TEST)",
        subtitle="As of 2026-05-10",
        ticker="TEST",
        shariah_status="halal",
    )
    b.section("1. Snapshot")
    b.snapshot({
        "Price": "$142.50", "Market Cap": "$3.5T", "Shares Out": "24.6B",
        "52W High": "$152.90", "52W Low": "$86.60", "Div Yield (TTM)": "0.03%",
        "Beta": "1.67", "Next Earnings": "2026-08-01", "Sector": "Technology",
    })
    b.section("2. Business Overview")
    b.prose(
        "This self-test exercises every component in the HTML builder to confirm "
        "layout, overflow handling, and chart rendering are all correct.",
        "Second paragraph of prose to verify spacing.",
    )
    b.bullets(["Item one — detail", "Item two — detail", "Item three — detail"])
    b.section("3. Shariah Compliance")
    b.subsection("3b. AAOIFI Screen")
    b.aaoifi([
        ("Haram revenue / Total revenue", "< 5%", "0.0%", True),
        ("Interest-bearing debt / Market Cap", "< 33%", "12.4%", True),
        ("Interest-bearing securities / Market Cap", "< 30%", "1.1%", True),
        ("Accounts Receivable / Market Cap", "< 49%", "0.7%", True),
    ])
    b.subsection("3c. PIF Step 1 — Industry exposure")
    b.pif_industries([
        ("Alcohol", "N", "—"),
        ("Tobacco", "N", "—"),
        ("Conventional financial services", "Partial", "Stripe integration; non-core."),
        ("Music", "N", "—"),
    ])
    b.section("4. Financial Fundamentals")
    b.html(svg_revenue_chart(
        ["FY22", "FY23", "FY24", "FY25e"],
        [26.9, 44.9, 60.9, 72.0],
        [4.37, 9.76, 16.7, 20.1],
    ))
    b.fundamentals(
        ["Line", "FY22", "FY23", "FY24", "YoY%"],
        [
            ("Revenue ($B)", "26.9", "44.9", "60.9", "+35.6%"),
            ("NPAT ($B)",    "4.37", "9.76", "16.7", "+71.1%"),
            ("FCF ($B)",     "3.81", "8.97", "14.3", "+59.4%"),
        ],
    )
    b.section("5. Valuation")
    b.multiples([
        ("P/E (TTM)", "38.2x", "26.4x", "32.1x", "Rich"),
        ("Fwd P/E",   "31.5x", "22.8x", "28.5x", "Moderate"),
        ("EV/EBITDA", "24.8x", "18.2x", "21.0x", "Moderate"),
    ])
    b.dcf([
        ("Bull", "$198", "+39%", "Rev CAGR 28%, margin expansion to 32%"),
        ("Base", "$165", "+16%", "Rev CAGR 22%, margins stable at 28%"),
        ("Bear", "$118", "-17%", "Rev CAGR 12%, margin compression to 22%"),
    ])
    b.section("6. Analyst Coverage")
    b.html(svg_analyst_dotplot(118, 165, 142.5, 220))
    b.analysts([
        ("Goldman Sachs", "2026-04-28", "Buy",  "Buy",  "$195", "$185", "+37%"),
        ("Morgan Stanley","2026-04-15", "OW",   "OW",   "$185", "$175", "+30%"),
        ("BofA",          "2026-04-02", "Buy",  "Neut", "$170", "$140", "+19%"),
    ])
    b.section("7. Technical Analysis")
    b.html(svg_price_chart(
        [100+i*0.8+5*math.sin(i/3) for i in range(52)],
        dates=[f"W{i}" for i in range(52)],
    ))
    b.section("8. Catalysts & Risks")
    b.subsection("Catalysts")
    b.bullets(["Q2 earnings beat on data-center revenue", "New product launch H2 2026"])
    b.subsection("Risks")
    b.bullets(["Export controls on advanced GPUs", "Customer concentration > 20% revenue"])
    b.section("10. Summary & Thesis")
    b.prose("Bull: AI capex cycle drives sustained revenue outperformance. Bear: valuation leaves no margin of error.")
    b.disclaimer()
    b.build(out)
    print("Sanity HTML written to:", out)
