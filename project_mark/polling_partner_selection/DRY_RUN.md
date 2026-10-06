# Dry run record

## Polling partner selection, 2026-10-06
Golden: Beacon Research/Shaw & Co. Research at 4.13 points; Harris (3.05) fails recency, InsiderAdvantage (3.75)
fails the 2022 test, NYT/Siena is the published number one and fourth under the standard; the previous selection
(Emerson 4.62) reproduces from the 2021 vintage only when the test is applied.

Local dry run with the strongest model: a fresh agent, the prompt text only, an isolated copy of inputs/, 34 tool
calls over ten minutes. It selected Beacon Research/Shaw & Co. Research at 4.13 (2022: 2.77 over 10, median
4.02), rejected Harris for its single 2022 poll and NYT/Siena as the published number one that ranks fourth on
the standard's measure, matched the funnel (356, 280, 182, 13, 8, 5), the runner up (Marist 4.29), the partner's
record by cycle and type, the previous selection (Emerson 4.62 on the 2021 vintage, with Siena/NYT Upshot at 4.11
failing the 2020 test) and the vintage comparison (Harris 3.04 on the current vintage, Emerson third at 5.03). So
the task is deterministic for a careful reader. Three readings differed from the golden on supplementary items and
were pinned: the chart population (25 by volume alone against 13 in order), bias and winner calls at the poll
level against the question level, and the flip stated as 0.17 (hand over) against 0.16 (tie). One tightening was
applied: the prompt no longer says the standards editor's choice is the top of the published ratings.

Expected platform behaviour: the headline is reachable by applying every stated test in order. The decisive
traps are the ones the handbook records as most common: shipping the raw leader (Harris) without the test cycle
count, shipping InsiderAdvantage after it fails the test, taking the published rating (NYT/Siena) as the measure,
or working from the older vintage with its precomputed error column (Emerson). The platform's rollouts decide.

### Platform stumped check, 2026-10-06
Failed. Both models certified Beacon Research/Shaw & Co. Research at 4.13 points. The eligibility tests and the
test cycle are stated in the standard, and both models applied them in order, as the dry run agent did. Seven
headlines across two datasets have now been reached by both platform models whenever the deciding rule is
written down, and the handbook's determinism bar requires it to be written down.
