# Rubric (100 points). Grader-only. Version 4

Ground truth: `author/reference_outputs/ground_truth.json` and `ground_truth_checks.json`. Tolerances per item. Every item checks numbers or the decision, not formatting.

## Deliverable 1: conformed usage CSV (30 pts)
| # | Check | Pts |
|---|-------|-----|
| 1 | Granular rows (workflow x day or finer) with workflow id, client id, date or month, and a business-run count. | 2 |
| 2 | Total business runs = 568,666 (+/-0.5%). Raw summing, or counting helper-workflow runs, fails. | 6 |
| 3 | Monthly totals within +/-1% of `monthly_totals` in ground_truth_checks.json for at least 10 of 12 months. | 6 |
| 4 | The 14 migrated workflows (W003, W004, W009, W029, W035, W037, W053, W062, W071, W074, W080, W092, W105, W116) total 64,608 runs (+/-1%): parallel-run mirrors not double counted. | 4 |
| 5 | Incident duplicates removed: 2025-02-11 Zapier-sourced = 764 (+/-3%); 2024-12-17 Make-sourced = 1,048 (+/-3%); n8n duplicate webhook deliveries removed via eventId. | 4 |
| 6 | INTERNAL workflows kept (92,567 runs, +/-1%); scratch/sandbox items excluded. | 2 |
| 7 | Platform splits (+/-1%): n8n 46,864, Make 260,731, Zapier 261,071. | 2 |
| 8 | Re-created / rebuilt ids handled (11 workflows W019, W021, W022, W052, W063, W065, W097, W100, W101, W111, W113; ~21,057 runs under ids missing from the crosswalk; zombie old ids not double counted). Per-workflow totals within +/-2%. | 2 |
| 9 | The 11 helper sub-flow workflows (W016, W024, W039, W047, W058, W069, W078, W082, W104, W106, W112) carry zero business runs; parents unchanged. | 2 |

## Deliverable 2: one-page PDF (70 pts)
| # | Check | Pts |
|---|-------|-----|
| 10 | Recommends **Make**. A wrong platform or no single committed recommendation scores 0. | 20 |
| 11 | Make 12-month total EUR 41,268 (+/-3%). | 10 |
| 12 | Comparators: Zapier EUR 44,901 and n8n EUR 45,600 (each +/-3%), and the stated lead over the runner-up is 5-12% (it is 8.8%). | 8 |
| 13 | Zapier plan-upgrade clause applied: starts on the 200k plan, December peak (~269k tasks) exceeds 125% of allowance, account moves to the 300k plan from January; Zapier subscription ~EUR 32.4k plus ~EUR 1.6k overage (USD converted at 1.124). | 8 |
| 14 | Forward volume built correctly: the two one-off bulk backfills (W079 12-21 Nov 2024; W012 10-14 Mar 2025, 20,139 runs) left out, churned clients (CL-004, CL-010, CL-015, CL-022; 101 workflows in scope) dropped, helper consumption added to parents, drafts ignored. Annual units: Make ~4.65M ops, Zapier ~2.53M tasks, n8n ~560k executions (each +/-2%). | 8 |
| 15 | Plan and migration mechanics: Make 250k plan with ~EUR 11.5k overage and +14% from Jan 2026; n8n 100k plan because the peak month (~59.5k) exceeds 50k; migration hours 56 workflows / ~402 h to Make, 66 / ~363 h to Zapier, 80 / ~896 h to n8n (each +/-5%) using current platforms from the change log and including connector gaps. At least 4 of these 6 facts correct. | 8 |
| 16 | The opening walk goes from raw recorded runs to 568,666 business runs, naming the removals (duplicate batches/mirrors/incidents, failures/retries/replays/manual, scratch, helper runs). | 4 |
| 17 | Chart: stacked by subscription, overage, migration labour per platform, pick marked, total in the title. | 4 |

## Wrong answers (each loses item 10 and cascades)
| Mistake | Platform recommended |
|---------|----------------------|
| Ignore the Zapier upgrade clause | Zapier |
| Include churned clients in forward scope | Zapier |
| Drop INTERNAL workflows | Zapier |
| Ignore helper consumption | Zapier |
| Ignore connector gaps | n8n |
| Compare subscription only | n8n |
Also wrong numbers (but Make kept): backfill bursts left in, stale catalog platform, omitting the Make +14%, USD treated as EUR.
