# Data notes (marketing ops, 1 Oct 2025)

Pulled on 1 Oct 2025. Leads cover 1 Jan 2024 - 30 Sep 2025.

- `ghl_contacts.csv` - GHL contact export. Timestamps before 1 Jul 2024 are Central local time (MM/DD/YYYY HH:MM); later ones are ISO UTC. `source` is whatever the form or front desk typed.
- `call_tracking.json` - call tracking log. `started_at` is epoch milliseconds UTC. Each tracking number is tied to one channel in `channel_map.csv`.
- `airtable_deals.json` - Airtable deals. Each deal points at a contact by email, phone and/or GHL contact id, whichever the rep had.
- `jobs_completed.xlsx` - completed jobs, one sheet per quarter. Most rows carry the Airtable deal id; some do not.
- `payments.csv` - payments, refunds and chargebacks by job.
- `ad_spend_daily.csv` - platform spend by channel by day. `platform_reported_conversions` is what each platform's own dashboard claims.
- `season_index.csv` - weekly demand index from the market data service (1.0 = average).
- `geo_map.csv`, `holdout_test_design.pdf`, `commission_and_cost_plan.pdf`, `measurement_policy_v2.docx`, `change_log.txt` - as named.
- Figures in this folder are synthetic.
