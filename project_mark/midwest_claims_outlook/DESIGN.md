# Fourth quarter 2026 Midwest claims outlook: task design

Domain: Economics & Econometrics (official weekly claims statistics; the domain can equally be entered as Survey
Research & Official Statistics)
Objective: Forecasting & Predictive Modeling
Prompt shape: Rule replayed on history (a back test over 26 origins) resolving to a scorecard of twelve states,
with a forecast across many periods (13 weeks by 12 states) as the deliverable.
Status: built. Every figure reproduces from inputs/ with golden/build_golden.py.

## Why this task
Seven headlines across two conformation tasks were reached by both platform models whenever the deciding rule
was written down. The handbook's most common decisive miss is a different kind: shipping a forecast that fails
its own back test. This task is built on that miss with real official data: a prescribed model, a prescribed
benchmark, a prescribed back test, and a decision rule under which three of twelve states must be held because
the model loses to a flat benchmark there, while the model wins for the region as a whole. Both offered drafts
are honest computations (a pooled regional test; an error level cut) and both ship the wrong list.

## The decision
Which Midwest states get the model path in the fourth quarter outlook and which are held on the benchmark
path, and the regional thirteen week total the outlook publishes. The desk's draft publishes all twelve; the
methods lead's holds five. The standard publishes nine and holds three.

## The forced answer
| Item | Value |
|---|---|
| Published on the model path | Illinois, Indiana, Kansas, Michigan, Minnesota, Missouri, Ohio, South Dakota, Wisconsin |
| Held on the benchmark path | Iowa (24.42 against 17.69), Nebraska (26.94 against 22.59), North Dakota (53.13 against 27.95) |
| Regional thirteen week total | 539,951 initial claims, weeks ending 3 October to 26 December 2026 |
| Desk's draft | all twelve on the model path, 560,749; its ground is true (pooled 18.71 against 23.34; region as one series 6.18 against 16.00) and is not the test; not adopted |
| Methods lead's draft | holds Iowa, Michigan, Missouri, Nebraska, North Dakota (model error above 20), 475,040; the level is not the test, Michigan and Missouri beat their benchmarks; not adopted |
| Back test, model against benchmark | MN 5.20/34.39, WI 6.82/23.77, KS 19.60/30.37, MO 24.54/34.10, MI 21.67/30.88, IN 11.02/17.05, IL 9.19/13.16, OH 9.97/13.61, SD 12.00/14.54, NE 26.94/22.59, IA 24.42/17.69, ND 53.13/27.95 |
| Why the held states miss | last year's profile over the back test span does not repeat: Iowa peaked at 3,168 in July 2025 against 2,466 in March 2026; Nebraska at 2,149 in May 2025 against 1,095 in September 2026; North Dakota at 1,452 in May 2025 against 488 in June 2026; the base year is sharper (coefficient of variation 28, 40 and 74 percent) than this year (20, 27 and 29) |
| Against a year earlier | 539,951 against 680,645 in the same thirteen weeks of 2025, minus 140,694 (minus 20.7 percent); largest published change Illinois, minus 50,990 |
| Smallest improvement that publishes a held state | Iowa 6.74 points, Nebraska 4.36, North Dakota 25.19 |

Determinism checks in build_golden.py: 352 weeks ending Saturday with no gaps for every state; the same three
holds under absolute error, under 20 and 30 origins and under a four and a thirteen week ratio; the desk's and the
methods lead's figures reproduce; the record's combined column is empty on 9,640 rows.

## Where the honest difficulty lives (trap inventory)
1. Ships a forecast that fails its back test. The model beats the benchmark for the region and loses in three
   states; the desk's draft ships all twelve. Decisive.
2. Takes a level for a comparison. The methods lead holds states by the model's error level; two of them beat
   their benchmarks by wide margins. Decisive for a reader who tests but misreads the test.
3. Column choice. The record carries regular, pandemic program and combined counts and rates; the combined
   column is empty for every week since February 2022, and the rates are per 100 of the 2019 labor force. The
   standard names regular program counts.
4. Week alignment. Weeks end on Saturday; the model's base is the week 364 days earlier, not the calendar date;
   a 371 day reading would hold South Dakota as well.
5. Dates assembled from three columns, states keyed by FIPS with the crosswalk file.
6. Tempting regressors. Employment and job postings series sit beside the claims; the standard's model uses
   neither.
7. The holds are honest: the base year's seasonal profile in the three Plains states (July, May, May peaks) does
   not repeat in 2026, and a ratio cannot fix timing.

## Deliverables
- q4_claims_outlook.csv: 156 weekly rows (12 states by 13 weeks: state, week_ending, model_forecast,
  benchmark_forecast, published_forecast, published_path) followed by 12 state rows carrying
  model_backtest_error_pct, benchmark_backtest_error_pct and status.
- backtest_by_state.png: paired horizontal bars per state, model (blue, orange where held) beside benchmark
  (grey), labelled, states ordered by the model's margin, held states at the bottom.
- claims_outlook_memo.pdf: two pages. Decision and total; the two drafts; the back test table with held rows
  shaded; why the held states miss; the outlook against a year earlier; what would publish the held states;
  closing.

## Input package (inputs/, zipped as inputs.zip, 10 MB, 16 files, three formats)
Seven tracker data files (state, national and county claims, two crosswalks, employment and job postings), six
documentation files in Markdown and PDF, the repository readme, the standard and the provenance note. Pulled
from the Opportunity Insights Economic Tracker repository at commit b8adef9 (5 October 2026), free use with
attribution to the Department of Labor and Opportunity Insights.
