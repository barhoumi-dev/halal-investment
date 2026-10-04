"""
build_slides.py — generate a self-contained HTML swing-trade-setup deck.

Usage:
    python build_slides.py --spec /path/to/setup.json --out /path/to/out.html

The spec JSON schema is documented in references/output_template.md.

Design rules:
- Single-file HTML output. No CDN, no external assets, no network calls when opened.
- All graphics are inline SVG. Palette: navy #0B3C5D, amber #C69214.
- 6 slides: title, trend+halal, levels chart, indicators, trade setup, catalysts+verdict.
- Keyboard navigation (arrow keys), prev/next buttons, page counter, progress bar.

The script is intentionally one file. It's easier to debug, easier to copy into another
skill, and the output is one HTML file by design.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

NAVY = "#0B3C5D"
NAVY_2 = "#14507A"
AMBER = "#C69214"
AMBER_2 = "#E0AE2D"
GREEN = "#2E7D32"
GREEN_LIGHT = "#5DA661"
RED = "#C62828"
GRAY_1 = "#F6F6F6"
GRAY_2 = "#E7E7E7"
GRAY_3 = "#C9C9C9"
GRAY_4 = "#888888"
INK = "#1d1d1d"
MUTED = "#555555"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def esc(s: Any) -> str:
    """HTML-escape a value for safe embedding."""
    if s is None:
        return ""
    return html.escape(str(s), quote=True)


def fmt_price(p: float | int | None, na: str = "n/d") -> str:
    if p is None:
        return na
    if isinstance(p, (int, float)):
        return f"${p:,.2f}"
    return str(p)


def verdict_color(v: str) -> tuple[str, str]:
    """Return (bg_color, fg_color) for a verdict pill."""
    v = (v or "").upper()
    if v == "BUY":
        return ("#DDF1DE", GREEN)
    if v == "AVOID":
        return ("#FAD7D7", RED)
    return ("#FFF1CC", "#7B5E00")  # WAIT / default


def halal_color(status: str) -> tuple[str, str]:
    s = (status or "").lower()
    if s == "compliant":
        return ("#DDF1DE", GREEN)
    if s == "non-compliant":
        return ("#FAD7D7", RED)
    return ("#FFF1CC", "#7B5E00")  # doubtful


# ---------------------------------------------------------------------------
# SVG building blocks
# ---------------------------------------------------------------------------

def _deconflict(positions: list[float], min_spacing: float = 16.0,
                ymin_clip: float = 0, ymax_clip: float = 1e9) -> list[float]:
    """Given a list of preferred y-positions, return adjusted positions where
    consecutive items (after sort) are at least min_spacing apart. Preserves
    the input ordering — caller can map back via index.

    The algorithm: sort with original indices, push items forward as needed,
    then push items back from the bottom if they exceed the clip range. A
    couple of relaxation passes converge for typical cluster sizes.
    """
    if not positions:
        return positions
    n = len(positions)
    indexed = sorted(enumerate(positions), key=lambda t: t[1])
    adj = [(idx, y_val) for idx, y_val in indexed]
    # forward pass
    for i in range(1, n):
        prev_y = adj[i - 1][1]
        cur_y = adj[i][1]
        if cur_y - prev_y < min_spacing:
            adj[i] = (adj[i][0], prev_y + min_spacing)
    # backward clip pass — if last item exceeds clip, shift cluster up
    if adj[-1][1] > ymax_clip:
        shift = adj[-1][1] - ymax_clip
        adj = [(idx, y_val - shift) for idx, y_val in adj]
        for i in range(n - 2, -1, -1):
            if adj[i + 1][1] - adj[i][1] < min_spacing:
                adj[i] = (adj[i][0], adj[i + 1][1] - min_spacing)
    if adj[0][1] < ymin_clip:
        shift = ymin_clip - adj[0][1]
        adj = [(idx, y_val + shift) for idx, y_val in adj]
        for i in range(1, n):
            if adj[i][1] - adj[i - 1][1] < min_spacing:
                adj[i] = (adj[i][0], adj[i - 1][1] + min_spacing)
    out = [0.0] * n
    for idx, y_val in adj:
        out[idx] = y_val
    return out


def levels_chart_svg(spec: dict, width: int = 900, height: int = 480) -> str:
    """Inline SVG for the key-levels visualization (slide 3).

    Vertical price ladder with supports, resistances, MAs, current, entry,
    stop, and targets. Labels are deconflicted vertically when levels cluster
    densely (e.g. price near 50DMA near 200DMA near nearest support); a thin
    leader line connects each label to its actual price line.
    """
    price = spec["price"]
    supports = spec.get("supports", []) or []
    resistances = spec.get("resistances", []) or []
    ma50 = spec.get("ma50")
    ma200 = spec.get("ma200")
    trade = spec.get("trade", {}) or {}
    entry_low = trade.get("entry_low")
    entry_high = trade.get("entry_high")
    stop = trade.get("stop")
    t1 = trade.get("t1")
    t2 = trade.get("t2")

    # collect all level values to determine y-range
    vals: list[float] = [price]
    for L in supports + resistances:
        if isinstance(L, dict) and L.get("price") is not None:
            vals.append(float(L["price"]))
    for v in (ma50, ma200, entry_low, entry_high, stop, t1, t2):
        if v is not None:
            vals.append(float(v))

    if not vals:
        return ""

    ymin = min(vals) * 0.96
    ymax = max(vals) * 1.04
    if ymax - ymin < 1e-6:
        ymax = ymin + 1.0

    pad_left = 60
    pad_right = 320
    pad_top = 36
    pad_bot = 36
    plot_h = height - pad_top - pad_bot
    plot_x_start = pad_left
    plot_x_end = width - pad_right
    label_x = plot_x_end + 14

    def y(v: float) -> float:
        # Higher prices = top of chart
        return pad_top + (ymax - v) / (ymax - ymin) * plot_h

    parts: list[str] = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Key levels chart" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">'
    )
    # Background grid (subtle horizontal gridlines at deciles of the range)
    n_grid = 5
    for i in range(n_grid + 1):
        gv = ymin + (ymax - ymin) * i / n_grid
        gy = y(gv)
        parts.append(
            f'<line x1="{plot_x_start}" y1="{gy:.1f}" x2="{plot_x_end}" y2="{gy:.1f}" '
            f'stroke="{GRAY_2}" stroke-width="0.5" />'
        )
        parts.append(
            f'<text x="{plot_x_start - 8}" y="{gy + 4:.1f}" text-anchor="end" '
            f'font-size="11" fill="{MUTED}">${gv:,.0f}</text>'
        )

    # Entry zone (amber tinted band) — drawn first so it sits behind level lines
    if entry_low is not None and entry_high is not None:
        ey1 = y(max(entry_low, entry_high))
        ey2 = y(min(entry_low, entry_high))
        parts.append(
            f'<rect x="{plot_x_start}" y="{ey1:.1f}" width="{plot_x_end - plot_x_start}" '
            f'height="{(ey2 - ey1):.1f}" fill="#FDF2D4" opacity="0.65" />'
        )

    # Stop band background
    if stop is not None:
        sy = y(stop)
        parts.append(
            f'<rect x="{plot_x_start}" y="{sy - 3:.1f}" width="{plot_x_end - plot_x_start}" '
            f'height="6" fill="#F8D7DA" opacity="0.55" />'
        )

    # Build a unified list of labels with their preferred y positions, then
    # deconflict so dense clusters don't pile on top of each other.
    # Each entry: (y_actual, label_html_template, line_html)
    # We'll lay down line_html (drawn at actual y), then labels at adjusted y
    # connected by a leader line.
    label_items: list[dict] = []

    def add_line(y_val: float, line_svg: str, label_text: str, label_color: str,
                 label_extra: str = "", weight: str = "600") -> None:
        label_items.append({
            "y_actual": y_val,
            "line": line_svg,
            "text": label_text,
            "color": label_color,
            "extra": label_extra,
            "weight": weight,
        })

    # Resistances
    for r in resistances:
        rv = float(r["price"])
        ry = y(rv)
        line = (
            f'<line x1="{plot_x_start}" y1="{ry:.1f}" x2="{plot_x_end}" y2="{ry:.1f}" '
            f'stroke="{GRAY_4}" stroke-width="0.9" stroke-dasharray="3,3" opacity="0.8" />'
        )
        add_line(ry, line, f"R  ${rv:,.2f}", MUTED, esc(r.get("label", "")), "500")

    # Supports
    for s in supports:
        sv = float(s["price"])
        sy_ = y(sv)
        line = (
            f'<line x1="{plot_x_start}" y1="{sy_:.1f}" x2="{plot_x_end}" y2="{sy_:.1f}" '
            f'stroke="{GRAY_4}" stroke-width="0.9" stroke-dasharray="3,3" opacity="0.8" />'
        )
        add_line(sy_, line, f"S  ${sv:,.2f}", MUTED, esc(s.get("label", "")), "500")

    # MAs
    if ma50 is not None:
        my = y(ma50)
        line = (
            f'<line x1="{plot_x_start}" y1="{my:.1f}" x2="{plot_x_end}" y2="{my:.1f}" '
            f'stroke="{AMBER}" stroke-width="1.5" />'
        )
        add_line(my, line, f"50DMA  ${ma50:,.2f}", AMBER)
    if ma200 is not None:
        my2 = y(ma200)
        line = (
            f'<line x1="{plot_x_start}" y1="{my2:.1f}" x2="{plot_x_end}" y2="{my2:.1f}" '
            f'stroke="{GRAY_4}" stroke-width="1.5" stroke-dasharray="6,3,1,3" />'
        )
        add_line(my2, line, f"200DMA  ${ma200:,.2f}", GRAY_4)

    # Stop
    if stop is not None:
        sy = y(stop)
        line = (
            f'<line x1="{plot_x_start}" y1="{sy:.1f}" x2="{plot_x_end}" y2="{sy:.1f}" '
            f'stroke="{RED}" stroke-width="1.6" />'
        )
        add_line(sy, line, f"Stop  ${stop:,.2f}", RED, "", "700")

    # Targets
    if t2 is not None:
        ty = y(t2)
        line = (
            f'<line x1="{plot_x_start}" y1="{ty:.1f}" x2="{plot_x_end}" y2="{ty:.1f}" '
            f'stroke="{GREEN}" stroke-width="1.4" stroke-dasharray="2,4" />'
        )
        add_line(ty, line, f"T2  ${t2:,.2f}", GREEN, "", "700")
    if t1 is not None:
        ty = y(t1)
        line = (
            f'<line x1="{plot_x_start}" y1="{ty:.1f}" x2="{plot_x_end}" y2="{ty:.1f}" '
            f'stroke="{GREEN}" stroke-width="1.6" stroke-dasharray="6,4" />'
        )
        add_line(ty, line, f"T1  ${t1:,.2f}", GREEN, "", "700")

    # Entry zone label (use midpoint y)
    if entry_low is not None and entry_high is not None:
        ey_mid = (y(entry_low) + y(entry_high)) / 2
        add_line(ey_mid, "", f"Entry  ${entry_low:,.2f}–${entry_high:,.2f}",
                 AMBER, "", "700")

    # Current price gets its own line+badge (drawn last so it's on top)
    py = y(price)
    current_line = (
        f'<line x1="{plot_x_start}" y1="{py:.1f}" x2="{plot_x_end}" y2="{py:.1f}" '
        f'stroke="{NAVY}" stroke-width="2.6" />'
        f'<rect x="{plot_x_start + 4}" y="{py - 12:.1f}" width="84" height="22" rx="3" fill="{NAVY}" />'
        f'<text x="{plot_x_start + 12}" y="{py + 4:.1f}" '
        f'font-size="12" font-weight="700" fill="#fff">${price:,.2f}</text>'
    )
    add_line(py, current_line, "CURRENT", NAVY, "", "800")

    # First, draw all the underlying horizontal lines at their actual positions
    for it in label_items:
        if it["line"]:
            parts.append(it["line"])

    # Now compute deconflicted label y-positions
    actual_ys = [it["y_actual"] for it in label_items]
    label_ys = _deconflict(actual_ys, min_spacing=15.0,
                           ymin_clip=pad_top + 8,
                           ymax_clip=pad_top + plot_h - 8)

    for it, ly in zip(label_items, label_ys):
        ay = it["y_actual"]
        col = it["color"]
        weight = it["weight"]
        text = it["text"]
        extra = it["extra"]
        # Leader line connecting the label position to the actual y on the chart edge
        if abs(ly - ay) > 1.5:
            parts.append(
                f'<path d="M {plot_x_end} {ay:.1f} L {plot_x_end + 6} {ay:.1f} '
                f'L {plot_x_end + 10} {ly:.1f} L {label_x - 4} {ly:.1f}" '
                f'stroke="{GRAY_3}" stroke-width="0.8" fill="none" />'
            )
        if extra:
            parts.append(
                f'<text x="{label_x}" y="{ly + 4:.1f}" '
                f'font-size="11" font-weight="{weight}" fill="{col}">{text}'
                f'  <tspan fill="{GRAY_4}" font-style="italic" font-weight="400">— {extra}</tspan></text>'
            )
        else:
            parts.append(
                f'<text x="{label_x}" y="{ly + 4:.1f}" '
                f'font-size="11" font-weight="{weight}" fill="{col}">{text}</text>'
            )

    parts.append("</svg>")
    return "".join(parts)


def rsi_gauge_svg(rsi: float | None, width: int = 280, height: int = 170) -> str:
    """Semicircular RSI gauge with zones."""
    if rsi is None:
        return _na_box(width, height, "RSI")
    rsi = max(0, min(100, float(rsi)))
    cx = width / 2
    cy = height - 24
    r = 110

    # Build the three zone arcs (oversold 0–30, neutral 30–70, overbought 70–100)
    def arc_d(start_deg: float, end_deg: float, radius: float) -> str:
        import math
        # angle 180 = leftmost, 0 = rightmost in standard math; we want
        # 0% RSI = left (180deg), 100% RSI = right (0deg)
        # so angle_deg(rsi) = 180 - rsi*1.8
        a1 = math.radians(180 - start_deg * 1.8)
        a2 = math.radians(180 - end_deg * 1.8)
        x1 = cx + radius * math.cos(a1)
        y1 = cy - radius * math.sin(a1)
        x2 = cx + radius * math.cos(a2)
        y2 = cy - radius * math.sin(a2)
        large = 1 if abs(end_deg - start_deg) > 50 else 0
        # sweep flag = 0 because we go counter-clockwise in SVG y-axis terms
        return f"M {x1:.1f} {y1:.1f} A {radius} {radius} 0 {large} 0 {x2:.1f} {y2:.1f}"

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="RSI gauge" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">',
        # zones (track)
        f'<path d="{arc_d(0, 30, r)}" stroke="#DDF1DE" stroke-width="14" fill="none" />',
        f'<path d="{arc_d(30, 70, r)}" stroke="{GRAY_2}" stroke-width="14" fill="none" />',
        f'<path d="{arc_d(70, 100, r)}" stroke="#FAD7D7" stroke-width="14" fill="none" />',
        # tick labels at 0/30/70/100
    ]
    import math
    for v, label in [(0, "0"), (30, "30"), (70, "70"), (100, "100")]:
        a = math.radians(180 - v * 1.8)
        tx = cx + (r + 14) * math.cos(a)
        ty = cy - (r + 14) * math.sin(a)
        parts.append(
            f'<text x="{tx:.1f}" y="{ty + 4:.1f}" text-anchor="middle" '
            f'font-size="10" fill="{MUTED}">{label}</text>'
        )
    # needle
    a_n = math.radians(180 - rsi * 1.8)
    nx = cx + (r - 6) * math.cos(a_n)
    ny = cy - (r - 6) * math.sin(a_n)
    parts.append(
        f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" '
        f'stroke="{NAVY}" stroke-width="3" stroke-linecap="round" />'
    )
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{NAVY}" />')
    # value readout
    if rsi < 30:
        zone_label, zc = "Oversold", GREEN
    elif rsi > 70:
        zone_label, zc = "Overbought", RED
    else:
        zone_label, zc = "Neutral", MUTED
    parts.append(
        f'<text x="{cx}" y="{cy - 28:.1f}" text-anchor="middle" '
        f'font-size="28" font-weight="800" fill="{NAVY}">{rsi:.0f}</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy - 8:.1f}" text-anchor="middle" '
        f'font-size="11" font-weight="600" fill="{zc}" letter-spacing="1.2">{zone_label.upper()}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def macd_tile_svg(macd: str | None, width: int = 280, height: int = 170) -> str:
    """Coloured tile showing MACD posture."""
    s = (macd or "").lower()
    if s in ("bullish", "bull", "positive"):
        bg, fg, label = "#DDF1DE", GREEN, "Bullish"
    elif s in ("bearish", "bear", "negative", "sell"):
        bg, fg, label = "#FAD7D7", RED, "Bearish"
    elif s in ("flat", "neutral", "mixed"):
        bg, fg, label = GRAY_1, MUTED, "Neutral"
    else:
        return _na_box(width, height, "MACD")

    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="MACD posture" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">'
        f'<rect x="6" y="6" width="{width - 12}" height="{height - 12}" rx="10" fill="{bg}" />'
        f'<text x="{width / 2}" y="{height / 2 - 18}" text-anchor="middle" '
        f'font-size="13" font-weight="600" fill="{MUTED}" letter-spacing="2">MACD</text>'
        f'<text x="{width / 2}" y="{height / 2 + 18}" text-anchor="middle" '
        f'font-size="32" font-weight="800" fill="{fg}">{label}</text>'
        f'</svg>'
    )


def ma_position_svg(price: float, ma50: float | None, ma200: float | None,
                    width: int = 280, height: int = 170) -> str:
    """Horizontal mini-bars showing where price sits relative to 50DMA and 200DMA."""
    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Price vs moving averages" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">',
        f'<text x="14" y="22" font-size="13" font-weight="600" fill="{MUTED}" letter-spacing="2">PRICE vs MA</text>',
    ]

    def bar(label: str, ma: float | None, y: float):
        if ma is None or ma == 0:
            parts.append(
                f'<text x="14" y="{y + 18}" font-size="12" fill="{MUTED}">{label}: n/d</text>'
            )
            return
        pct = (price - ma) / ma * 100.0
        # bar centered at x=140, max width ±100
        max_pct = 15.0
        clamped = max(-max_pct, min(max_pct, pct))
        bar_w = clamped / max_pct * 100  # in px
        cx = 140
        color = GREEN if pct >= 0 else RED
        # midline
        parts.append(
            f'<line x1="{cx}" y1="{y + 8}" x2="{cx}" y2="{y + 26}" stroke="{GRAY_3}" stroke-width="1" />'
        )
        # background track
        parts.append(
            f'<rect x="{cx - 100}" y="{y + 14}" width="200" height="6" fill="{GRAY_2}" rx="3" />'
        )
        # value bar
        if bar_w >= 0:
            parts.append(
                f'<rect x="{cx}" y="{y + 14}" width="{bar_w:.1f}" height="6" fill="{color}" rx="3" />'
            )
        else:
            parts.append(
                f'<rect x="{cx + bar_w:.1f}" y="{y + 14}" width="{-bar_w:.1f}" height="6" fill="{color}" rx="3" />'
            )
        # label and value
        parts.append(
            f'<text x="14" y="{y + 18}" font-size="12" fill="{NAVY}" font-weight="600">{label}</text>'
        )
        sign = "+" if pct >= 0 else ""
        parts.append(
            f'<text x="{width - 14}" y="{y + 18}" text-anchor="end" '
            f'font-size="13" font-weight="700" fill="{color}">{sign}{pct:.1f}%</text>'
        )

    bar("50DMA", ma50, 44)
    bar("200DMA", ma200, 92)
    parts.append("</svg>")
    return "".join(parts)


def earnings_tile_svg(in_horizon: bool | None, days_away: int | None, date_str: str | None,
                      width: int = 280, height: int = 170) -> str:
    if in_horizon is None and days_away is None and not date_str:
        return _na_box(width, height, "Earnings")
    if in_horizon:
        bg, fg, label = "#FAD7D7", RED, "INSIDE horizon"
    else:
        bg, fg, label = "#DDF1DE", GREEN, "OUTSIDE horizon"

    days_text = f"{days_away}d away" if days_away is not None else (date_str or "—")
    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Earnings window flag" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">'
        f'<rect x="6" y="6" width="{width - 12}" height="{height - 12}" rx="10" fill="{bg}" />'
        f'<text x="{width / 2}" y="38" text-anchor="middle" '
        f'font-size="13" font-weight="600" fill="{MUTED}" letter-spacing="2">EARNINGS</text>'
        f'<text x="{width / 2}" y="86" text-anchor="middle" '
        f'font-size="22" font-weight="800" fill="{fg}">{esc(date_str or "—")}</text>'
        f'<text x="{width / 2}" y="115" text-anchor="middle" '
        f'font-size="14" font-weight="700" fill="{fg}">{label}</text>'
        f'<text x="{width / 2}" y="140" text-anchor="middle" '
        f'font-size="12" fill="{MUTED}">{esc(days_text)}</text>'
        f'</svg>'
    )


def rr_bar_svg(spec: dict, width: int = 520, height: int = 360) -> str:
    """Risk vs reward visualization. Vertical bar centered on entry-mid: red
    section to stop (downside), green sections to T1 and T2."""
    trade = spec.get("trade", {}) or {}
    entry_low = trade.get("entry_low")
    entry_high = trade.get("entry_high")
    stop = trade.get("stop")
    t1 = trade.get("t1")
    t2 = trade.get("t2")
    price = spec.get("price")

    # determine entry midpoint
    if entry_low is not None and entry_high is not None:
        entry = (entry_low + entry_high) / 2
        entry_label = f"Entry  ${entry_low:,.2f}–${entry_high:,.2f}"
    elif entry_low is not None:
        entry = entry_low
        entry_label = f"Entry  ${entry_low:,.2f}"
    elif price is not None:
        entry = price
        entry_label = f"Entry  ${price:,.2f}"
    else:
        return _na_box(width, height, "Risk / Reward")

    if stop is None or t1 is None:
        return _na_box(width, height, "Risk / Reward")

    risk = entry - stop
    reward1 = t1 - entry
    reward2 = (t2 - entry) if t2 is not None else None
    rr1 = reward1 / risk if risk > 0 else None
    rr2 = (reward2 / risk) if (reward2 is not None and risk > 0) else None

    # Compute scale
    max_above = max(reward1 or 0, reward2 or 0)
    max_below = max(risk, 1e-6)
    total = max_above + max_below
    pad_top = 50
    pad_bot = 50
    plot_h = height - pad_top - pad_bot
    # center y at entry (proportional)
    if total <= 0:
        return _na_box(width, height, "Risk / Reward")
    above_h = max_above / total * plot_h
    below_h = max_below / total * plot_h
    entry_y = pad_top + above_h

    bar_x = width / 2 - 32
    bar_w = 64

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Risk-reward bar" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">',
        # T2 reward (lighter green) — drawn first, behind
    ]
    if reward2 is not None and reward2 > 0:
        t2_h = (reward2) / total * plot_h
        t2_y = entry_y - t2_h
        parts.append(
            f'<rect x="{bar_x}" y="{t2_y:.1f}" width="{bar_w}" height="{t2_h:.1f}" '
            f'fill="{GREEN_LIGHT}" opacity="0.55" rx="6" />'
        )
        parts.append(
            f'<text x="{bar_x + bar_w + 14}" y="{t2_y + 18:.1f}" '
            f'font-size="13" font-weight="700" fill="{GREEN}">T2 ${t2:,.2f}'
            f'{"  ·  " + f"R:R 1:{rr2:.1f}" if rr2 else ""}</text>'
        )
    if reward1 > 0:
        t1_h = reward1 / total * plot_h
        t1_y = entry_y - t1_h
        parts.append(
            f'<rect x="{bar_x}" y="{t1_y:.1f}" width="{bar_w}" height="{t1_h:.1f}" '
            f'fill="{GREEN}" opacity="0.95" rx="6" />'
        )
        parts.append(
            f'<text x="{bar_x + bar_w + 14}" y="{t1_y + 18:.1f}" '
            f'font-size="13" font-weight="700" fill="{GREEN}">T1 ${t1:,.2f}'
            f'{"  ·  " + f"R:R 1:{rr1:.1f}" if rr1 else ""}</text>'
        )
    # Risk (red, downward)
    risk_h = risk / total * plot_h
    parts.append(
        f'<rect x="{bar_x}" y="{entry_y:.1f}" width="{bar_w}" height="{risk_h:.1f}" '
        f'fill="{RED}" opacity="0.9" rx="6" />'
    )
    parts.append(
        f'<text x="{bar_x + bar_w + 14}" y="{entry_y + risk_h - 6:.1f}" '
        f'font-size="13" font-weight="700" fill="{RED}">Stop ${stop:,.2f}  ·  Risk ${risk:,.2f}</text>'
    )

    # Entry line
    parts.append(
        f'<line x1="{bar_x - 10}" y1="{entry_y:.1f}" x2="{bar_x + bar_w + 10}" y2="{entry_y:.1f}" '
        f'stroke="{NAVY}" stroke-width="2.4" />'
    )
    parts.append(
        f'<text x="{bar_x - 14}" y="{entry_y + 4:.1f}" text-anchor="end" '
        f'font-size="13" font-weight="700" fill="{NAVY}">{esc(entry_label)}</text>'
    )

    parts.append("</svg>")
    return "".join(parts)


def _na_box(width: int, height: int, label: str) -> str:
    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{esc(label)} not available" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">'
        f'<rect x="6" y="6" width="{width - 12}" height="{height - 12}" rx="10" '
        f'fill="{GRAY_1}" stroke="{GRAY_2}" stroke-dasharray="4,4" />'
        f'<text x="{width / 2}" y="{height / 2 - 6}" text-anchor="middle" '
        f'font-size="13" font-weight="600" fill="{MUTED}" letter-spacing="2">{esc(label.upper())}</text>'
        f'<text x="{width / 2}" y="{height / 2 + 18}" text-anchor="middle" '
        f'font-size="14" fill="{GRAY_4}" font-style="italic">data not available</text>'
        f'</svg>'
    )


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_1_title(spec: dict) -> str:
    bg, fg = verdict_color(spec.get("verdict", ""))
    hbg, hfg = halal_color(spec.get("halal", {}).get("status", ""))
    price_str = fmt_price(spec.get("price"))
    return f"""
