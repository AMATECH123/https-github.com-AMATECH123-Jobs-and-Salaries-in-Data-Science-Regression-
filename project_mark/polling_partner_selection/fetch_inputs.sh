#!/usr/bin/env bash
# Pulls the input package from the FiveThirtyEight data repository (CC BY 4.0). Run from the task folder.
set -euo pipefail
cd "$(dirname "$0")/inputs"
B=https://raw.githubusercontent.com/fivethirtyeight/data/4c1ff5e3aef1816ae04af63218015066e186c147
mkdir -p pollster-ratings/2023 pollster-ratings/2021
for f in raw_polls.csv pollster-ratings-combined.csv README.md README_PRE2024.md 2023/raw-polls.csv 2023/pollster-ratings.csv 2023/pollster-stats-full.xlsx 2021/raw-polls.csv 2021/pollster-ratings.csv 2021/pollster-stats-full.xlsx; do
  curl -fsSL -o "pollster-ratings/$f" "$B/pollster-ratings/$f" && echo "pollster-ratings/$f pulled $(date -u +%Y-%m-%d)"
done
curl -fsSL -o pollster-ratings/LICENSE "$B/LICENSE"
