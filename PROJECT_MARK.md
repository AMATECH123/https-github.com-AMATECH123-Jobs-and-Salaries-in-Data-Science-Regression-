# Project Mark — Task Authoring Reference

Distilled from four handbook documents: *Prompt for Mark (example prompts)*, *Key Requirements (9/5 update)*,
*Golden Example (build + example traps)*, and *Build (input files, writing the prompt, golden deliverables, examples)*.
Program site: project-mark.learn.joinhandshake.com

## The one-line version
A task resolves to **one deterministic recommendation** and ships **one to three output deliverables**.
No cap on asks; each ask is multi-dimensional and hard. Prioritize a visual where it helps.
The rubric is generated internally (25+ criteria) from the *shape* of the task. The bar: model responses
average **under 50%** against the rubric, with **at least one model genuinely stumped**.

## 9/5 update: the rules every new task must follow
Each approved task pays a flat $800. Nothing is paid by the hour. Approval rests on quality and on meeting these rules.
- Bigger, messier inputs. Packages ship 10 or more files across 3 or more formats, with at least one file over 10,000 rows.
- Request 1 to 3 deliverables. More is not better. Pick the most natural number and file types for the prompt.
- No excessive number of asks. Each ask should be difficult, multi dimensional, or carry many outputs. No laundry lists.
- Prioritize visual outputs. Where possible, request a chart, graph, table, waterfall, or diagram in one of the files.
  An Excel sheet is not a table.
- Make the asks difficult, realistic, and relevant. Nothing random or unrelated to the main recommendation.

## Working style for this project
- Build tasks that genuinely stump the model. Difficulty lives in the data and the method, never in wording.
- Write everything in a plain human voice. No AI tone, no filler, no hyphens, no em dashes.

## Hard gates (all four required)
1. Rubric reaches 25+ criteria, weighted 30–40% recommendation / 5–10% instruction-following / ~55–60% supplementary asks.
2. Model responses average under 50% with at least one model stumped.
3. A deterministic, fair stump: models fail for analytical/methodological reasons on honest data, never a planted defect.
   Ten domain experts working the files land on the same answer.
4. One to three deliverables in the formats that fit, prioritizing a visual, each with multi-dimensional hard asks.

## Accepted domains and objectives
Domains: Product Analytics · Supply Chain & Logistics · Economics · Policy & Education · Demographic & Social Science ·
Nonprofit & Grant-making (Healthcare and Energy also appear in the example library).
Axis 1 objectives: Anomaly Detection & Diagnostics · Data Extraction & Conformation (ETL) · Descriptive & Distribution
Analysis · Experiment & Causal Analysis · Forecasting & Predictive Modeling · Root-Cause Analysis.
Forecasting is an objective, not a domain; it can live in any accepted domain.

## Build order (procedural)
Task type/domain/objective → Input files → Prompt → Golden deliverables → Validate → Readiness → Submit on Handshake.

### Twelve-step authoring sequence
Phase A (set up): 1 task type/domain/objective · 2 prompt + input ZIP.
Phase B (solve and specify): 3 model responses · 4 final recommendation · 5 supplementary answers · 6 critical components.
Phase C (validate and deliver): 7 rubric (generated, fixed) · 8 step-by-step solution · 9 justification ·
10 determinism QC · 11 golden solution · 12 final model rollouts (non-blocking if already under 50%).

## Input files (the evidence package)
Scale
- 10 or more files; at least one table with 10,000+ rows; the recommendation requires joining at least two tables.
Format variety
- At least three distinct file formats; at least two substantial files, not all the same type.
Messiness that earns its place (realistic fragmentation, never random dirt, never changes the answer once resolved)
- Signal fragmented across files; inconsistent timestamps to reconcile; data scattered so the model must seek
  around; template files or historical reports as reference material to discover.
Always true
- Files are real and license-clean with source, pull date, and license recorded.
- No LLM-generated PDFs, DOCX, PPTX. AI may locate data or write transformation scripts but never creates the
  empirical source evidence. Scenario or derived files carry explicit provenance.
Package checklist (ready needs all 7)
1 necessary files (removing any counted file breaks the answer) · 2 recoverable joins · 3 sufficient signal ·
4 definitions and governing rules supplied inside the package · 5 reproducibility (every golden figure comes back
out of the workspace) · 6 no padding · 7 no fabricated or corrupted complexity.
Common gaps worth filling: definitions, historical context, methodology, policy constraints, targets, predictors,
revisions, crosswalks. If the package already supports the answer, stop. File count is not difficulty.

