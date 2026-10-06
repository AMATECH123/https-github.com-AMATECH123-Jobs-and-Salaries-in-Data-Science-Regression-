# MBTA Fall 2026 added weekday round trip: task design (version 6)

Domain: Transportation & Mobility
Objective: Data Extraction & Conformation (ETL / Pipeline Build)
Prompt shape: Before and after with a control (peak share of boardings at two certifications), carried by the
conformation of two count seasons to their own schedules.
Status: built. Every figure reproduces from inputs/ with golden/build_golden.py. The folder keeps its version 1
name (mbta_bus_rating_change) so the branch history stays in one place.

## Why version 6
Version 5 (crowding priority) scored 94 and 94 on the platform: both models executed every stated rule from the
data, including the slot join, once the rule existed in any wording. Five versions showed that a convention
precise enough for ten experts to converge is also precise enough for these models, as long as the deciding
fact is in the convention. Version 6 keeps the convention precise and moves the deciding fact into the data: the
Spring 2018 season of the count carries every stop time five hours ahead of the schedule, while the Fall 2024
season's times are right. Nothing in the convention says so. A reader who uses the count's own clock gets the
opposite placement, and the convention's rule that periods come from the scheduled departure is the only guard.

## The decision
Certify the Fall 2026 weekday peak share of Commuter Rail boardings and its change since the Spring 2018
certification, and place the Fall 2026 added weekday round trip: peak if the share held or rose, off peak if it
fell. Finance places it in the peak on the Fall 2024 share alone (59.9 percent); Planning places it in the peak on
the claim that the share has risen since 2018. Both are rejected.

## The forced answer
| Item | Value |
|---|---|
| Placement | off peak |
| Peak share, Spring 2018 certification | 71.9 percent (91,167 peak of 126,749 placed boardings) |
| Peak share, Fall 2024 count | 59.9 percent (58,456 of 97,537) |
| Change | minus 12.0 points (minus 11.995 before rounding) |
| Finance's 59.9, peak | the Fall 2024 share alone; the convention tests the change; not certified |
| Planning's "share has risen", peak | the Spring 2018 periods read from the count's own stop times, which run five hours ahead of the schedule (501 of 515 matched trains at exactly 300 minutes); read that way the 2018 share is 1.4 percent and the change plus 58.5; not certified |
| Peak boardings | 91,167 to 58,456, 64.1 percent of 2018 |
| Off peak boardings | 35,582 to 39,081, 109.8 percent of 2018 |
| Placed trains | Fall 2024: 514 of 514. Spring 2018: 515 of 516; the one unplaced is Providence 8805 outbound (6 boardings), listed in the feed only under a service that ended 18 May 2018 |
| Join | train number compared by its digits, and direction; the feeds write Old Colony numbers 044, the count 44, and the 2018 feed prefixes four numbers with B (B787, B789, B910, B912); matched as text 80 Fall 2024 trains (15,720 boardings) and 77 Spring 2018 trains fall out |
| Lines | every line fell; Fitchburg fell most (73.2 to 50.9, minus 22.2); Haverhill held best (71.9 to 70.2, minus 1.7) |
| Off peak above 2018 | 8 lines: Fairmount 206 percent, Middleborough/Lakeville 171, Franklin 152, Needham 132, Fitchburg 126, Kingston 125, Worcester 111, Newburyport 105 |
| Fall 2026 weekday supply | 547 trains on 54 of 55 weekdays: 126 peak, 421 off peak |
| Flip point | 11,700 Fall 2024 boardings would have to move from off peak to peak to hold 71.9 percent |

Determinism checks in build_golden.py: the four count formats hold the same rows; the sign and size of the change
hold under four boundary variants (always below minus 10 points); the Spring 2018 share is the same to one decimal
on the 16 May 2018 schedule; the Fall 2024 share is the same on 15 and 17 October 2024; the number and direction
key is unique in both feeds; the counted clock agrees with the schedule on 498 of 514 Fall 2024 trains and sits
300 minutes ahead on 501 of 515 Spring 2018 trains; the count clock reading flips the sign; the text join leaves
80 Fall 2024 trains unplaced; the flip point brackets the 2018 share exactly.

## Where the honest difficulty lives (trap inventory)
1. Clock and timing, decisive. The Spring 2018 count's stop_time field is five hours ahead of the schedule on
   every train and evening trains carry the next day's placeholder date; the Fall 2024 field is right to the
   minute. The convention places trains by scheduled departure from the season's feed. A reader who takes the
   count's ready made time, having checked it against the 2024 feed, gets a 2018 peak share of 1.4 percent, a
   rise of 58.5 points, and the peak placement. Planning's draft is that reading.
2. Close but inexact key. Old Colony train numbers are 044 in the feeds and 44 in the count; a text join drops
   80 Fall 2024 trains (16 percent of boardings) and 77 Spring 2018 trains. The share still falls, so this trap
   moves the supplementary figures (placed counts, line table) rather than the headline.
3. Definition swap. Finance's 59.9 percent is correct and is not the test; the convention tests the change.
4. Rows versus units. Rows are stops; the unit is the train; boardings are summed per train before placement.
5. Unplaced train. One Spring 2018 train (Providence 8805) has no scheduled train of its number on 23 May 2018;
   the convention leaves it out rather than placing it by a clock that is wrong. Four others carry a B prefix in
   the feed and are placed once numbers are compared by their digits.
6. Population by flag and label. The Fall 2026 supply by period comes from the schedule in effect on most rating
   weekdays, which carries a Spring/Summer label and a modified service flag on the south side.
7. Line replaced. Middleborough/Lakeville is in both counts and has no Fall 2026 service; Fall River/New Bedford
   has Fall 2026 service and no count.

## Deliverables
- period_register.csv: 1,030 rows (516 Spring 2018 and 514 Fall 2024 counted trains), columns season, line_id,
  line_name, train, direction, first_stop, counted_time, scheduled_departure, period, weekday_boardings, placed.
- peak_share_by_line.png: a dumbbell chart, one row per line ordered by the change plus a system row, Spring
  2018 and Fall 2024 shares labelled, the change in points at the right, the placement stated in the subtitle.
- service_allocation_memo.pdf: two pages. Placement and shares; the two drafts; the boardings and recovery
  table; how the counts were placed; the line table ranked by change; Fall 2026 supply by period; flip point;
  closing.

## Convention wording after the dry run
Rule 5 now says train numbers are compared by their digits, because the 2018 feed prefixes four numbers with a
letter and an expert would place them. Rule 4 no longer says that the scheduled departure is the one in the
season's feed; rules 5 and 7 already make the counted train the scheduled train of its season, so the guard is
intact without a sentence that points straight at the time source.

## Input package (inputs/, zipped as inputs.zip, 55 MB, 14 files, seven formats)
Four exports of the ridership layer, the Fall 2026 feed, the Fall 2024 and Spring 2018 archived feeds, the archive
index, the two references, the two licences, the convention document and the provenance note.
