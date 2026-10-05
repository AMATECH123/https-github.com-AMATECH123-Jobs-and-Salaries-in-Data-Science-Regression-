# Rubric (100 points). Grader-only. Task: Brightwater 2024 federal income tax (C corporation)

Ground truth: `author/world_truth.json`; reference solution reproduces it from the files alone (balance due USD 446,747). Auto-scored items by `author/score_tax.py` (90 pts, amounts within 0.25% or about 1 USD for small items); 10 pts by reading.

## Final answer and key figures (all exact to 0.25%)
| Item | Truth | Pts |
|---|---|---|
| Balance due | 446,747 | 30 |
| Book pre-tax income (ledger, excluding the federal provision) | 9,480,222 | 6 |
| Taxable income before NOL (after 163(j)) | 15,041,600 | 6 |
| Taxable income after NOL | 3,008,320 | 4 |
| Permanent items: 50% of meals 105,935; client entertainment 86,644; fines 70,960; lobbying share of dues 36,240; key-man life 62,400; gifts over USD 25 per recipient 20,535; transit passes 213,600 | 596,714 total | 4 |
| Bad debts: provision 312,000 less specific write-offs | 82,867 | 3 |
| Accruals: 2.5-month rule for non-owner bonuses and PTO; owner bonus only when paid; prior-year items paid in 2024 | 149,846 | 5 |
| Depreciation: book 2,014,097 add-back less tax depreciation (existing 2024 plus additions) | -2,546,591 | 7 |
| Section 179 deduction after phase-out (limit 860,000) | 860,000 | 2 |
| Section 1245 gain on disposals less book gain/loss | 194,898 | 3 |
| Section 174: capitalise 2024 domestic and foreign research and amortise (10%/20%/20% domestic; 1/30, 2/30 foreign) | net adjustment 6,242,444 | 6 |
| Section 163(j): limit 6,558,400 on ATI that is not increased by depreciation; disallowed interest added back | 841,600 | 5 |
| NOL deduction limited to 80% of taxable income | 12,033,280 | 5 |
| Tax at 21% | 631,747 | 2 |
| Payments to date | 185,000 | 1 |
| Mid-quarter convention stated as applying | yes (Q4 share 44.2% after section 179; 34.4% before) | 2 |
| Memo form: one page, balance due on top, elections and biggest adjustments listed, waterfall chart from book income to taxable income | | 10 |

## Authorities (for review)
IRC 11(b) 21%; 274(n) meals 50%; 274(a) entertainment; 274(e)(4) employee social events 100%; 274(b)(1) gifts USD 25; 274(a)(4) transit; 162(f) penalties; 162(e) lobbying; 264(a)(1) key-man life; 166 specific charge-off; 404(a)(5)/Reg. 1.404(b)-1T and 267(a)(2) accruals; 168(k) bonus 60% for 2024; 179 limits USD 1,220,000 / 3,050,000 (Rev. Proc. 2023-34); 280F auto cap USD 20,400 first year with bonus (Rev. Proc. 2024-13); 168(d)(3) mid-quarter test (basis reduced by section 179, not bonus); Reg. 1.263(a)-1(f) de minimis USD 5,000 with an AFS; 1245; 174 as in effect for 2024 (the 2025 legislation expensing rules apply to tax years beginning after 2024); 163(j) 30% ATI without depreciation add-back for 2022-2024; 172(a)(2) 80% NOL limit.

## Effect of plausible mistakes on the balance due
| Mistake | Balance due | Change |
|---|---|---|
| Section 174 costs expensed immediately (2025-law mix-up) | 262,891 | -41% |
| NOL deducted at 100% | 143,566 | -68% |
| 163(j) ATI with depreciation add-back (EBITDA) | 392,500 | -12% |
| 100% bonus depreciation | 415,763 | -7% |
| Section 174 first-year deduction 20% (no midpoint) | 416,078 | -7% |
| Owner bonus deducted when accrued | 433,517 | -3% |
| Section 179 phase-out ignored | 443,538 | -0.7% |
| Mid-quarter convention missed | 445,976 | -0.2% |