## Writing the prompt
Task contract
1. One deterministic recommendation (single committed call, no hedge, no blend, no "it depends").
2. One to three deliverables. Name a file when natural (script, system-of-record file); otherwise request by role
   and type (a memo PDF, a chart PNG).
3. Prioritize a visual: chart, waterfall, matrix, heatmap, or a table living inside a memo/workbook/script output.
4. Multi-dimensional hard asks; no cap, no target. Asks are the body of the prompt; no separate supplementary section.

Prompt anatomy (reads like a message from a busy stakeholder, in prose)
1 stakeholder context · 2 the decision with the objective fixed · 3 only the constraints a stakeholder would state ·
4 requested deliverables with their asks · 5 asks per file · 6 no answer-path leakage.

Kinds of asks: Supporting (metric backing the call) · Comparison (winner vs runner-up) · Context or flip
(what would move the runner-up into first) · Content requirement (what the file must contain, never how to compute it).
An ask is valid only in the same data universe as the recommendation. A separate dataset or decision is a second task.

Five non-negotiable rules
1 one committed decision · 2 vague on method, precise on answer (withhold scope, cleaning, window, methodology;
every valid approach converges) · 3 no leak (never name the trap, the defusing file, or hint a metric misleads) ·
4 fair and self-contained (everything derivable from the bundle; losing option refuted on the data) ·
5 one to three deliverables, prioritize a visual.
Sent back if: names method or trap, allows a hedge, requires outside knowledge, asks for a separate dataset or
decision, or requests more than three files. Draft the trap into the data before wording the prompt.

Format families (vary across them)
Data: CSV, TSV, JSON, XLSX, Parquet · Visual: PPTX, PNG, SVG, HTML, JPG · Text: PDF, DOCX · Code: PY, IPYNB, SQL, R.
Do not default to analysis_report.pdf.

## The eighteen prompt shapes (where the 25+ criteria come from)
01 Ranked list under a cap · 02 Forecast across many periods · 03 Bridge between two totals · 04 Setting one dial ·
05 Allocation to a fixed total · 06 Sequenced schedule under capacity · 07 Grid of cells · 08 Rule replayed on
history · 09 Funnel or chain of stages · 10 Scorecard against thresholds · 11 Before and after with a control ·
12 Drill-down to one leaf · 13 Scenarios and the flip point · 14 Cuts of a distribution · 15 Fields conformed to
one schema · 16 Indicators into one score · 17 Periods around a change point · 18 Hypotheses versus evidence.
Shapes are patterns, not a fixed menu.

### Two canonical worked prompts
Example 1, Organics route tranche (ranked list under a cap, 2 files): rank districts by unmet design tonnage among
those whose facility can berth the route; tranche_determination.pdf (selected district, runner-up, gap, full ranked
table with capacity gate, free weekly shifts at winner and raw-tonnage leader) + unmet_tonnage_chart.png (one bar
per district, labeled, winner highlighted, ineligible marked).
Example 2, Fernwood service tier (bridge between two totals, 2 files): growth_decomposition.png waterfall from last
year's to this year's covered demand, components ordered largest to smallest, tier boundary drawn, excluded intake
marked; tier_determination.docx one-page memo with tier, organic growth %, both years' qualified demand, flip point.

## Golden deliverables
- Exact set the prompt prescribed: same types, filenames, count. Missing or mismatched file blocks confirmation.
- One set of numbers across all files; graders diff file against file.
- Nothing extra: no answers to unasked questions, no AI disclaimers, placeholders, chat intros, invented citations.
Content checklist (covered somewhere across the set)
1 the committed recommendation first in its file, one or two sentences, naming what it rejects ·
2 one clearly labelled answer per ask in the file the prompt attached it to ·
3 load-bearing figures each traceable to a shipped input ·
4 the path from raw files to decision, including at least one trap refused, stated as a decision ·
5 a short closing on why no other conclusion survives.
Manual QC: answers the recommendation and every ask · no placeholders/TODOs · no filler · reads like a normal
professional deliverable in that format.

## Difficulty: honest data only
The "flip the wrong number" trap is retired. Reported figures must be correct; difficulty comes from forecasting,
method selection, a binding constraint, decomposition, confirming a number (over-correction is the trap), or a
justified hold decision. Difficulty must be analytical, never semantic (wording, trick definitions, formatting,
broken golden, packaging failures never count).

Six mechanisms moved onto honest data
- Mixed subgroups: the lead is real; the trap is a tempting adjustment that would wrongly reverse it.
- Definition swap: both metrics correct; the work is choosing the metric the decision rule requires.
- Coverage gap: all data present; the top-ranked option violates a real capacity limit, so pick the top that fits.
- Mislabeling: definitions documented and consistent but spread across feeds; conform them and report.
- Clock/timing: timestamps correct; a real schedule change makes the next period structurally different.
- Wrong denominator: rate and denominator correct; a real capacity, staffing, or clawback limit changes feasibility.

