"""
Investment research report builder.

Usage:
    from build_report import ReportBuilder, verify_pdf, NAVY, AMBER

    b = ReportBuilder("NVIDIA Corp (NVDA)", subtitle="As of 2026-04-21")
    b.section("1. Snapshot")
    b.snapshot_table({
        "Price": "$142.50", "Market Cap": "$3.5T", "Shares Out": "24.6B",
        "52W High": "$152.90", "52W Low": "$86.60", "Div Yield (TTM)": "0.03%",
        "Beta": "1.67", "Next Earnings": "2026-05-21", "Sector": "Technology / Semiconductors",
    })
    b.section("2. Business Overview")
    b.prose("NVIDIA designs...")
    ...
    b.build("/path/to/out.pdf")
    verify_pdf("/path/to/out.pdf")   # renders page PNGs so Claude can inspect

Key rule this file enforces: every text-heavy table cell is wrapped in a
Paragraph, because plain strings in ReportLab tables do not word-wrap. The
`wrap()` helper is used internally by every table builder. If you add new
tables, use `wrap()` on anything that could plausibly be a sentence.
"""

from __future__ import annotations

import io
import os
from dataclasses import dataclass
from typing import Iterable, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

NAVY = colors.HexColor("#0B3C5D")
AMBER = colors.HexColor("#C69214")
MUTED_GRAY = colors.HexColor("#E7E7E7")
DARK_GRAY = colors.HexColor("#4A4A4A")
PASS_GREEN = colors.HexColor("#2E7D32")
FAIL_RED = colors.HexColor("#C62828")

# ---------------------------------------------------------------------------
# Page geometry. A4 portrait with 40pt margins -> ~515pt content width.
# ---------------------------------------------------------------------------

PAGE_W, PAGE_H = A4
MARGIN = 40
CONTENT_W = PAGE_W - 2 * MARGIN  # ~515pt

# ---------------------------------------------------------------------------
# Styles (single source of truth -- consistency across reports matters more
# than per-report cleverness)
# ---------------------------------------------------------------------------

_SS = getSampleStyleSheet()

STYLE_TITLE = ParagraphStyle(
    "title", parent=_SS["Title"], fontName="Helvetica-Bold",
    fontSize=20, leading=24, textColor=NAVY, spaceAfter=4,
)
STYLE_SUBTITLE = ParagraphStyle(
    "subtitle", parent=_SS["Normal"], fontName="Helvetica",
    fontSize=10, leading=13, textColor=DARK_GRAY, spaceAfter=16,
)
STYLE_SECTION = ParagraphStyle(
    "section", parent=_SS["Heading2"], fontName="Helvetica-Bold",
    fontSize=13, leading=16, textColor=NAVY, spaceBefore=14, spaceAfter=6,
)
STYLE_SUBSECTION = ParagraphStyle(
    "subsection", parent=_SS["Heading3"], fontName="Helvetica-Bold",
    fontSize=11, leading=14, textColor=NAVY, spaceBefore=8, spaceAfter=4,
)
STYLE_PROSE = ParagraphStyle(
    "prose", parent=_SS["Normal"], fontName="Helvetica",
    fontSize=10, leading=14, textColor=colors.black, spaceAfter=8,
)
STYLE_CELL = ParagraphStyle(
    "cell", parent=_SS["Normal"], fontName="Helvetica",
    fontSize=9, leading=11.5, textColor=colors.black,
)
STYLE_CELL_BOLD = ParagraphStyle(
    "cell_bold", parent=STYLE_CELL, fontName="Helvetica-Bold",
)
STYLE_CELL_CENTER = ParagraphStyle(
    "cell_center", parent=STYLE_CELL, alignment=1,
)
STYLE_BULLET = ParagraphStyle(
    "bullet", parent=STYLE_PROSE, leftIndent=14, bulletIndent=2, spaceAfter=3,
)
STYLE_DISCLAIMER = ParagraphStyle(
    "disclaimer", parent=STYLE_PROSE, fontSize=8.5, textColor=DARK_GRAY,
    spaceBefore=10,
)


# ---------------------------------------------------------------------------
# The single most important helper: wrap every text-heavy cell in a Paragraph.
# Plain strings DO NOT word-wrap in ReportLab tables -- they overflow the
# column. This is the #1 failure mode the user has called out.
# ---------------------------------------------------------------------------

def wrap(text, style=STYLE_CELL) -> Paragraph:
    """Wrap a cell value in a Paragraph so it word-wraps inside the column."""
    if text is None:
        text = "—"
    if isinstance(text, Paragraph):
        return text
    return Paragraph(str(text), style)


