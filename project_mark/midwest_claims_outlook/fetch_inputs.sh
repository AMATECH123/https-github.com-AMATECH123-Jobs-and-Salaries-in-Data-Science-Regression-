#!/usr/bin/env bash
# Pulls the input package from the Opportunity Insights Economic Tracker repository. Run from the task folder.
set -euo pipefail
cd "$(dirname "$0")/inputs"
B=https://raw.githubusercontent.com/OpportunityInsights/EconomicTracker/b8adef9d292873d7e45b07adc188f1785a035279
mkdir -p data docs
for f in "UI Claims - State - Weekly.csv" "UI Claims - National - Weekly.csv" "UI Claims - County - Weekly.csv" "GeoIDs - State.csv" "GeoIDs - County.csv" "Employment - State - Weekly.csv" "Job Postings - State - Weekly.csv"; do
  curl -fsSL -o "data/$f" "$B/data/${f// /%20}" && echo "data/$f pulled $(date -u +%Y-%m-%d)"
done
for f in oi_tracker_data_dictionary.md oi_tracker_data_dictionary.pdf oi_tracker_data_documentation.md oi_tracker_data_documentation.pdf oi_tracker_data_revisions.md oi_tracker_data_revisions.pdf; do
  curl -fsSL -o "docs/$f" "$B/docs/$f"
done
curl -fsSL -o README.md "$B/README.md"
