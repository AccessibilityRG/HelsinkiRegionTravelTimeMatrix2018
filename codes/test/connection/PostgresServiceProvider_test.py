import os
import unittest

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

from codes.src.comparison.Comparison import Comparison
from codes.src.connection.PostgresServiceProvider import PostGISServiceProvider
from codes.src.util import FileActions, GeometryType, GPD_CRS


class PostGISServiceProviderTest(unittest.TestCase):
    def setUp(self):
        self.dir = os.getcwd()
        self.comparison = Comparison()
        self.postGISServiceProvider = PostGISServiceProvider()
        self.fileActions = FileActions()
        self.testTableName = "test_travel_time_matrix"
        self.rushHourTableName = "rush_hour_time_car"
        self.middayTableName = "midday_time_car"
        self.rushHourTableNameDetailed = "rush_hour_time_car_detailed"

    def test_insertTestData(self):
        columns = {
            "startPoint_YKR_ID": "ykr_from_id",
            "endPoint_YKR_ID": "ykr_to_id",
            "total_travel_time": "travel_time"
        }

        travelTimeMatrix = self.dummyTravelTimeMatrix()

        travelTimeMatrix = self.postGISServiceProvider.renameColumnsAndExtractSubSet(travelTimeMatrix=travelTimeMatrix,
                                                                                     columns=columns)

        travelTimeMatrix = self.postGISServiceProvider.insertableTravelTimeMatrixGeoDataFrame(
            travelTimeMatrix=travelTimeMatrix, tableName=self.testTableName, column1="ykr_from_id",
            column2="ykr_to_id")

        isExecuted = self.postGISServiceProvider.insert(dataFrame=travelTimeMatrix,
                                                        tableName=self.testTableName,
                                                        isTableExist="append")
        self.assertTrue(isExecuted)

    def test_insertGridData(self):
        gridcellsURL = self.dir + "%data%testData%YKRGridCells.geojson".replace("%", os.sep)
        tableName = "ykr_gridcells"

        gridcellsURLDF = gpd.GeoDataFrame.from_file(gridcellsURL)
        columns = {
            "X": "x",
            "Y": "y",
            "YKR_ID": "ykr_id"
        }

        gridcellsURLDF = gridcellsURLDF.rename(index=str, columns=columns)
        gridcellsURLDF = gridcellsURLDF.to_crs(GPD_CRS.PSEUDO_MERCATOR)

        isExecuted = self.postGISServiceProvider.insert(gridcellsURLDF,
                                                        tableName=tableName,
                                                        isTableExist="replace",
                                                        geometryType=GeometryType.POLYGON)
        self.assertTrue(isExecuted)

    def dummyTravelTimeMatrix(self):
        data = {
            'startPoint_YKR_ID': pd.Series([1., 2., 3., 1.], index=[1, 2, 3, 4]),
            'endPoint_YKR_ID': pd.Series([4., 5., 6., 5.], index=[1, 2, 3, 4]),
            'total_travel_time': pd.Series([20., 30., 40., 50.], index=[1, 2, 3, 4])
        }
        lineString1 = LineString([[2793620.4483544305, 8460782.78014875], [2748951.962723606, 8424743.938335517]])
        geometries = [lineString1, lineString1, lineString1, lineString1]
        dataframe = pd.DataFrame(data)
        crs = {"init": 'epsg:3857'}
        travelTimeMatrix = gpd.GeoDataFrame(dataframe, crs=crs, geometry=geometries)
        return travelTimeMatrix

    def test_givenARowThatAlreadyExist_then_returnTrue(self):
        travelTimeMatrix = self.dummyTravelTimeMatrix()

        columns = {
            "startPoint_YKR_ID": "ykr_from_id",
            "endPoint_YKR_ID": "ykr_to_id",
            "total_travel_time": "travel_time"
        }

        travelTimeMatrix = travelTimeMatrix.rename(index=str, columns=columns)

        self.assertEqual(0,
                         len(self.postGISServiceProvider.insertableTravelTimeMatrixGeoDataFrame(
                             travelTimeMatrix=travelTimeMatrix,
                             tableName=self.testTableName,
                             column1="ykr_from_id",
                             column2="ykr_to_id")))

    def test_givenAYKRID_then_getItsTravelTimeMatrix(self):
        ykrid = 5973738

        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)
        filename = self.rushHourTableName + "_%s-3.geojson" % ykrid

        geodataframe = self.postGISServiceProvider.getTravelTimeMatrix(ykrid=ykrid,
                                                                       tableName=self.rushHourTableName)

        geojson = self.postGISServiceProvider.convertToGeojson(geodataframe)

        self.fileActions.writeFile(folderPath=outputFolder, filename=filename, data=geojson)

        self.assertGreater(len(geojson["features"]), 0)

    def test_givenAYKRID_then_getItsTravelTimeMatrixDifferences(self):
        ykrid = 5973738

        outputFolder = self.dir + "%data%outputData%".replace("%", os.sep)
        filename = self.rushHourTableNameDetailed + "_%s.geojson" % ykrid

        geodataframe = self.postGISServiceProvider.getTravelTimeMatrixDifferences(
            ykrid=ykrid,
            tableName=self.rushHourTableNameDetailed
        )

        geojson = self.postGISServiceProvider.convertToGeojson(geodataframe)

        self.fileActions.writeFile(folderPath=outputFolder, filename=filename, data=geojson)

        self.assertGreater(len(geojson["features"]), 0)