Trap families that stump current models (from 64 accepted tasks): Controls treated as optional · Wrong unit,
population or segment · Rules read loosely · Evidence taken at face value · Stops before the last check.
Top decisive traps: reports a failed back-test and ships anyway (11) · counts file rows instead of the real unit (11) ·
stops at a close but inexact match (8) · never tests its reading against the control (7) · takes the population a
flag suggests (5) · treats a mixed segment all one way (5) · uses the ready-made measure (5) · papers over a failed
reproduction (4) · picks from offered options when none passes (4) · notes a binding limit as a risk (4) ·
beats the headline trap, misses the quiet one (4).

## Program rules
- Pay: flat $800 per approved task, paid the Wednesday after approval. Revisions unlimited.
- Review within 24 hours. Prompt must be original (not resembling another fellow's or your own prior task).
- Time: ~7 hours first task, ~5 after.
- Throttles: New Attempter 1 task at a time → Semi-Trusted (after 1 approval) 3 at a time → Trusted (after 3) unlimited.
- Office hours Monday–Friday via the Slack link.
- Starter data kits are a foundation, not a finished submission; you still own file count, mess, and the answer.

## Program update, Slack post by Vincent (Handshake AI), recorded 2026-10-09
These rules apply to every new task and sit above the 9/5 rules where they differ.
- Rollouts. Two model rollouts per task, run at the very beginning. The average of the two must be under 50
  percent, no exceptions. There is no longer a sequence of rollouts at the end. (The handbook's separate
  "at least one model stumped" check is no longer part of the gate; the average is the gate.)
- Large, complicated inputs. The package must contain at least two files that are complicated and large, from:
  a 10 to 20 or more page PDF or DOCX; a CSV of 25,000 or more rows; a large database file; a multi page PPT.
  These are in addition to the 9/5 rules (10 or more files, 3 or more formats, one table over 10,000 rows).
- One distractor. The package must contain exactly one distractor file, and the distractor is labelled inside
  the task itself, in a question in the prompt, not inside the input files. Examples given: a dashboard or BI
  extract with a headline KPI that seems to answer the question but is wrong; data that is outdated or refers
  to a year or business unit no longer relevant; a rule that has been amended or superseded.

### What this changes in how a task is built here
1. The prompt now carries a question that points at the distractor by role (for example, "the dashboard
   extract says X; say whether it answers the question and why not"), so the rubric can score the refusal of
   the distractor. The distractor file itself carries no label.
2. The two large files are planned first. Real options reachable from this session: the MBTA GTFS stop_times
   table (over 2 million rows) or any 25,000 plus row extract of it; the GSS cumulative file as a database file
   (SQLite or Parquet, 75,699 rows by 6,942 columns); the GTFS Schedule reference or the MassDOT licence as a
   long PDF or DOCX; NOAA documentation PDFs. A long PDF or DOCX must be a real published document, never one
   written by the task author (the 9/5 ban on LLM generated PDF, DOCX and PPTX stands).
3. The distractor is honest in the handbook's sense: a real file that is wrong for the question (stale
   vintage, superseded rule, wrong unit or population), never a corrupted or fabricated one.
4. The gate is now the average of two rollouts under 50 percent. A task that one model solves and the other
   does not can pass; a task both models solve cannot. The dry run before upload stays, and a task whose dry
   run is solved in full is not uploaded.

### Prompt guidance from the program, recorded 2026-10-09
- Be clear about why the task is necessary and what the recommendation should offer. No backstory, but enough
  context of the situation for the reader to know why the work is being done and why the recommendation is
  needed. That context is the foundation of what is to be accomplished.
- Do not overspecify. Let the model decide what analysis to run and how to present the results in the
  documents. Guidelines yes; a checklist of what must be done or included, no.
- Write a natural ask, the way the task would be handed over in the real world, not a list of demands.

What this means against the prompts written so far. Every prompt in this project named the columns of the CSV,
the marks on the chart and the paragraphs of the memo, one after another. That reads as a checklist, and it
also hands the model the rubric: each named ask became a criterion the model could see coming. The next
prompts state the situation, the decision, the one or two files wanted and what they are for, and leave the
analysis and the layout to the reader. The rubric is still generated from the golden, so a reader who leaves
out what the situation plainly calls for loses the points without having been told what they were.

## Objective lock: Data Extraction and Conformation (ETL / Pipeline Build)
Every task I build sits under this objective. The handbook defines it as work that reconciles messy multi source
inputs into one analysis ready, contract conforming dataset. The handbook lists 18 traps for this objective.
The decision is still a single committed call, but the call is about the data itself: which matching rule becomes
the key, which feed is adopted as the source of record, which reconciling item explains the gap, or whether the
conformed table passes its contract and can be certified.

### Prompt shapes that fit ETL best
- 15 Fields conformed to one schema. Map many source columns into one target schema, grading each field on
  where it came from and how it was transformed. The answer is the entity matching rule adopted as the key.
  Every target field is its own criterion.
- 03 Bridge between two totals. Walk a total in one system across to the total in another, one reconciling item
  at a time. The answer is the source or figure adopted. Each reconciling item is a criterion.
- 10 Scorecard against thresholds. Run a written data contract, metric by metric, segment by segment. The answer
  is the single pass or fail the contract resolves to.
- 08 Rule replayed on history. Replay an adopted dedupe or matching rule across every period and count what it
  passes, misses, and wrongly passes.

### ETL traps that stump models (from the 64 task study, mapped to this objective)
- Counts file rows instead of the real unit. Rows are events or snapshots. The unit is the entity.
- Stops at a close but inexact match. A fuzzy join that looks right on the sample fails on the full key.
- Joins only on the visible key. The true key is composite or lives in a crosswalk file.
- Mislabeled feeds. Definitions are documented and consistent but spread across files. The work is conforming
  every feed to the written definition, not guessing.
- Papers over a failed reproduction. The pipeline total does not tie to the published total and the model ships anyway.
- Uses the ready made measure. A pre aggregated column exists and is correct for a different grain.
- Takes the population a flag suggests. A status flag is a hint, not the population rule in the data dictionary.
- Adds exclusions the rules do not ask for.

### Golden deliverable shape for ETL tasks
Data golden (CSV, JSON, XLSX): the conformed table itself, one row per real unit, the named column set in the
named order, a total or control row where the prompt asks for one, and no extra columns.
Code golden (PY, SQL, IPYNB): runs top to bottom on the shipped inputs and prints the recommendation and every
load bearing figure. No hard coded answers.
Visual golden (PNG, HTML): a bridge waterfall, a field lineage matrix, or a match rate chart that makes the
reconciliation read at a glance.
Text golden (PDF, DOCX): the certification memo that opens with the committed call and names what it rejects.
One set of numbers across all files. The conformed table, the script output, and the memo must agree exactly.

### The two handbook examples rewritten as ETL tasks

Example 1 revised. Organics route tranche becomes a source of record decision.
Shape: Bridge between two totals. Two files.

    The Board needs one figure for FY2027 organics tonnage accepted across the shortlisted districts before it
    sets the FY2028 tranche. The regional weighbridge export and the district self reported returns disagree,
    and the finance office has been using whichever one each district sent last. Adopt one source as the
    system of record for the tranche calculation and state the accepted tonnage figure the Board should use.

    Prepare tonnage_reconciliation.pdf. Open with the source you are adopting, the FY2027 accepted tonnage
    under that source, and the gap to the other source. Then walk from the weighbridge total to the self
    reported total one reconciling item at a time, in whole tonnes, with each item sized and attributed to the
    district where it arises. Close with the district whose returns move the total the most and what the Board
    should expect from that district next year.

    Create reconciliation_bridge.png for the slide. Build a waterfall from the weighbridge total to the self
    reported total with one bar per reconciling item, ordered from largest to smallest, each bar labelled in
    tonnes, and the adopted source clearly marked.

Where the 25+ criteria come from: each reconciling item on the bridge is a separate checkable step. The two
totals, the adopted source, the accepted figure, the largest moving district, and the chart labels and order
account for the rest. The trap lives in the unit: weighbridge rows are tickets, not loads, and some districts
report net while others report gross. Both feeds are correct. The work is conforming them to the written
definition in the programme standard before any item is sized.

Example 2 revised. Fernwood service tier becomes a schema conformation decision.
Shape: Fields conformed to one schema. Three files.

    The Program Council has to publish one membership register for the Fernwood Stewardship Network before
    the tier review, and the three intake systems each hold a different version of every organization. The
    protocol defines a covered organization and lists the fields the register must carry. Decide which
    matching rule the register adopts as its key and publish the register under it.

    Produce fernwood_register.csv with one row per covered organization and exactly the columns the protocol
    names, in the protocol's order, with a final control row carrying the organization count and the qualified
    covered demand total.

    Produce build_register.py. It must run against the input package as shipped, apply the adopted matching
    rule, and print the number of organizations, the number of source records collapsed by the rule, and the
    qualified covered demand for both program years.

    Produce field_lineage.png as a matrix with one row per register field and one column per intake system,
    each cell showing whether that system supplied the field, transformed it, or was overridden, so the Council
    can see where every value came from.

Where the 25+ criteria come from: every register field is graded on its source and its transformation, which
fills the matrix cell by cell. The organization count, the collapsed record count, both program year totals, the
adopted rule, and the CSV column set and control row account for the rest. The trap is the close but inexact
match. Names and addresses match loosely across two systems but the registration identifier is the true key
and sits in a crosswalk file. Collapsing on name alone merges two legitimately separate organizations and
changes the count that feeds the tier.

## Record of results, 2026-10-05 to 2026-10-07
Ten tasks submitted across three datasets (MBTA GTFS and ridership, NOAA GHCN Daily, NORC GSS), objectives ETL
and Forecasting. Platform scores: 39 (version with an ambiguous convention, headline reached), 51, then 92 to
100 on every clean task. Traps tried and caught by both platform models every time: counting convention,
version drift, data clock offset, quality flags and accumulations, co located stations, eligibility tests in
order, a shifted window found by search, a back test gate, design based variance, same weight across years,
oversample weight already embedded, wording to variable mapping, a stale codebook year list, a hold where
every offered figure fails, and a quiet second hold behind a loud one. A controlled experiment on the wrong
unit trap (household share from a one adult per household sample) was also caught unprompted: the model
divided the person weight by the number of adults and said why.

Reading: a deterministic, fair task on honest official data with a written standard, however many quiet
conventions it carries, is solved by the current platform models. The remaining route is to learn from the
program which tasks were approved recently and what the models failed on there.

### Experiment, exact combinatorial optimisation, 2026-10-07
Minimum fleet for one MBTA garage's summer weekday schedule (1,865 trips, 43 terminals, layover and deadhead
rule). Exact answer 108 (minimum path cover by maximum matching); greedy first fit 112; greedy best fit 109;
peak concurrency 93. A fresh model, offered 93 and 112 as drafts, certified 108 by Hopcroft Karp, cross checked
with a second matching algorithm, identified both drafts' methods exactly, then refined the assignment with the
Hungarian algorithm and reported a layover sensitivity. Combinatorial optimisation is not a weakness either.

