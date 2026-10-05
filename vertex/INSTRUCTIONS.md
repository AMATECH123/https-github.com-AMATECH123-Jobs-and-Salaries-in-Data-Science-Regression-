# Project Vertex: Distilled Instructions

Source: Finance Reasoning Questions project guide (both versions) and the
Golden Example document. This file is the working reference. When in doubt,
the source PDFs win.

---

## 1. What the project is

Write (i) complex financial questions for AI models and (ii) the verified
answers used to grade them.

A good question cannot be answered from memory and cannot be answered with a
single search. It forces the model to chain several real factual look-ups
together, do exact arithmetic on what it finds, and arrive at one specific
answer. If a model could guess it, recall it, or find it in one place, the
question has no value.

Domain: company filings submitted to the U.S. Securities and Exchange
Commission, historical market closes published by exchanges, and US statistical
series published by authorities such as the Board of Governors of the Federal
Reserve System.

---

## 2. The two fundamental rules

### Rule 1: Accuracy

Every fact must be exactly as published by an authoritative source. Every
calculation must be exact. The final answer must be correct and not subject to
interpretation. A question with a wrong answer is worse than no question. If you
are not certain of a value, do not submit the question. Flag it instead.

Concretely:

- Right entity. Alphabet Inc. is not Google LLC.
- Right period. Fiscal years are often not calendar years (Apple FY2024 ends September 2024).
- Right line item. "Revenue" may be net sales, net operating revenues, or total revenues. Record which one.
- Right units and currency. If the filing reports thousands, record thousands. If EUR, do not use USD.
- Verified twice, from the source. Re-open the source and re-read. Never verify from memory or notes.

### Rule 2: Nothing that can change

Every fact must be a settled historical fact pinned to a specific past date or
completed period, reading identically whenever it is graded. Words such as
"current", "latest", "today", "now" invalidate the question.

Concretely:

- A line item in a filed 10-K. Never not-yet-reported earnings.
- A historical index close on a named date. Never a live quote.
- A 10-K filing date. Never "latest" or "current".
- A given year's macro data. Never the "most recent unemployment rate".
- Bureau of Economic Analysis (BEA) data is revised for up to 5 calendar years. Until Q1 2027 BEA data is released, anything from Q1 2021 onward can change. Avoid it or pin the vintage.

The test: if the true answer could differ depending on when it is graded, the
question is broken.

Restatements are fair game if you pin both the fiscal period the figure covers
and which fiscal year's filing you read it from.

The prompt names only the publishing authority. The direct source, accession
number, CIK and URL belong in your citation, never in the prompt.

---

## 3. How a question is built: nodes

Two node kinds only:

- **Retrieval node**: looks up one atomic fact from an authoritative source. One node, one fact, never two.
- **Compute node**: one exact calculation on values already held (ratio, difference, growth rate, "which quarter does this date fall in"). Looks nothing up. Never rounds until the final answer.

**Multi-hop** means a later node needs an earlier node's result. A retrieval
node's key (company, date, period) can be the output of an earlier node.

- Multi-hop: "The S&P 500 close on the date Apple filed its FY2024 10-K." The close cannot be looked up until the filing date is found.
- Not multi-hop: "The S&P 500 close on 2024-11-01." Two independent facts.

Look-ups that run in parallel sit in the same layer and count as one hop. Depth
comes from layers stacked on each other, not from the number of look-ups.

### The over-used pattern

"Find the 10-K filing date, then use that date as the key into a Treasury or
index series" is so over-represented that models pattern-match it. It is still
valid as one hop inside a longer chain. It must never be the backbone.

### The preferred shape: cross-document resolution

A figure in one filing points to a note, the note names a counterparty, and the
counterparty's own filing holds the value you need. Nothing after the first
look-up is knowable until the one before it has returned.

