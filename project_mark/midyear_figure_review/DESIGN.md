# Mid year claims figure review: task design

Domain: Economics & Econometrics (official weekly claims statistics; can equally be entered as Survey Research &
Official Statistics)
Objective: Data Quality & Validation (a published figure reviewed against its record)
Prompt shape: A published statement that does not reproduce on its label; the reviewer must establish what it
measured by exact reproduction, and the outcome follows from the standard's three branches.
Status: built. Every figure reproduces from inputs/ with golden/build_golden.py.

## Why this task
Eight headlines across three datasets were reached by both platform models whenever the deciding rule was
written down and the inputs to it were named. The one item both models failed, on the Midwest claims outlook,
was the one where a position's ground was withheld and the reader had to find what had been measured; both
asserted a plausible story (the desk skipped the back test) instead of searching. This task puts that step on
the headline: the published figure's basis is not stated anywhere and must be found by reproduction. The
standard is explicit about everything else (the order of the review, what reproduction means, the three
outcomes), so experts converge, and rule 5 removes the stories (revisions, clerical error, rounding) that a
reader who does not search would otherwise reach for.

## The decision
The outcome of the review of the mid year note, in the standard's words (stands, reissued, withdrawn), and the
figures published.

## The forced answer
| Item | Value |
|---|---|
| Outcome | Reissued. The figure does not reproduce on its label and the review establishes the basis it was computed on. |
| Basis established | The same twelve states, series and formula with both half years taken one week later than the label: weeks ending 10 January to 4 July 2026 against 11 January to 5 July 2025. Reproduces every number: 1,058,808 against 1,211,608, 12.6 percent. |
| Figures published | The reissued figure with that basis in its label, and beside it the figure on the original label: 1,082,313 against 1,230,465, a fall of 12.0 percent. |
| Committee member's figures | Right: they are the label's basis computed from the record. |
| Exchange of weeks | 2026: week ending 3 January (69,759) leaves, week ending 4 July (46,254) enters, net 23,505 lower. 2025: 4 January (74,195) leaves, 5 July (55,338) enters, net 18,857 lower. The other twenty five weeks are shared. |
| State moving most | Missouri: 11.4 percent fall on the label, 4.4 on the basis, 7.0 points (its July week 8,857 outweighs its first week 5,024 in 2026; the reverse in 2025, 6,840 against 3,524). North Dakota next, 6.3 points the other way. No state changes direction. |
| Wrong outcomes available | Stands (a story about revisions or rounding; rule 5 excludes it, and the count is 23,505 off). Withdrawn (the reader who does not find the basis corrects the figure to 1,082,313 and 12.0; the committee member's request). Reissued on a wrong basis (a reader who matches the percentage only: the eleven states without Indiana give 12.6 on the label's window, 1,005,869 against 1,150,465; the Chicago and Kansas City regions give 12.6 on the later window, 1,043,263 against 1,193,103; rule 3 requires every number). |

Determinism checks in build_golden.py: weeks end on Saturday with no gaps; the label's basis reproduces the
committee member's figures; the later window reproduces the statement; in a family of 180 window
specifications (shifts of up to four weeks, lengths 24 to 28, four memberships) plus the twelve states less any
one or two of them on both windows, the published count 1,058,808 is matched by the later window alone, while
the percentage 12.6 is matched by sixteen specifications; the combined column is empty throughout; Missouri's
two exchanged weeks have the stated order.

## Where the honest difficulty lives (trap inventory)
1. The basis is not written anywhere. The reader must search. A reader who asserts a cause instead of
   reproducing one lands on stands or withdrawn. Decisive.
2. Percentage matches are plentiful; count matches are unique. A reader who stops at the percentage reissues on
   the wrong basis with the wrong totals beside it. Decisive for a reader who searches but not exactly.
3. The committee member's figures are right. A reader primed to find the challenger wrong wastes the search on
   the challenger's computation.
4. Rule 5 closes the stories. Revisions since publication cannot be shown from the one vintage in the
   workspace; the tracker's revisions note records no claims revision since 2023; the published count differs
   from the label's by 23,505, not rounding.
5. The natural cause is documented in the publisher's own notes: the tracker's 2021 error assigned claims to
   the report date rather than the week they reflect, one week later; a sheet keyed by the Sunday a week begins
   does the same. The reviewer need not name the cause; the basis is the weeks.
6. Tempting distractors: the county file (imputed weekly values for Illinois and Iowa), the rate columns (per
   hundred of the 2019 labour force), the national file (sum of 51 series, not the region).

## Deliverables
- figure_review.csv: 13 rows (twelve states and the region): state, label_h1_2026, label_h1_2025,
  label_change_pct, basis_h1_2026, basis_h1_2025, basis_change_pct, basis_minus_label_change_points.
- weekly_claims_windows.png: weekly twelve state claims for 2025 (grey) and 2026 (blue) by week ending date,
  the labelled window and the established window as brackets, the leaving and entering weeks shaded and
  labelled with their claims.
- figure_review_memo.pdf: two pages. Outcome and figures; the committee member's figures; what the figure
  measured and the search; the week by week exchange table; the state table with Missouri shaded; the reply.

## Wording fixed after the dry run
The dry run agent reproduced the headline by a brute force search over every span of weeks. The one tightening
applied: the prompt no longer states the committee member's figures, only that the note does not reproduce on
its own label.

## Input package (inputs/, zipped as inputs.zip, 10 MB, 19 files)
The Opportunity Insights Economic Tracker files pulled at commit b8adef9 (5 October 2026) exactly as served:
seven data files, six documentation files, the repository readme; plus the two scenario documents (the review
standard and the note under review) and the provenance note.
