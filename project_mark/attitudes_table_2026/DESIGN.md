# Design note: the 2026 attitudes table

Domain: Survey Research and Official Statistics. Objective: Data Extraction and Conformation (ETL / pipeline
build). Shape: a scorecard against a threshold, run over twenty indicators conformed from a 6,942 variable
survey file to the compendium's table schema, with the previous edition reproduced as the continuity gate.

## Why this task, after eight solved ones
Every earlier task put the deciding check in the prompt's own asks (how many days measured, whether a station
qualifies, how counted trains were placed against the schedule), so the models were pointed at the trap. Here
the prompt asks only for outcomes: the figures, the set of indicators reported as moved, what the drafts
measured, the restatements, the movers and the closest call. The checks that decide the set live in the
standard and in the data, and a single systematic shortcut costs many criteria at once.

## The forced answer
Nine of the eighteen indicators with a 2024 figure are reported as moved over the decade (2014 to 2024):
welfare spending too little (+13.9 points), abortion for any reason (+13.0), confidence in medicine (minus 12.8),
very happy (minus 8.5), Democrat including leaners (minus 7.7), environment spending too little (+7.5), health
excellent (minus 6.9), financially satisfied (minus 4.7), no religion (+4.7). Nine are not reported: death
penalty, gun permits, confidence in television, America a better country (strongly agree), moderate, lower
class, afraid to walk, liberal, confidence in press. Two were not fielded in 2024 (parks and recreation spending,
aged living with children) and are carried without a change. Neither draft is certified.

## The mechanisms, all on honest data
1. Design based sampling error. The standard says the error is estimated under the survey design from the
   variance strata and PSUs in the file. The design effects on these items run from 1.6 to 3.2, so simple random
   sampling errors are a fifth to nearly a half too small. Research's draft (fifteen moved) is exactly the
   simple random sampling reading on the right weight: six indicators (trust, death penalty, gun permits,
   suicide, Bible, get ahead) sit between the two margins, with design based t values of 1.62 to 1.86 against
   SRS t values of 2.14 to 2.68. A model that skips the design, or implements it wrongly, ships the wrong set.
2. One weight for all years. The standard says all years in the table are on the same weight and earlier years
   are restated when the weight changes. The editor's draft (ten moved) keeps the 2016 edition's 2014 figures
   (WTSSALL) beside 2024 figures on WTSSPS; the mixed weights add up to 1.2 points of spurious change and push
   gun permits over the margin. Nineteen of the twenty 2014 figures restate at one decimal;
   the largest restatement is Democrat including leaners, 44.7 to 43.6.
3. Over correction on the 1987 column. The 2016 edition's note says it applied OVERSAMP to 1987 because WTSSALL
   does not adjust for the Black oversample, and the codebook labels OVERSAMP as the weight for the oversamples.
   WTSSPS already carries that adjustment: on WTSSPS the Black share of the 1987 sample is 11.0 percent, in
   line with 1988 on the same weight (11.0); on WTSSPS times OVERSAMP it is 4.1 percent. A model that carries
   OVERSAMP forward moves the 1987 figures of trust, Democrat, death penalty and others by one to two points.
   The first edition column and the long run mover depend on it (marijuana, 17.4 to 67.0, is the mover either
   way; the 1987 figures are each their own criterion).
4. Mapping by wording. The previous edition's table names indicators by their published wording and the
   response counted, never by variable. Welfare maps to NATFARE (form X wording "Welfare"), not NATFAREY
   ("Assistance to the poor", 70 percent too little), and environment to NATENVIR, not NATENVIY. The continuity
   gate (reproduce the 2016 figures on the 2016 method, to 0.1 and to the respondent count) catches a wrong
   mapping: all twenty reproduce when mapped right, so none is held.
5. The ready made measure. The codebook carries unweighted record counts by year for every variable. A model
   that computes 2024 shares from those counts gets unweighted figures; the table is weighted.
