#!/usr/bin/env python3
"""Plot explicitly named numeric CSV columns without altering source values."""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--x", required=True)
    parser.add_argument("--y", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--kind", choices=("line", "scatter"), default="line")
    parser.add_argument("--xlabel")
    parser.add_argument("--ylabel")
    parser.add_argument("--title")
    parser.add_argument("--yerr", help="Column with nonnegative error values")
    args = parser.parse_args()
    xs, ys, errors = [], [], []
    with args.csv.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        needed = [args.x, args.y] + ([args.yerr] if args.yerr else [])
        missing = [name for name in needed if name not in (reader.fieldnames or [])]
        if missing:
            parser.error(f"Missing columns: {missing}")
        for row_num, row in enumerate(reader, start=2):
            try:
                x, y = float(row[args.x]), float(row[args.y])
                err = float(row[args.yerr]) if args.yerr else None
            except (TypeError, ValueError) as exc:
                parser.error(f"Non-numeric value at CSV row {row_num}: {exc}")
            if err is not None and err < 0:
                parser.error(f"Negative error at CSV row {row_num}")
            xs.append(x); ys.append(y)
            if err is not None: errors.append(err)
    if not xs:
        parser.error("CSV has no data rows")
    fig, ax = plt.subplots(figsize=(6.4, 4.0), constrained_layout=True)
    if args.yerr:
        ax.errorbar(xs, ys, yerr=errors, fmt="o-" if args.kind == "line" else "o", capsize=3)
    elif args.kind == "line":
        ax.plot(xs, ys, marker="o")
    else:
        ax.scatter(xs, ys)
    ax.set(xlabel=args.xlabel or args.x, ylabel=args.ylabel or args.y, title=args.title or "")
    ax.grid(alpha=0.25)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)
    print(f"Plot: {args.output}; rows: {len(xs)}")


if __name__ == "__main__":
    main()

