#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check generated DOCX runs for Chinese font and heading style issues."""
from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
CHINESE_RE = re.compile(r"[\u3400-\u9fff]")
HEADING_RE = re.compile(r"(title|heading|标题)", re.I)
BODY_STYLE_RE = re.compile(r"(normal|body|正文)", re.I)
EXPECTED_BODY_SIZE_HALF_POINTS = "24"


def attr(element: ET.Element | None, name: str) -> str | None:
    if element is None:
        return None
    return element.attrib.get(f"{{{NS['w']}}}{name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = Path(args.docx)
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))

    total_chinese_runs = 0
    missing_east_asia: list[str] = []
    east_asia_fonts: Counter[str] = Counter()
    ascii_fonts: Counter[str] = Counter()
    heading_font_issues: list[str] = []
    heading_color_issues: list[str] = []
    body_font_issues: list[str] = []
    body_color_issues: list[str] = []
    body_size_issues: list[str] = []
    body_spacing_issues: list[str] = []

    for run in root.findall(".//w:r", NS):
        text = "".join(node.text or "" for node in run.findall(".//w:t", NS))
        if not text or not CHINESE_RE.search(text):
            continue
        total_chinese_runs += 1
        r_fonts = run.find("./w:rPr/w:rFonts", NS)
        east_asia = attr(r_fonts, "eastAsia")
        ascii_font = attr(r_fonts, "ascii")
        if east_asia:
            east_asia_fonts[east_asia] += 1
        else:
            missing_east_asia.append(text[:80])
        if ascii_font:
            ascii_fonts[ascii_font] += 1

    for para in root.findall(".//w:p", NS):
        p_style = para.find("./w:pPr/w:pStyle", NS)
        style_name = attr(p_style, "val") or ""
        if not HEADING_RE.search(style_name):
            continue
        para_text = "".join(node.text or "" for node in para.findall(".//w:t", NS)).strip()
        if not para_text:
            continue
        for run in para.findall(".//w:r", NS):
            text = "".join(node.text or "" for node in run.findall(".//w:t", NS))
            if not text:
                continue
            r_fonts = run.find("./w:rPr/w:rFonts", NS)
            east_asia = attr(r_fonts, "eastAsia")
            if CHINESE_RE.search(text) and east_asia and east_asia != "宋体":
                heading_font_issues.append(f"{style_name}: {para_text[:80]} -> eastAsia={east_asia}")
            color = run.find("./w:rPr/w:color", NS)
            color_value = attr(color, "val")
            if color_value and color_value.lower() not in {"000000", "auto"}:
                heading_color_issues.append(f"{style_name}: {para_text[:80]} -> color={color_value}")

    for para in root.findall(".//w:p", NS):
        p_style = para.find("./w:pPr/w:pStyle", NS)
        style_name = attr(p_style, "val") or "Normal"
        if HEADING_RE.search(style_name):
            continue
        para_text = "".join(node.text or "" for node in para.findall(".//w:t", NS)).strip()
        if not para_text or not CHINESE_RE.search(para_text):
            continue
        is_likely_body = BODY_STYLE_RE.search(style_name) or len(para_text) >= 20
        if not is_likely_body:
            continue
        spacing = para.find("./w:pPr/w:spacing", NS)
        line = attr(spacing, "line")
        line_rule = attr(spacing, "lineRule")
        if line and line != "360":
            body_spacing_issues.append(f"{style_name}: {para_text[:80]} -> line={line}, lineRule={line_rule}")
        elif line is None:
            body_spacing_issues.append(f"{style_name}: {para_text[:80]} -> missing explicit 1.5 line spacing")
        for run in para.findall(".//w:r", NS):
            text = "".join(node.text or "" for node in run.findall(".//w:t", NS))
            if not text or not CHINESE_RE.search(text):
                continue
            r_pr = run.find("./w:rPr", NS)
            r_fonts = run.find("./w:rPr/w:rFonts", NS)
            east_asia = attr(r_fonts, "eastAsia")
            if east_asia and east_asia != "宋体":
                body_font_issues.append(f"{style_name}: {para_text[:80]} -> eastAsia={east_asia}")
            color = run.find("./w:rPr/w:color", NS)
            color_value = attr(color, "val")
            if color_value and color_value.lower() not in {"000000", "auto"}:
                body_color_issues.append(f"{style_name}: {para_text[:80]} -> color={color_value}")
            size = attr(r_pr.find("./w:sz", NS) if r_pr is not None else None, "val")
            if size and size != EXPECTED_BODY_SIZE_HALF_POINTS:
                body_size_issues.append(f"{style_name}: {para_text[:80]} -> size_half_points={size}")

    result = {
        "docx": str(path),
        "chinese_runs": total_chinese_runs,
        "missing_east_asia_count": len(missing_east_asia),
        "east_asia_fonts": dict(east_asia_fonts),
        "ascii_fonts": dict(ascii_fonts),
        "examples_missing_east_asia": missing_east_asia[:10],
        "heading_font_issue_count": len(heading_font_issues),
        "heading_color_issue_count": len(heading_color_issues),
        "body_font_issue_count": len(body_font_issues),
        "body_color_issue_count": len(body_color_issues),
        "body_size_issue_count": len(body_size_issues),
        "body_spacing_issue_count": len(body_spacing_issues),
        "examples_heading_font_issues": heading_font_issues[:10],
        "examples_heading_color_issues": heading_color_issues[:10],
        "examples_body_font_issues": body_font_issues[:10],
        "examples_body_color_issues": body_color_issues[:10],
        "examples_body_size_issues": body_size_issues[:10],
        "examples_body_spacing_issues": body_spacing_issues[:10],
        "revision_recommended": (
            bool(missing_east_asia)
            or len(east_asia_fonts) > 3
            or bool(heading_font_issues)
            or bool(heading_color_issues)
            or bool(body_font_issues)
            or bool(body_color_issues)
            or bool(body_size_issues)
            or bool(body_spacing_issues)
        ),
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
