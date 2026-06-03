# Validation

Validate before final delivery.

## Required Checks

- Output file exists.
- Required sections from the task book are present.
- Template cover fields are filled or have clear placeholders.
- Required tables exist.
- Required screenshots exist, were generated from reproducible/local artifacts, or have placeholders only after the reproduction check failed or was inappropriate.
- Data, analysis, and conclusion agree.
- Evidence mode is known.
- Multiple versions are meaningfully different.
- If a finished sample report was used, the generated report is meaningfully different from the sample in data, examples, analysis angle, conclusion emphasis, and non-required layout choices.

## DOCX Checks

Run:

```powershell
python scripts/verify_report_docx.py path\to\report.docx
```

Review:

- Paragraph count.
- Table count.
- Image count.
- Placeholder count.
- Detected headings.

For Chinese reports, also run:

```powershell
python scripts/check_docx_fonts.py path\to\report.docx
```

Review:

- Chinese runs without `w:eastAsia`.
- Unexpectedly mixed East Asian fonts.
- Generated titles/headings using non-black colors or non-`宋体` East Asian fonts.
- Generated body text not using black `宋体`, 小四 12 pt, or 1.5 line spacing.
- Whether revision is recommended.

For reports with formulas, also run:

```powershell
python scripts/check_docx_latex_literals.py path\to\report.docx
```

Review:

- Raw `$$...$$`, `\[...\]`, or `\(...\)` blocks.
- LaTeX commands such as `\frac`, `\theta`, `\lambda`, or `\left`.
- Whether formula conversion is still needed.

If a DOCX sample report exists, also run:

```powershell
python scripts/compare_docx_similarity.py path\to\sample.docx path\to\report.docx
```

Review:

- Line similarity.
- Shared distinctive phrases.
- Matching table count and image count.
- Whether revision is recommended.

## Placeholder Policy

Placeholders are acceptable when:

- Personal information is missing.
- Screenshots are required but unavailable after reproduction check.
- Real measurements are absent and the report fails to provide plausible simulated data.

For software/computing screenshots, "unavailable" requires runtime probing and at least one reasonable minimal reproduction attempt unless clearly impossible.

Mention placeholders in the final response.

## Final Response

Include:

- Report path.
- Evidence mode used outside the report body.
- Any placeholders left.
- Screenshot reproduction attempts or generated screenshot folders when relevant.
- Runtime probe result when placeholders remain for software/computing screenshots.
- Any files generated, such as DOCX, PDF, ZIP, data files, or screenshots.
- Validation summary.
