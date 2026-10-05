# Project Mark task v8: Brightwater 2024 federal tax (Accounting, Audit and Forensic / tax; ETL from a messy ledger)
- `inputs/` (11 files, 7 formats, 20k-row ledger); `prompt.md`; `rubric.md`.
- Why this design: earlier tasks stated their rules, so a strong model applied them exactly (95-100%). Here the answer depends on US tax law the solver must recall, not read, and the law that applies to 2024 differs from the 2025 changes: bonus 60%, section 174 amortisation, 163(j) without add-back, 80% NOL, mid-quarter test, section 179 phase-out, 280F, gifts, transit, related-party accruals, de minimis.
- `author/taxlaw.py` holds every rule with its authority. `generate.py` builds the data and the truth; `reference_solution.py` re-derives the answer from the files only (matches to the cent); `score_tax.py` scores a deliverable pair.
- All data is synthetic.
