# Data notes (Ops, 2 Oct 2025)

Exports pulled on 2 Oct 2025 covering 1 Oct 2024 - 30 Sep 2025.

- `zapier_usage_daily.csv` - Zapier usage by zap by day, from three admin exports. Dates are UTC.
  `runs_success` = first-attempt successful runs. `runs_replayed` = replays of earlier errored runs. `test_runs` = runs from the editor.
  `tasks_billed` is what Zapier counted against our plan.
- `make_operations_daily.csv` - Make usage by scenario by day. Semicolon separated. Our Make org is set to German formatting.
  `Executions` is all executions that day; `Failed`, `Retries` and `Manual runs` are subsets of it. `Operations` is what Make billed.
- `n8n_executions.json` - execution log from the n8n API. `startedAt` is in the instance's local time.
- `id_crosswalk.csv` - native platform id to workflow_id. Blank workflow_id means a scratch item.
- `workflow_catalog.xlsx` - workflows (platform column last refreshed March 2025) and per-version module/step counts.
- `client_master.xlsx` - client list from the CRM. Internal workflows use client_id INTERNAL, which is not in this list.
- `connector_support.csv`, `fx_rates.csv`, `incident_log.csv`, `change_log.txt` - as named.
- Over the year a few zaps and scenarios were rebuilt or re-created by hand, so the crosswalk may not have every newest id.
- PDFs and the costing standard are as received / as published by Finance.
- Figures in this folder are synthetic.