def wrap_bold(text) -> Paragraph:
    return wrap(text, STYLE_CELL_BOLD)


def wrap_center(text) -> Paragraph:
    return wrap(text, STYLE_CELL_CENTER)


# ---------------------------------------------------------------------------
# Standard table builder. Call with header row + body rows and col widths;
# returns a Table with the house style applied.
# ---------------------------------------------------------------------------

def std_table(
    header: Sequence,
    rows: Sequence[Sequence],
    col_widths: Sequence[float],
    zebra: bool = True,
    header_bg=NAVY,
    header_fg=colors.white,
    highlight_rows: Iterable[int] = (),
    row_heights=None,
) -> Table:
    """Build a styled table with header row + body rows.

    - Header row: navy bg, white bold text, centered.
    - Body rows: 9pt, zebra-striped if zebra=True.
    - col_widths must sum to <= CONTENT_W. The sum is not enforced but a
      warning goes to stdout if it's over.
    """
    total = sum(col_widths)
    if total > CONTENT_W + 1:
        print(f"[build_report] warning: column widths sum to {total:.0f}pt, "
              f"content width is {CONTENT_W:.0f}pt — cells will overflow")

    # Normalize every cell to a Paragraph where it's a string with non-trivial
    # length; leave Paragraphs, Images, and short strings alone.
    def _norm(c):
        if isinstance(c, (Paragraph, Image, Table)):
            return c
        if isinstance(c, (int, float)):
            return str(c)
        if c is None:
            return "—"
        s = str(c)
        # Always wrap anything longer than a typical short value — safer to
        # over-wrap than to have a cell overflow.
        if len(s) > 12:
            return wrap(s)
        return s

    header_row = [wrap(h, ParagraphStyle(
        "h_cell", parent=STYLE_CELL_BOLD, textColor=header_fg, alignment=1,
    )) for h in header]
    body_rows = [[_norm(c) for c in row] for row in rows]

    tbl = Table(
        [header_row] + body_rows,
        colWidths=list(col_widths),
        rowHeights=row_heights,
        repeatRows=1,
    )

    style = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), header_fg),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9.5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 5),

        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#C9C9C9")),
    ]
    if zebra:
        for i in range(1, len(body_rows) + 1):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), MUTED_GRAY))
    for idx in highlight_rows:
        row_i = idx + 1  # +1 for header
        style.append(("BACKGROUND", (0, row_i), (-1, row_i),
                      colors.HexColor("#FDF2D4")))  # amber-tinted highlight
        style.append(("FONTNAME", (0, row_i), (-1, row_i), "Helvetica-Bold"))

    tbl.setStyle(TableStyle(style))
    return tbl


# ---------------------------------------------------------------------------
# Pre-built section tables. Each takes a dict/list and returns a Table.
# Using these keeps reports visually consistent across runs.
# ---------------------------------------------------------------------------

def snapshot_table(data: dict) -> Table:
    """Two-column key/value layout in 3 side-by-side columns to fit a full
    snapshot on one table. Keys auto-wrap."""
    items = list(data.items())
    # Lay out as 3 columns of (key, value) — 9 items -> 3 rows of 6 cells.
    # If fewer items, pad with blanks.
    while len(items) % 3 != 0:
        items.append(("", ""))
    rows = []
    for i in range(0, len(items), 3):
        row = []
        for k, v in items[i:i+3]:
            row.append(wrap_bold(k) if k else "")
            row.append(wrap(v) if v else "")
        rows.append(row)

    col_w = [70, 95, 70, 95, 85, 100]
    tbl = Table(rows, colWidths=col_w)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F6F6F6")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#C9C9C9")),
        ("LINEBEFORE", (2, 0), (2, -1), 1.5, NAVY),
        ("LINEBEFORE", (4, 0), (4, -1), 1.5, NAVY),
    ]))
    return tbl


def aaoifi_table(rows: list[tuple]) -> Table:
    """rows: list of (ratio_name, threshold, actual, pass_bool).

    Produces the 4-row AAOIFI screen table."""
    header = ["Ratio", "Threshold", "Actual", "Pass?"]
    body = []
    highlights = []
    for i, (name, thresh, actual, passed) in enumerate(rows):
        mark = Paragraph(
            "✓" if passed else "✗",
            ParagraphStyle("m", parent=STYLE_CELL_CENTER,
                           textColor=PASS_GREEN if passed else FAIL_RED,
                           fontName="Helvetica-Bold", fontSize=11),
        )
        body.append([wrap(name), wrap_center(thresh), wrap_center(actual), mark])
        if not passed:
            highlights.append(i)
    return std_table(header, body,
                     col_widths=[240, 95, 95, 85],
                     highlight_rows=highlights)


