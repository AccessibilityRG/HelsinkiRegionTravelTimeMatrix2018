import unittest

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
