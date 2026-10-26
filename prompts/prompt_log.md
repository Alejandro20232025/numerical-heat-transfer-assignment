# Prompt log

One row per prompt. Save the exact prompt text and the complete AI output as numbered files in this folder, then commit with a message such as `Prompt 02: independent audit of the transient section`. Do not edit old rows — add new ones.

| # | Date | Student | Tool and model | Prompt file | Output file(s) | Purpose | What we kept / corrected | Verified by hand? |
|---|---|---|---|---|---|---|---|---|
| 01 | 2026-10-26 | [name] | Claude (claude.ai) | 01_base_and_adapted_prompt.md | Claude report doc (export as PDF to 01_output_report.pdf) + this repository kit | Select problem, solve base and adapted exercises, report, slides, code | Selected 5-35; adaptation h_comb = 40 W/m²·K; 5 drafting errors corrected (see 04_audit/ai_error_log.md) | yes|
| 02 | | | | 02_audit_prompt.md | | Independent audit of our numbers by a second AI | |yes |
| 03 | | | | 03_adapted_exercise_prompt.md | | Solve the adapted exercise from scratch and compare | |yes |
| 04 | | | | | | | | |

Templates: copy the prompt-engineering templates from the class GitHub into `templates/` and note which template each prompt follows.
