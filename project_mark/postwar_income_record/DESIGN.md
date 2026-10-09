# Postwar farm and nonfarm income record (Survey Research and Official Statistics)

Objective: Data Extraction and Conformation. Built 2026-10-09 under the program's 9 October rules
(two long scanned PDFs as the large files, one distractor named inside a question in the prompt,
a natural prompt without a checklist).

## The ask
A historian wants the farm and nonfarm family income gap for 1956 to 1961 from the Census Bureau's
contemporaneous Current Population Reports, the full residence detail of the three reports lined up in
one table, a chart, and a memo. The 1955 persons report is the distractor, raised in a question.

## Inputs (9 files, 12.1 MB zipped)
Three scanned P-60 reports (47, 62 and 44 pages, IRIS scans with no usable text layer), the persons
only report for 1953 (24 pages), five of the Bureau's historical income table pages (F-1, F-7, P-2, P-3,
changes in methodology). All pulled from the GovDocs1 corpus copies of census.gov files, unchanged.

## Deterministic recommendation
The three reports do not support one farm series across 1956 to 1961. The farm definition changed to the
1960 Census definition from the 1959 income year (No. 37 page 13, which says the change cut the farm
population by about one fifth; footnote 1 to Table 17 of No. 37 and Table 19 of No. 39 suppresses farm
figures before 1959 for that reason). The like for like comparison runs 1959 to 1961: farm family median
2,799 to 3,238 dollars (+15.7 percent), nonfarm 5,619 to 5,930 (+5.5 percent), farm to nonfarm ratio
0.50 to 0.55. The 1956 figures (farm 2,375, nonfarm 5,061, Table 13 of No. 27; Table 1 rural farm 2,371)
stand under the 1950 definition and the 36.7 percent 1956 to 1961 rise read off Table 1 is not to be reported
as a like for like change.

## Critical numbers
1. Farm definition change, 1960 Census basis, effective 1959 income year; farm population down about one fifth.
2. Comparable series (No. 39 Table 19): farm 2,799 / 2,876 / 3,238; nonfarm 5,619 / 5,813 / 5,930 (1959 to 1961).
3. 1956 (No. 27): Table 1 rural farm 4,908 thousand families, median 2,371; Table 13 nonfarm 5,061, farm 2,375.
4. 1960 and 1961 farm families 3,490 thousand (both reports); farm share 11.3 percent (1956) to 7.5 percent (1961), part reclassification.
5. The 1960 report prints no urban or rural nonfarm counts; nonfarm for 1956 and 1960 can only be derived by
   taking farm out of the national distribution with the printed counts (38,537 and 41,945 thousand), medians by
   linear interpolation about 5,051 and 5,799 dollars, which are estimates.
6. Modern F-7 revised the counts (43,497; 45,539; 46,418) and two medians (4,780; 5,735) against the reports.

## Honest traps
- The naive answer (Table 1 farm 1956 against Table 1 farm 1961) ignores the definition break that the package
  states three times.
- Nonfarm is not printed for 1956 or 1960 in Table 1 and the 1960 report has no sub national counts, so the
  only route is subtraction, and the derived medians have to be labelled as estimates.
- The 1960 and 1961 reports split 7,000 to 9,999 dollars; 1956 does not.
- The 1960 scan is bound out of order (pages 9 to 16 after 17 to 24, 17 to 24 twice); page 13 with the
  definitions is PDF page 29.
- Table 1 and Table 19 medians differ (5,737 against 5,744 for 1961) because of the households universe.
- Alaska and Hawaii from 1959; housing unit definition from 1960; nonresponse imputation from 1961.
- About 1,000 cells have to be read off scans; percent columns sum to 100 within rounding, which is the check.
- The persons report has no family tables (its own page 2 says a later report will carry families).

## Deliverables (golden/)
residence_income_1956_1960_1961.csv (1,160 rows, long format with status and source per cell),
farm_nonfarm_medians.png, farm_nonfarm_memo.pdf, figures.json. build_golden.py and transcription.py rebuild them.

## Rubric (20 items, weight 5 each)
1. CSV covers 1956, 1960 and 1961 for both families and unrelated individuals.
2. 1956 residence detail present for all eleven classes (urbanized by size, other urban by size, rural nonfarm, rural farm).
3. 1960 residence detail present for all eleven classes.
4. 1956 cells: rural farm families 4,908 thousand, median 2,371; urban families median 5,221; rural nonfarm 4,619.
5. 1960 cells: all families 45,435, rural farm 3,490, medians 5,620 and 2,875; urban median 5,911.
6. 1961 cells: families 46,341 / 42,851 / 3,490, medians 5,737 / 5,924 / 3,241; unrelated 11,163 / 10,741 / 422.
7. Five spot checked distribution cells correct (1956 rural farm under 500 dollars 11.8; 1960 urbanized 1,000,000 and over 10,000 to 14,999 dollars 14.0; 1961 farm families 2,000 to 2,499 dollars 8.6; 1956 unrelated rural nonfarm 500 to 999 dollars 27.8; 1960 unrelated total under 500 dollars 14.6).
8. The 7,000 to 9,999 dollar bracket is conformed across years (combined for 1960 and 1961 or 1956 flagged as coarser).
9. The 1960 urban and rural nonfarm counts are shown as not available, not invented or borrowed from 1956.
10. Nonfarm for 1956 and 1960 derived by removing farm from the national distribution with the printed counts (or for 1956 by weighting urban and rural nonfarm), within 0.3 points of the golden cells.
11. Derived nonfarm medians labelled as estimates, within 75 dollars of 5,051 (1956) and 5,799 (1960), or the Table 13 and Table 17 series values 5,061 and 5,813 cited with their universe.
12. Memo states the farm definition changed to the 1960 Census definition between the 1956 and 1960 income years and that this breaks comparability (cites page 13 of No. 37 or the Table 17 or 19 footnote).
13. Memo gives the comparable 1959 to 1961 farm and nonfarm medians from Table 19 (or Table 17 for 1959 and 1960).
14. Memo does not present the 1956 to 1961 farm median rise (about 37 percent) as a like for like change.
15. Memo notes the farm family count fell from 4,908 to 3,490 thousand and that the fall mixes exodus with reclassification.
16. Memo notes at least two of: Alaska and Hawaii from 1959; housing unit definition from 1960; nonresponse imputation from 1961; Table 1 against households universe.
17. Memo notes the modern F-7 figures differ from the reports and gives at least one pair (for example 45,435 against 45,539 for 1960).
18. Persons report identified as persons only for 1953 with no family or residence tables, to be left aside.
19. Chart does not draw a continuous farm line from 1956 into 1959 to 1961 without marking the break.
20. No fabricated figures: every number in the memo traces to a page in the package.

## Path from raw data to the recommendation
1. Render the scans (pdftoppm), find Table 1 in each report (pages 21, 25 and 16), read the cells, check column sums.
2. Note the 1961 report prints farm and nonfarm only and the 1960 report prints no sub national counts.
3. Find the series tables (No. 27 Table 13, No. 37 Table 17, No. 39 Table 19) and their footnote on the farm definition; read No. 37 page 13.
4. Derive nonfarm for 1956 and 1960 by subtraction; validate on 1961 where nonfarm is printed; interpolate medians by the Bureau's method.
5. Line the detail up in one CSV, chart the two definitions separately, write the memo with the comparable change and the caveats.
