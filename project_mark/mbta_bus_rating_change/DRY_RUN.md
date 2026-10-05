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

Expected platform behaviour: version 1 showed that the platform models solve explicit trip counting. Version 2
requires them to recognise that a trip is not a bus, to assemble trips into blocks across five million stop
rows, and to test their method against the 615 control. The platform's own trap record puts "counts file rows
instead of the real unit" and "never tests its reading against the control" among the most common decisive
misses, so this is the honest place to put the difficulty. If the rollouts still clear 50 percent, the next
step is to drop the phrase that names the unit ("from the start of its first trip to the end of its last trip
of its day's work") and let the 615 control alone pin the method, after confirming that the gap splitting
variant (620) cannot also reproduce 615.
