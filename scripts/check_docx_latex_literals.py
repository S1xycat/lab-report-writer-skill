#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detect raw LaTeX formula literals left in a generated DOCX."""
from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
DISPLAY_RE = re.compile(
    r"(?s)(\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)|"
    r"\\begin\{(?:equation|align|gather|multline|cases|matrix|pmatrix|bmatrix)\}.*?\\end\{[^}]+\})"
)
COMMAND_RE = re.compile(
    r"\\(?:frac|dfrac|tfrac|sqrt|left|right|theta|lambda|alpha|beta|gamma|Delta|"
    r"sin|cos|tan|log|ln|exp|sum|prod|int|iint|iiint|infty|partial|cdot|times|"
    r"text|mathrm|mathbf|overline|hat|vec|begin|end)\b"
)


def paragraph_texts(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    paragraphs: list[str] = []
    for para in root.findall(".//w:p", NS):
        text = "".join(node.text or "" for node in para.findall(".//w:t", NS)).strip()
        if text:
            paragraphs.append(text)
    return paragraphs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = Path(args.docx)
    raw_blocks: list[str] = []
    command_lines: list[str] = []
    for text in paragraph_texts(path):
        raw_blocks.extend(match.group(0) for match in DISPLAY_RE.finditer(text))
        if COMMAND_RE.search(text):
            command_lines.append(text)

    examples = []
    seen = set()
    for item in raw_blocks + command_lines:
        compact = item.replace("\n", " ").strip()
        if compact not in seen:
            seen.add(compact)
            examples.append(compact[:160])

    result = {
        "docx": str(path),
        "raw_latex_block_count": len(raw_blocks),
        "latex_command_line_count": len(command_lines),
        "examples": examples[:20],
        "revision_recommended": bool(raw_blocks or command_lines),
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
