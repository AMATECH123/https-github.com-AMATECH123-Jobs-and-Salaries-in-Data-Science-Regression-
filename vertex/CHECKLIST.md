# Project Vertex: Pre-submission Checklist

Tick every line before submitting a question. Any unticked line means do not submit.

## Chain shape
- [ ] Longest chain has at least 3 chained retrieval hops (4 retrievals keyed in sequence). Target 4 to 6.
- [ ] Chain length is 6 to 9 steps on the longest path (4 to 5 is acceptable minimum).
- [ ] Hops counted down one chain, not summed across branches. Layers counted, not boxes.
- [ ] Past the opening look-ups, every retrieval takes its key from an earlier step's result.
- [ ] Backbone is cross-document resolution, not filing-date into a market series.
- [ ] Filing-date into index or yield appears at most once, and only as a hop inside a longer chain.

## Questions
- [ ] Exactly 3 numbered questions.
- [ ] Q1 feeds Q2 feeds Q3, or Q1 and Q2 both feed Q3. No question stands alone.
- [ ] All three converge on one shared final answer.
- [ ] Every question ends in a value the chain retrieves or computes. None is answered by absence of data.
- [ ] Exactly one defensible answer per question.

## Prompt
- [ ] Written as prose an analyst would recognize, ending in explicit questions, not commands.
- [ ] Names only the publishing authority. No URL, CIK, accession number, filing date, or search surface.
- [ ] No "current", "latest", "today", "now", or anything that can change.
- [ ] Rounding instructions stated once, applied only at the final answer.
- [ ] Tie-break rules stated wherever a selection could tie.

## Facts
- [ ] Right entity, right period, right line item, right units, right currency recorded for every retrieval.
- [ ] Every value re-opened and re-read from the source a second time.
- [ ] Fiscal period and filing year pinned for every figure (restatement-safe).
- [ ] No BEA data from Q1 2021 onward unless the vintage is pinned.
- [ ] Every citation lists the direct source, accession number or identifier.

## Compute
- [ ] Each compute node does one operation.
- [ ] Full precision carried throughout. Rounding only at the final answer.
- [ ] Arithmetic re-run independently (calculator or script) and matches.

## Stump
- [ ] Model 1 attempted. At least one final answer wrong. Justification written.
- [ ] Model 2 attempted independently. At least one final answer wrong. Justification written.
- [ ] Each miss is a genuine analytical mistake, not formatting or wording.

## Rubric
- [ ] One row per final answer at the top.
- [ ] One row per intermediate retrieval and compute step below.
- [ ] Each row: expected, type, grader, tolerance, criterion, category, step, weight.
- [ ] Finals total 50 marks, intermediates total 50 marks.
- [ ] Accepted variants listed or explicitly "none".

## Batch
- [ ] Companies, periods, facts and operations differ from every other question in the batch.
