# Design note: the trust row of the 2026 attitudes chapter

Domain: Survey Research and Official Statistics. Objective: Data Extraction and Conformation (ETL / pipeline
build). Shape: a long run series conformed from the cumulative file to the chapter's series schema, with a
continuity gate on the previous edition and a hold decision as the headline.

## Why a hold
Nine tasks in a row were solved by both platform models whenever an answer existed to compute. The handbook's
most frequent decisive traps are the ones where no offered option passes and the model must publish nothing
new: picks from offered options when none passes, notes a binding limit as a risk, reports a failed check and
ships anyway. This task is built on those. The prompt asks only for outcomes.

## The forced answer
The 2026 edition carries the 2018 figure, 33.8 percent (33.85 unrounded; sampling error 1.68; 1,556
respondents), labelled as the latest figure. No 2024 figure and no decade change are published. The 2022 figure
the 2024 edition printed, 26.2 percent, is withdrawn. Neither draft is certified.

## The two traps, both honest and both in the data
1. The loud one. From 2021 NORC fielded the trust question to its web respondents in two experimental versions,
   TRUSTV ("depends" offered on screen: 15.7 percent trusting, 39.6 percent choosing depends in 2024) and
   TRUSTNV (not offered: 35.4 percent), keeping the standard question for in person and phone interviews. In
   2024 the standard question reached 946 of 3,309 respondents and none of the 1,762 web respondents. Research's
   draft (24.8 percent) is that figure. Rule 3 of the standard (full sample, standard instrument) rules it out,
   and rules out pooling the versions (25.4 percent) and every other combination.
2. The quiet one. 2022 has the same structure: 1,198 of 3,544 respondents got the standard question, all 1,633
   web respondents got the versions. The 2024 edition printed 26.2 percent for 2022, the editor's draft carries
   it, and the continuity gate reproduces it exactly. Rule 7 withdraws it. A model that holds at 2022 beats the
   headline trap and misses the quiet one. 2021 had no standard question at all. The last full sample figure is
   2018.
3. Also present: OVERSAMP on 1987 (43.1 on WTSSPS, 45.2 if multiplied), the codebook's record counts as a ready
   made measure, and the codebook's year list, which shows 2022 as fielded without saying to whom.

## Determinism
- Rule 3 is explicit about mode selection, experimental assignment and offered options; every 2022 and 2024
  reading except a hold fails one of them. Experts converge on 2018.
- The series figures, the high (1984, 49.2), the low (2014, 29.6) and the largest consecutive change (1983 to
  1984, +14.4, 5.4 times its error) are fixed by the weight and the design based error named in the standard.
- All 30 rows of the 2024 edition reproduce to the printed precision; only 2022 is withdrawn.

## Critical components
1. The edition carries 2018 at 33.8 percent; no 2024 figure; no decade change; 2022 withdrawn; neither draft
   certified.
2. Research's draft measured the standard question on the 946 in person, phone and multimode respondents of
   2024, excluding all 1,762 web respondents, who received experimental versions.
3. The editor's draft carried a 2022 figure that rests on 1,198 non web respondents in the same way.
4. Every other figure the 2024 edition printed stands (29 of 30 rows).
5. High 1984 (49.2), low 2014 (29.6), largest consecutive change 1983 to 1984 (+14.4 points, significant).

## Supplementary answers
1. Carried figure: 2018, 33.8 percent, sampling error 1.68, 1,556 respondents.
2. 2024 standard question: 946 respondents (755 in person, 156 phone, 35 multimode), 24.8 percent, 10.5 percent
   depends; TRUSTV 587, TRUSTNV 631; pooled 2,164 at 25.4 percent.
3. 2022: 1,198 respondents (1,036 in person, 132 phone, 30 multimode), 26.2 percent; TRUSTV 577 at 17.1,
   TRUSTNV 590 at 30.3.
4. 2021: standard question not fielded; 2,664 respondents received the versions.
5. 2014 base 29.6; 2018 stood 4.2 points above it, sampling error 2.26, not significant; no change published.
6. Series CSV: 31 rows (every survey year with the question in any form, 1972 to 2024), columns year,
   respondents, figure, sampling_error, status, reason; 1972 and 1973 without sampling error (no design
   variables in the file).
7. Chart: published figures 1972 to 2018 with 95 percent intervals, 2018 marked as carried, 2014 marked as the
   base year, 2021, 2022 and 2024 shaded as years without a published figure.
8. The next edition needs the standard question fielded to every respondent in every mode with the same
   offered options and no experimental version in its place.
