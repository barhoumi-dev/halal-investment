"""
make_levels_chart.py — single-chart helper for swing-trade-setup skill.

Produces ONE PNG: a horizontal-level diagram showing the current price, 50DMA,
200DMA, support/resistance ladders, the recommended entry zone, the stop-loss,
and the two targets. This is the "optional chart" the skill offers at the end
of a chat answer.

Usage:
    python make_levels_chart.py \\
        --ticker NVDA \\
        --price 142.50 \\
        --supports 138.0,134.5,128.0 \\
        --resistances 148.0,152.5,160.0 \\
        --ma50 137.0 \\
        --ma200 130.0 \\
        --entry-low 138.0 --entry-high 140.5 \\
        --stop 134.0 \\
        --t1 152.5 --t2 165.0 \\
        --out /path/to/nvda_levels.png

The output PNG is intended to be ~1500x750 px — readable on a phone, sharp on
a desktop. Style matches the investment-research-report skill (navy/amber).
"""
from __future__ import annotations

import argparse
import os
import sys


NAVY_HEX = "#0B3C5D"
AMBER_HEX = "#C69214"
PASS_GREEN_HEX = "#2E7D32"
FAIL_RED_HEX = "#C62828"


def parse_floats(s: str) -> list[float]:
    if not s:
        return []
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def make_chart(
    ticker: str,
    price: float,
    supports: list[float],
    resistances: list[float],
    ma50: float | None,
    ma200: float | None,
    entry_low: float | None,
    entry_high: float | None,
    stop: float | None,
    t1: float | None,
    t2: float | None,
    out_path: str,
    as_of: str | None = None,
) -> str:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))

    all_levels = list(supports) + list(resistances) + [price]
    for v in (ma50, ma200, stop, t1, t2, entry_low, entry_high):
        if v is not None:
            all_levels.append(v)
    if not all_levels:
        raise SystemExit("Need at least the current price.")

    ymin = min(all_levels) * 0.95
    ymax = max(all_levels) * 1.04

    # Entry zone (amber-tinted)
    if entry_low is not None and entry_high is not None:
        ax.axhspan(
            entry_low,
            entry_high,
            color="#FDF2D4",
            alpha=0.7,
            label=f"Entry zone ${entry_low:.2f}–${entry_high:.2f}",
        )

    # Stop band (faint red)
    if stop is not None:
        ax.axhspan(stop * 0.992, stop * 1.008, color="#F8D7DA", alpha=0.55)

    # Targets
    if t2 is not None:
        ax.axhline(
            t2,
            color=PASS_GREEN_HEX,
            linestyle=":",
            linewidth=1.5,
            label=f"Target 2 ${t2:.2f}",
        )
    if t1 is not None:
        ax.axhline(
            t1,
            color=PASS_GREEN_HEX,
            linestyle="--",
            linewidth=1.5,
            label=f"Target 1 ${t1:.2f}",
        )

    # Resistance levels
    for r in resistances:
        ax.axhline(r, color="#888888", linestyle="--", linewidth=0.8, alpha=0.7)
        ax.text(
            0.985,
            r,
            f"R ${r:.2f}",
            color="#555555",
            fontsize=8,
            ha="right",
            va="bottom",
            transform=ax.get_yaxis_transform(),
        )

    # Support levels
    for s in supports:
        ax.axhline(s, color="#888888", linestyle="--", linewidth=0.8, alpha=0.7)
        ax.text(
            0.985,
            s,
            f"S ${s:.2f}",
            color="#555555",
            fontsize=8,
            ha="right",
            va="top",
            transform=ax.get_yaxis_transform(),
        )

    # Moving averages
    if ma50 is not None:
        ax.axhline(
            ma50, color=AMBER_HEX, linewidth=1.3, label=f"50DMA ${ma50:.2f}"
        )
    if ma200 is not None:
        ax.axhline(
            ma200,
            color="#666666",
            linewidth=1.3,
            linestyle="-.",
            label=f"200DMA ${ma200:.2f}",
        )

    # Stop-loss
    if stop is not None:
        ax.axhline(
            stop, color=FAIL_RED_HEX, linewidth=1.7, label=f"Stop ${stop:.2f}"
        )

    # Current price (most prominent)
    ax.axhline(
        price, color=NAVY_HEX, linewidth=2.4, label=f"Current ${price:.2f}"
    )
    ax.text(
        0.02,
        price,
        f"${price:.2f}",
        color=NAVY_HEX,
        fontsize=10,
        ha="left",
        va="bottom",
        fontweight="bold",
        transform=ax.get_yaxis_transform(),
    )

    ax.set_ylim(ymin, ymax)
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    for s in ("top", "bottom", "right"):
        ax.spines[s].set_visible(False)

    title = f"{ticker} — Key Levels & Trade Zones"
    if as_of:
        title += f"  (as of {as_of})"
    ax.set_title(title, color=NAVY_HEX, fontweight="bold", loc="left")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.92)
    ax.yaxis.grid(True, alpha=0.2)
    ax.set_ylabel("USD ($/share)")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate a swing-trade levels chart.")
    p.add_argument("--ticker", required=True)
    p.add_argument("--price", type=float, required=True)
    p.add_argument("--supports", type=str, default="",
                   help="Comma-separated list, e.g. '138.0,134.5,128.0'")
    p.add_argument("--resistances", type=str, default="",
                   help="Comma-separated list")
    p.add_argument("--ma50", type=float, default=None)
    p.add_argument("--ma200", type=float, default=None)
    p.add_argument("--entry-low", type=float, default=None)
    p.add_argument("--entry-high", type=float, default=None)
    p.add_argument("--stop", type=float, default=None)
    p.add_argument("--t1", type=float, default=None)
    p.add_argument("--t2", type=float, default=None)
    p.add_argument("--as-of", type=str, default=None,
                   help="Date string, e.g. '2026-05-01'")
    p.add_argument("--out", required=True, help="Output PNG path")
    args = p.parse_args(argv)

    out = make_chart(
        ticker=args.ticker,
        price=args.price,
        supports=parse_floats(args.supports),
        resistances=parse_floats(args.resistances),
        ma50=args.ma50,
        ma200=args.ma200,
        entry_low=args.entry_low,
        entry_high=args.entry_high,
        stop=args.stop,
        t1=args.t1,
        t2=args.t2,
        as_of=args.as_of,
        out_path=args.out,
    )
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