<section class="slide title-slide active">
  <div class="title-bg"></div>
  <div class="title-inner">
    <h3>Swing-Trade Setup</h3>
    <h1>{esc(spec.get('ticker', ''))}<span class="title-name"> · {esc(spec.get('name', ''))}</span></h1>
    <div class="rule"></div>
    <div class="title-row">
      <div class="title-stat">
        <span class="title-label">As of</span>
        <span class="title-value">{esc(spec.get('as_of', ''))}</span>
      </div>
      <div class="title-stat">
        <span class="title-label">Price</span>
        <span class="title-value">{esc(price_str)}</span>
      </div>
      <div class="title-stat">
        <span class="title-label">Halal</span>
        <span class="title-pill" style="background:{hbg};color:{hfg};">{esc(spec.get('halal', {}).get('status', '—'))}</span>
      </div>
    </div>
    <div class="big-verdict">
      <div class="verdict-pill" style="background:{bg};color:{fg};">{esc(spec.get('verdict', '—'))}</div>
      <p class="verdict-reason">{esc(spec.get('verdict_reason', ''))}</p>
    </div>
  </div>
</section>
"""


def slide_2_trend_halal(spec: dict) -> str:
    halal = spec.get("halal", {}) or {}
    hbg, hfg = halal_color(halal.get("status", ""))
    non_compliant_callout = ""
    if (halal.get("status") or "").lower() == "non-compliant":
        non_compliant_callout = f"""
