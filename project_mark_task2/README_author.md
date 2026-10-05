# Project Mark task v6: Harbor & Pine channel budget (Business & Operations / Marketing analytics, ETL + measurement)

- `inputs/` (14 files, 7 formats) is the package given to the model; `prompt.md` / `prompt_to_paste.txt` is the prompt; `rubric.md` the rubric.
- `author/` is hidden: `model.py` (data-generating model and truth), `generate.py` (seeded generator, `TASK_SEED`), `make_docs.py`, `reference_solution.py` (reads only inputs), `robustness.py` (multi-seed check), `reference_outputs/`.
- Why this design: the earlier ETL-with-rules task (Make/Zapier/n8n) was solved at ~98% by every blind attempt because every trap had checkable evidence in the files. Here the correct answer needs measurement choices the documents do not spell out: identity resolution, maturity adjustment of open deals, geo-holdout incrementality, marginal (not average) response with seasonality controlled, and net contribution after commission tiers and lagged refunds.
- Truth: meta 1.66, lsa 1.11, non-brand 1.06, brand 0.71, retargeting 0.48 (incremental contribution per marginal dollar). Reference estimate picks meta on 6 of 6 seeds tested.
- All data is synthetic.
