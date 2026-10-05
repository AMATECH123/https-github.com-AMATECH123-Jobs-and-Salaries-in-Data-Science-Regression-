# Project Mark task: Automation platform consolidation (Business & Operations Analytics, ETL / pipeline build)

- `inputs/` is the package given to the model (14 files, 7 formats, the Zapier CSV has ~22k rows, Make ~15.7k, n8n JSON ~52k executions).
- `prompt.md` is the prompt. `rubric.md` is the grading rubric.
- `author/` is hidden from the model: generator (`generate_data.py`, seed 20251005), shared constants (`params.py`), doc builder, reference solution, variant checks, and `reference_outputs/` (ground truth, reference CSV and PDF).
- All data is synthetic. Vendor names are real products but every price, plan limit and connector-support flag is invented for this exercise.
- Rebuild: `cd author && python3 generate_data.py && python3 make_docs.py && python3 reference_solution.py`.
- `reference_solution.py` reads only `inputs/` and reproduces the generator's hidden true daily counts with 0 mismatches.

## Hardening history
- v1 (memo spelled out every cleaning rule): a blind attempt by a same-class model scored ~100%. Judged too easy.
- v2: memo reduced to principles; added re-created zaps/scenarios (new ids missing from the crosswalk, matched by exact name) and rebuilt ones (old id keeps firing after its valid_to); labour rate and custom-build hours retuned so five plausible mistakes flip the winner to n8n.