| Node | Look-up / operation | Result |
| --- | --- | --- |
| N1 retrieval | Largest equity-method investment carrying value in the investor's Form 10-K | Carrying amount and investee name |
| N2 retrieval | The equity-method note in that filing identifying the counterparty | Counterparty legal name |
| N3 retrieval | Counterparty's own annual report, same period: total stockholders' equity | Equity figure |
| N4 compute | Carrying value as a share of counterparty equity | The answer |

That is 3 chained retrieval hops: the minimum. One more keyed look-up reaches the goal.

A single filing can carry 3 chained hops on its own (one note naming the
segment, item or period that unlocks the next) but it is harder and less
reliable. Treat it as the exception.

---

## 4. Depth and hops: the measures that decide the verdict

### Chained retrieval hops (decides the verdict)

A chained retrieval hop is a look-up you could not even issue until an earlier
look-up had returned. Count the gaps, not the retrievals: 4 retrievals in one
chain give 3 hops, because the opening look-up waits on nothing.

| Hops | Verdict |
| --- | --- |
| 2 or fewer | Not enough. A parallel look-up plus arithmetic. |
| 3 | Minimum. 4 retrievals in the chain. |
| 4 to 6 | Goal. This is what the client wants. |
| 7+ | Exceptional. |

Chain length counts compute steps too, so an 8-step chain can still have only 2
hops. If every source was knowable when you wrote the prompt, you built a
parallel look-up plus arithmetic, not multi-hop research.

### Chain length in layers (secondary, never decides on its own)

| Layers | Tier |
| --- | --- |
| 1 to 3 | Too short. Not accepted. |
| 4 to 5 | Basic. Fine on its own. |
| 6 to 9 | Healthy. |
| 10+ | Exceptional. |

### How to count

Find the longest chain of stages where each stage needs the previous stage's
result. Count the stages (columns). That is depth. Parallel look-ups inside one
stage are width, not depth. Boxes are not depth: 20 boxes can be depth 11, 7
boxes can be depth 3. Hops are counted down the longest single chain, never
added up across branches.

Depth is your friend. Every extra layer is another node where the model can
slip, and one wrong node poisons the final answer.

---

## 5. The three questions

Every prompt asks exactly 3 interconnected questions that land on the same
shared final answer. Allowed shapes:

- Q1 feeds Q2, Q2 feeds Q3.
- Q1 and Q2 stand independently and both feed Q3.

Never allowed: a question that touches nothing else. That is two tasks
stitched together and is rejected. More questions are not more value; depth is.
Reach depth by chaining hops inside the questions, not by stacking unrelated
ones.

Every numbered question must end in a value the chain computes or retrieves.
A question answered by the absence of data has no chain to review.

---

## 6. Stump requirement

After the prompt is written, Model 1 then Model 2 attempt it in sequence. Each
must independently get at least one final answer wrong. Write a short stump
justification per model: which final answer it got wrong, what it returned, and
why the miss is a genuine stump (an analytical mistake, not formatting or
wording).

---

## 7. The five deliverables per question

The reasoning chain is the backbone. The graph, prompt and rubric are
projections of it.

| Deliverable | Description |
| --- | --- |
| Natural-language prompt | Prose an analyst would recognize, ending in explicit questions, not commands. Names only the publishing authority. |
| Model stump justification | Per model: which final answer was wrong, what it returned, why it counts. |
| Reasoning chain | Numbered walkthrough from first look-up to final answer with every source, value, citation and calculation. |
| Reasoning graph | The chain as nodes and edges, derived from it and verified by you. |
| Rubric | One row per final answer and one per intermediate step: expected answer, type, grader, tolerance, criterion, step graded, weight. Finals and intermediates carry half the marks each. |

Rubric row format (from the worked example):

| Expected | Type | Grader | Tolerance | Criterion | Category | Step | Weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1.81 | Percentage points | Numeric | ±1% relative | The response reports Microsoft's net profit margin change FY2023 to FY2024 (34.15% to 35.96%) as 1.81 pp. | final | Q1 | 16.67 |

Three finals at 16.67 each sum to 50. Intermediates share the other 50.

