# Workspace contents and provenance

This note was written by the task author to record where each file came from. Every data file is exactly as its
publisher served it on the pull date. The two documents written for this task, the office figure review standard and the
mid year claims note under review, say so in their first lines.

All files under data/ and docs/, and README.md, were pulled on 2026-10-06 from the Opportunity Insights Economic
Tracker repository on GitHub (https://github.com/OpportunityInsights/EconomicTracker) at commit
b8adef9d292873d7e45b07adc188f1785a035279 (5 October 2026), by sparse clone. Each file is byte identical to the
repository copy and keeps the repository's own name and folder. Terms of use (README.md): the data are made
freely available; users are asked to list the data provider of each series used and to cite the Economic
Tracker and its paper (Chetty, Friedman, Hendren, Stepner and the Opportunity Insights Team, 2020).

| File | What it is | Data provider | Rows |
|---|---|---|---|
| data/UI Claims - State - Weekly.csv | Weekly initial and continued unemployment insurance claims by state, counts and rates per 100 of the 2019 labor force, regular program, pandemic programs (empty since they ended) and combined, weeks ending 4 January 2020 to 26 September 2026. | U.S. Department of Labor | 17,952 |
| data/UI Claims - National - Weekly.csv | The same series for the nation. | U.S. Department of Labor | 352 |
| data/UI Claims - County - Weekly.csv | Weekly initial claims for the counties of the states that publish them. | State workforce agencies | 174,000 |
| data/GeoIDs - State.csv | State FIPS codes, names, abbreviations and 2019 population. | Opportunity Insights | 51 |
| data/GeoIDs - County.csv | County FIPS codes, names, states and 2019 population. | Opportunity Insights | 3,220 |
| data/Employment - State - Weekly.csv | Weekly employment level relative to January 2020 by state and wage quartile, from payroll and timesheet providers. | Paychex, Intuit, Earnin, Kronos via Opportunity Insights | 28,305 |
| data/Job Postings - State - Weekly.csv | Weekly job postings relative to January 2020 by state, industry and preparation level. | Lightcast via Opportunity Insights | 17,901 |
| docs/oi_tracker_data_dictionary.md, .pdf | Variable by variable dictionary for every tracker file. | Opportunity Insights | |
| docs/oi_tracker_data_documentation.md, .pdf | Sources and processing for every series, including the Department of Labor claims. | Opportunity Insights | |
| docs/oi_tracker_data_revisions.md, .pdf | Record of revisions to posted series since June 2021. | Opportunity Insights | |
| README.md | The repository's own readme: terms of use, citation, document links. | Opportunity Insights | |
| office_figure_review_standard.md | Scenario document written by the task author stating the office's standard for reviewing a published figure. Not a Department of Labor or Opportunity Insights publication. | task author | |
| midyear_claims_note_2026-07-10.md | Scenario document written by the task author: the office's mid year claims note as published, the statement under review. Its figures were computed from the record in this workspace. | task author | |

Attribution: unemployment insurance claims data from the U.S. Department of Labor, compiled by the Opportunity
Insights Economic Tracker (https://tracktherecovery.org; Chetty, Friedman, Hendren, Stepner and the Opportunity
Insights Team, "The Economic Impacts of COVID-19: Evidence from a New Public Database Built Using Private Sector
Data", 2020).
