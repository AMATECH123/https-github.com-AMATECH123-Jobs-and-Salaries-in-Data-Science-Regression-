# Workspace contents and provenance

This note was written by the task author to record where each file came from. The survey data file is the NORC General Social Survey cumulative file as the gssr package distributes it, converted to Parquet with values unchanged. The scenario documents say so in their first lines.

| File | Format | What it is | Publisher | Source | Pulled | Licence |
|---|---|---|---|---|---|---|
| gss_all.parquet | Parquet | General Social Survey Cumulative Data File 1972 to 2024, Release 3: 75,699 respondent records, 6,942 variables, numeric codes. Converted by the task author with pyreadr and pyarrow from data/gss_all.rda in the gssr R package, values unchanged (missing responses of every kind are empty values). | NORC at the University of Chicago, General Social Survey; packaged by Kieran Healy (gssr 0.9); conversion by the task author | https://github.com/kjhealy/gssr (data/gss_all.rda), built from NORC gss7224_r3.dta | 2026-10-07 | GSS data are public use; gssr package MIT (gssr_LICENSE.md) |
| gss_codebook_1972_2024.txt | TXT | Variable codebook: label, question text, codes and labels, years and ballots, unweighted record counts by year for 6,943 variables. Plain text rendering of the gssrdoc R package documentation, generated from NORC GSS Data Explorer pages. | NORC GSS Data Explorer, via gssrdoc by Kieran Healy; rendering by the task author | https://github.com/kjhealy/gssrdoc (man/*.Rd) | 2026-10-07 | as above |
| gssr_README.md | Markdown | README of the gssr package. | Kieran Healy | https://github.com/kjhealy/gssr | 2026-10-07 | MIT |
| gssr_NEWS.md | Markdown | Release notes of the gssr package, including the move to Release 3 of the 1972 to 2024 file. | Kieran Healy | https://github.com/kjhealy/gssr | 2026-10-07 | MIT |
| gssr_DESCRIPTION.txt | TXT | Package metadata (version 0.9). | Kieran Healy | https://github.com/kjhealy/gssr | 2026-10-07 | MIT |
| gssr_data_documentation.R | R | Roxygen documentation of the data objects. | Kieran Healy | https://github.com/kjhealy/gssr (R/data.R) | 2026-10-07 | MIT |
| gssr_LICENSE.md | Markdown | Licence of the gssr package. | Kieran Healy | https://github.com/kjhealy/gssr | 2026-10-07 | MIT |
| trust_series_2024_edition.csv | CSV | Scenario document: the trust series as the 2024 edition printed it, every survey year 1972 to 2022, computed by the task author from the cumulative file by the method in edition_2024_method_note.md. | task author | computed from gss_all.parquet | 2026-10-07 | n/a |
| edition_2024_method_note.md | Markdown | Scenario document: the method note of the 2024 edition. | task author | written for this task | 2026-10-07 | n/a |
| attitudes_series_standard.md | Markdown | Scenario document: the chapter standard for long run series. | task author | written for this task | 2026-10-07 | n/a |
| research_draft_2026.csv | CSV | Scenario document: Research's draft for the 2026 trust row, as circulated. Computed by the task author from the cumulative file by the method Research used, which is not recorded in the workspace. | task author | computed from gss_all.parquet | 2026-10-07 | n/a |
| editor_draft_2026.csv | CSV | Scenario document: the editor's draft for the 2026 trust row, as circulated. | task author | computed from gss_all.parquet | 2026-10-07 | n/a |

The General Social Survey is conducted by NORC at the University of Chicago with principal funding from the National Science Foundation. GSS data are released for public use. Attribution: Davern, Michael; Bautista, Rene; Freese, Jeremy; Herd, Pamela; and Morgan, Stephen L.; General Social Survey 1972-2024. Sponsored by the National Science Foundation. NORC ed. Chicago: NORC, 2025. The task author has not altered any value in the survey file.
