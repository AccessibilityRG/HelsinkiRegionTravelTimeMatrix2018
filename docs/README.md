# Documentation about testing etc. 

**Format:** GeoJson 

**Files:** 
* Test_Points_Reititin.geojson
* Test_Points_Reititin_with_MatrixID (similar to the "test_points_reititin" file but with MatrixID joined)
* Test_Points_MetropA_Digiroad.geojson

**METROPACCESS DIGIROAD**
The [test points][digiroad_2015_test_points] are the centroids of the grid squares that were sampled from MetropAccess grid using a random sample (n=100). 

**REITITIN**
The [test points for Reititin][reititin_test_points] were selected mostly along the metro line (n=101). Three points per station were set, one on the right side, one on the left and one on top of the station to see that the connections are working as they should. The rest of the points are located in the housing disticts in Espoo, Helsinki and Vantaa. 

![TestPointImageMetropADigiroad](https://github.com/AccessibilityRG/HelsinkiRegionTravelTimeMatrix2018/blob/master/docs/LocationsOfDigiroadTestPoints.png)
Locations of the MetropAccess Digiroad quality test points 

![TestPointsImageReititin](https://github.com/AccessibilityRG/HelsinkiRegionTravelTimeMatrix2018/blob/master/docs/LocationsOfReititinTestPoints.png)
Locations of the Reititin quality test points 


[reititin_test_points]: ./../data/testData/TestPointsReititin.geojson
[digiroad_2015_test_points]: ./../data/testData/Test_Points_MetropA_Digiroad.geojson
