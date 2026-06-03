---
name: lab-report-writer
description: Generate complete, template-aware lab reports for any course from experiment task books, related files, report templates, sample finished reports, raw data, course materials, rubrics, personal cover information, output requirements, writing style preferences, and allowed evidence-generation modes. Use when the user asks Codex to draft, format, differentiate, validate, or regenerate lab reports, including cases with no real experiment data where Codex should reproduce locally, use public sources, or create report-ready simulated data.
---

# Lab Report Writer

## Purpose

Create a complete lab report from user-provided experiment materials. Preserve template structure, extract requirements from the task book, use any real data first, and when real data is absent generate plausible simulated data by default.

Do not require the user to provide process screenshots, videos, detailed environment information, or teacher oral requirements. If the report requires screenshots and none are provided, first investigate whether related files can be run or rendered to produce screenshots. Insert placeholders only after that check fails or is inappropriate.

## Inputs

Accept any subset of:

- A standard input folder containing role-named subfolders/files. Read useful filled content and skip empty files or empty folders.
- Experiment task book or assignment instructions.
- Related experiment files: source code, datasets, projects, SQL, models, documents, courseware, installers, logs, or exported results.
- Report template.
- Finished sample report.
- Raw experiment data.
- Courseware or textbook chapters.
- Rubric or scoring standard.
- Personal or cover-page information.
- Output requirements: DOCX/PDF/ZIP, filename rules, number of versions, report sections to generate.
- Writing style preference: concise, detailed, student voice, formal technical report, similar to sample structure but not copied.

Standard input folder names:

- `实验任务书`
- `实验所需文件`
- `实验报告模板`
- `成品实验报告`
- `实验相关课件`
- `实验原始数据.md`
- `个人信息.md`
- `评分标准.md`
- `输出文件要求.md`
- `目标写作风格.md`

## Core Workflow

1. Inventory inputs.
   - If a folder is provided, run `scripts/inspect_inputs.py <folder>` to summarize file types and likely roles.
   - If the folder matches the standard input-folder layout, read files by role name. Use non-empty files/folders; skip empty `.md` files and empty role folders without asking.
   - Identify task book, template, sample report, raw data, and related files.
   - For software/computing experiments, run `scripts/probe_runtime.py` before deciding that an environment is unavailable.

2. Extract requirements.
   - Read the task book first.
   - Extract experiment title, purpose, required steps, required tables, required screenshots, required analysis, and submission rules.
   - If a rubric exists, map report sections to scoring points.

3. Extract template and sample conventions.
   - Use the template for section order, cover fields, headings, tables, and visual style.
   - If both a template and a finished sample are provided, the template controls formatting; the sample is only a weak reference for expected completeness.
   - Use the sample report only to infer required completeness, likely section types, and teacher expectations. Do not mirror its layout choices, paragraph order, table order, example choices, data profile, or conclusion path unless required by the task/template.
   - Do not copy sample wording, table data, screenshots, or conclusions unless the user explicitly says it is reusable.
   - When a sample exists, create a short difference plan before drafting: new evidence backbone, different data/test cases, different analysis angle, and different conclusion emphasis.

4. Decide evidence mode.
   - Prefer real user data when provided.
   - If real user data is absent, generate plausible simulated data by default and track provenance outside the report body.
   - Use local reproduction or public sources when helpful for understanding the experiment, calibrating simulated values, or creating reproducible screenshots/artifacts.
   - For any required screenshot, inspect related files and local runtimes for runnable apps, notebooks, scripts, HTML pages, test suites, existing images, or generated outputs before deciding to use a placeholder.
   - Do not mark a software/computing screenshot as unavailable until runtime probing and one reasonable minimal reproduction attempt have been made or ruled out.
   - Leave placeholders for missing screenshots, videos, personal fields, or non-data materials that should not be invented.

5. Draft before finalizing.
   - Build a short report plan: sections, evidence per section, missing items, and chosen evidence mode.
   - For missing screenshots, insert placeholders like `【此处插入实验运行截图】` only after screenshot reproduction has been checked.
   - For missing personal cover fields, insert placeholders like `【姓名】`, `【学号】`.

6. Generate the report.
   - Create DOCX unless the user requests another format.
   - Before generating Chinese DOCX content, read `references/docx-generation.md` and use explicit East Asian font settings for every run.
   - Default generated titles/headings to black `宋体` unless the template or user explicitly requires another style.
   - Default generated body text to black `宋体`, 小四 12 pt, 1.5 line spacing unless the template or user explicitly requires another style.
   - Preserve template structure and formatting as much as practical.
   - Insert tables, converted formulas, code snippets, figures, and placeholders where required. Do not leave raw LaTeX formula syntax such as `$$...$$` in the final DOCX.
   - If a finished sample is provided, generate from the task requirements and difference plan, not by rewriting the sample section by section.
   - If generating multiple versions, vary data, examples, wording, section emphasis, chart/table ordering, and conclusions.

7. Validate.
   - Run `scripts/verify_report_docx.py <report.docx>` after DOCX generation.
   - For Chinese DOCX reports, run `scripts/check_docx_fonts.py <report.docx>` and fix mixed or missing East Asian font settings.
   - If the report contains formulas, run `scripts/check_docx_latex_literals.py <report.docx>` and convert any remaining raw LaTeX before delivery.
   - If a DOCX sample report was used, run `scripts/compare_docx_similarity.py <sample.docx> <report.docx>` and revise if the output is too similar.
   - Check required sections, placeholder count, table count, image count, and consistency of results and conclusions.
   - Report any missing evidence or assumptions to the user.

## Evidence Rules

- Never present simulated, inferred, or web-sourced data as the user's personally measured data.
- When data is generated by the agent, prefer reproducible local execution over pure simulation.
- When simulation is used, make values physically or logically plausible: include realistic variation, measurement noise, and non-perfect results when appropriate.
- In the finished report body, do not label result values as simulated, inferred, public-source, or locally reproduced unless the user explicitly requests those labels or the template requires them. Present generated values as ordinary experiment result data.
- Keep an internal note or final-response summary of data provenance outside the report body: real user data, local reproduction, public source, or simulated.
- Do not fabricate external citations. Browse when current or source-specific information is needed.

## Screenshot Rules

- Do not ask the user to provide process screenshots or videos by default.
- If the task book or template requires screenshots and no image is available, actively inspect `实验所需文件`, task instructions, and sample reports to determine whether screenshots can be produced.
- If a software/computing experiment can be locally reproduced, run it or build a minimal equivalent from the provided files and create screenshots.
- If tests, UI pages, notebooks, scripts, logs, or generated artifacts can demonstrate the required result, prefer producing real screenshots from those artifacts over placeholders.
- For physical, hardware, chemistry, biology, or classroom-only screenshots that cannot be reproduced, use placeholders rather than invented images unless the user explicitly asks for illustrative mockups.

## Minimal Questions

Ask only when necessary. Prefer proceeding with reasonable defaults.

Ask for clarification only if:

- No task book or experiment topic is available.
- The output location or format is ambiguous and cannot be inferred.
- Required personal cover fields are unknown and cannot be left as placeholders.

## References

- Read `references/workflow.md` for the full report-generation workflow.
- Read `references/template-folder.md` when the user provides a standard input folder.
- Read `references/evidence-modes.md` when real experiment data is missing.
- Read `references/docx-generation.md` before generating any DOCX with Chinese content.
- Read `references/screenshot-reproduction.md` when screenshots are required or the template/sample contains screenshot positions.
- Read `references/differentiation.md` when generating multiple unique reports or rewriting from a finished sample.
- Read `references/validation.md` before final delivery.
