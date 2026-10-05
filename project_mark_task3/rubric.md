# Rubric (100 points). Grader-only. Task: Calloway AP forensic review

Ground truth: `author/world_truth.json` (59 planted cases, USD 4,168,306 total exposure) and `author/reference_outputs/`. The register is scored by `author/score_d1.py`.

## Deliverable 1: exceptions register CSV (50 pts)
Credit per scheme = weight x (cases found / cases). A case counts 1.0 if the vendor (or document ids for tests 1 and 3) is identified and its exposure is within 10% of truth, 0.5 if identified with a different exposure.
| Test | Truth | Weight |
|---|---|---|
| 1 Duplicate payment (across the ERP re-key; voided and refunded duplicates are NOT exposure) | 28 payments, USD 276,730 | 6 |
| 2 Employee-linked vendor (bank account or address+phone match; disclosed related parties and name-only matches excluded) | 3 vendors, USD 785,226 | 6 |
| 3 Split approvals (2+ invoices each 90-100% of the approver's limit, same vendor, 5 days) | 9 clusters, USD 268,691 | 6 |
| 4 Receipts shortfall (goods POs with receipts under 80% of invoice; credited shortfalls and service POs excluded) | 2 vendors, USD 1,186,199 | 6 |
| 5 Bank change diversion (unverified change then payment of USD 25k+ within 14 days) | 5 vendors, USD 498,771 | 6 |
| 6 Shell vendor (creator also entered 80%+ of invoices, TIN not matched) | 2 vendors, USD 504,351 | 5 |
| 7 Contract overrun (paid above 110% of the amended cap) | 4 contracts, USD 467,826 | 5 |
| 8 Blocked vendor payments without override | 6 vendors, USD 180,511 | 5 |
| Precision: share of register rows that match no truth case (decoys flagged as cases) | at least 90% = 5, 80% = 3, 60% = 1 | 5 |

## Deliverable 2: one-page memo PDF (50 pts)
| # | Check | Pts |
|---|-------|-----|
| 9 | Total confirmed exposure USD 4,168,306 (+/-3%). | 10 |
| 10 | The three cases to deal with first are the largest by exposure: V10749 (USD 594k, receipts shortfall), V10748 (USD 592k, receipts shortfall), V10742 (USD 285k, employee-linked vendor). | 8 |
| 11 | Freeze list: exactly the 12 vendors with confirmed test 2, 4, 5 or 6 exposure (V10016, V10136, V10306, V10407, V10633, V10740, V10741, V10742, V10748, V10749, V10753, V10754); credit = 8 x F1 of the list. Tests 1, 3, 7, 8 are recover-and-fix, not freeze. | 8 |
| 12 | Cleared items explained: at least 4 of the 7 lookalike types named with the reason (disclosed related-party vendors; duplicates voided or refunded; short shipments credited; bank changes verified; amended contracts; block overrides logged; near-limit invoices that are single, apart in time, different vendors or approved at a higher limit). | 8 |
| 13 | Chart of exposure by type with bars matching truth within 5% for at least 6 of the 8 types. | 8 |
| 14 | Actions classified correctly (freeze vs recover/fix) and the memo states the recovery priority. | 8 |

## Wrong answers
| Shortcut | Effect |
|---|---|
| Flag every repeated amount or every vendor with no goods receipt | many false positives, precision score 0, total exposure overstated |
| Flag name-only employee/vendor matches or disclosed related parties | false positives in test 2 |
| Treat every unverified bank change as fraud | false positives in test 5 |
| Treat voided or refunded duplicates as exposure | inflated test 1 |
| Use gross short shipment without credit memos | inflated test 4 |
| Miss the vendor re-keying (V##### vs VN-######) | test 1 and test 8 recall falls |