<div class="callout">
  <strong>Halal-mandate readers:</strong> this trade is not yours to take. The verdict on slide 1 already reflects that, regardless of how the chart looks.
</div>
"""
    return f"""
<section class="slide">
  <h3>Trend &amp; Halal flag</h3>
  <h1>The setup in one read</h1>
  <div class="rule"></div>
  <div class="halal-card">
    <span class="title-label">Halal status</span>
    <div class="halal-row">
      <span class="halal-pill" style="background:{hbg};color:{hfg};">{esc(halal.get('status', '—'))}</span>
      <p class="halal-summary">{esc(halal.get('summary', ''))}</p>
    </div>
    {non_compliant_callout}
  </div>
  <div class="trend-card">
    <span class="title-label">Trend read</span>
    <p class="trend-text">{esc(spec.get('trend', ''))}</p>
  </div>
</section>
"""


def slide_3_levels(spec: dict) -> str:
    chart = levels_chart_svg(spec)
    return f"""
<section class="slide">
  <h3>Key levels</h3>
  <h1>Where the trader cares about price</h1>
  <div class="rule"></div>
  <div class="chart-wrap">{chart}</div>
  <p class="caption">Supports · resistances · 50DMA / 200DMA · entry zone (amber) · stop (red) · targets (green) · current price (navy).</p>
