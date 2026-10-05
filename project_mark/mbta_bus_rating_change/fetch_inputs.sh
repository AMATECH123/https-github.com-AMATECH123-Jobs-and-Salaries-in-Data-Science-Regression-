#!/usr/bin/env bash
# Pulls the MBTA input package. Run from the task folder once cdn.mbta.com and the ArcGIS hub are reachable.
# Records the pull date next to each file so the manifest can be completed.
set -euo pipefail
cd "$(dirname "$0")/inputs"
stamp=$(date -u +%Y-%m-%d)

curl -fsSL -o archived_feeds.txt https://cdn.mbta.com/archive/archived_feeds.txt
echo "archived_feeds.txt pulled $stamp"

pick() { # $1 = rating name, $2 = output file
  url=$(python3 - "$1" <<'PY'
import csv,sys
name=sys.argv[1]
rows=[r for r in csv.DictReader(open('archived_feeds.txt')) if name.lower() in r['feed_version'].lower()]
rows.sort(key=lambda r:r['feed_start_date'])
print(rows[-1]['archive_url'] if rows else '')
PY
)
  if [ -z "$url" ]; then echo "no archived feed matched '$1'"; exit 1; fi
  curl -fsSL -o "$2" "$url"
  echo "$2 <- $url pulled $stamp"
}
pick "Summer 2025" MBTA_GTFS_summer_2025.zip
pick "Fall 2025"   MBTA_GTFS_fall_2025.zip

# Ridership: open the hub item below, choose Download, CSV, and save as mbta_bus_ridership_by_route_stop.csv
echo "Ridership: https://mbta-massdot.opendata.arcgis.com (search: MBTA Bus Ridership by Time Period, Season, Route/Line, and Stop)"
# Service Delivery Policy: https://www.mbta.com/policies/service-delivery-policy (save the PDF as mbta_service_delivery_policy.pdf)
# NTD monthly: https://www.transit.dot.gov/ntd/data-product/monthly-module-raw-data-release (save as ntd_monthly_ridership.xlsx)
