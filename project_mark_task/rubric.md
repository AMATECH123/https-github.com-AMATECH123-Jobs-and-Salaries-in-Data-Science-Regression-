# Rubric (100 points). Grader-only.

Ground truth comes from `author/reference_outputs/` (ground_truth.json, ground_truth_checks.json). Tolerances are stated per item.
Every item is an analytical check on the numbers or the decision, not formatting.

## Deliverable 1: conformed usage CSV (44 pts)
| # | Check | Pts |
|---|-------|-----|
| 1 | One row per workflow per day (or finer) with workflow id, client id, date or month, and a business-run count. Keyed so it can be pivoted by workflow, client and month. | 4 |
| 2 | Total business runs = 593,579 (+/-0.5%). Over-counting from raw rows (~687k) or under-counting both fail. | 8 |
| 3 | Monthly totals each within +/-1% of truth for at least 10 of 12 months (e.g. Feb 2025 = 41,274). Catches overlapping Zapier export batches. | 8 |
| 4 | The 14 migrated workflows (W003, W004, W009, W029, W035, W037, W053, W062, W071, W074, W080, W092, W105, W116) total 64,608 runs (+/-1%). Parallel-run mirror days are not double counted and cutover is honoured. | 6 |
| 5 | Incident duplicates removed: 2025-02-11 Zapier-sourced runs = 821 (+/-3%) and 2024-12-17 Make-sourced runs = 1,133 (+/-3%); n8n duplicate webhook deliveries removed via eventId. | 6 |
| 6 | INTERNAL workflows kept (84,051 runs, +/-1%); sandbox/scratch items (blank workflow_id in crosswalk) excluded. | 5 |
| 7 | n8n-sourced runs = 48,479 (+/-1%): retries, manual runs and errored first attempts excluded; UTC date used (offset converted). Make-sourced = 272,698 and Zapier-sourced = 272,402 (+/-1%) also hold. | 7 |

## Deliverable 2: one-page PDF (56 pts)
| # | Check | Pts |
|---|-------|-----|
| 8 | Recommends **Zapier**. (Wrong platform = 0. No single committed recommendation = 0.) | 15 |
| 9 | Zapier 12-month total EUR 38,927 (+/-3%). | 8 |
| 10 | Comparators: n8n EUR 42,120 and Make EUR 42,352 (each +/-3%), and the stated margin of Zapier over the runner-up is 5-12% (it is 8.2%). | 6 |
| 11 | Churned clients excluded from forward volume and migration (CL-004, CL-010, CL-015, CL-022 -> 101 workflows in scope; 19 workflows dropped). | 5 |
| 12 | Plan selection and contract mechanics: Zapier 200k tasks/month plan with 20% annual discount and ~EUR 1.7k overage, USD converted at 1.124 (revised Sep 2025 rate); Make 250k ops plan with overage and the +14% from Jan 2026; n8n 100k plan because the busiest month (~56k) exceeds the 50k plan (hard cap). At least 2 of 3 platforms correct. | 6 |
| 13 | Migration effort uses current platforms from the change log, not the stale catalog column: 66 workflows / ~382 h to Zapier, 56 / ~418 h to Make, 80 / ~1,040 h to n8n (each +/-5%) with connector-gap hours included. | 5 |
| 14 | Forward units use deployed versions only (draft ignored): Zapier annual tasks ~2.40M (+/-2%), Make ~4.38M ops (+/-2%). | 4 |
| 15 | A chart is present that splits cost by platform into at least subscription and migration labour, readable, labelled in EUR. | 4 |
| 16 | States the main assumptions and says the call is reasonably close (about 8%) rather than overselling certainty. | 3 |

## Known wrong answers (for graders; each loses the decision item #8)
| Mistake | Platform it recommends |
|---------|-----------------------|
| Compare subscription cost only | n8n |
| Ignore connector gaps in migration effort | n8n |
| Use draft versions for per-run units | n8n |
| No dedupe of batches / mirror runs / incidents | n8n |
| Drop INTERNAL workflows (inner join to client master) | n8n |
| Chooses the platform with the most workflows today | Make |

## Scoring note
A model that gets cleaning right but skips any one of connector gaps, draft versions, INTERNAL workflows, or the dedupe rules reaches the wrong platform.
