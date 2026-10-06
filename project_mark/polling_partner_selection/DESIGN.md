# 2026 polling partner selection: task design

Domain: Survey Research & Official Statistics
Objective: Data Extraction & Conformation (ETL / Pipeline Build)
Prompt shape: Scorecard against thresholds (eligibility tests and a test cycle), resolving to a ranked list under
the standard, carried by the conformation of a multi vintage polling record.
Status: built. Every figure reproduces from inputs/ with golden/build_golden.py.

## Why this task
Six versions of the MBTA task (folder mbta_bus_rating_change) were solved by the platform's models because every
deciding fact was reachable by executing a stated convention on clean data. The handbook's most common decisive
miss is a different kind of failure: shipping a result that fails its own last check, taking the ready made
measure, and picking an offered option when none passes. A pollster selection with a back test on the latest
cycle is built out of those failures on real data: the raw accuracy leader has no record in the test cycle, the
second fails the test, the published rating points elsewhere, and an older vintage of the same record with a
precomputed error column points elsewhere again.

## The decision
Select the 2026 midterm polling partner under the board's standard: general election polls of the 2016 to 2022
cycles, the poll as the unit, unadjusted mean error, eligibility (active, no partisan work, 40 polls, 10 polls in
2022), a test cycle (2022 error at or below the median of all 2022 polls), lowest certified error among those
passing. The desk offers Harris Insights & Analytics at 3.05; the standards editor offers NYT/Siena, the published
number one. Both are rejected.

## The forced answer
| Item | Value |
|---|---|
| Selected partner | Beacon Research/Shaw & Co. Research, certified error 4.13 points (58 polls, 84 questions) |
| 2022 test | 2.77 over 10 polls against a median of 4.02 |
| Desk's draft, Harris 3.05 | correct figure, lowest of the volume eligible; one poll in 2022 (50 of 51 from 2018 and 2020); fails the recency test; not certified |
| Standards editor's draft, NYT/Siena | rank 1 in the published ratings (a different measure); fourth among passing at 4.69; best 2022 record (2.11); not certified |
| Funnel | 356 pollsters with a poll in the window; 280 active; 182 with no partisan polls; 13 with 40 polls; 8 with 10 polls in 2022; 5 pass the test |
| Volume eligible, in order | Harris 3.05 (1 in 2022), InsiderAdvantage 3.75 (fails, 4.92), Beacon 4.13 (selected), Marist 4.29, Emerson 4.38, Suffolk 4.45 (fails, 4.12), NYT/Siena 4.69, Morning Consult 4.79 (fails, 6.05), YouGov 4.94, Monmouth 5.62 (2 in 2022), Quinnipiac 5.67 (7), SurveyMonkey 5.88 (1), Redfield & Wilton 6.03 (1) |
| Runner up and flip | Marist 4.29; a rise of 0.16 points ties and the tie goes to Beacon on polls (58 to 56); 0.17 hands it to Marist |
| Partner's record | by cycle 2016 2.69 (11), 2017 3.15 (7), 2018 4.87 (17), 2020 5.83 (10), 2021 6.31 (3), 2022 2.77 (10); by race type Governor 3.08, House district 6.96, generic ballot 3.30, President 3.97, Senate 4.22; bias +1.96; called the winner 79.7 percent; all live phone; published rank 16 |
| Previous selection reproduced | 2021 vintage, 2014 to 2020 with 2020 as test (median 4.79): Emerson College 4.62; the raw leader Siena/NYT Upshot 4.11 fails the 2020 test at 5.55 |
| Same cycles on the current vintage | not the same pollster: Harris 3.04 is selected, Emerson 5.03 third of four |

Determinism checks in build_golden.py: funnel counts; the selection holds with the question as the unit, with
partisan rows dropped instead of pollsters, with a 50 poll gate, with a 5 poll recency gate, with the test median
taken over non partisan polls only, and with odd year elections removed; the previous selection reproduces from
the 2021 vintage; the flip is 0.16; the traps give their recorded answers.

## Where the honest difficulty lives (trap inventory)
1. Ships the raw leader (stops before the last check). Harris Insights has the lowest certified error of any
   pollster that clears the volume test and one poll in the test cycle. Decisive.
2. Reports a failed test and ships anyway. InsiderAdvantage is second on certified error and fails the 2022 test
   (4.92 against 4.02). Decisive for a reader who applies recency but not the test.
3. Uses the ready made measure. The published ratings file ranks NYT/Siena first on a plus minus model; the
   standard's measure is the unadjusted poll error, on which it is fourth. The published rank of the partner is 16.
4. Stops at the older vintage. The 2023 vintage carries precomputed error, bias and rightcall columns and a
   narrower population; on it the standard selects Emerson College.
5. Counts rows instead of units. 25 of the partner's 58 polls carry two or more questions; the unit is the poll.
   The selection holds either way but the figures move (3.86 against 4.13).
6. Population by flag. Partisan is a pollster level exclusion under the standard; the flag is coded NA, DEM, REP
   in the current vintage and blank, D, R in the older ones. Activity exists only in the current vintage.
7. Identity across vintages. Names change (Siena College/The New York Times Upshot is NYT/Siena College by
   rating id); the standard keys on the id.
8. Gate values matter. At a 30 poll gate Research Co. (33 polls) edges the partner by 0.03; the standard says 40.

## Deliverables
- pollster_scorecard.csv: 356 rows, one per pollster with a poll in the window, columns pollster,
  pollster_rating_id, active, partisan_polls, polls, questions, certified_error, polls_2022, error_2022,
  meets_volume, meets_recency, passes_test, selection_rank; passing pollsters first by rank, then by error.
- accuracy_vs_test.png: a scatter of the 13 volume eligible pollsters, certified error against 2022 error, the
  4.02 test line, passing in blue, failing in orange, no test record hollow, every point labelled with name and
  both figures, the partner marked.
- polling_partner_memo.pdf: two pages. Selection; the two drafts; the funnel table; the 13 pollster table; runner
  up and flip; the partner's record by cycle and race type with bias and call rate; the previous selection
  reproduced and the vintage comparison; closing.

## Input package (inputs/, zipped as inputs.zip, 2.3 MB, 13 files, four formats)
The current vintage record and published ratings, the 2023 and 2021 vintages (record, ratings, statistics
workbook), the two codebooks, the licence, the standard and the provenance note. Pulled from the FiveThirtyEight
data repository at commit 4c1ff5e under CC BY 4.0; the Census hosts the first design needed were blocked by the
environment's network policy, and the repository was the publisher hosted source that was reachable.
