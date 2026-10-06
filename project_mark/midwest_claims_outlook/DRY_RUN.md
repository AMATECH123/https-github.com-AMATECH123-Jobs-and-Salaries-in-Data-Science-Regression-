# Dry run record

## Midwest claims outlook, 2026-10-06
Golden: nine states on the model path, Iowa, Nebraska and North Dakota held, regional total 539,964. The desk's
regional reading (model beats benchmark pooled) is true and ships three failing states; the methods lead's
20 percent level cut holds two states whose model beats its benchmark.

Local dry run with the strongest model: a fresh agent, the prompt text only, an isolated copy of inputs/, 30 tool
calls over seven minutes. It published nine states and held Iowa, Nebraska and North Dakota, matched every back
test figure to two decimals, rejected the desk's regional reading and the methods lead's level cut with the right
figures, explained the three misses from the base year's spikes (Iowa July 2025, Nebraska May 2025, North Dakota
May and July 2025) that did not recur, and gave the same held state fixes (6.74, 4.36, 25.19). Two readings
differed and were pinned: rounding (half up, now rule 7; regional total 539,964) and the regional series reading
(the standard applied to the summed series, 6.65 against 16.00). It also noted, correctly and unprompted, that
the back test window runs March to September while the outlook runs through December. One tightening was
applied: the prompt no longer gives the desk's ground.

Expected platform behaviour: the headline is reachable by applying the standard's back test state by state.
The decisive traps are shipping all twelve on the regional result and holding by error level; both drafts are
true computations that give the wrong list. The platform's rollouts decide.

### Platform rubric evaluation, 2026-10-06
1. 92%
2. 92%
Average: 92%

Both responses passed criterion 1 (nine published, Iowa, Nebraska and North Dakota held, both drafts rejected),
the regional total (539,964), every back test figure, the year earlier comparison (680,645, minus 140,681,
Illinois minus 50,990) and the improvements needed (4.36 and 25.19 or 25.18). Both failed criteria 16 and 17
(weight 4 each): neither said the desk's draft measured the model against the benchmark on the pooled regional
series; both wrote that the desk skipped the back test. That is the one place the tightening (the desk's ground
removed from the prompt) cost the models, and it is a supplementary item, not the headline. The average sits
far above the 50 percent bar, so the task does not stump either model. Eight headlines across three datasets
have now been reached by both platform models whenever the deciding rule is written in the package.