</section>
"""


def slide_4_indicators(spec: dict) -> str:
    ind = spec.get("indicators", {}) or {}
    rsi = ind.get("rsi")
    rsi_note = ind.get("rsi_note")
    macd = ind.get("macd")
    macd_note = ind.get("macd_note")
    ma50 = spec.get("ma50")
    ma200 = spec.get("ma200")
    price = spec.get("price")
    next_e = ind.get("next_earnings")
    in_h = ind.get("earnings_in_horizon")
    days_a = ind.get("earnings_days_away")
    beta = ind.get("beta")
    dvol = ind.get("daily_vol_pct")

    return f"""
<section class="slide">
  <h3>Indicator dashboard</h3>
  <h1>Momentum, trend, and the earnings clock</h1>
  <div class="rule"></div>
  <div class="ind-grid">
    <div class="ind-card">{rsi_gauge_svg(rsi)}{f'<p class="ind-note">{esc(rsi_note)}</p>' if rsi_note else ''}</div>
    <div class="ind-card">{macd_tile_svg(macd)}{f'<p class="ind-note">{esc(macd_note)}</p>' if macd_note else ''}</div>
    <div class="ind-card">{ma_position_svg(price, ma50, ma200)}</div>
    <div class="ind-card">{earnings_tile_svg(in_h, days_a, next_e)}</div>
  </div>
  <div class="stat-strip">
    <div><span class="title-label">Beta</span><span class="strip-val">{esc(beta) if beta is not None else 'n/d'}</span></div>
    <div><span class="title-label">Daily vol</span><span class="strip-val">{('{:.1f}%'.format(dvol)) if dvol is not None else 'n/d'}</span></div>
    <div><span class="title-label">Position size</span><span class="strip-val">{esc(spec.get('trade', {}).get('sizing', '—'))}</span></div>
  </div>
