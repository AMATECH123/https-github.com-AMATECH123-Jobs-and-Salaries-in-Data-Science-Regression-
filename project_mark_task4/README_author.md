# Project Mark task v8: Brightwater 2024 federal tax (Accounting, Audit and Forensic / tax; ETL from a messy ledger)
- `inputs/` (11 files, 7 formats, 20k-row ledger); `prompt.md`; `rubric.md`.
- Why this design: earlier tasks stated their rules, so a strong model applied them exactly (95-100%). Here the answer depends on US tax law the solver must recall, not read, and the law that applies to 2024 differs from the 2025 changes: bonus 60%, section 174 amortisation, 163(j) without add-back, 80% NOL, mid-quarter test, section 179 phase-out, 280F, gifts, transit, related-party accruals, de minimis.
- `author/taxlaw.py` holds every rule with its authority. `generate.py` builds the data and the truth; `reference_solution.py` re-derives the answer from the files only (matches to the cent); `score_tax.py` scores a deliverable pair.
- All data is synthetic.

## Blind-test history
- v1 ground truth applied the de minimis safe harbor to all items under USD 5,000. Both blind runs correctly pointed out that Reg. 1.263(a)-1(f) covers only amounts expensed on the AFS under the written policy (USD 1,800 here), so the small items are depreciated and count toward the 179 phase-out. Truth corrected; 179 limit 812,454.
- Gift recipients now map to one client company each (the name-only vs name+company ambiguity is removed).
- Blind runs on the pre-correction ledger, scored against the corrected truth: 48 and 42 (average 45). Both got every tax-law item right and each failed on one ledger-mechanics slip (double-counting the book provision; treating allowance write-offs as book expense) that flowed through 163(j), the NOL and the balance due.
