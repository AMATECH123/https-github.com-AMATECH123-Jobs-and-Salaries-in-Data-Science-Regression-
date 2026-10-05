# MBTA Summer 2026 to Fall 2026 bus rating change: task design

Domain: Transportation & Mobility
Objective: Data Extraction & Conformation (ETL / Pipeline Build)
Prompt shape: Bridge between two totals, carried by a conformed route register
Status: built. Every figure below reproduces from inputs/ with golden/build_golden.py.

## The decision
Certify one figure for the net change in scheduled weekday bus trips between the Summer 2026 and Fall 2026
ratings, counted on a typical school day weekday (Monday to Thursday) across MBTA bus routes, and name the
route that drives it. Finance says +321 and Service Planning says +121. Both are honest numbers computed under
their own conventions, and neither is the Board's figure.

## The forced answer
| Item | Value |
|---|---|
| Summer rating weekday bus trips (Wed 2 Sep 2026) | 12,893 |
| Fall rating weekday bus trips (Wed 23 Sep 2026) | 13,042 |
| Certified net change | +149 |
| Driving route | Route 65, 86 to 131, +45 |
| Runner up | Route 465, 0 to 32, +32 (gap 13, flip point 14) |
| Routes with a changed count | 28 of 152 |
| School day supplemental trips | 137 Summer, 138 Fall |
| Route 65 span | Summer 05:58 to 21:03; Fall 05:00 to 25:33; inbound end moved from Kenmore to Ruggles |
| Finance +321 reproduced | first weekday of the feed named Fall 2026 (Mon 24 Aug, 12,721, a no school Summer day) vs 13,042 |
| Planning +121 reproduced | trips counted on every route they are listed under: 13,128 to 13,249 |

Determinism checks in build_golden.py: the Summer register is identical on 1, 2, and 3 September and identical
in the 20260812 and 20260821 feeds; the Fall register is identical on 8, 9, 10, 23, and 30 September.

## Where the honest difficulty lives
All of it is how the MBTA really publishes its data. Nothing is planted.
1. Rating versus feed. The feed named Fall 2026 starts 21 August but the Fall rating starts 6 September; its first
   two weeks are still Summer service. The current feed has already dropped the Summer rating entirely.
2. Rating label versus date. Long running services labelled Spring/Summer keep operating under the Fall rating.
   Counting by label misses them; counting by date catches them. Summing every weekday service in a rating
   (Monday to Thursday, Weekday, Friday variants) double counts to 45,221 against 37,275.
3. School day versus no school day. The Summer rating runs a no school weekday until 28 August (12,721) and a
   school day weekday from 31 August (12,893). Only the second matches the Board's convention.
4. Typicality. Holiday (7 Sep), modified, and reduced weekday services carry typicality 3, 4, or 5 and are not a
   typical weekday. Fridays differ from Monday to Thursday.
5. Population. 216 rail replacement shuttle routes and 3,939 shuttle trips sit in the feed as bus type routes.
   The five bus categories in route_desc define the population. On 24 August the wide count is 13,806.
6. Rows versus the real unit. stop_times has 5.2 million rows; the unit is the trip, counted once under its own
   route. multi_route_trips lists trips under extra routes for timetable display, which is Planning's +121.
7. Offered options. Neither office's number is right, so picking one of the two offered figures fails.

## Deliverables
- route_service_change.csv: 152 route rows plus a TOTAL row; rows tie exactly to the totals.
- service_change_bridge.png: waterfall, 28 route bars ordered by absolute change, driver highlighted.
- certification_memo.pdf: two pages, recommendation first, rejects both figures with their reproductions,
  ranked table, supplemental counts, Route 65 span and extension, flip point, closing.

## Input package (inputs/, zipped as inputs.zip, 82 MB)
Three MBTA GTFS feeds (32 tables each), the archive index, the MBTA GTFS reference, the GTFS specification and
its licence, the MassDOT developer licence, and a provenance note. Formats: txt, csv, md, pdf, zip. Largest table
stop_times.txt at 5.2 million rows. See MANIFEST.csv and inputs/README_provenance.md.