</section>
"""


def slide_5_setup(spec: dict) -> str:
    trade = spec.get("trade", {}) or {}

    def row(k: str, v: Any) -> str:
        return f"<tr><td>{esc(k)}</td><td>{esc(v) if v is not None else '—'}</td></tr>"

    entry_a = ""
    if trade.get("entry_low") is not None and trade.get("entry_high") is not None:
        entry_a = f"${trade['entry_low']:,.2f} – ${trade['entry_high']:,.2f}"
    elif trade.get("entry_low") is not None:
        entry_a = f"${trade['entry_low']:,.2f}"
    rows = [
        row("Direction", trade.get("direction")),
        row("Entry A", entry_a or "—"),
        row("Entry B", trade.get("entry_b_label")),
        row("Stop-loss", fmt_price(trade.get("stop"))),
        row("Target 1", fmt_price(trade.get("t1"))),
        row("Target 2", fmt_price(trade.get("t2"))),
        row("R:R (Entry → T1)", f"≈ 1 : {trade['rr_t1']:.1f}" if trade.get("rr_t1") else "—"),
        row("R:R (Entry → T2)", f"≈ 1 : {trade['rr_t2']:.1f}" if trade.get("rr_t2") else "—"),
        row("Position sizing", trade.get("sizing")),
        row("Invalidation", trade.get("invalidation")),
    ]
    return f"""