Time budget: 30 to 40 minutes per question. About 10 minutes for Model 1 and its
write-up, about 15 for Model 2 and its write-up, the rest for planning, chain
and rubric. Most of the time is verification.

---

## 8. How work is reviewed

A reviewer re-derives the answer from scratch, opening each cited source,
before reading your chain. They check accuracy, time-insensitivity, the period
rule, prompt and rubric alignment, and verify the auto-derived reasoning graph.
Score is 1 to 5 (Standard Quality Score) with written feedback. Rejected work
comes back with specific feedback to fix and resubmit.

### What good looks like

- Ends in a value.
- At least 3 chained retrieval hops. 4 to 6 is the goal.
- Chain length 6 to 9 steps.
- 3 interconnected questions converging on one answer.
- Cross-document retrieval.
- Genuinely dependent: past the opening look-ups, every retrieval takes its key from an earlier step.
- Varied across the batch: change companies, periods, facts, operations. Ten questions on Apple's margins count as roughly one.
- Unambiguous: exactly one defensible answer.

---

## 9. Worked examples from the guides

### Excellent: BlackRock proxy chain (5 hops, 26 nodes)

Prompt never names the analyzed company. BlackRock FY2025 proxy names Apple
(first directorship for Susan L. Wagner). Apple FY2025 proxy names NVIDIA
(single company added to peer group). NVIDIA FY2024 proxy names Cisco (fourth
alphabetically in peer group). Cisco FY2023 proxy names Microsoft (11th peer
alphabetically). Then Microsoft FY2023 and FY2024 net income and revenue, a
fiscal-year alignment test picks Super Micro Computer over Alphabet, and the
three answers are 1.81 pp, 1.29 pp and 1.3981.

### Excellent: 1951 call report chain (13 layers, 10 hops)

City National Bank of Colorado City June 30, 1951 Report of Condition selects
the largest US Government obligation category (Treasury bills). That category
keys the October 10, 1951 Member Bank Call Report district table (Kansas City
highest at 18.4540%). That district's Federal Reserve Bank 1951 annual report
names the special-election director (W. S. Kennedy, First National Bank,
Junction City, Kansas). The Comptroller evaluation gives the later title and
charter 3543. The Federal Reserve 2014 holding-company filing (Exchange
Company, Kearney, Nebraska acquiring JCK, Inc.) leads to the FDIC 2014 merger
decision (Exchange Bank, Gibbon, Nebraska: total assets 549,949 thousand,
assets acquired 109,634 thousand). Final: 109,634 / 549,949 × 100 = 19.9353%.

Document decides document, straight down one chain.

### Rejected: Microsoft FY2024 standalone questions (depth 2, 0 hops)

Prompt gives away CIK, accession number, URL, filing date and the databases to
search. Three questions (revenue growth, close on filing date, dividend growth)
never touch each other. Fix shape: make Q3 consume Q1 and Q2 (share price ÷
growth rate). Even fixed, it has 1 hop, so still short of the floor.

### Rejected: wide not deep (7 boxes, depth 3, 1 repeated hop)

Three filing dates, three quarter-end index closes, one comparison. Width is
not depth. Repetition of one memorizable shape is not three ideas.

---

## 10. Golden Example: building a rigorous analytical task

This is the sibling task format (Handshake, Project Mark): a precise decision
over messy, multi-source real files with one deterministic answer.

### Artifacts

| Artifact | File | Role |
| --- | --- | --- |
| Prompt | `prompt.md` | The committed question the analyst must answer plus per-file asks |
| Input files | `inputs.zip` | The raw, load-bearing evidence |
| Golden deliverable | 1 to 3 files, prioritize a visual | Reference answers as matching output files |

Downstream: an internally generated rubric fixed at 25 or more criteria (not
editable), then model validation. The task passes when model responses average
under 50% against the rubric and at least one model is genuinely stumped.

### Sequence

