# MBTA Fall 2026 weekday crowding priority: task design (version 5)

Domain: Transportation & Mobility
Objective: Data Extraction & Conformation (ETL / Pipeline Build)
Prompt shape: Ranked list under a cap (counted trains by certified peak load, the top operated one certified),
carried by a conformation of a ridership count to a later schedule.
Status: built. Every figure reproduces from inputs/ with golden/build_golden.py. The folder keeps its version 1
name (mbta_bus_rating_change) so the branch history stays in one place; version 5 is a Commuter Rail task.

## Version 5 change: ridership data with real measurement mess
Versions 1 to 4 were built on GTFS schedule feeds alone, and the platform's models solved every version at the
headline (scores 39, 51 and expected above 51), because clean schedule data cannot stump them once the counting
convention is stated. Version 5 moves the certified figure onto ridership: the MBTA's published Commuter Rail
count by trip, season, line and stop (Spring 2012, Spring 2018, Fall 2024; 15,761 rows), supplied by the user as
the hub's four export formats because the build container's network policy blocks the MassDOT hub. The bus count
asked for in the brief was not available; the Commuter Rail count is the same publisher's series with the same
mechanics (sampled averages, loads by stop, seasons), and the Fall 2026 GTFS feed carries the Commuter Rail
schedule, so the design transfers. The schedule conformation (count to the Fall 2026 weekday schedule) is the
layer underneath the decision.

## The decision
Certify the Fall 2026 weekday crowding priority: the one counted train, among those the Fall 2026 weekday
schedule operates, with the highest peak load in the latest published count. The added bilevel coach set goes to
the Fall 2026 train that operates it. Finance's draft names train 827 at 896; Planning's names 829 at 1,110; the
Spring 2018 certification (1,384) is the control.

## The forced answer
| Item | Value |
|---|---|
| Certified priority | Providence/Stoughton Line train 829 (Fall 2024 count), outbound from South Station 17:40 |
| Certified peak load | 1,064 riders leaving Ruggles at 17:49 |
| Fall 2026 train operating it | train 867, South Station 17:37 to Wickford Junction 19:29, same 13 stops |
| Finance's 827 at 896 | the counted 827 (16:52, 896 at Ruggles) shares only a number with the Fall 2026 827, a 09:25 off peak train; the counted 827 is operated as 861 at 16:52; 896 is sixth, tied with Needham 606; not certified |
| Planning's 829 at 1,110 | right train, wrong measure: 1,110 is the train's weekday boardings, not its peak load; not certified as stated |
| Runner up | Franklin/Foxboro 723, outbound 16:27, 1,036 leaving Ruggles 16:36, operated as 759 at 16:27 |
| Flip point | a fall of 29 in the certified load (to 1,035) hands the priority to 723; third is Franklin 706 at 979 |
| Counted trains operated / not | 411 / 103 (Middleborough/Lakeville 28, Kingston 21, Greenbush 15, Haverhill 12, Franklin 10, Worcester 9, and 2 each on Fairmount, Lowell, Newburyport, Providence) |
| Fall 2026 trains with no counted train behind them | 137 of 547 (Fall River/New Bedford 57 of 57, Haverhill 23 of 44, Kingston 20 of 25, Greenbush 13 of 24, Lowell 12 of 46, Franklin 6, Fairmount 3, Providence 2, Worcester 1) |
| Certified train stop by stop | 13 stops; 789 of 1,110 boardings at South Station; 1,111 alightings; load ends at minus 1 at Wickford Junction |
| Spring 2018 reproduced | Worcester 508 inbound, 1,384 leaving West Natick; Fall 2026 load is 320 (23 percent) below it |
| Fall 2026 weekday schedule | 547 Commuter Rail trains on 54 of the rating's 55 weekdays; south side (361 trains) on the service the feed labels modified (typicality 4), north side on typical services |