<section class="slide">
  <h3>Trade setup</h3>
  <h1>Entry, stop, targets, sizing</h1>
  <div class="rule"></div>
  <div class="setup-grid">
    <table class="setup-table">
      <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    <div class="rr-wrap">{rr_bar_svg(spec)}</div>
  </div>
</section>
"""


def slide_6_summary(spec: dict) -> str:
    bg, fg = verdict_color(spec.get("verdict", ""))
    cats = spec.get("catalysts", []) or []
    srcs = spec.get("sources", []) or []
    cats_html = "".join(f"<li>{esc(c)}</li>" for c in cats) or "<li class='muted'>No specific catalysts identified inside the swing horizon.</li>"
    srcs_html = "".join(
        f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s.get("label") or s["url"])}</a></li>'
        for s in srcs
    )
    return f"""
<section class="slide">
  <h3>Catalysts &amp; verdict</h3>
  <h1>What to watch — and the call</h1>
  <div class="rule"></div>
  <div class="summary-grid">
    <div>
      <h2 class="sub">Catalysts inside horizon</h2>
      <ul class="catalysts">{cats_html}</ul>
      <h2 class="sub">Sources</h2>
      <ul class="sources">{srcs_html or '<li class="muted">No public sources cited.</li>'}</ul>
    </div>
    <div>
      <div class="verdict-card">
        <span class="title-label">Verdict</span>
        <div class="verdict-pill big" style="background:{bg};color:{fg};">{esc(spec.get('verdict', '—'))}</div>
        <p class="verdict-reason">{esc(spec.get('verdict_reason', ''))}</p>
      </div>
    </div>
  </div>
  <p class="disclaimer">Technical read, not financial advice — do your own due diligence.</p>
