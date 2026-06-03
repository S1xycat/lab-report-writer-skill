# DOCX Chinese Generation

Use this reference before generating any DOCX that contains Chinese text.

## Font Rule

For Chinese DOCX output, never rely only on `run.font.name`. In Word, Chinese fonts use the `w:eastAsia` attribute. Every run that contains report text must set all relevant font slots:

- `w:ascii`
- `w:hAnsi`
- `w:eastAsia`
- `w:cs`

Use a helper and call it for every run, including headings, table cells, captions, headers, footers, text boxes when accessible, and code blocks.

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_LINE_SPACING


def set_run_font(run, name="宋体", size=12, bold=None, color="000000"):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    r_fonts.set(qn("w:ascii"), name)
    r_fonts.set(qn("w:hAnsi"), name)
    r_fonts.set(qn("w:eastAsia"), name)
    r_fonts.set(qn("w:cs"), name)
```

Use the helper for every generated run. Do not use bare `run.font.name = ...`.

For body paragraphs, also set paragraph spacing explicitly:

```python
def set_body_paragraph(paragraph):
    fmt = paragraph.paragraph_format
    fmt.line_spacing = 1.5
    fmt.space_before = Pt(0)
    fmt.space_after = Pt(0)
```

Call `set_body_paragraph(paragraph)` for every generated body paragraph and table-cell body paragraph unless the template explicitly requires a different style.

## Default Title Style

Unless a user-provided template clearly requires otherwise, generated report titles and headings must use black `宋体`, not theme-blue headings and not `黑体`.

- Main title: `宋体`, black, bold, 16 pt or template-equivalent size.
- First-level heading: `宋体`, black, bold, 14 pt or template-equivalent size.
- Second-level heading: `宋体`, black, bold, 12 pt or template-equivalent size.
- Body text: `宋体`, black, 小四 12 pt, 1.5 line spacing.

If the template has its own heading sizes or numbering, preserve size/numbering but still set generated heading runs to black `宋体` unless the user asks to copy the template font exactly.

## Recommended Font System

- Cover title / headings: black `宋体`, bold if appropriate.
- Body text: black `宋体`, 小四 12 pt, 1.5 line spacing.
- Table text: black `宋体`, 小四 12 pt unless the template table style is clearly smaller.
- Figure and table captions: `宋体`.
- Code: `Consolas` for ASCII code; use `宋体` or a mixed-font helper if Chinese comments appear.
- Common body size: 小四 12 pt.

When a template is provided, inspect its styles and match required layout, but default generated body text to black `宋体`, 小四 12 pt, 1.5 line spacing unless the user explicitly requests copying the template body style.

## Common Traps

- `document.styles["Normal"].font.name = "宋体"` does not reliably fix every generated run.
- `add_run()` may not inherit East Asian font settings from the paragraph style.
- Table cell paragraphs and runs need the same explicit font handling.
- Reusing sample/template styles can still produce mixed fonts if newly added runs lack `w:eastAsia`.
- Setting only paragraph style is not enough for runs created after the style change.
- Line spacing must be set on the paragraph, not the run.

## Formula Rule

Do not leave LaTeX delimiters or commands as raw text in the final DOCX. Text such as `$$ ... $$`, `\[ ... \]`, `\( ... \)`, `\frac{...}{...}`, `\theta`, or `\left(...\right)` is a source notation, not a finished Word formula.

When the report contains formulas:

- Prefer native Word equations/OMML if the generation path supports them.
- If native equations are not practical, render display formulas as high-resolution transparent PNGs and insert them centered at the formula position.
- For simple inline formulas, convert to readable Unicode/plain mathematical notation when possible, or use a small formula image.
- Preserve formula numbering and captions if the task/template requires them.
- Never deliver a DOCX that still contains raw `$$...$$` formula blocks.

Useful fallback:

```powershell
python scripts/render_latex_formula.py "$$ I(\theta)=I_0\left(\frac{\sin\beta}{\beta}\right)^2 $$" artifacts\formula_01.png
```

Then insert `formula_01.png` into the DOCX instead of the raw LaTeX text.

## Validation

After generating the DOCX, run:

```powershell
python scripts/check_docx_fonts.py path\to\report.docx
```

If missing East Asian fonts or unexpected font families are reported, fix the generator and regenerate the report instead of manually patching only a few paragraphs.

Also check formula conversion:

```powershell
python scripts/check_docx_latex_literals.py path\to\report.docx
```

If LaTeX literals are reported, convert them to Word equations or rendered formula images and regenerate the report.
