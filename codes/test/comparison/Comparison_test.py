import os
import unittest

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

from codes.src.comparison.Comparison import Comparison
from codes.src.util import FileActions


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
        gridCellsURL = self.dir + "%data%testData%YKRGridCells.geojson".replace("%", os.sep)
        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)
        filename = "sampleYKRGridPoints.geojson"

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
        carRoutingCostSummaryURL = self.dir + "%data%testData%rush_hour_delay_time_YKRCostSummary-5-13000.geojson".replace("%", os.sep)
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
        travelTimeSummaryURL = self.dir + "%data%outputData%comp_rush_hour_delay_time_mergedCostSummaryWithMetropAccessData.geojson".replace("%", os.sep)
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
        travelTimeProblematicPoints.to_csv(outputFolder+filename, sep=';', index=False)

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
