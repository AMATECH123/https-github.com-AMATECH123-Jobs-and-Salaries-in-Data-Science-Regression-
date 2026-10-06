# Workspace contents and provenance

Written by the task author to record where each file came from. Every data file is exactly as NOAA's National
Centers for Environmental Information served it from the GHCN Daily public archive on Amazon S3
(https://noaa-ghcn-pds.s3.amazonaws.com/) on the pull date. GHCN Daily is a U.S. Government work in the public
domain; cite Menne et al. (2012), doi:10.1175/JTECH-D-11-00103.1 and the dataset doi:10.7289/V5D21VHZ. The one
document written for this task, the bulletin compilation standard, says so in its first lines.

| File | What it is | Pulled |
|---|---|---|
| ghcnd/readme.txt | GHCN Daily readme: file formats, element codes and units, measurement, quality and source flags | 2026-10-06 |
| ghcnd/readme-by_station.txt, readme-by_year.txt | Field definitions of the csv extracts | 2026-10-06 |
| ghcnd/status.txt, status-by_station.txt, status-by_year.txt, ghcnd-version.txt | NOAA status notes and the dataset version in force | 2026-10-06 |
| ghcnd/ghcnd-stations.txt | Station registry: identifier, coordinates, elevation, state, name, networks | 2026-10-06 |
| ghcnd/ghcnd-inventory.txt | Period of record by station and element | 2026-10-06 |
| ghcnd/ghcnd-states.txt | State and province codes | 2026-10-06 |
| ghcnd/parquet/by_year/YEAR=2025/ELEMENT=PRCP, MDPR, DAPR | The 2025 partition of the archive for those three elements, all stations worldwide, as published (24 parquet files) | 2026-10-06 |
| ghcnd/csv/by_station/USW00014739.csv | Boston Logan International Airport station file, as served (its last update was 9 February 2025) | 2026-10-06 |
| ghcnd/csv/by_station/USC00190736.csv | Blue Hill cooperative observer station file, as served | 2026-10-06 |
| ghcnd/csv/by_station/USW00014753.csv | Blue Hill LCD station file, as served (its last update was 30 September 2024) | 2026-10-06 |
| bulletin_compilation_standard.md | Scenario document written by the task author: the standard the bulletin applies | 2026-10-06 |
