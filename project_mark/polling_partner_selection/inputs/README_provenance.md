# Workspace contents and provenance

This note was written by the task author to record where each file came from. Every data file is exactly as its
publisher served it on the pull date. The one document written for this task, the board's polling partner
standard, says so in its first lines.

All files under pollster-ratings/ were pulled on 2026-10-06 from the FiveThirtyEight data repository on GitHub
(https://github.com/fivethirtyeight/data, directory pollster-ratings), at commit
4c1ff5e3aef1816ae04af63218015066e186c147 (25 February 2025), by sparse clone and by direct download from
raw.githubusercontent.com. Each file is byte identical to the repository copy. The directory layout is the
repository's own. Licence: Creative Commons Attribution 4.0 International (pollster-ratings/LICENSE), which
requires attribution to FiveThirtyEight.

| File | What it is | Rows |
|---|---|---|
| pollster-ratings/raw_polls.csv | The current vintage of the pollster ratings record (2024 methodology): every poll analysed for the ratings, 1998 to 2023 cycles, one row per question, with poll and actual margins, methodology, sponsor flags, transparency score, activity and AAPOR/Roper flags. No precomputed error column. | 20,466 |
| pollster-ratings/pollster-ratings-combined.csv | The published ratings output for the current vintage: rank, numeric grade, POLLSCORE, transparency, error and bias plus minus. | 540 |
| pollster-ratings/README.md | The codebook for the current vintage and links to the methodology articles. | |
| pollster-ratings/README_PRE2024.md | The codebook for the 2014 to 2023 vintages. | |
| pollster-ratings/LICENSE | CC BY 4.0 licence text. | |
| pollster-ratings/2023/raw-polls.csv | The 2023 vintage of the record (2014 to 2023 methodology): 1998 to 2022 cycles, with precomputed error, bias, rightcall and advanced plus minus columns, partisan codes D and R, and no activity or transparency fields. | 11,475 |
| pollster-ratings/2023/pollster-ratings.csv | The published ratings output for the 2023 vintage. | 517 |
| pollster-ratings/2023/pollster-stats-full.xlsx | The full statistics workbook behind the 2023 ratings. | |
| pollster-ratings/2021/raw-polls.csv | The 2021 vintage of the record: 1998 to 2020 cycles, same layout as the 2023 vintage; pollster names of that date. | 10,776 |
| pollster-ratings/2021/pollster-ratings.csv | The published ratings output for the 2021 vintage. | |
| pollster-ratings/2021/pollster-stats-full.xlsx | The full statistics workbook behind the 2021 ratings. | |
| board_polling_partner_standard.md | Scenario document written by the task author stating the board's polling partner standard. Not a FiveThirtyEight publication. | |

Attribution: polling data by FiveThirtyEight (https://github.com/fivethirtyeight/data), used under CC BY 4.0.