6. The codebook snapshot is incomplete for 2024: it lists CLASS and HEALTH as fielded through 2022 and CAPPUN
   on ballots B and C only, while the file carries 3,268 class, 3,294 health and 2,067 death penalty responses
   in 2024 across every mode. The file decides; a model that trusts the codebook's year list marks lower class
   and health as not updated and loses a reported mover.

## Items excluded for determinism (first dry run)
In 2024 NORC fielded several classic items (TRUST, GRASS, BIBLE, GETAHEAD, FAIR, HELPFUL, COURTS, POSTLIFE,
RELITEN, DIVLAW, RACOPEN) only to in person and phone respondents, while the 1,762 web respondents received
experimental versions (TRUSTV, TRUSTNV and so on). Their 2024 figures rest on a non random half of the sample,
and SUICIDE1 reached only part of the web sample. The first dry run flagged this and held four indicators as
not updated, which ten experts would not agree on. Those five indicators were replaced with items that reached
the full 2024 sample (health, confidence in television, moderate, lower class, America better), checked by the
share of web respondents among those answering (0.53 to 0.57, matching the sample).

## Determinism
- Weight, denominator, years, margin and the design based error are each fixed by the standard.
- Domain and subset variance estimation give the same errors here (every PSU keeps respondents in the domain).
- The set is unchanged at a margin of 2.0, under t with the design degrees of freedom, and under WTSSNRPS in
  place of WTSSPS. Nearest t values to 1.96 are 1.86 (death penalty) and 2.77 (financially satisfied).
- The closest call is measured in points of the 2024 figure, as the prompt asks: death penalty needs 0.20
  points (61.9 instead of 62.1); next is lower class at 0.28.
- Research's 15 and the editor's 10 are each reproduced exactly by their method (checked in build_golden.py);
  the draft tables are in the workspace, and the editor's 2014 column equals the 2016 edition's figures, so the
  reader can test readings against them.

## Critical components (what the rubric should weigh)
1. Nine indicators reported as moved, named; neither draft certified.
2. Research's draft measured with simple random sampling errors; the editor's draft mixed WTSSALL 2014 figures
   with WTSSPS 2024 figures.
3. 2014 figures restated on WTSSPS; largest restatement Democrat including leaners, 44.7 to 43.6 (minus 1.2).
4. Largest decade mover welfare spending (+13.9); largest since the first edition confidence in medicine
   (53.1 to 26.3, minus 26.7).
5. Closest unreported indicator the death penalty, 0.20 points short (61.9 instead of 62.1).

## Supplementary answers
1. 2024 figures (percent): very happy 23.4; health excellent 18.9; death penalty 62.1; gun permits 68.5;
   confidence in television 8.2; abortion any reason 58.0; welfare too little 33.4; environment too little 65.7;
   financially satisfied 22.6; afraid to walk 32.8; liberal 27.5; Democrat 35.9; no religion 25.7; confidence
   press 7.5; confidence medicine 26.3; moderate 37.5; lower class 9.7; America better strongly agree 22.5.
2. First edition (1987) figures on WTSSPS: happy 33.6; health 34.9; death penalty 73.5; gun permits 70.9;
   television 11.3; abortion 41.0; welfare 23.4; environment 69.3; parks 31.1; satisfied 29.4; afraid 36.9;
   liberal 28.2; Democrat 48.8; no religion 7.6; press 18.3; medicine 53.1; moderate 39.7; lower class 4.9;
   aged 52.7; America better not fielded in 1987.
3. Sampling errors of the decade change (points): happy 1.55; health 1.49; death penalty 1.95; gun permits
   2.01; television 1.29; abortion 2.46; welfare 2.17; environment 2.43; satisfied 1.70; afraid 2.22; liberal
   1.66; Democrat 1.74; no religion 1.39; press 1.13; medicine 1.95; moderate 1.85; lower class 1.00; America
   better 2.36.
4. All twenty 2016 edition figures reproduce under the 2016 method; none held.
5. Not updated: parks and recreation spending (2014 figure 30.8), aged living with children (54.9).
