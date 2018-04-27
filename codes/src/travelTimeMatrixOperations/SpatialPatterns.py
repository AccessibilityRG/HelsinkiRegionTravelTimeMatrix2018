import os

from codes.src.util import dgl_timer, FileActions, Logger


class SpatialPatterns(object):
    def __init__(self, comparison,
                 postGISServiceProvider):
        self.comparison = comparison
        self.postGISServiceProvider = postGISServiceProvider

    @dgl_timer
    def insertData(self, travelTimeMatrixURL, tableName, columns, outputFolder):
        csv_separator = ';'

        # travelTimeMatrix = self.comparison.calculateTravelTime(travelTimeMatrixURL)
        #
        # travelTimeMatrix = self.postGISServiceProvider.renameColumnsAndExtractSubSet(
        #     travelTimeMatrix=travelTimeMatrix,
        #     columns=columns
        # )
        # # travelTimeMatrix = self.postGISServiceProvider.insertableTravelTimeMatrixGeoDataFrame(
        # #     travelTimeMatrix=travelTimeMatrix, tableName=tableName, column1="ykr_from_id",
        # #     column2="ykr_to_id")
        #
        # # isExecuted = self.postGISServiceProvider.insert(dataFrame=travelTimeMatrix,
        # #                                                 tableName=tableName)
        #
        # csv_filename = tableName + ".csv"
        # FileActions().createFile(outputFolder, csv_filename)
        #
        #
        #
        # csv_path = os.path.join(outputFolder, csv_filename)
        # travelTimeMatrix.to_csv(csv_path, sep=csv_separator, index=False)
        # columns = tuple(travelTimeMatrix.columns.values)
        #
        # csv_file = open(csv_path, 'r')
        # csv_file.readline()  # dismiss the first row with the column names

        try:
            csv_file = open(travelTimeMatrixURL, 'r')
            csv_file.readline()  # dismiss the first row with the column names

            isExecuted = self.postGISServiceProvider.copyData(csvData=csv_file,
                                                              tableName=tableName,
                                                              columns=columns,
                                                              separator=csv_separator)
        finally:
            csv_file.close()
        return isExecuted