</section>
"""


# ---------------------------------------------------------------------------
# CSS / JS
# ---------------------------------------------------------------------------

CSS = f"""
:root {{
  --navy: {NAVY};
  --navy-2: {NAVY_2};
  --amber: {AMBER};
  --amber-2: {AMBER_2};
  --green: {GREEN};
  --red: {RED};
  --gray-1: {GRAY_1};
  --gray-2: {GRAY_2};
  --gray-3: {GRAY_3};
  --gray-4: {GRAY_4};
  --ink: {INK};
  --muted: {MUTED};
}}
* {{ box-sizing: border-box; }}
html, body {{
  margin: 0; padding: 0; height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  color: var(--ink); background: #0a0f15; overflow: hidden;
}}
.deck {{ position: relative; width: 100vw; height: 100vh; overflow: hidden; }}
.slide {{
  position: absolute; inset: 0; background: #fff;
  padding: 56px 72px 72px;
  display: flex; flex-direction: column;
  opacity: 0; transform: translateX(28px);
  transition: opacity .25s ease, transform .25s ease;
  pointer-events: none; overflow-y: auto;
}}
.slide.active {{ opacity: 1; transform: none; pointer-events: auto; }}
.slide h1 {{ color: var(--navy); margin: 0; font-size: 32px; line-height: 1.15; letter-spacing: -.4px; }}
.slide h2 {{ color: var(--navy); margin: 0 0 12px 0; font-size: 18px; }}
.slide h3 {{ color: var(--amber); margin: 0; font-size: 13px; text-transform: uppercase; letter-spacing: .14em; font-weight: 700; }}
.slide p {{ font-size: 15.5px; line-height: 1.5; }}
.rule {{ height: 3px; width: 88px; background: var(--amber); margin: 12px 0 22px; border-radius: 2px; }}
.title-label {{
  display: block; font-size: 11px; color: var(--muted);
  text-transform: uppercase; letter-spacing: .12em; font-weight: 700;
  margin-bottom: 4px;
}}
.muted {{ color: var(--muted); }}