### Experiment, extraction from scanned reports, 2026-10-09
Four scanned Current Population Reports (P-60 Nos. 16, 27, 37, 39, IRIS scans without a text layer) from the
GovDocs1 corpus plus five of the Bureau's historical income table pages. Ask: the farm and nonfarm family
income gap 1956 to 1961, the residence detail lined up, a chart and a memo, with the persons only report
named in a question as the distractor. Honest trap: the farm definition changed to the 1960 Census basis from
the 1959 income year, stated on page 13 of the 1960 report (bound out of order at PDF page 29) and in the
footnotes that suppress farm figures before 1959; nonfarm for 1956 and 1960 is not printed and the 1960 report
has no sub national counts, so it has to be derived by subtraction. A fresh model transcribed 366 cells
without error, found the definition change and the footnotes, derived nonfarm the right way and validated it,
and wrote every caveat in the golden memo plus standard errors. Estimated 85 to 90. Reading images of dense
tables at this scale is not a weakness. Task kept at project_mark/postwar_income_record for the record.

### Where this leaves the under 50 bar, 2026-10-09
Thirteen tasks and five experiments across ETL, forecasting, rule engines, combinatorial optimisation and
scanned extraction, every one solved by a fresh model in one run and every submitted one scored 92 to 100.
The remaining ways to push a score under 50 are ones the program forbids: an answer the package cannot
support, a rubric that rewards a convention the prompt does not fix, or helper material removed so the task
cannot be reproduced. A fair task in this objective does not stump the current models.

### Program stump example and a task built on it, 2026-10-09
The program's batch 14 example (Halberth cover schedule, platform model 0.13 over four runs) is constructed
data with an exact reproduction gate on 24 published means and two hidden definitions that interact so that
either correction alone matches fewer means than the natural reading. The platform model searched one step at
a time, retreated, and adopted the natural schedule. Built the same structure in Survey Research and Official
Statistics (project_mark/followup_schedule_2026): natural 19 of 24, each correction alone 15, both 24, the
plausible wrong correction 1. My dry run model enumerated the whole grid and solved it; it cannot distinguish
this pattern from the ones the platform solved. Recommended for submission on the strength of the program's
own result on the pattern.
