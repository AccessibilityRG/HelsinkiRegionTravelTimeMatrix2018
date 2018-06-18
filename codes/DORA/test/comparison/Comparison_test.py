import os
import unittest

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

from codes.src.comparison.Comparison import Comparison
from codes.src.util import FileActions, GPD_CRS


class ComparisonTest(unittest.TestCase):
    def setUp(self):
        self.fileActions = FileActions()
        self.dir = os.getcwd()
        self.comparison = Comparison()

    def test_getGridCellSamples(self):
        gridCellsURL = self.dir + "%data%testData%YKRGridCells.geojson".replace("%", os.sep)
        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)
        filename = "sampleYKRGridCells-5.geojson"

        gridCellSamples = self.comparison.getGridSamples(gridCellsURL=gridCellsURL, sampleSie=5)
        geojson = self.comparison.convertToGeojson(gridCellSamples)

        self.fileActions.writeFile(folderPath=outputFolder, filename=filename, data=geojson)

        self.assertIsNotNone(gridCellSamples)

    def test_givenGridCellsPolygons_then_transformCentroidsInPoints(self):
        gridCellsURL = self.dir + "%data%testData%points.geojson".replace("%", os.sep)
        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)
        filename = "points.geojson"

        points = self.comparison.createPointsFromGrigCells(gridCellsURL=gridCellsURL)
        geojson = self.comparison.convertToGeojson(points)
        self.fileActions.writeFile(folderPath=outputFolder, filename=filename, data=geojson)

        self.assertIsNotNone(points)

    def test_loadTravelTimeMatrixDataFrameSubset(self):
        travelTimeMatrixURL = "C:%Users%jeisonle%Downloads%HelsinkiRegion_TravelTimeMatrix2015".replace("%", os.sep)
        # gridCellsURL = self.dir + "%data%testData%Test_Points_Reititin_with_MatrixID.geojson".replace("%", os.sep)
        originGridCellsURL = self.dir + "%data%testData%sampleYKRGridPoints-5.geojson".replace("%", os.sep)
        destinationGridCellsURL = self.dir + "%data%testData%sampleYKRGridPoints-13000.geojson".replace("%", os.sep)

        travelTimeMatrixSubset = self.comparison.loadTravelTimeMatrixDataFrameSubset(
            travelTimeMatrixURL=travelTimeMatrixURL,
            originGridCellsURL=originGridCellsURL,
            destinationGridCellsURL=destinationGridCellsURL,
            gridID="YKR_ID"
        )

        # out = r"...\Travel_times_from_chosen_originIDs_to_selected_destinationIDs.txt"
        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)
        filename = "travelTime5-13000PointsSubset.csv"
        travelTimeMatrixSubset.to_csv(outputFolder + filename, sep=';', index=False)

        self.assertIsNotNone(travelTimeMatrixSubset)

    def test_givenCarRoutingCostSummary_then_mergeItWithMetropAccessData(self):
        travelTimeMatrixURL = self.dir + "%data%outputData%travelTime5-13000PointsSubset.csv".replace("%", os.sep)
        carRoutingCostSummaryURL = self.dir + "%data%testData%rush_hour_delay_time_YKRCostSummary-5-13000.geojson".replace(
            "%", os.sep)
        # carRoutingCostSummaryURL = self.dir + "%data%testData%midday_delay_time_YKRCostSummary-100Points.geojson".replace(
        #    "%", os.sep)
        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)
        filename = "comp_rush_hour_delay_time_mergedCostSummaryWithMetropAccessData.geojson"
        # filename = "comp_midday_delay_time_mergedCostSummaryWithMetropAccessData.geojson"

        mergeResult = self.comparison.mergeMetropAccessData(
            travelTimeMatrixURL=travelTimeMatrixURL,
            carRoutingCostSummaryURL=carRoutingCostSummaryURL
        )

        geojson = self.comparison.convertToGeojson(mergeResult)

        self.fileActions.writeFile(folderPath=outputFolder, filename=filename, data=geojson)

        self.assertIsNotNone(mergeResult)

    def test_givenTravelTimeMergedDataLayer_then_calculateTheDifferenceBetweenOldAndNewData(self):
        travelTimeSummaryURL = self.dir + "%data%outputData%comp_rush_hour_delay_time_mergedCostSummaryWithMetropAccessData.geojson".replace(
            "%", os.sep)
        # travelTimeSummaryURL = self.dir + "%data%outputData%comp_midday_delay_time_mergedCostSummaryWithMetropAccessData.geojson".replace(
        #    "%", os.sep)
        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)
        filename = "rush_hour_travelTimeMatrixDifference.geojson"
        # filename = "midday_delay_travelTimeMatrixDifference.geojson"

        travelTimeDifferenceLayer = self.comparison.calculateDifferenceBetweenOldAndNewTravelTimes(
            travelTimeSummaryURL=travelTimeSummaryURL)

        geojson = self.comparison.convertToGeojson(travelTimeDifferenceLayer)

        self.fileActions.writeFile(folderPath=outputFolder, filename=filename, data=geojson)

        self.assertIsNotNone(travelTimeDifferenceLayer)

    def test_getProblematicSetOfPoints(self):
        rush_hour_travel_time_filename = self.dir + "%data%outputData%rush_hour_travelTimeMatrixDifference.geojson".replace(
            "%", os.sep)
        midday_travel_time_filename = self.dir + "%data%outputData%midday_delay_travelTimeMatrixDifference.geojson".replace(
            "%", os.sep)

        threshold = 10
        travelTimeProblematicPoints = self.comparison.extractSummaryThatExceedAThreshold(
            travelTimeSummaryURL=rush_hour_travel_time_filename, threshold=threshold
        )

        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)
        filename = "problematicPoints.txt"
        travelTimeProblematicPoints.to_csv(outputFolder + filename, sep=';', index=False)

        print(len(travelTimeProblematicPoints[0:]))
        self.assertIsNotNone(travelTimeProblematicPoints)

    def test_givenYKRPoints_then_createHeatLayer(self):
        gridCellsURL = self.dir + "%data%testData%Test_Points_MetropA_Digiroad.geojson".replace("%", os.sep)
        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)

        gridCellSamples = self.comparison.getGridSamples(gridCellsURL=gridCellsURL, sampleSie=4, YKR_ID="ID")
        geojson = self.comparison.convertToGeojson(gridCellSamples)

        filename = "sampleYKRGridCellsForHeatMap.geojson"
        self.fileActions.writeFile(folderPath=outputFolder, filename=filename, data=geojson)

        selectedGridCellsURL = outputFolder + filename
        travelTimeMatrixDifferenceURL = outputFolder + "midday_delay_travelTimeMatrixDifference.geojson"
        heatMapLayer = self.comparison.createMultiPointHeatMapLayer(
            selectedGridCellsURL=selectedGridCellsURL,
            travelTimeMatrixDifferenceURL=travelTimeMatrixDifferenceURL
        )

        self.assertIsNotNone(heatMapLayer)

    def test_createWalkingDistanceLayer(self):
        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)
        filename = "walking_distance_regions.geojson"

        p1 = Polygon([
            (387678.024778, 6675360.99039),
            (387891.53396, 6670403.35286),
            (383453.380944, 6670212.21613),
            (383239.871737, 6675169.85373),
            (387678.024778, 6675360.99039)
        ])
        g = [p1]
        d = {
            'region': pd.Series(["Helsinki City Center"], index=['a']),
            'walking_distance': pd.Series([180], index=['a'])
        }

        df = pd.DataFrame(d)

        crs = {"init": 'epsg:3067'}
        walking_distance = gpd.GeoDataFrame(df, crs=crs, geometry=g)

        geojson = self.comparison.convertToGeojson(walking_distance)
        self.fileActions.writeFile(folderPath=outputFolder, filename=filename, data=geojson)

    def test_readShapefileAsADataFrame(self):
        # 5973738 rautatientori
        # 5870644
        # 5963599
        # 5920413
        # 5878018
        ykr_id = 5878018
        ykrGridGeojson = self.dir + "%data%testData%YKRGridCells.geojson".replace("%", os.sep)
        shapefile = self.dir + ("&data&outputData&data-13000-5&Car_Rush_hour_2015_to_%s.shp" % ykr_id).replace("&",
                                                                                                               os.sep)
        pgGeojson = self.dir + "%data%outputData%rush_hour_delay_time_YKRCostSummary-13000-5.geojson".replace(
            "%", os.sep)
        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)
        filename = "detailedAttributeDifferences_newRoeadNetwork_%s.geojson" % ykr_id

        oldMetropAccessDataFrame = gpd.read_file(shapefile)
        newPgRoutingDataFrame = gpd.read_file(pgGeojson)
        ykrDataFrame = gpd.read_file(ykrGridGeojson)

        ykrDataFrame = ykrDataFrame[["YKR_ID", "x", "y", "geometry"]]
        ykrDataFrame = ykrDataFrame.to_crs(GPD_CRS.PSEUDO_MERCATOR)

        newPgRoutingDataFrame.startPoint_id = [int(x) for x in newPgRoutingDataFrame.startPoint_YKR_ID.values]
        newPgRoutingDataFrame.endPoint_id = [int(y) for y in newPgRoutingDataFrame.endPoint_YKR_ID.values]
        newPgRoutingDataFrame = newPgRoutingDataFrame.drop(['geometry'], axis=1)

        columns = {
            "Kavely_O_T": "old_startPoint_EuclideanDistanceWalkingTime",
            "Kavely_T_P": "old_startPoint_AVGWalkingDistanceWalkingTime",
            "Kavely_T_D": "old_endPoint_EuclideanDistanceWalkingTime",
            "Kavely_P_T": "old_endPoint_AVGWalkingDistanceWalkingTime",
            "Parkkiaika": "old_endPoint_ParkingTime",
            "Ruuhka_aa": "old_rush_hour_delay_time",
            "Keskpva_aa": "old_midday_delay_time",
            "Kokopva_aa": "old_day_average_delay_time",
            "Digiroa_aa": "old_speed_limit_time",
        }
        oldMetropAccessDataFrame = oldMetropAccessDataFrame.rename(index=str, columns=columns)
        oldMetropAccessDataFrame = oldMetropAccessDataFrame.to_crs(GPD_CRS.PSEUDO_MERCATOR)
        oldMetropAccessDataFrame = oldMetropAccessDataFrame.drop(['geometry'], axis=1)

        mergedData = oldMetropAccessDataFrame.merge(
            ykrDataFrame,
            left_on="from_id",
            right_on="YKR_ID"
        )

        mergedData = mergedData.merge(
            newPgRoutingDataFrame,
            left_on=("from_id", "to_id"),
            right_on=("startPoint_id", "endPoint_id")
        )

        costAttribute = newPgRoutingDataFrame["costAttribute"][0]
        mergedData["dif_start_EuclideanDistanceWalkingTime"] = mergedData.startPoint_EuclideanDistanceWalkingTime - \
                                                               mergedData.old_startPoint_EuclideanDistanceWalkingTime
        mergedData[
            "dif_startPoint_AVGWalkingDistanceWalkingTime"] = mergedData.startPoint_AVGWalkingDistanceWalkingTime - \
                                                              mergedData.old_startPoint_AVGWalkingDistanceWalkingTime
        mergedData["dif_endPoint_EuclideanDistanceWalkingTime"] = mergedData.endPoint_EuclideanDistanceWalkingTime - \
                                                                  mergedData.old_endPoint_EuclideanDistanceWalkingTime
        mergedData["dif_endPoint_AVGWalkingDistanceWalkingTime"] = mergedData.endPoint_AVGWalkingDistanceWalkingTime - \
                                                                   mergedData.old_endPoint_AVGWalkingDistanceWalkingTime
        mergedData["dif_endPoint_ParkingTime"] = mergedData.endPoint_ParkingTime - \
                                                 mergedData.old_endPoint_ParkingTime

        difCostAttribute = "dif_" + costAttribute
        mergedData[difCostAttribute] = mergedData["old_%s" % costAttribute] - \
                                       mergedData[costAttribute]

        # mergedData = mergedData[["from_id", "to_id"]]

        # self.assertIsNotNone(oldMetropAccessDataFrame)
        # self.assertIsNotNone(newPgRoutingDataFrame)

        geojson = self.fileActions.convertDataFrameToGeojson(mergedData)
        self.fileActions.writeFile(folderPath=outputFolder,
                                   filename=filename,
                                   data=geojson)

        self.assertIsNotNone(geojson)
