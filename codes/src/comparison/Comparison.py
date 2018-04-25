import json

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

from codes.src.comparison.SelectFiles_tools import selectFilesQuery, listFiles, \
    selectIdsQueryParallelized
from codes.src.util import dgl_timer


class Comparison(object):
    def getGridSamples(self, gridCellsURL, sampleSie, YKR_ID="YKR_ID"):
        gridCellsDataFrame = gpd.GeoDataFrame.from_file(gridCellsURL)
        r_sample = np.random.choice(gridCellsDataFrame[YKR_ID].values, size=sampleSie, replace=False)
        sample = gridCellsDataFrame.loc[gridCellsDataFrame[YKR_ID].isin(r_sample)]

        return sample

    def convertToGeojson(self, geoDataFrame):
        crs = geoDataFrame.crs["init"].replace(":", "::")

        jsonResult = geoDataFrame.to_json()
        newJson = json.loads(jsonResult)

        newJson["crs"] = {
            "properties": {
                "name": "urn:ogc:def:crs:%s" % crs
            },
            "type": "name"
        }
        return newJson

    def createPointsFromGrigCells(self, gridCellsURL):
        gridCellsDataFrame = gpd.GeoDataFrame.from_file(gridCellsURL)
        geometry = [Point(xy) for xy in zip(gridCellsDataFrame["x"], gridCellsDataFrame["y"])]
        gridCellsDataFrame = gridCellsDataFrame.drop(["x", "y"], axis=1)
        crs = gridCellsDataFrame.crs
        points = gpd.GeoDataFrame(gridCellsDataFrame, crs=crs, geometry=geometry)
        return points

    def loadTravelTimeMatrixDataFrameSubset(self, travelTimeMatrixURL, originGridCellsURL, destinationGridCellsURL,
                                            gridID="ID"):
        originGridCellsDataFrame = gpd.GeoDataFrame.from_file(originGridCellsURL)
        destinationGridCellsDataFrame = gpd.GeoDataFrame.from_file(destinationGridCellsURL)
        origIDs = originGridCellsDataFrame[gridID].values
        destIDs = destinationGridCellsDataFrame[gridID].values

        files = listFiles(travelTimeMatrixURL)
        # Select files to chosen destinations
        destFiles = selectFilesQuery(files, destIDs)

        # Search chosen origin YKR-IDs within the selected files
        selection = selectIdsQueryParallelized(self, destFiles, origIDs, searchColumn="from_id", sep=";")
        # selection = selectIdsQuery(destFiles, origIDs, searchColumn="from_id", sep=";")

        # Save selection to disk
        # out = r"...\Travel_times_from_chosen_originIDs_to_selected_destinationIDs.txt"
        # selection.to_csv(out, sep=";", index=False)

        return selection

    def mergeMetropAccessData(self, travelTimeMatrixURL, carRoutingCostSummaryURL):
        travelTimeSubset = pd.read_csv(travelTimeMatrixURL, sep=";")
        costSummaryDF = gpd.GeoDataFrame.from_file(carRoutingCostSummaryURL)

        carTravelTimeSubset = travelTimeSubset[
            ["from_id", "to_id", "walk_t", "walk_d", "car_r_t", "car_r_d", "car_m_t", "car_m_d"]
        ]

        # transform string values into integer values
        costSummaryDF.startPoint_id = [int(x) for x in costSummaryDF.startPoint_YKR_ID.values]
        costSummaryDF.endPoint_id = [int(y) for y in costSummaryDF.endPoint_YKR_ID.values]

        mergedData = costSummaryDF.merge(
            carTravelTimeSubset,
            left_on=("startPoint_id", "endPoint_id"),
            right_on=("from_id", "to_id")
        )

        return mergedData

    @dgl_timer
    def calculateTravelTime(self, travelTimeSummaryURL):
        travelTimeSummaryDF = gpd.GeoDataFrame.from_file(travelTimeSummaryURL)

        if len(travelTimeSummaryDF["costAttribute"]) > 0:
            costAttribute = travelTimeSummaryDF["costAttribute"][0]
            travelTimeSummaryDF["total_travel_time"] = travelTimeSummaryDF.startPoint_EuclideanDistanceWalkingTime + \
                                                       travelTimeSummaryDF.startPoint_AVGWalkingDistanceWalkingTime + \
                                                       travelTimeSummaryDF[costAttribute] + \
                                                       travelTimeSummaryDF.endPoint_ParkingTime + \
                                                       travelTimeSummaryDF.endPoint_AVGWalkingDistanceWalkingTime + \
                                                       travelTimeSummaryDF.endPoint_EuclideanDistanceWalkingTime

        return travelTimeSummaryDF

    def calculateDifferenceBetweenOldAndNewTravelTimes(self, travelTimeSummaryURL):
        travelTimeSummaryDF = self.calculateTravelTime(travelTimeSummaryURL=travelTimeSummaryURL)
        if len(travelTimeSummaryDF["costAttribute"]) > 0:
            costAttribute = travelTimeSummaryDF["costAttribute"][0]
            if costAttribute == "rush_hour_delay_time":
                travelTimeSummaryDF[
                    "travel_time_difference"] = travelTimeSummaryDF.total_travel_time - travelTimeSummaryDF.car_r_t
            elif costAttribute == "midday_delay_time":
                travelTimeSummaryDF[
                    "travel_time_difference"] = travelTimeSummaryDF.total_travel_time - travelTimeSummaryDF.car_m_t

        return travelTimeSummaryDF

    def createMultiPointHeatMapLayer(self, selectedGridCellsURL, travelTimeMatrixDifferenceURL):
        selectedGridCellsDF = gpd.GeoDataFrame.from_file(selectedGridCellsURL)
        travelTimeMatrixDifferenceDF = gpd.GeoDataFrame.from_file(travelTimeMatrixDifferenceURL)

    def extractSummaryThatExceedAThreshold(self, travelTimeSummaryURL, threshold):
        travelTimeSummaryDF = gpd.GeoDataFrame.from_file(travelTimeSummaryURL)

        upperThreshold = travelTimeSummaryDF[travelTimeSummaryDF.travel_time_difference > threshold]
        lowerThreshold = travelTimeSummaryDF[travelTimeSummaryDF.travel_time_difference < -threshold]

        extractedSummary = pd.concat([upperThreshold, lowerThreshold], ignore_index=True)
        return extractedSummary[["from_id", "to_id"]]
