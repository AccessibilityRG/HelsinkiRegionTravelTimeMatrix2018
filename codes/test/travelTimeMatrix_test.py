import unittest

import os

from codes.src.travelTimeMatrix import runTravelTimeMatrixOperations


class TravelTimeMatrixTest(unittest.TestCase):
    def test_main_query_function(self):
        querying = True
        uploading = False
        zippath = r"C:/Users/jeisonle/repository/Car-Routing/DigiroadPreDataAnalysis/digiroad/test/data/geojson/Subsets/subset1/summary1.zip"
        outputFolder = os.getcwd() + "%data%outputFolder%summary1%".replace("%", os.sep)

        directionality = "TO"
        target = 5793265
        runTravelTimeMatrixOperations(querying, uploading, outputFolder, zippath, directionality, target)

    def test_main_upload_function(self):
        querying = False
        uploading = True
        # zippath = r"C:/Users/jeisonle/repository/Car-Routing/DigiroadPreDataAnalysis/digiroad/test/data/geojson/Subsets/subset1/summary1.zip"
        zippath = r"C:/Users/jeisonle/repository/Car-Routing/DigiroadPreDataAnalysis/digiroad/test/data/outputFolder/summary/rush_hour_delay_time_metroAccessDigiroadSummary.zip"
        outputFolder = os.getcwd() + "%data%outputFolder%summary1%".replace("%", os.sep)

        directionality = "TO"
        target = 5793265
        runTravelTimeMatrixOperations(querying, uploading, outputFolder, zippath, directionality, target)
