# Dry run record

## Versions 1 to 4 (schedule only), 2026-10-05
Built on GTFS feeds alone. Local dry runs with the strongest model solved every version in full. Platform scores:
version 2, 39 percent with the headline reached; version 3, 51; version 4 not scored. Conclusion: clean schedule
data cannot stump these models once the counting convention is stated, and a convention has to be stated for
determinism. The fix is data with real measurement mess, which means ridership.

## Version 5 (crowding priority from the Commuter Rail ridership count), 2026-10-06
Built on the MBTA Commuter Rail count (supplied by the user as the hub's four export formats; the hub hosts
stayed blocked) and the Fall 2024 archived feed. Two local dry runs reproduced the headline (train 829 at 1,064
operated by Fall 2026 train 867). The convention was softened once so that it no longer named the number reuse
or the by date rule. Platform result: both models 94 percent; stumped check failed. Every stated rule, in any
wording, was executed from the data. Recorded in the git history.

## Version 6 (peak share and the placement of the added round trip), 2026-10-06
The deciding fact moved out of the convention and into the data: the Spring 2018 count's stop times run five
hours ahead of the schedule (497 of 511 matched trains at exactly 300 minutes), the Fall 2024 times are right, and
the convention says only that periods come from the scheduled departure in the season's feed. Golden: off peak;
72.0 to 59.9 percent, minus 12.0 points. The count's clock gives 1.4 percent for 2018 and the peak placement.
Determinism: the sign holds under every boundary variant, both 2018 schedules and three 2024 dates.

Local dry run: recorded below when the isolated agent reports.
