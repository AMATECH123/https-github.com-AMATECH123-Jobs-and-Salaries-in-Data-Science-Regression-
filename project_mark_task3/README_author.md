# Project Mark task v7: Calloway AP forensic review (Accounting, Audit & Forensic Analytics; ETL + discovery)
- `inputs/` (13 files, 7 formats, 29k invoices / 29k payments / 20k POs) is the package; `prompt.md` the prompt; `rubric.md` the rubric.
- Eight planted scheme types with exact ground truth (59 cases, USD 4,168,306) and about 100 lookalike decoys that pass a naive test but are legitimate.
- `author/generate.py` (seeded, `TASK_SEED`), `make_docs.py`, `reference_solution.py` (detectors reading only inputs; reproduce all 59 cases and flag nothing else), `score_d1.py` (register scorer), `make_reference_outputs.py`.
- Why this design: earlier tasks (rule-based ETL, measurement methodology) were solved ~97% because every trap had evidence a careful analyst finds by reconciliation. Forensic review is open-ended discovery with no stopping signal: each scheme needs a different join across files, and naive tests produce many false positives.
- All data is synthetic.
