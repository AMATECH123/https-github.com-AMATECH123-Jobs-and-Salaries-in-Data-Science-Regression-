# Fare engine acceptance standard

1. The fares in force are those encoded in the fare tables of the MBTA GTFS feed in the workspace (fare
   products, fare media, fare leg rules, fare transfer rules, fare leg join rules, areas, stop areas,
   timeframes, route networks), applied as the GTFS Schedule reference specifies, together with the MBTA's
   documented extension fields.
2. The fare of a journey on a fare medium is the lowest total the rules allow for that journey using only fare
   products available on that medium. A leg for which no rule offers a product on the medium has no fare on
   that medium, and the journey is then reported as having no fare on that medium.
3. Journey times are the scheduled times of the trips named in the test plan on the test date, 15 October 2026.
4. The engine passes acceptance only when its result for every journey in the test plan equals the fare under
   rules 1 to 3, to the cent, including the journeys that have no fare on their medium.
