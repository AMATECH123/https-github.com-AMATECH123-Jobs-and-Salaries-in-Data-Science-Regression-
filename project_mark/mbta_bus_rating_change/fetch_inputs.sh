#!/usr/bin/env bash
# Pulls the MBTA input package. Run from the task folder. Records the pull date next to each file.
# The ridership layer must be downloaded from the MassDOT open data hub by hand (the hub hosts are not always
# reachable from a build container); keep the hub's file names and all four export formats.
set -euo pipefail
cd "$(dirname "$0")/inputs"
stamp=$(date -u +%Y-%m-%d)
S3=https://mbta-gtfs-s3.s3.amazonaws.com
curl -fsSL -o archived_feeds.txt $S3/archive/archived_feeds.txt && echo "archived_feeds.txt pulled $stamp"
curl -fsSL -o MBTA_GTFS.zip https://cdn.mbta.com/MBTA_GTFS.zip && echo "MBTA_GTFS.zip pulled $stamp"
curl -fsSL -o 20241014.zip $S3/archive/20241014.zip && echo "20241014.zip pulled $stamp"
RAW=https://raw.githubusercontent.com
curl -fsSL -o mbta_gtfs_reference.md $RAW/mbta/gtfs-documentation/master/reference/gtfs.md
curl -fsSL -o massdot_developers_license_agreement.pdf $RAW/mbta/gtfs-documentation/master/developers-license-agreement.pdf
curl -fsSL -o gtfs_schedule_reference.md $RAW/google/transit/master/gtfs/spec/en/reference.md
curl -fsSL -o gtfs_spec_LICENSE.txt $RAW/google/transit/master/LICENSE
echo "Ridership: https://mbta-massdot.opendata.arcgis.com (search: MBTA Commuter Rail Ridership by Trip, Season, Route/Line, and Stop); download CSV, GeoJSON, KML and Shapefile"
