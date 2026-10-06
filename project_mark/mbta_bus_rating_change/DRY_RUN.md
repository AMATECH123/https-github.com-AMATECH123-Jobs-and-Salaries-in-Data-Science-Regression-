# Dry run record

## Version 1 (trip count certification), 2026-10-05
Local dry run with the strongest model available here, then two platform rollouts: all three reproduced the
golden set in full (+149, Route 65, both office figures explained). The platform's stumped check failed.
Reading: with the counting convention explicit, trip counting on clean GTFS is mechanical.

## Version 2 (fleet certification: buses in service, not trips), 2026-10-05
Local dry run with the same strongest model, 39 tool calls over 13 minutes, no access to the golden files.
It certified 621, reproduced 615, placed the peak at 07:51, explained Finance's 521 as concurrent trips, and
got +149 and Route 65. So the top model still clears the headline when the convention names the unit.
It also exposed a determinism flaw: the hourly "most buses in service" profile differs in 17 of 23 hours
depending on whether the last arrival minute counts as in service, while the daily peak does not. The register
was changed to pull outs and pull ins per hour, which is exact under any convention, and the memo ask changed
with it. The chart still shows the minute level in service profile, and its only labelled values are the peaks.

## Version 3 (certification day is the schedule the rating mostly ran), 2026-10-05
Local dry run with the strongest model: it read the convention document, found that the no school weekday ran
most of the Summer rating, reproduced 607 from the August feed, certified 621 (+14), certified Finance's +321
and rejected the planners' +149 and Finance's 521, and matched the golden on every supplementary ask. Platform
result: 51 percent, above the bar.

## Version 4 (peak allocation by route), 2026-10-05
Local dry run with the strongest model: solved in full, including the attribution (Route 111 at 18, 118 buses
between trips, allocation summing to 607 and 621). Conclusion recorded for the next version: clean schedule
data cannot stump these models once the counting convention is stated, and a convention has to be stated for
determinism. The fix is data with real measurement mess, which means ridership.

## Version 5 (crowding priority from the Commuter Rail ridership count), 2026-10-06
The MassDOT hub, the FTA site and www.mbta.com stayed blocked by the network policy, so the user supplied the
MBTA Commuter Rail ridership count in the hub's four export formats; the Fall 2024 archived feed came from the
S3 archive, which is open. The task was rebuilt on that count (see DESIGN.md).

Local dry run with the strongest model: a fresh general purpose agent, the prompt text only, an isolated copy
of inputs/, no access to golden/ or the design notes; 36 tool calls over about ten minutes. It reproduced the
golden headline in full: Providence 829 outbound 17:40, 1,064 leaving Ruggles 17:49, operated by Fall 2026 train
867 at 17:37. It rejected Finance's 827 (number only, the Fall 2026 827 is a 09:25 train; the counted 827 is
operated as 861), rejected the then offered Planning figure, found the runner up (723 at 1,036, operated as
759), the flip (29), South Station as the boarding stop (789 of 1,110), and the Spring 2018 control (508 at
1,384). It read the schedule by date (547 trains on 54 of 55 weekdays, south side on the modified service),
resolved the station spellings, and certified the count as published despite the minus 1 residue, because the
first wording of convention rule 2 told it to.

Two things came out of the run.
1. A determinism flaw. Rule 5 said the operating train is "scheduled to leave the counted train's first stop";
   the agent read that as calling at the stop, matched twelve counted Bradford trains to Haverhill trains that
   pass through Bradford, and reported 424 operated and 126 uncovered where the golden has 411 and 139. The
   headline and the top fifteen were unaffected. Rule 5 now says the operating train's own first stop must be
   the counted train's first stop.
2. The stump was tightened once, as the brief requires when the agent reproduces the headline. The prompt had
   offered Planning's figure as "train 829 at 1,110" (boardings instead of load), which named the certified
   train. Planning's figure is now "Franklin train 723 at 1,036": the runner up's correct peak load, which is
   the answer a model reaches when it validates the count and sets aside train 829 for its minus 1 terminal
   residue. Rule 2 of the convention no longer lists the residues it tolerates; it says only that counts are
   certified as published and none is rescaled or adjusted. Both offered figures (827 at 896, 723 at 1,036) are
   now honest computations that fail one fixed point each, and the certified figure is named nowhere in the
   prompt. The golden memo explains what each office measured. The conformation itself (numbers reassigned, the
   slot key, the modified service flag, the retired line and the renamed stations) stands as the layer under
   the headline, and the register, coverage and flip asks carry the supplementary weight.

Expected platform behaviour: the platform's models scored 39 and 51 on the schedule only versions. Version 5
asks them to join a count keyed by train number to a schedule that reused the numbers, to keep a measured count
that fails a reconciliation check, to keep a schedule flagged as modified service, and to pick neither offered
figure. The top model clears it with the convention in hand; the platform's rollouts decide the score.

### Platform result and second tightening, 2026-10-06
The platform's stumped check came back failed: both models certified 829 at 1,064 operated by 867. The
convention was doing the models' work for them. Rule 5 had said "train numbers are reassigned between
schedules, so a counted train is not identified in the rating's schedule by its number" and rule 7 had said
the schedule is "taken by date from the feed". Those two sentences named traps 1 and 4 outright. They are
removed. Rule 5 now defines operation as the schedule still running that train (same line, direction, first
stop, departure within ten minutes) without a word about numbers; rule 7 names only the dates. The data still
settles the question for an expert: the Fall 2024 feed shows 434 of 514 counted numbers valid at the counted
minute in 2024, the Fall 2026 feed shows those numbers on other trains (827 at 09:25, 829 absent), and a number
join under the ten minute clause leaves two Fitchburg trains at 162 and 72 riders, which no expert would certify
as the system's crowding priority. The golden set is unchanged. A second isolated dry run with the strongest
model was launched on the revised wording to confirm that the slot reading still converges; its result is
recorded below.

Second dry run (revised wording), 2026-10-06: a fresh agent, prompt only, isolated inputs, 40 tool calls over
eleven minutes. It certified 829 at 1,064 operated by 867 at 17:37, with train numbers playing no part in the
matching ("only 2 of 411 matches happen to share the counted number"), rejected 827 as a number match and 723
as the runner up, and matched the golden on operated and not operated counts by line (411 and 103), the flip
(29), the stop profile (South Station 789; 1,110 and 1,111) and the control (508 at 1,384). So the softened
rule 5 still converges for a careful reader working from the data, which is the determinism the handbook
asks for; whether the platform's models discover the number reuse unaided is what the next rollout tests.
One supplementary figure was improved by the run: it counted the Fall 2026 trains that operate no counted
train (139 of 547, with three Fall 2026 trains each operating two counted trains) where the golden had
counted trains with no counted departure within ten minutes (137). The one to one reading follows rule 5,
and the golden now uses it.
