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

## Fare engine acceptance, revised under the 9 October rules, 2026-10-09
Second dry run, a fresh agent, the natural prompt (no checklist, no named rules), two long PDFs instead of
markdown, the vendor results sheet named in the prompt as the thing not to trust, and the standard left for
the model to find. The agent read the schedule reference PDF and the MBTA reference PDF, rebuilt the Fares v2
matching from the specification, verified every trip against the calendar for 15 October 2026, and priced all
38 journeys. It matched the golden on 37 of 38 journeys, found the same verdict (fails acceptance), the same
largest error (J28, 4.75 certified against 12.25), the same over and under totals (17.05 and 9.90), and the
same defect groups. The one difference is again J25, cash on the Mattapan trolley: the corrected golden now
gives 2.40 and the agent gave no fare on cash, applying the empty area exclusion across the whole column. The
GTFS text supports either reading, so J25 cannot be used to separate a right answer from a wrong one. It also
flagged, unasked, that the Blue Line platforms carry no smartcard rule under the literal reading.

Estimated rubric score: 90 or above. Taking the checklist out of the prompt did not stop it: the model
derived the checklist from the standard and the specification on its own. The labelled distractor did not
mislead it: it priced the journeys independently and used the vendor sheet only for the comparison.

Reading: three forms of this task (checklist prompt, markdown references; natural prompt, PDF references,
distractor) were all solved in one run each. Conditional rule engines over a real feed are not a stump for
this model. Not submitted. The remaining levers are ones the program's rules do not favour: material the
model has no way to verify, or a correct answer the package cannot support, both of which are unfair traps.
