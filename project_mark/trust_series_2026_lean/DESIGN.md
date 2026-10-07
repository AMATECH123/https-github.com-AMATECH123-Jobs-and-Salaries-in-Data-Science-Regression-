# Design note: the trust row, lean package

Same task, data, standard logic and golden answer as project_mark/trust_series_2026 (carry 2018 at 33.8 percent,
no 2024 figure, no decade change, 2022 withdrawn, neither draft certified). What changed, following the
program's note that starter kit data dictionaries and overviews give the answer away:

- No codebook. The 6,943 variable rendering with labels, years, ballots and record counts by year is gone. The
  reader has the Parquet file's column names, the gssr package documentation (which names the weight and design
  variables), the 2024 edition's printed series and its method note, and the standard.
- No provenance narration. A four column manifest (file, source, pulled, licence) replaces the README that
  explained what each file was for.
- No draft tables. The drafts' figures are in the prompt only, so there are no sampling error columns to test
  readings against.
- A terse standard. Rule 3 says full sample on the standard instrument and stops; it no longer enumerates mode
  selection, experimental assignment and offered response options.

The mapping of the question to its codes is now learned from the continuity gate: reproducing the 2024
edition's 1972 figure (46.6) identifies code 1 as "most people can be trusted". The existence of TRUSTV and
TRUSTNV, and the fact that TRUST reached no web respondent from 2021, must be found in the data.
