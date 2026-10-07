# Design note: fare engine acceptance

Domain: Transportation and Mobility. Objective: Data Extraction and Conformation (ETL / pipeline build). Shape:
rule replayed on history (shape 08) over a conditional rule system with wildcards, precedence, time windows
and media restrictions, the structure on which published data agent benchmarks report their lowest scores
(DABstep hard tasks: multi step conditional rules read from documentation).

## The task
A vendor's fare engine is up for acceptance against a 38 journey test plan on scheduled trips of 15 October
2026, each paid with one medium. The workspace holds the MBTA GTFS feed (609 fare leg rules, 72 transfer rules,
119 product rows, 45 areas over 1,228 stops, join rules, a timeframe), the GTFS Schedule reference, the MBTA's
notes on its extension fields, the test plan, the vendor's results and a four rule acceptance standard. No data
dictionary, no overview, no narration of the trap.

## The forced answer
The engine fails acceptance: 18 of 38 journeys mispriced; net +7.15 USD over the plan (+17.05 overcharged,
minus 9.90 undercharged); eight journeys have no fare on their medium and the engine priced them anyway; the
largest error is J28 (Beverly to Newburyport, certified 4.75 interzone, vendor 12.25); the one journey whose fare
changes under a ninety minute window is J19 (2.40 to 4.10, second leg 115 minutes after the first departure).

## Why it should be hard
1. Empty field semantics in fare_leg_rules: an empty area or network means every value not listed anywhere
   in that column, not a wildcard. Stops sit in up to two areas. Exact matches take precedence.
2. transfer_only rules: the cash rule for rapid transit may only match as the second leg of a transfer, so cash
   has no fare at a fare gate (J06, J08, J10, J25) but does on a surface Green Line stop (J07).
3. Media: a product exists per medium; mTicket has no bus or subway product (J04, J37), CharlieCard and
   contactless have no commuter rail product (J31, J32), a CharlieTicket on a bus is the 2.40 quick ticket (J03).
4. Transfer rules: the two hour window runs departure to departure (type 1), transfer_count 1 on bus to bus,
   filter products and product behaviour decide which transfers exist (cash and quick ticket have none from a
   bus), and chained transfers change the product carried (J13, J16, J38, J11, J15).
5. Free fares: SL1 from the airport terminals is a free product and transfers free to the Red Line (J20, J21).
6. Commuter rail: a 154 rule zone matrix with interzone products (J27, J28), special areas at South Station,
   Porter and the Fairmount Line, and a join rule for commuter rail legs at one station.
Every one of these is documented in the specification or the MBTA notes in the workspace; none is named in the
prompt or the standard.

## Determinism
The engine in golden/fare_engine.py follows the specification text step by step. The standard fixes the two
places the specification leaves open: the journey fare is the lowest total the rules allow on the medium, and a
leg with no product on the medium makes the journey one with no fare on that medium. Window edge cases sit at
115 minutes (inside) and 158 minutes (outside).
