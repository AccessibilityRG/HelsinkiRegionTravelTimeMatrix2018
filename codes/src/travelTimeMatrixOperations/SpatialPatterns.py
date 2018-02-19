class SpatialPatterns(object):
    def __init__(self, comparison,
                 postGISServiceProvider):
        self.comparison = comparison
        self.postGISServiceProvider = postGISServiceProvider

    def insertData(self, travelTimeMatrixURL, tableName, columns):
        travelTimeMatrix = self.comparison.calculateTravelTime(travelTimeMatrixURL)
        travelTimeMatrix = self.postGISServiceProvider.renameColumnsAndExtractSubSet(
            travelTimeMatrix=travelTimeMatrix,
            columns=columns
        )
        travelTimeMatrix = self.postGISServiceProvider.insertableTravelTimeMatrixGeoDataFrame(
            travelTimeMatrix=travelTimeMatrix, tableName=tableName, column1="ykr_from_id",
            column2="ykr_to_id")
        isExecuted = self.postGISServiceProvider.insert(dataFrame=travelTimeMatrix,
                                                        tableName=tableName)
        return isExecuted
