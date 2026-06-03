#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a LaTeX-style math formula to a transparent PNG for DOCX insertion."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


DELIMITER_RE = re.compile(r"^\s*(?:\$\$|\\\[|\\\()\s*(.*?)\s*(?:\$\$|\\\]|\\\))\s*$", re.S)


def strip_delimiters(formula: str) -> str:
    match = DELIMITER_RE.match(formula)
    if match:
        return match.group(1).strip()
    return formula.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("formula", help="Formula text, with or without $$ delimiters")
    parser.add_argument("output", help="Output PNG path")
    parser.add_argument("--fontsize", type=float, default=18)
    parser.add_argument("--dpi", type=int, default=240)
    args = parser.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    formula = strip_delimiters(args.formula)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(1, 1), dpi=args.dpi)
    text = fig.text(0, 0, f"${formula}$", fontsize=args.fontsize)
    fig.canvas.draw()
    bbox = text.get_window_extent(renderer=fig.canvas.get_renderer()).expanded(1.08, 1.25)
    width = max(bbox.width / args.dpi, 0.4)
    height = max(bbox.height / args.dpi, 0.2)
    plt.close(fig)

    fig = plt.figure(figsize=(width, height), dpi=args.dpi)
    fig.text(0.02, 0.5, f"${formula}$", fontsize=args.fontsize, va="center")
    fig.savefig(output, transparent=True, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(output)


if __name__ == "__main__":
    main()
