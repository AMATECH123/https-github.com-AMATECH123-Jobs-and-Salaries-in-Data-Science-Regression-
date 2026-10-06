# Annual Precipitation Bulletin: compilation standard

Scenario document. Written by the task author to state the standard the state climate office applies when it
compiles the annual precipitation bulletin in this task. It is not a NOAA or Commonwealth publication. The
observation data it is applied to is NOAA's Global Historical Climatology Network Daily, real and unaltered.

1. Source. Daily precipitation records from GHCN Daily for every station registered to Massachusetts in the
   station registry (ghcnd-stations.txt). Element codes, units, flags and the multi day elements are as the
   GHCN Daily readme defines them.

2. Quality. A value that carries any quality flag failed NOAA's quality assurance and is treated as missing.
   This applies to daily values, to multi day totals and to the day counts that accompany them.

3. Trace. A trace of precipitation is a measured day with a value of zero.

4. Multi day totals. A multi day precipitation total covers the day it is reported on and the days before it
   that its day count says it covers. A total is usable only when its day count is present, unflagged, and
   the whole covered period lies within the bulletin year. A usable total counts every covered day as
   measured and contributes its full amount to the station's annual total; any daily value reported on a
   covered day is superseded by it. A total that is not usable is ignored entirely.

5. Completeness. A station qualifies for the bulletin year only when every calendar day of the year is
   measured, by a daily value or by a usable multi day total.

6. One record per site. Where two station identifiers share the same registered latitude and longitude, the
   bulletin keeps the identifier whose precipitation record begins earliest in the station inventory
   (ghcnd-inventory.txt) and drops the other.

7. The statewide figure. The bulletin's statewide annual precipitation is the arithmetic mean of the annual
   totals of the qualifying stations, in millimetres to one decimal place, together with the number of
   stations it rests on.

8. The Boston record. The bulletin's Boston figure is the annual total at Boston Logan International Airport
   (USW00014739). Its rank is taken among the years of that station's record that satisfy rule 5, wettest
   first.
