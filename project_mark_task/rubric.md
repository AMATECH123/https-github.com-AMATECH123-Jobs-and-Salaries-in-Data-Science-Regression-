# Rubric (100 points). Grader-only.

Ground truth: `author/reference_outputs/ground_truth.json` and `ground_truth_checks.json`. Tolerances are per item. Every item checks numbers or the decision, not formatting.

## Deliverable 1: conformed usage CSV (44 pts)
| # | Check | Pts |
|---|-------|-----|
| 1 | Granular rows (workflow x day or finer) with workflow id, client id, date or month and a business-run count, so it can be pivoted by workflow, client and month. | 3 |
| 2 | Total business runs = 549,310 (+/-0.5%). Raw summing, or counting helper-workflow runs (~593.6k), fails. | 8 |
| 3 | Monthly totals within +/-1% of `monthly_totals` in ground_truth_checks.json for at least 10 of 12 months (e.g. Feb 2025). Catches overlapping Zapier export batches and helper runs. | 8 |
| 4 | The 14 migrated workflows (W003, W004, W009, W029, W035, W037, W053, W062, W071, W074, W080, W092, W105, W116) total 64,608 runs (+/-1%): parallel-run mirrors not double counted, cutover honoured. | 5 |
| 5 | Incident duplicates removed: 2025-02-11 Zapier-sourced = 764 (+/-3%); 2024-12-17 Make-sourced = 1,048 (+/-3%); n8n duplicate webhook deliveries removed via eventId. | 5 |
| 6 | INTERNAL workflows kept (84,051 runs, +/-1%); scratch/sandbox items excluded. | 3 |
| 7 | Platform splits hold (+/-1%): n8n 46,864, Make 252,215, Zapier 250,231. | 4 |
| 8 | Re-created and rebuilt ids handled: 11 workflows (W019, W021, W022, W052, W063, W065, W097, W100, W101, W111, W113) have ~21,057 runs under ids missing from the crosswalk (matched by exact workflow name); zombie old ids after valid_to not double counted. Per-workflow totals within +/-2%. | 4 |
| 9 | The 11 helper (sub-flow) workflows identified from the catalog notes (W016, W024, W039, W047, W058, W069, W078, W082, W104, W106, W112) carry zero business runs; their parents' runs are unchanged. | 4 |

## Deliverable 2: one-page PDF (56 pts)
| # | Check | Pts |
|---|-------|-----|
| 10 | Recommends **Zapier**. A wrong platform or no single committed recommendation scores 0. | 15 |
| 11 | Zapier 12-month total EUR 32,008 (+/-3%). | 8 |
| 12 | Comparators: n8n EUR 35,160 and Make EUR 41,428 (each +/-3%), and the stated margin of Zapier over the runner-up is 7-13% (it is 9.8%). | 6 |
| 13 | Churned clients excluded from forward volume and migration (CL-004, CL-010, CL-015, CL-022: 101 workflows in scope, 19 dropped). | 4 |
| 14 | Plan selection and contract mechanics: Zapier 200k tasks/month plan, 20% annual discount, ~EUR 2.8k overage, USD converted at 1.124 (revised Sep 2025 rate); Make 250k ops plan with overage and +14% from Jan 2026; n8n 100k plan because the busiest month (~59.5k) exceeds the 50k plan (hard cap). At least 2 of 3 correct. | 6 |
| 15 | Migration effort uses current platforms from the change log, not the stale catalog column: 66 workflows / ~190 h to Zapier, 56 / ~406 h to Make, 80 / ~548 h to n8n (each +/-5%), with connector-gap hours. | 4 |
| 16 | Forward units use deployed versions only (drafts ignored) AND add each helper's consumption to its parent's per-run cost: Zapier annual tasks ~2.53M, Make ~4.66M ops, n8n ~561k executions (each +/-2%). | 5 |
| 17 | A chart is present that splits cost by platform into at least subscription and migration labour, labelled in EUR. | 4 |
| 18 | States key assumptions and says the call is reasonably close (about 10%) rather than overselling certainty. | 4 |

## Wrong answers (each loses item 10 and cascades)
| Mistake | Platform recommended |
|---------|----------------------|
| Compare subscription cost only | n8n |
| Use draft versions for per-run units | n8n |
| Treat USD prices as EUR | n8n |
| Count helper runs as business runs and add helper units | n8n |
Mistakes that keep Zapier but break the numbers (and many items): dropping/including helpers incorrectly, stale catalog platform, including churned clients, no dedupe of batches/mirrors/incidents, dropping re-created ids, omitting the Make +14%, ignoring connector gaps.
