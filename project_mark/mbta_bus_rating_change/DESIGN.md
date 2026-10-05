# MBTA Fall 2025 bus rating change: task design

Domain: Transportation & Mobility
Objective: Data Extraction & Conformation (ETL / Pipeline Build)
Prompt shape: Bridge between two totals, carried by a conformed route register
Status: design only. Every figure below is to be confirmed against the shipped files before the prompt is final.

## The decision
MBTA Service Planning must certify one figure for the net change in scheduled weekday bus trips between the
Summer 2025 rating and the Fall 2025 rating, and name the single route that drove the largest share of it.
Two offices quote different totals. The analyst adopts one and shows the bridge that gets there.

## Why it is deterministic
GTFS is a complete schedule. Once the population, the unit, and the representative weekday are conformed to the
MBTA's own written definitions, which ship in the package, every analyst lands on the same trip counts per route,
the same net change, and the same driving route. There is no estimation anywhere in the chain.

## Where the honest difficulty lives
All of these come from how the MBTA really publishes its data. Nothing is planted.
1. Rows versus the real unit. stop_times rows are stop events. Trips are the unit. A trip listed under a second
   route in multi_route_trips.txt is one trip at the system level but appears on two route schedules. A route
   level sum does not equal the system total, and the bridge only closes when the analyst reconciles the two.
2. Two ratings inside one feed. An MBTA feed can carry service_ids from more than one rating. calendar_attributes
   gives each service its rating_start_date, rating_end_date, and rating_description. Counting every weekday
   service in the feed double counts. The feed version is not the rating.
3. The representative weekday. calendar_attributes.service_schedule_typicality defines typical service. A
   holiday, a no school day, or a storm schedule is a weekday in calendar.txt but not a typical weekday.
4. The population. route_type 3 includes rail replacement shuttles and supplemental routes. routes.txt route_desc
   and listed_route, together with trips.trip_route_type, define what counts as an MBTA bus route. Both the
   narrow and the wide count are correct numbers; only one is the bus service figure the Board asked for.
5. The close but inexact join. The ridership dataset keys routes by public route number. GTFS keys by route_id.
   Silver Line and a few others differ. The join needs route_short_name, not route_id.
6. A thin margin. The driving route is to be chosen so that one shortcut above flips it.

## Deliverables (three files, one visual)
- route_service_change.csv: one row per bus route with summer weekday trips, fall weekday trips, change,
  percent change, and average weekday boardings from the latest ridership season, plus one control row carrying
  the system totals that the memo certifies.
- service_change_bridge.png: a waterfall from the Summer 2025 weekday total to the Fall 2025 weekday total,
  one bar per route whose schedule changed, ordered largest to smallest by absolute change, net change labelled,
  the driving route highlighted.
- certification_memo.pdf: opens with the certified net change and the driving route, names the total it rejects
  and why, then the ranked table of changed routes with riders affected, and the figure that would result if the
  rejected population were adopted so the Board sees the gap.

## Asks (multi dimensional, no laundry list)
- Every bus route's weekday trips under both ratings and the change, as the register.
- The ten largest reductions ranked, each with average weekday boardings per trip removed.
- The net change under the alternative population the other office used, stated once, so the Board sees why it
  is rejected.
- The nearest change in a single route's trip count at which a different route would become the driver.

## Input package plan (target 10+ files, 3+ formats, one table over 10,000 rows)
See MANIFEST.csv. The two archived GTFS feeds each hold roughly 30 text tables; stop_times alone exceeds one
million rows. The ridership extract, the GTFS reference, the developer licence, the archived feed index, and the
Service Delivery Policy complete the package. Every file does work; nothing decorative is counted.

## Validation plan before submission
1. Rebuild every number in the golden set from the shipped files with build_register.py and diff against the CSV.
2. Confirm the margin between the driving route and the runner up is thin enough that each shortcut flips it.
3. Dry run the prompt against a model here and score it against the rubric shape. Target well under 50 percent.
