# Rubric (100 points). Grader-only.

Ground truth: `author/reference_outputs/ground_truth.json` and `ground_truth_checks.json`. Tolerances are per item. Every item checks numbers or the decision, not formatting.

## Deliverable 1: conformed usage CSV (44 pts)
| # | Check | Pts |
|---|-------|-----|
| 1 | Granular rows (workflow x day or finer) with workflow id, client id, date or month and a business-run count, so it can be pivoted by workflow, client and month. | 3 |
| 2 | Total business runs = 593,579 (+/-0.5%). Raw-row summing (~690k) or under-counting both fail. | 7 |
| 3 | Monthly totals within +/-1% of `monthly_totals` in ground_truth_checks.json for at least 10 of 12 months (e.g. Feb 2025 = 41,274). Catches overlapping Zapier export batches. | 7 |
| 4 | The 14 migrated workflows (W003, W004, W009, W029, W035, W037, W053, W062, W071, W074, W080, W092, W105, W116) total 64,608 runs (+/-1%): parallel-run mirrors not double counted, cutover honoured. | 6 |
| 5 | Incident duplicates removed: 2025-02-11 Zapier-sourced = 821 (+/-3%); 2024-12-17 Make-sourced = 1,133 (+/-3%); n8n duplicate webhook deliveries removed via eventId. | 6 |
| 6 | INTERNAL workflows kept (84,051 runs, +/-1%); scratch/sandbox items (blank workflow_id in crosswalk) excluded. | 4 |
| 7 | Platform splits hold (+/-1%): n8n 48,479 (retries, manual runs and errored first attempts excluded; offsets converted to UTC dates), Make 272,698, Zapier 272,402. | 5 |
| 8 | Re-created and rebuilt ids handled: 11 workflows (W019, W021, W022, W052, W063, W065, W097, W100, W101, W111, W113) have ~21,057 runs under ids that are missing from the crosswalk and must be mapped by exact workflow name; stale/zombie old ids after their valid_to window must not be double counted. Per-workflow totals for those 11 within +/-2%. | 6 |

## Deliverable 2: one-page PDF (56 pts)
| # | Check | Pts |
|---|-------|-----|
| 9 | Recommends **Zapier**. A wrong platform or no single committed recommendation scores 0. | 15 |
| 10 | Zapier 12-month total EUR 32,437 (+/-3%). | 8 |
| 11 | Comparators: n8n EUR 35,520 and Make EUR 38,524 (each +/-3%), and the stated margin of Zapier over the runner-up is 6-13% (it is 9.5%). | 6 |
| 12 | Churned clients excluded from forward volume and migration (CL-004, CL-010, CL-015, CL-022: 101 workflows in scope, 19 dropped). | 5 |
| 13 | Plan selection and contract mechanics: Zapier 200k tasks/month plan with 20% annual discount and ~EUR 1.7k overage, USD converted at 1.124 (the revised Sep 2025 rate); Make 250k ops plan with overage and +14% from Jan 2026; n8n 100k plan because the busiest month (~56k) exceeds the 50k plan (hard cap). At least 2 of 3 correct. | 6 |
| 14 | Migration effort uses current platforms from the change log, not the stale catalog column: 66 workflows / ~242 h to Zapier, 56 / ~374 h to Make, 80 / ~1,028 h to n8n (each +/-5%), with connector-gap hours. | 4 |
| 15 | Forward units use deployed versions only (drafts ignored): Zapier annual tasks ~2.40M and Make ~4.38M ops (each +/-2%). | 4 |
| 16 | A chart is present that splits cost by platform into at least subscription and migration labour, labelled in EUR. | 4 |
| 17 | States key assumptions and says the call is reasonably close (about 9%) rather than overselling certainty. | 4 |

## Wrong answers (each loses item 9 and cascades)
| Mistake | Platform recommended |
|---------|----------------------|
| Compare subscription cost only | n8n |
| Ignore connector gaps in migration effort | n8n |
| Use draft versions for per-run units | n8n |
| Drop INTERNAL workflows (inner join to client master) | n8n |
| Treat USD prices as EUR | n8n |
| Pick the platform with the most workflows today | Make |
Mistakes that keep Zapier but break the numbers: stale catalog platform, including churned clients, no dedupe of batches/mirrors/incidents, dropping re-created ids, omitting the Make +14%.