/* Title slide */
.title-slide {{ padding: 0; color: #fff; }}
.title-bg {{
  position: absolute; inset: 0;
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-2) 100%);
}}
.title-inner {{ position: relative; padding: 80px 96px; flex: 1; display: flex; flex-direction: column; }}
.title-slide h3 {{ color: var(--amber-2); }}
.title-slide h1 {{ color: #fff; font-size: 64px; line-height: 1.05; letter-spacing: -1.5px; }}
.title-slide .rule {{ background: var(--amber); }}
.title-name {{ font-weight: 400; color: rgba(255,255,255,.7); font-size: .55em; vertical-align: middle; }}
.title-row {{
  display: flex; gap: 36px; margin: 18px 0 28px; color: rgba(255,255,255,.92);
}}
.title-row .title-label {{ color: var(--amber-2); }}
.title-row .title-value {{ font-size: 22px; font-weight: 700; }}
.title-pill {{
  display: inline-block; padding: 4px 14px; border-radius: 999px;
  font-size: 13px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
}}
.big-verdict {{ margin-top: auto; padding-top: 24px; }}
.verdict-pill {{
  display: inline-block; padding: 14px 36px; border-radius: 14px;
  font-size: 48px; font-weight: 800; letter-spacing: 4px;
}}
.verdict-pill.big {{ font-size: 40px; padding: 12px 30px; }}
.verdict-reason {{ font-size: 18px; max-width: 760px; margin-top: 16px; color: rgba(255,255,255,.92); }}

/* Trend & Halal */
.halal-card, .trend-card {{
  border: 1px solid var(--gray-2); border-radius: 12px;
  padding: 18px 22px; margin-bottom: 16px; background: #fff;
}}
.halal-card {{ background: var(--gray-1); }}
.halal-row {{ display: flex; gap: 18px; align-items: center; }}
.halal-pill {{
  display: inline-block; padding: 8px 18px; border-radius: 999px;
  font-size: 14px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
  white-space: nowrap;
}}
.halal-summary {{ margin: 0; flex: 1; color: var(--ink); }}
.callout {{
  margin-top: 14px; padding: 12px 16px; border-radius: 8px;
  background: #FAD7D7; border-left: 4px solid var(--red);
  color: var(--red); font-size: 14.5px;
}}
.trend-text {{ margin: 0; }}

/* Levels chart */
.chart-wrap {{
  flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center;
  background: #fff; border: 1px solid var(--gray-2); border-radius: 12px;
  padding: 16px;
}}
.chart-wrap svg {{ width: 100%; height: auto; max-height: 100%; }}
.caption {{ font-size: 12.5px; color: var(--muted); margin: 12px 0 0; text-align: center; }}

/* Indicator dashboard */
.ind-grid {{
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  flex: 1; min-height: 0;
}}
.ind-card {{
  border: 1px solid var(--gray-2); border-radius: 12px; padding: 12px;
  background: #fff; display: flex; flex-direction: column;
  align-items: center; justify-content: flex-start;
}}
.ind-card svg {{ width: 100%; height: auto; }}
.ind-note {{ font-size: 12px; color: var(--muted); margin: 6px 4px 0; text-align: center; }}
.stat-strip {{
  display: flex; gap: 36px; margin-top: 18px; padding: 14px 18px;
  background: var(--gray-1); border-radius: 10px;
}}
.stat-strip > div {{ display: flex; flex-direction: column; }}
.strip-val {{ font-size: 18px; font-weight: 700; color: var(--navy); }}

/* Setup slide */
.setup-grid {{
  display: grid; grid-template-columns: 1fr 1fr; gap: 28px;
  flex: 1; min-height: 0; align-items: stretch;
}}
.setup-table {{
  width: 100%; border-collapse: collapse; font-size: 14px; align-self: start;
}}
.setup-table th {{
  background: var(--navy); color: #fff; text-align: left; padding: 10px 14px;
  font-size: 12px; text-transform: uppercase; letter-spacing: .08em;
}}
.setup-table td {{ padding: 9px 14px; border-bottom: 1px solid var(--gray-2); }}
.setup-table td:first-child {{ font-weight: 600; color: var(--navy); width: 40%; }}
.setup-table tr:nth-child(even) td {{ background: var(--gray-1); }}
.rr-wrap {{
  border: 1px solid var(--gray-2); border-radius: 12px; padding: 12px;
  display: flex; align-items: center; justify-content: center; background: #fff;
}}
.rr-wrap svg {{ width: 100%; height: auto; max-height: 360px; }}

/* Summary slide */
.summary-grid {{
  display: grid; grid-template-columns: 1.2fr 1fr; gap: 28px;
  flex: 1; min-height: 0;
}}
.sub {{ font-size: 13px; color: var(--amber); text-transform: uppercase; letter-spacing: .12em; margin: 12px 0 8px; }}
.catalysts li, .sources li {{ font-size: 14px; line-height: 1.5; margin: 4px 0; }}
.sources a {{ color: var(--navy); text-decoration: none; border-bottom: 1px dotted var(--navy); }}
.sources a:hover {{ color: var(--amber); border-bottom-color: var(--amber); }}
.verdict-card {{
  background: var(--gray-1); border-radius: 12px; padding: 22px; height: 100%;
  display: flex; flex-direction: column; justify-content: center; align-items: flex-start;
}}
.verdict-card .verdict-reason {{ color: var(--ink); font-size: 15px; margin-top: 14px; }}
.disclaimer {{
  margin-top: 18px; font-size: 12.5px; color: var(--muted); font-style: italic;
}}

/* Footer / nav */
.footer {{
  position: absolute; left: 72px; right: 72px; bottom: 18px;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 12px; color: var(--muted);
}}
.title-slide ~ .footer, .footer.title {{}}
.nav {{ display: flex; gap: 8px; align-items: center; }}
.nav button {{
  background: #fff; border: 1px solid var(--gray-3); color: var(--navy);
  padding: 4px 12px; border-radius: 6px; cursor: pointer; font-size: 12px;
}}
.nav button:hover {{ background: var(--gray-1); }}
.progress {{
  position: absolute; left: 0; top: 0; height: 3px; background: var(--amber);
  width: 0; transition: width .25s ease; z-index: 10;
}}
.keypress {{
  font-family: ui-monospace, "SF Mono", Menlo, monospace;
  font-size: 11px; padding: 1px 6px; border: 1px solid var(--gray-3);
  border-radius: 4px; background: #fff; color: var(--navy);
}}
"""


JS = """
(function(){
  const slides = Array.from(document.querySelectorAll('.slide'));
  const counter = document.getElementById('counter');
  const progress = document.getElementById('progress');
  let i = 0;
  function show(n){
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach((s, idx) => s.classList.toggle('active', idx === i));
    counter.textContent = (i + 1) + ' / ' + slides.length;
    progress.style.width = ((i + 1) / slides.length * 100) + '%';
    slides[i].scrollTop = 0;
  }
  document.getElementById('prev').onclick = () => show(i - 1);
  document.getElementById('next').onclick = () => show(i + 1);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') { e.preventDefault(); show(i + 1); }
    if (e.key === 'ArrowLeft'  || e.key === 'PageUp')                   { e.preventDefault(); show(i - 1); }
    if (e.key === 'Home') show(0);
    if (e.key === 'End')  show(slides.length - 1);
  });
  show(0);
})();
"""


# ---------------------------------------------------------------------------
# Top-level HTML assembly
# ---------------------------------------------------------------------------

def build_html(spec: dict) -> str:
    title = f"{spec.get('ticker', 'Setup')} — Swing Trade Setup ({spec.get('as_of', '')})"
    slides_html = (
        slide_1_title(spec)
        + slide_2_trend_halal(spec)
        + slide_3_levels(spec)
        + slide_4_indicators(spec)
        + slide_5_setup(spec)
        + slide_6_summary(spec)
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="deck" id="deck">
  <div class="progress" id="progress"></div>
  {slides_html}
  <div class="footer">
    <div>{esc(spec.get('ticker', ''))} swing setup · {esc(spec.get('as_of', ''))}</div>
    <div class="nav">
      <button id="prev">‹ Prev</button>
      <span id="counter">1 / 6</span>
      <button id="next">Next ›</button>
      <span style="margin-left: 12px;">Use <span class="keypress">←</span> <span class="keypress">→</span> to navigate</span>
    </div>
  </div>
</div>
<script>{JS}</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build a swing-trade-setup HTML slide deck.")
    p.add_argument("--spec", required=True, help="Path to JSON spec file (schema in references/output_template.md).")
    p.add_argument("--out", required=True, help="Output HTML file path.")
    args = p.parse_args(argv)

    with open(args.spec, "r", encoding="utf-8") as f:
        spec = json.load(f)

    # minimal validation
    required = ["ticker", "name", "as_of", "verdict", "verdict_reason", "halal", "trend", "price"]
    missing = [k for k in required if k not in spec]
    if missing:
        print(f"[build_slides] WARNING: spec missing required fields: {missing}", file=sys.stderr)

    html_doc = build_html(spec)
    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
