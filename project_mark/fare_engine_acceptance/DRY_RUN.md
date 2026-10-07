# Dry run record

## Fare engine acceptance, 2026-10-07
A fresh agent, the prompt only, the package without any dictionary or narration. It unpacked the feed, read
the specification and the MBTA notes, implemented the Fares v2 matching itself (empty field exclusion
semantics, transfer_only, timeframes against the calendar, media restrictions, transfer rules with filter
products and product behaviour, duration limit types, transfer counts, join rules) and searched every
assignment of rules per journey for the minimum total. It found the engine fails acceptance, 17 journeys
mispriced, net +7.15 USD, every error group, the largest error (J28, +7.50) and the ninety minute journey
(J19, 2.40 to 4.10). Its one difference from the golden was J25, cash on the Mattapan trolley: the golden
applied the empty area exclusion across the whole column and found no cash fare; the agent applied it within
the leg's network and found 2.40, which is also what happens on the street. The specification is ambiguous on
that point and the agent's reading is the better one, so the golden is the one to correct, not the agent.

Reading: the conditional rule structure that published benchmarks report as hardest for data agents was solved
in full by this model in one run, with a specification implementation from scratch. Not submitted.
