# Quarterly claims outlook: forecasting standard

Scenario document. Written by the task author to state the standard the office applies in this task. It is not a
Department of Labor or Opportunity Insights publication. The claims record it is applied to is real and
unaltered.

1. Purpose. Each quarter the office publishes a thirteen week outlook of weekly initial unemployment insurance
   claims for each state of the Census Bureau's Midwest Region (Illinois, Indiana, Iowa, Kansas, Michigan,
   Minnesota, Missouri, Nebraska, North Dakota, Ohio, South Dakota and Wisconsin). For each state the outlook
   publishes either the model path or the benchmark path, and the choice is made by the back test below.

2. The record. The state weekly claims series in the workspace, regular program initial claims, as counts.
   A week is identified by the Saturday it ends on. The latest week in the record is the origin of the outlook,
   and the outlook covers the thirteen weeks after it.

3. The model. The model forecast for a target week is the count of the week ending 364 days before the target,
   multiplied by the ratio of the sum of the counts of the eight weeks ending at the origin to the sum of the
   counts of the eight weeks ending 364 days before the origin.

4. The benchmark. The benchmark forecast for every target week is the mean of the counts of the four weeks
   ending at the origin.

5. The back test. The back test origins are the twenty six weeks ending between four and twenty nine weeks
   before the latest week in the record. From each origin, both the model and the benchmark forecast the four
   following weeks using only the record up to that origin. A method's back test error is the mean, over the
   one hundred and four forecasts, of the absolute difference between forecast and actual as a percentage of the
   actual, stated to two decimal places.

6. The decision. A state's model path is published when the model's back test error is lower than the
   benchmark's. Otherwise the state is held: the benchmark path is published in place of the model path and
   the state is flagged as held. There is no regional test; each state stands on its own back test.

7. Figures. Forecasts are stated as whole claims, rounded at the end with halves rounded up. The outlook's
   regional total is the sum of the published weekly figures as stated.