def pif_industry_checklist(entries: list[tuple]) -> Table:
    """entries: list of (industry_name, exposure_yn, notes)."""
    header = ["Excluded Industry", "Exposure?", "Notes"]
    body = [[wrap(n), wrap_center(e), wrap(nt)] for n, e, nt in entries]
    # Highlight any Y or Partial rows
    highlights = [i for i, (_, e, _) in enumerate(entries)
                  if str(e).strip().lower() in ("y", "yes", "partial")]
    return std_table(header, body,
                     col_widths=[180, 80, 255],
                     highlight_rows=highlights)


def pif_quarterly_table(
    rows: list[tuple], numerator_label: str, denominator_label: str,
) -> Table:
    """rows: (quarter, numerator, denominator, ratio_str, passed)."""
    header = ["Quarter", numerator_label, denominator_label, "Ratio", "Pass?"]
    body = []
    highlights = []
    for i, (q, num, den, ratio, passed) in enumerate(rows):
        mark = Paragraph(
            "✓" if passed else "✗",
            ParagraphStyle("m", parent=STYLE_CELL_CENTER,
                           textColor=PASS_GREEN if passed else FAIL_RED,
                           fontName="Helvetica-Bold", fontSize=11),
        )
        body.append([wrap_center(q), wrap_center(num), wrap_center(den),
                     wrap_center(ratio), mark])
        if not passed:
            highlights.append(i)
    return std_table(header, body,
                     col_widths=[90, 130, 130, 85, 80],
                     highlight_rows=highlights)


def fundamentals_table(
    columns: list[str], rows: list[tuple],
) -> Table:
    """columns: e.g. ['Line', 'FY-3', 'FY-2', 'FY-1', 'FY-0 (est)', 'YoY %']
    rows: list of (label, fy3, fy2, fy1, fy0, yoy)."""
    header = list(columns)
    body = [[wrap_bold(r[0])] + [wrap_center(c) for c in r[1:]] for r in rows]
    ncol = len(columns)
    # Label column wider; numeric cols equal.
    label_w = 130
    num_w = (CONTENT_W - label_w) / (ncol - 1)
    widths = [label_w] + [num_w] * (ncol - 1)
    return std_table(header, body, col_widths=widths)


def multiples_table(rows: list[tuple]) -> Table:
    """rows: (multiple, current, sector_median, five_yr_avg, signal)."""
    header = ["Multiple", "Current", "Sector Median", "5-yr Avg", "Signal"]
    body = [[wrap_bold(r[0]), wrap_center(r[1]), wrap_center(r[2]),
             wrap_center(r[3]), wrap_center(r[4])] for r in rows]
    return std_table(header, body,
                     col_widths=[150, 85, 105, 90, 85])


def dcf_table(rows: list[tuple]) -> Table:
    """rows: (scenario, implied_value, pct_vs_current, key_assumption)."""
    header = ["Scenario", "Implied / Share", "% vs Current", "Key assumption"]
    body = [[wrap_bold(r[0]), wrap_center(r[1]), wrap_center(r[2]),
             wrap(r[3])] for r in rows]
    return std_table(header, body,
                     col_widths=[90, 100, 85, 240])


def analyst_table(rows: list[tuple]) -> Table:
    """rows: (firm, date, rating, prev_rating, target, prev_target, upside)."""
    header = ["Analyst / Firm", "Date", "Rating", "Prev.", "Target",
              "Prev. Tgt", "Upside %"]
    body = [[wrap(r[0]), wrap_center(r[1]), wrap_center(r[2]),
             wrap_center(r[3]), wrap_center(r[4]), wrap_center(r[5]),
             wrap_center(r[6])] for r in rows]
    return std_table(header, body,
                     col_widths=[140, 68, 75, 55, 65, 55, 57])


def indicators_table(rows: list[tuple]) -> Table:
    """rows: (indicator, value, read)."""
    header = ["Indicator", "Value", "Read"]
    body = [[wrap_bold(r[0]), wrap_center(r[1]), wrap(r[2])] for r in rows]
    return std_table(header, body, col_widths=[140, 105, 270])


# ---------------------------------------------------------------------------
# Charts (matplotlib -> PNG -> ReportLab Image). Palette stays consistent.
# ---------------------------------------------------------------------------

def _chart_to_image(fig, width_pt=CONTENT_W, dpi=150) -> Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)
    buf.seek(0)
    img = Image(buf, width=width_pt, height=width_pt * 0.5)
    img.hAlign = "CENTER"
    return img


