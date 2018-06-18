import unittest
import zipfile

from gevent import os

from codes.src.comparison.Comparison import Comparison
from codes.src.connection.PostgresServiceProvider import PostGISServiceProvider
from codes.src.travelTimeMatrixOperations.SpatialPatterns import SpatialPatterns
from codes.src.util import FileActions


class SpatialPatternsTest(unittest.TestCase):
    def setUp(self):
        self.dir = os.getcwd()

        self.spatialPatter = SpatialPatterns(
            comparison=Comparison(),
            postGISServiceProvider=PostGISServiceProvider()
        )

        self.fileActions = FileActions()
        self.testTableName = "test_travel_time_matrix"
        self.rushHourTableName = "rush_hour_time_car"
        self.middayTableName = "midday_time_car"
        self.rushHourTableNameDetailed = "rush_hour_time_car_detailed"
        self.bicycleTravelTimeMatrix = "bicycle_travel_time_matrix"

    def test_givenAGeojson_then_storedItInATheCorrectTable(self):
        travelTimeMatrixURL = self.dir + "%data%testData%rush_hour_delay_time_YKRCostSummary-13000-5-oldRoadNetwork.geojson".replace(
            "%", os.sep)

        columns = {
            "startPoint_YKR_ID": "ykr_from_id",
            "endPoint_YKR_ID": "ykr_to_id",
            "total_travel_time": "travel_time"
        }

        isExecuted = self.spatialPatter.insertData(travelTimeMatrixURL, columns)
        self.assertTrue(isExecuted)

    def test_givenAGeojsonWithtravelTimeDifference_then_storedItInATheCorrectTable(self):
        travelTimeMatrixURL = self.dir + "%data%outputData%rush_hour_travelTimeMatrixDifference.geojson".replace(
            "%", os.sep)

        columns = {
            "startPoint_id": "ykr_from_id",
            "endPoint_id": "ykr_to_id",
            "total_travel_time": "travel_time",
            "travel_time_difference": "travel_time_difference"
        }

        isExecuted = self.spatialPatter.insertData(travelTimeMatrixURL, self.rushHourTableNameDetailed, columns)
        self.assertTrue(isExecuted)

    def test_givenSlowBicycleCostSummaryGeojson_then_storedItInBicycleCostSummaryTable(self):
        travelTimeMatrixURL = self.dir + "%data%outputData%slow_time_BicycleRoadNetwork-13000-5.geojson".replace(
            "%", os.sep)

        columns = {
            "startPoint_YKR_ID": "ykr_from_id",
            "endPoint_YKR_ID": "ykr_to_id",
            "total_travel_time": "travel_time",
        }

        isExecuted = self.spatialPatter.insertData(travelTimeMatrixURL, "slow_" + self.bicycleTravelTimeMatrix, columns)
        self.assertTrue(isExecuted)

    def test_givenFastBicycleCostSummaryGeojson_then_storedItInBicycleCostSummaryTable(self):
        travelTimeMatrixURL = self.dir + "%data%outputData%cardat2%fast_time_dijsktraCostMetroAccessDigiroadSummary.geojson".replace(
            "%", os.sep)

        columns = {
            "startPoint_YKR_ID": "ykr_from_id",
            "endPoint_YKR_ID": "ykr_to_id",
            "total_travel_time": "travel_time",
        }

        tableName = "cardat_two_fast_" + self.bicycleTravelTimeMatrix + ""

        isExecuted = self.spatialPatter.insertData(travelTimeMatrixURL, tableName, columns)
        self.assertTrue(isExecuted)

    def test_decompressZip_to_uploadGeojsonFilesToPostgresTable(self):
        zippath = "C:/Users/jeisonle/repository/Car-Routing/DigiroadPreDataAnalysis/digiroad/test/data/geojson/Subsets/subset1/summary1.zip"

        outputFolder = self.dir + "%data%outputData%summaries".replace("%", os.sep)
        outputFolder = os.path.join(outputFolder, os.path.basename(zippath).split(".")[-2])

        self.fileActions.decompressZipfile(zippath, outputFolder)

        columns = {
            "startPoint_YKR_ID": "ykr_from_id",
            "endPoint_YKR_ID": "ykr_to_id",
            "total_travel_time": "travel_time",
        }

        tableName = "cardat_fast_" + self.bicycleTravelTimeMatrix + ""

        for root, dirs, files in os.walk(outputFolder):
            for filename in files:
                if filename.endswith("geojson"):
                    f = os.path.join(root, filename)
                    print("Loading: %s" % filename)
                    isExecuted = self.spatialPatter.insertData(f, tableName, columns)
                    if isExecuted:
                        os.remove(f)

                    self.assertTrue(isExecuted)
