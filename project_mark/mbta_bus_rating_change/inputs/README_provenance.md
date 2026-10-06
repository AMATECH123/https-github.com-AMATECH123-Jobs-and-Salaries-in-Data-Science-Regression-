# Workspace contents and provenance

This note was written by the task author to record where each file came from. Every data file is exactly as its
publisher served it on the pull date. The one document written for this task, the Board certification convention,
says so in its first lines.

| File | What it is | Publisher | Source | Pulled | Licence |
|---|---|---|---|---|---|
| MBTA_Commuter_Rail_Ridership_by_Trip2C_Season2C_Route_Line2C_and_Stop..csv | MBTA Commuter Rail Ridership by Trip, Season, Route/Line, and Stop: average weekday boardings, alightings and load at every stop of every counted train, Spring 2012, Spring 2018 and Fall 2024 seasons, 15,761 rows. CSV export of the hub layer. | MassDOT / MBTA Office of Performance Management and Innovation | MassDOT GIS open data hub, item "MBTA Commuter Rail Ridership by Trip, Season, Route/Line, and Stop" (feature service Commuter_Rail_Ridership_by_Trip on services1.arcgis.com, hub pubdate 7 April 2025) | 2025-08-01 (hub export), supplied to the workspace 2026-10-06 | CC0 (stated in the layer metadata) |
| MBTA_Commuter_Rail_Ridership_by_Trip2C_Season2C_Route_Line2C_and_Stop..geojson | The same layer, GeoJSON export (geometry is null on every feature). | as above | as above | as above | CC0 |
| MBTA_Commuter_Rail_Ridership_by_Trip2C_Season2C_Route_Line2C_and_Stop..kml | The same layer, KML export. | as above | as above | as above | CC0 |
| MBTA_Commuter_Rail_Ridership_by_Trip2C_Season2C_Route_Line2C_and_Stop..zip | The same layer, shapefile export: .dbf table (field names truncated to ten characters), .shp, .shx, .prj, .cpg and the FGDC metadata .xml that carries the layer's data dictionary and licence statement. | as above | as above | as above | CC0 |
| MBTA_GTFS.zip | MBTA GTFS schedule feed as currently published (feed version "Fall 2026, 2026-10-02T16:00:50+00:00, version D", valid 25 September to 12 December 2026). 32 text tables. | MBTA | https://cdn.mbta.com/MBTA_GTFS.zip | 2026-10-05 | MassDOT Developers License Agreement |
| 20241014.zip | MBTA GTFS schedule feed, archived version valid 14 to 17 October 2024 (feed version "Fall 2024, 2024-10-21T17:30:53+00:00, version D"). 31 text tables. | MBTA | MBTA GTFS archive, listed in archived_feeds.txt (https://cdn.mbtace.com/archive/20241014.zip, served from mbta-gtfs-s3.s3.amazonaws.com/archive/20241014.zip) | 2026-10-06 | MassDOT Developers License Agreement |
| archived_feeds.txt | Index of every archived MBTA feed with the dates each one should be used for. | MBTA | https://cdn.mbta.com/archive/archived_feeds.txt | 2026-10-05 | MassDOT Developers License Agreement |
| mbta_gtfs_reference.md | The MBTA's documentation of its GTFS implementation, including its non-standard files and fields. | MBTA | https://github.com/mbta/gtfs-documentation (reference/gtfs.md) | 2026-10-05 | Published by the MBTA for developers |
| gtfs_schedule_reference.md | The General Transit Feed Specification, schedule reference. | MobilityData / GTFS community | https://github.com/google/transit (gtfs/spec/en/reference.md) | 2026-10-05 | Apache License 2.0 (gtfs_spec_LICENSE.txt) |
| gtfs_spec_LICENSE.txt | Licence text for the GTFS specification. | MobilityData / GTFS community | https://github.com/google/transit (LICENSE) | 2026-10-05 | Apache License 2.0 |
| massdot_developers_license_agreement.pdf | The licence that governs use of MBTA and MassDOT data. | MassDOT | https://github.com/mbta/gtfs-documentation (developers-license-agreement.pdf) | 2026-10-05 | Licence text itself |
| board_crowding_priority_convention.md | Scenario document written by the task author stating the Board's certification convention. Not an MBTA publication. | task author | written for this task | 2026-10-06 | n/a |

The four ridership files are the hub's four export formats of one layer, downloaded from the hub item on the same
day and supplied to the workspace unchanged, file names included. Their row sets are identical.

Attribution: schedule and ridership data provided by the Massachusetts Department of Transportation and the
Massachusetts Bay Transportation Authority. MassDOT and the MBTA are not responsible for any use of the data in
this workspace and shall not be held liable for any errors in it.