Determinism checks in build_golden.py: the four count formats hold the same rows; every Fall 2024 train is listed
from stop sequence 1; the same winner and runner up under departure windows of 5, 10, 15, 20 and 30 minutes; the
same trip set on 30 September, 21 October and 9 December; the certified train's 13 counted stops equal the Fall
2026 train's stops; 434 of 514 counted trains carry their number in the Fall 2024 feed and 421 leave at the counted
minute (the count's keys were valid when taken); only 132 share a number with a Fall 2026 train on the same line
and direction and only 2 of those keep their departure (numbers were reassigned); every count station name
resolves to a feed station or is documented as gone.

## Where the honest difficulty lives (trap inventory)
1. Train number taken as identity (evidence at face value; close but inexact match). The count keys trains by
   number; the Fall 2026 feed reuses nearly every number for a different train. 829 is not in the Fall 2026 feed
   and 827 is, so a number join certifies 827 at 896 (Finance). The honest key is the slot: line, direction,
   first stop and departure, which the Fall 2024 archived feed shows was valid when the count was taken. Decisive
   at the headline.
2. Measure swap (definition swap, both numbers correct). Peak load is the largest load on leaving a stop (1,064);
   boardings summed over the run are 1,110 (Planning). The data dictionary that defines average_load lives only in
   the shapefile's metadata xml.
3. Over correction of a correct measured number. The certified train's count ends at minus 1 at Wickford Junction,
   a rounding residue of averaged boardings and alightings; 57 of 514 Fall 2024 trains end off zero, one fails the
   cumulative load identity, one has an NA stop sequence, six rows have no stop time. The convention certifies
   counts as published; a model that sets aside the certified train for its residue certifies 723. Decisive.
4. Population a flag suggests. The whole south side weekday schedule in the Fall 2026 feed (361 of 547 trains, the
   certified train among them) runs on a service the feed flags typicality 4, modified service, for the entire
   rating. The convention takes the schedule by date; excluding modified service removes every south side train and
   hands the priority to a north side train. Wholesale failure.
5. Line replaced and station renamed (mislabeling, crosswalk). The Middleborough/Lakeville Line in the count has no
   Fall 2026 service and its terminal is no longer a feed station; the Fall River/New Bedford Line has no count.
   Count spellings differ from the feed (Littleton/Rte 495, Dedham Corp Center, Porter Square), Lynn is a feed
   station the schedule no longer serves, and the 2024 feed carries the old spellings under the same stop ids. Five
   Fitchburg trains originate at Littleton and are operated only after the name is resolved.
6. Clock and timing. The Fall 2024 count stores every stop time on a placeholder date, earlier seasons store after
   midnight stops on the next placeholder day, and the Spring 2018 and 2012 clocks are offset from the schedule.
   The Spring 2018 control is reproduced from the count alone (max load), so the offset is mess, not a trap.
7. Rating label. The Commuter Rail services in the Fall 2026 feed carry a Spring/Summer rating label with no end
   date; the schedule in effect for the Fall 2026 rating is found by date, not by label.
8. Rows versus units. Rows are stops; the unit is the train (line, number, direction); 514 trains in 5,773 rows.

## Deliverables
- crowding_priority_register.csv: 514 rows ranked by peak load (competition ranking), columns rank, line_id,
  line_name, train, direction, first_stop, counted_departure, peak_load, peak_load_stop, peak_load_time,
  weekday_boardings, fall_2026_status, fall_2026_train, fall_2026_departure, departure_difference_minutes.
- top_trains_by_peak_load.png: fifteen ranked bars, operated in blue and not operated in orange, each labelled with
  the load, the stop and the Fall 2026 train and departure; the certified priority labelled.
- crowding_priority_memo.pdf: two pages. Certified priority; the two draft figures; the conformation and coverage
  both ways; runner up and flip; the certified train stop by stop; Spring 2018 reproduced; closing.

## Input package (inputs/, zipped as inputs.zip, 43 MB, 13 files, seven formats)
Four exports of the ridership layer (csv, geojson, kml, shapefile zip with the metadata xml), the Fall 2026 feed,
the Fall 2024 archived feed, the archive index, the two references, the two licences, the convention document and
the provenance note. The June and August 2026 feeds from version 4 were dropped: the Commuter Rail schedule for
the rating lives in the Fall 2026 feed and the zip must stay under 100 MB.