1. Select task type and objective.
2. Assemble the necessary input files.
3. Write one deterministic recommendation request plus per-file asks, each multi-dimensional and hard, no cap on number.
4. Prescribe 1 to 3 deliverables, prioritizing a visual, in formats that fit the decision.
5. Complete the golden deliverables and matching golden output files.
6. Read the generated rubric (25+ criteria). Do not edit it.
7. Run model responses. Confirm average under 50% with at least one model stumped.
8. Clear Readiness and submit on Handshake.

### Standards

| Standard | Meaning |
| --- | --- |
| Deterministic | Competent experts converge on the same recommendation |
| Reproducible | Every number and step comes back from the shipped files |
| Analytically difficult | Difficulty lives in reasoning and method, not ambiguous wording |
| Self-contained | Every load-bearing fact is in the prompt, files, or standard domain knowledge |
| Supported by necessary files | Each shipped file does work, nothing load-bearing is missing |

### The trap to avoid

Do not build "flip the wrong number": a stakeholder cites a number, a planted
defect proves it wrong, the answer flips. Keep reported figures honest and put
the difficulty in confirming a number (the trap is over-correcting it),
forecasting, method selection, a binding constraint, or decomposition.

### Traps that stump the current model (64 accepted tasks, 4 runs each)

Trap families: Controls treated as optional · Wrong unit, population or
segment · Rules read loosely · Evidence taken at face value · Stops before
the last check.

| Trap | Tasks decided | Scored < 0.50 |
| --- | --- | --- |
| Reports a failed back-test, ships anyway | 11 | 9 |
| Counts file rows instead of the real unit | 11 | 7 |
| Stops at a close but inexact match | 8 | 5 |
| Never tests its reading against the control | 7 | 5 |
| Takes the population a flag or filter suggests | 5 | 3 |
| Treats a mixed segment all one way | 5 | 2 |
| Uses the ready-made measure | 5 | 2 |
| Papers over a failed reproduction | 4 | 4 |
| Picks from the offered options when none passes | 4 | 3 |
| Notes a binding limit as a risk | 4 | 3 |
| Beats the headline trap, misses the quiet one | 4 | 2 |
| Stops at the first control that passes | 3 | 2 |
| Validates on one population, applies to another | 3 | 2 |
| Coarsens the segment it was asked about | 3 | 1 |
| Follows the requester's hunch over the rule | 3 | 1 |
| Lets small shortcuts flip a thin margin | 3 | 1 |
| Guesses an attribution the data can settle (emerging) | 2 | 2 |
| Joins only on the visible key (emerging) | 2 | 1 |
| Breaks a big tie instead of questioning it (emerging) | 2 | 1 |
| Leaves the deciding comparison unstated (emerging) | 2 | 1 |
| Adds exclusions the rules do not ask for (emerging) | 2 | 0 |
| Solves a self-referencing rule in one pass (emerging) | 1 | 1 |
| Reads a closure notice as a market exit (emerging) | 1 | 1 |
| Treats an unpublished figure as unknown (emerging) | 1 | 0 |
| Assumes an effect the log could measure (emerging) | 1 | 0 |
| Picks a window across a documented confounder (emerging) | 1 | 0 |

Two rules carry over: the trap must be reconcilable from the supplied files
alone, and the failure must be a genuine analytical mistake, not formatting or
wording. Build the trap into the evidence, not the wording.

### Analytical objectives (104 traps in the library)

| Objective | Description | Traps |
| --- | --- | --- |
| Descriptive & Distribution Analysis | Decision turns on how a population is composed or a metric distributed | 15 |
| Anomaly Detection & Diagnostics | Something looks wrong; separate a real event from an artifact | 18 |
| Root-Cause Analysis | A metric moved; name the driver with rivals ruled out | 16 |
| Experiment & Causal Analysis | Conclusion depends on a causal claim with confounders | 19 |
| Forecasting & Predictive Modeling | Decision depends on a future value the history can pin down | 18 |
| Data Extraction & Conformation (ETL) | Reconcile messy multi-source inputs into one contract-conforming dataset | 18 |
