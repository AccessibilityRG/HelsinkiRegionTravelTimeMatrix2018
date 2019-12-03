# Travel Time Matrix 2018 - Public Transport


## Parameters:

Origins: 100 origin points (per run) from the extended MetropAccess-YKR-grid -file.
Destinations: Extended MetropAccess-YKR-grid (14 645 grid centroids)
Conf PT: /homeappl/home/hentenka/Data/Confit/confMassaAjo2015.json
Conf Walking: /homeappl/home/hentenka/Data/Confit/confMassaAjo2015_kavely.json


## Pipeline:

1) PT schedules (Kalkati) have been tested that they function correctly / additional walking squares were added to Reititin for new metrostations in Espoo. 
2) Calculations are run in parallel using Taito Array jobs (altogether 249 jobs) with public transport and walking 
3) The results of the files will be written in $WRKDIR/Results/Matrix2018 for different travel modes 

