# Rubric (100 points). Grader-only. Version 5

Ground truth: `author/reference_outputs/ground_truth.json` and `ground_truth_checks.json`. Tolerances per item. Every item checks numbers or the decision, not formatting.

## Deliverable 1: conformed usage CSV (30 pts)
| # | Check | Pts |
|---|-------|-----|
| 1 | Granular rows (workflow x day or finer) with workflow id, client id, date or month, and a business-run count. | 2 |
| 2 | Total business runs = 573,908 (+/-0.5%). One-off backfill runs are real history and stay in; helper runs and Zapier replays are out. | 6 |
| 3 | Monthly totals within +/-1% of `monthly_totals` in ground_truth_checks.json for at least 10 of 12 months. | 6 |
| 4 | The 14 migrated workflows (W003, W004, W009, W024, W026, W045, W046, W050, W055, W061, W078, W080, W101, W116) total 58,793 runs (+/-1%): parallel-run mirrors not double counted. | 3 |
| 5 | Incident duplicates removed (rate is divided out as reported / (1 + rate)): Zapier 2025-02-11 = 751, Make 2024-12-17 = 1,011, Zapier 2025-08-12 = 601, Make 2025-03-04 = 738 (each +/-3%), and n8n duplicates removed via eventId. At least 3 of 4. | 4 |
| 6 | INTERNAL workflows kept (92,567 runs, +/-1%); scratch/sandbox items excluded. | 2 |
| 7 | Zapier-sourced runs for Jun-Sep 2025 = 69,419 (+/-1%): the newest Zapier export's `runs_completed` includes replays and must have `runs_replayed` subtracted; platform splits make 257,193 / n8n 46,645 / zapier 270,070 (+/-1%). | 3 |
| 8 | Re-created / rebuilt ids handled (W019, W021, W022, W056, W065, W066, W094, W100, W102, W111, W113; ~25,766 runs under ids missing from the crosswalk, matched by exact name; zombie old ids not double counted). Per-workflow totals within +/-2%. | 2 |
| 9 | The 11 helper workflows (W016, W025, W039, W048, W060, W071, W079, W083, W103, W106, W112) carry zero business runs; parents unchanged. | 2 |

## Deliverable 2: one-page PDF (70 pts)
| # | Check | Pts |
|---|-------|-----|
| 10 | Recommends **Zapier**. A wrong platform or no single committed recommendation scores 0. | 20 |
| 11 | Zapier 12-month total EUR 45,258 (+/-3%). | 10 |
| 12 | Comparators: Make EUR 48,541 and n8n EUR 49,476 (each +/-3%), and the stated lead over the runner-up (Make) is 4-11% (it is 7.3%). | 8 |
| 13 | Zapier plan-upgrade clause applied: starts on the 200k plan, December peak (~274k tasks) exceeds 125% of allowance, account moves to the 300k plan from January; subscription ~EUR 32.4k plus ~EUR 1.7k overage (USD converted at 1.124). | 6 |
| 14 | Client scope: only CL-015 and CL-022 are churned. CL-004 and CL-010 are flagged churned in the CRM but re-signed (successor records CL-029 / CL-030; usage continues past their end dates), so their workflows stay in scope: 109 workflows in forward scope, 11 dropped. | 8 |
| 15 | Forward volume built correctly: the two one-off backfills (W057 12-21 Nov 2024; W012 10-14 Mar 2025) left out of the baseline only, helper consumption added to parents, drafts ignored. Annual units: Make ~4.77M ops, Zapier ~2.59M tasks, n8n ~576k executions (each +/-2%). | 6 |
| 16 | Plan and migration mechanics: Make 250k plan at the negotiated EUR 1,534 (not the EUR 1,716 quote) with ~EUR 16.1k overage and +14% from Jan 2026; n8n 100k plan because the busiest month (~61.1k) exceeds 50k; migration 63 workflows / ~397 h to Make, 68 / ~371 h to Zapier, 87 / ~1,025 h to n8n (each +/-5%) using current platforms and including connector gaps. At least 4 of these 6 facts correct. | 6 |
| 17 | The opening walk goes from raw recorded runs to 573,908 business runs, naming the removals. | 3 |
| 18 | Chart: stacked by subscription, overage, migration labour per platform, pick marked, total in the title. | 3 |

## Wrong answers (each loses item 10 and cascades)
| Mistake | Platform recommended |
|---------|----------------------|
| Treat all four CRM-flagged clients as churned | Make |
| Treat USD prices as EUR | Make |
| Omit the Make +14% increase | Make |
| Ignore connector gaps | n8n |
| Compare subscription only | n8n |
Also wrong numbers with Zapier kept: ignoring the Zapier upgrade clause, using the Make list price, the Zapier replay drift, including backfills in the forward baseline, drafts, helper units.
