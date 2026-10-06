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
71.9 to 59.9 percent, minus 12.0 points. The count's clock gives 1.4 percent for 2018 and the peak placement.
Determinism: the sign holds under every boundary variant, both 2018 schedules and three 2024 dates.

Local dry run with the strongest model: a fresh agent, the prompt text only, an isolated copy of inputs/, 33
tool calls over nine minutes. It placed the round trip in the off peak at 59.9 against 71.9 percent, minus 12.0
points, found the five hour offset by comparing the 2018 count against the 2018 feed, rejected Finance's reading
as the single season share and Planning's as the count clock reading, and matched the golden on the recovery
figures, the line ranking, the eight lines above their 2018 off peak level, the Fall 2026 supply (126 peak, 421
off peak) and the flip point (11,700). It also found something the golden had missed: the 2018 feed prefixes four
train numbers with a letter (B787, B789, B910, B912), which an expert comparing digits places. The golden now
places them (515 of 516 Spring 2018 trains, one unplaced), the 2018 share moved from 72.0 to 71.9 and the flip
from 11,753 to 11,700, and rule 5 now says numbers are compared by their digits.

Tightening, as the brief requires when the agent reproduces the headline: rule 4 no longer tells the reader that
the scheduled departure is the one in the season's feed. Rules 5 and 7 still make the counted train the
scheduled train of its season, so experts converge; a reader who takes the count's own time field, which agrees
with the schedule to the minute in Fall 2024, is no longer warned off it by the period rule.

Expected platform behaviour: the headline is reachable by a model that joins both counts to their feeds and
takes the departure from the feed. A model that takes the count's ready made time after checking it on the
2024 season certifies the peak with a rise of 58.5 points, which Planning's draft invites it to confirm. The
decisive fact is in the data, not in any rule.