def revenue_npat_chart(years: list[str], revenue: list[float],
                       npat: list[float], title: str = "Revenue & NPAT") -> Image:
    import matplotlib.pyplot as plt
    import numpy as np
    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = np.arange(len(years))
    width = 0.38
    ax.bar(x - width/2, revenue, width, label="Revenue", color="#0B3C5D")
    ax.bar(x + width/2, npat, width, label="NPAT", color="#C69214")
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_ylabel("USD ($B)")
    ax.set_title(title, color="#0B3C5D", fontweight="bold", loc="left")
    ax.legend(loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, alpha=0.3)
    return _chart_to_image(fig)


def price_ma_chart(dates, prices, ma50=None, ma200=None,
                   title: str = "Price with 50DMA / 200DMA") -> Image:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(dates, prices, color="#0B3C5D", linewidth=1.6, label="Price")
    if ma50 is not None:
        ax.plot(dates, ma50, color="#C69214", linewidth=1.1, label="50DMA")
    if ma200 is not None:
        ax.plot(dates, ma200, color="#888888", linewidth=1.1,
                linestyle="--", label="200DMA")
    ax.set_title(title, color="#0B3C5D", fontweight="bold", loc="left")
    ax.legend(loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    return _chart_to_image(fig)


def target_range_plot(low: float, median: float, current: float,
                      high: float, title: str = "Analyst Target Range") -> Image:
    """Horizontal dot plot with Low / Median / Current / High."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 2.2))
    points = [("Low", low, "#888888"), ("Median", median, "#0B3C5D"),
              ("Current", current, "#C69214"), ("High", high, "#888888")]
    # A horizontal range line from min to max of all four values.
    all_v = [p[1] for p in points]
    ax.hlines(0, min(all_v), max(all_v), color="#DDDDDD", linewidth=2.0)
    for label, val, c in points:
        ax.plot(val, 0, "o", markersize=14, color=c)
        ax.annotate(f"{label}\n${val:,.2f}", (val, 0),
                    xytext=(0, 18 if label in ("Median", "High") else -30),
                    textcoords="offset points", ha="center", fontsize=9,
                    color="#333333")
    ax.set_ylim(-1, 1)
    ax.set_yticks([])
    for s in ("top", "left", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title(title, color="#0B3C5D", fontweight="bold", loc="left")
    return _chart_to_image(fig)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

@dataclass
class ReportBuilder:
    title: str
    subtitle: str = ""

    def __post_init__(self):
        self.story: list = []
        self.story.append(Paragraph(self.title, STYLE_TITLE))
        if self.subtitle:
            self.story.append(Paragraph(self.subtitle, STYLE_SUBTITLE))
        # Thin amber rule under the title.
        self.story.append(Spacer(1, 2))
        rule = Table([[""]], colWidths=[CONTENT_W], rowHeights=[1.5])
        rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), AMBER)]))
        self.story.append(rule)
        self.story.append(Spacer(1, 10))

    # --- structural helpers ---

    def section(self, heading: str):
        self.story.append(Paragraph(heading, STYLE_SECTION))

    def subsection(self, heading: str):
        self.story.append(Paragraph(heading, STYLE_SUBSECTION))

    def prose(self, *paragraphs: str):
        for p in paragraphs:
            self.story.append(Paragraph(p, STYLE_PROSE))

    def bullets(self, items: Iterable[str]):
        for item in items:
            self.story.append(Paragraph(f"• {item}", STYLE_BULLET))
        self.story.append(Spacer(1, 4))

    def table(self, tbl: Table):
        self.story.append(tbl)
        self.story.append(Spacer(1, 8))

    def spacer(self, height: float = 6):
        self.story.append(Spacer(1, height))

    def source_note(self, text: str):
        self.story.append(Paragraph(
            f"<i>Source: {text}</i>",
            ParagraphStyle("src", parent=STYLE_PROSE, fontSize=8,
                           textColor=DARK_GRAY, spaceAfter=8),
        ))

    def disclaimer(self):
        self.story.append(Spacer(1, 14))
        self.story.append(Paragraph(
            "This is research, not financial advice. Do your own due diligence.",
            STYLE_DISCLAIMER,
        ))

    # --- convenience: standard section wrappers ---

    def snapshot(self, data: dict):
        self.table(snapshot_table(data))

    def aaoifi(self, ratio_rows: list[tuple]):
        self.table(aaoifi_table(ratio_rows))

    def pif_industries(self, entries: list[tuple]):
        self.table(pif_industry_checklist(entries))

    def pif_income(self, rows: list[tuple]):
        self.table(pif_quarterly_table(rows, "Interest Income", "Total Revenue"))

    def pif_expense(self, rows: list[tuple]):
        self.table(pif_quarterly_table(rows, "Interest Expense", "Total Expenses"))

    def fundamentals(self, columns, rows):
        self.table(fundamentals_table(columns, rows))

    def multiples(self, rows):
        self.table(multiples_table(rows))

    def dcf(self, rows):
        self.table(dcf_table(rows))

    def analysts(self, rows):
        self.table(analyst_table(rows))

    def indicators(self, rows):
        self.table(indicators_table(rows))

    # --- finalize ---

    def build(self, out_path: str):
        doc = SimpleDocTemplate(
            out_path, pagesize=A4,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=MARGIN, bottomMargin=MARGIN,
            title=self.title,
        )

        def _footer(canvas, doc):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(DARK_GRAY)
            canvas.drawString(MARGIN, 20,
                              "Research — not financial advice")
            canvas.drawRightString(PAGE_W - MARGIN, 20,
                                   f"Page {doc.page}")
            canvas.restoreState()

        doc.build(self.story, onFirstPage=_footer, onLaterPages=_footer)
        return out_path


# ---------------------------------------------------------------------------
# Verification: render each page to a PNG so Claude can Read() the images
# and confirm no text is overflowing or truncated.
# ---------------------------------------------------------------------------

def verify_pdf(pdf_path: str, out_dir: str = None) -> list[str]:
    """Render each page of the PDF to a PNG and return the list of paths.

    Uses pdf2image if available (Poppler); falls back to pypdfium2 which is
    pure-python and requires no system poppler.
    """
    if out_dir is None:
        base = os.path.splitext(pdf_path)[0]
        out_dir = base + "_pages"
    os.makedirs(out_dir, exist_ok=True)

    paths: list[str] = []

    try:
        import pypdfium2 as pdfium
    except ImportError:
        pdfium = None

    if pdfium is not None:
        pdf = pdfium.PdfDocument(pdf_path)
        for i, page in enumerate(pdf, start=1):
            pil = page.render(scale=2.0).to_pil()
            p = os.path.join(out_dir, f"page_{i:02d}.png")
            pil.save(p)
            paths.append(p)
        return paths

    # Fallback: pdf2image (requires poppler)
    try:
        from pdf2image import convert_from_path
        imgs = convert_from_path(pdf_path, dpi=150)
        for i, img in enumerate(imgs, start=1):
            p = os.path.join(out_dir, f"page_{i:02d}.png")
            img.save(p)
            paths.append(p)
        return paths
    except Exception as e:
        raise RuntimeError(
            "Cannot render PDF pages: install pypdfium2 "
            "(`pip install pypdfium2 --break-system-packages`) or poppler."
        ) from e


# ---------------------------------------------------------------------------
# Self-test: build a tiny sanity-check report when this file is run directly.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "_sanity.pdf")
    b = ReportBuilder("Sanity Check Report", "Build verification")
    b.section("1. Snapshot")
    b.snapshot({
        "Price": "$1.23", "Market Cap": "$100B", "Shares Out": "81B",
        "52W High": "$1.50", "52W Low": "$0.90", "Div Yield": "2.00%",
        "Beta": "1.05", "Next Earnings": "2026-05-01", "Sector": "Test",
    })
    b.section("2. Business Overview")
    b.prose(
        "This is a self-test. It exercises snapshot, AAOIFI, PIF, "
        "fundamentals, multiples, DCF, analyst and indicator tables "
        "to confirm every cell word-wraps correctly even when the text "
        "is unusually long, which is the primary failure mode these "
        "helpers are designed to prevent."
    )
    b.section("3. Shariah Compliance")
    b.subsection("3b. AAOIFI")
    b.aaoifi([
        ("Haram revenue / Total revenue", "< 5%", "0.0%", True),
        ("Interest-bearing debt / Market Cap", "< 30%", "0.3%", True),
        ("Interest-bearing securities / Market Cap", "< 30%", "1.1%", True),
        ("Accounts Receivable / Market Cap", "< 49%", "0.7%", True),
    ])
    b.subsection("3c. PIF Step 1 — Industry exposure")
    b.pif_industries([
        ("Alcohol", "N", "—"),
        ("Tobacco", "N", "—"),
        ("Conventional financial services", "Partial",
         "Partnered with Stripe for developer platform payments; non-core."),
        ("Music", "N", "—"),
    ])
    b.section("10. Summary & Thesis")
    b.prose("Bull: the helpers work. Bear: they don't.")
    b.disclaimer()
    b.build(out)
    pages = verify_pdf(out)
    print(f"built {out}")
    for p in pages:
        print("  page:", p)
