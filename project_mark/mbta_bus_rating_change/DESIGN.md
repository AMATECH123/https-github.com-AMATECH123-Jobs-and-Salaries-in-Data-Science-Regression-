# MBTA Fall 2026 weekday bus requirement: task design (version 3)

Domain: Transportation & Mobility
Objective: Data Extraction & Conformation (ETL / Pipeline Build)
Prompt shape: Profile across many periods (hourly buses in service), carried by a conformed trip to block register
Status: built. Every figure reproduces from inputs/ with golden/build_golden.py.

## Version 3 change
Version 2 named the certification day in the prompt ("typical school day weekday"), and both platform rollouts
reached 621. Version 3 moves the convention into a scenario document in the package and changes the
certification day to the weekday schedule in effect for most of the rating. The Summer rating ran a no school
weekday on 34 of its 48 Monday to Thursday dates and a school day weekday on 10, so the Summer certification is
607 buses and 12,721 trips, not 615 and 12,893. Finance's +321 is therefore right and certified; the planners'
+149 is the like for like school day comparison every model reached for in versions 1 and 2, and it is rejected.
The June feed (20260610.zip) was added because the August feed's calendar starts on 12 August and hides how long
the no school schedule ran. Forced answer: 621 buses at 07:51, +14 on 607 at 07:59; +321 trips; Route 65 +45;
Route 465 +32; 59 routes changed; pull outs peak in the 05:00 hour (260 and 266) and grow most in the 14:00 hour
(+34); Route 65 buses 22 to 33; flip point 14.

## Why version 2
Version 1 certified the net trip change (+149) and the driving route. Two platform rollouts and one local dry run
solved it in full: with the counting convention explicit, trip counting on clean GTFS is mechanical. Version 2
keeps that work as supplementary and moves the certified figure to the unit that models get wrong: buses, not
trips. The platform's trap record names "counts file rows instead of the real unit" as the most common decisive
miss, and the real data makes it bite here.

## The decision
Certify the Fall 2026 weekday bus requirement: the most buses in service at one time on a typical school day
weekday, Monday to Thursday, across MBTA bus routes, a bus counted from its first departure to its last arrival
of its block. The Summer rating was certified at 615 (the control). Finance's draft says 521.

## The forced answer
| Item | Value |
|---|---|
| Fall 2026 weekday bus requirement | 621 buses at 07:51 |
| Summer 2026 reproduced | 615 buses at 07:50 |
| Change | +6 |
| Finance's 521 reproduced | most trips underway at once, 17:26 (Summer equivalent 513) |
| Net weekday trip change | +149 (12,893 to 13,042) |
| Driving route | Route 65, 86 to 131, +45; runner up Route 465 +32; flip point 14 |
| Hour with the largest gain | 22:00 hour, +16 (233 to 249) |
| Buses carrying Route 65 trips | 23 Summer, 33 Fall |
| Route 65 span | 05:58 to 21:03 Summer; 05:00 to 25:33 Fall; inbound end Kenmore to Ruggles |
| Hourly profile | 23 hours (04:00 to the 02:00 hour next day), both ratings, in weekday_bus_requirement.csv |

Determinism checks in build_golden.py: peak and time identical in the 20260812 and 20260821 feeds, on 1, 2, 3
September and 8, 23, 30 September; identical whether the last arrival minute is counted in or out; every block
has a block_id (13,042 of 13,042 Fall bus trips).

## Where the honest difficulty lives
1. Trips are rows, buses are the unit. Concurrent trips peak at 521 in the afternoon; concurrent blocks peak at
   621 in the morning. Both numbers are correct measurements; only one is the requirement, and the control 615
   tells the analyst which. Between trips a bus is on layover and still out.
2. Blocks interline. 760 of 1,824 Fall blocks carry more than one route, so per route bus counts are not asked;
   the driving route is defined on trips, and "buses carrying its trips" is a block count.
3. Everything from version 1 still applies underneath: the feed named Fall 2026 starts two weeks before the
   Fall rating; rating labels versus dates; the no school versus school day Summer weekday (Finance's +321);
   timetable listings versus trips (the planners' +121); shuttles stored as bus type routes; typicality flags.
4. Offered options. Finance's 521, 321 and the planners' 121 are all honest computations and none is certified.

## Deliverables
- weekday_bus_requirement.csv: 23 hourly rows plus a DAY PEAK row; columns hour, summer_buses_in_service,
  fall_buses_in_service, change.
- bus_requirement_profile.png: two minute level lines across the service day, peaks marked and labelled.
- fleet_certification_memo.pdf: two pages. Certified figure first; what each other figure counted; how the
  figures were built; hour with the largest gain; ranked route table (28 rows); Route 65 buses, span and
  extension; flip point; closing.

## Input package (inputs/, zipped as inputs.zip, 82 MB) is unchanged from version 1.
