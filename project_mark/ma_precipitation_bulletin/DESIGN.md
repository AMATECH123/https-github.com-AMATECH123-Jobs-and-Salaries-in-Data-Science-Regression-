# Massachusetts 2025 annual precipitation bulletin: task design

Domain: Survey Research & Official Statistics
Objective: Data Extraction & Conformation (ETL / Pipeline Build)
Prompt shape: Grid of cells (428 stations qualified under a written standard) resolving to one statistic
Status: built; every figure reproduces from inputs/ with golden/build_golden.py.

## The decision
Certify the statewide 2025 annual precipitation figure for the bulletin and the number of stations it rests on,
under the compilation standard in inputs/bulletin_compilation_standard.md, from NOAA GHCN Daily as published.

## Forced answer
| Item | Value |
|---|---|
| Statewide figure | 1,141.1 mm, mean of 97 qualifying stations (exact 1,141.127) |
| Draft table figure reproduced | 864.2 mm across 428 stations: plain daily sums, no completeness test, multi day totals ignored |
| Reviewer figure reproduced | 1,138.7 mm across 59 stations: only stations with a daily row on all 365 days; Blue Hill counted twice |
| Wettest, driest | Conway 3.4 WSW (US1MAFR0041) 1,440.8 mm; Groveland 0.5 WSW (US1MAES0004) 911.1 mm |
| Boston Logan | 943.6 mm; 64th wettest of 89 complete years, 2003 left out (2 days not measured) |
| Largest leave one out move | Conway 3.4 WSW, statewide falls to 1,138.0 mm, a move of minus 3.1 mm |
| Sensitivity | Blue Hill unmerged gives 98 stations and 1,141.8 mm; counting multi day periods as unmeasured gives 59 and 1,138.7; accepting flagged or cross year accumulations gives 101 |

## Where the honest difficulty lives
All of it is how NOAA publishes the archive. Nothing is planted.
1. Multi day accumulations (MDPR with DAPR day counts) at 252 stations: a daily sum drops the rain and a daily
   row count disqualifies complete stations. 23 accumulations begin in 2024 and are unusable for 2025.
2. Quality flags on daily values, totals and day counts: 27 stations carry them.
3. Trace values are zeros with a measurement flag.
4. Values are tenths of a millimetre.
5. Blue Hill is registered twice at one coordinate pair; the inventory decides which record the bulletin keeps.
6. The Boston Logan station file stopped updating on 6 February 2025 while the 2025 partition is current; the
   Blue Hill LCD station file stopped in September 2024; the status notes are dated 2021.
7. Two honest offered figures that the files reproduce exactly.

## Deliverables
- station_certification_2025.csv: 430 station rows plus a STATEWIDE row.
- statewide_precipitation_2025.png: ranked bars of the 97 qualifying totals with the statewide line and labels.
- bulletin_certification_memo.pdf: one page.

## Input package
NOAA GHCN Daily as served from its public S3 archive on 2026-10-06: readme and extract notes, status and
version files, station registry and inventory, the 2025 parquet partitions for PRCP, MDPR and DAPR (24 files,
all stations), and the station files for Boston Logan and both Blue Hill identifiers, plus the scenario
compilation standard with its provenance stated. Formats: txt, parquet, csv, md. 39 files, 115 MB unzipped.
