import getopt
import os
import sys
import traceback

# dir_path = os.path.dirname(os.path.realpath(__file__))
# os.chdir(os.path.join(os.sep.join(dir_path.split(os.sep)[0:-1])))
# print("Working directory: %s" % os.getcwd())
from codes.src.comparison.Comparison import Comparison
from codes.src.connection.PostgresServiceProvider import PostGISServiceProvider
from codes.src.exceptions import NotParameterGivenException
from codes.src.travelTimeMatrixOperations.SpatialPatterns import SpatialPatterns
from codes.src.util import getConfigurationProperties, Logger, FileActions


def printHelp():
    print(
        "Travel Time Matrix tool\n"
        "\n\t[--help]: Print information about the parameters necessary to run the tool."
        "\n\t[-q, --query]: Execute travel time matrix query function."
        "\n\t[-u, --upload]: Execute travel time matrix data upload function."
        "\n\t"
        "\n\t[-z, --zip]: Zip file path containing the cost summary values."
        "\n\t[-o, --outputFolder]: The output folder to decompress the cost summary geojson files."
        "\n\t"
        "\n\t[-d, --directionality]: Directionality (to or from) to define either the start or end point of the travel matrix."
        "\n\t[-t, --target]: Id of the grid square centroid to retrieve the travel time matrix."
        "\n\t"
        "\n\nDirectionality values allowed:"
        "\n\tTO"
        "\n\tFROM"
    )


def main():
    argv = sys.argv[1:]
    opts, args = getopt.getopt(
        argv, "q:u:z:o:d:t:",
        ["query", "upload", "zip=", "outputFolder=", "directionality=", "target", "help"]
    )

    zippath = None
    outputFolder = None
    uploading = False
    querying = False
    directionality = "TO"
    target = 0

    for opt, arg in opts:
        if opt in "--help":
            printHelp()
            return

        print("options: %s, arg: %s" % (opt, zippath))

        if opt in ("-u", "--upload"):
            uploading = True

        if opt in ("-q", "--query"):
            querying = True

        if opt in ("-z", "--zip"):
            zippath = arg

        if opt in ("-o", "--outputFolder"):
            outputFolder = arg

        if opt in ("-d", "--directionality"):
            directionality = arg

        if opt in ("-t", "--target"):
            target = arg

    if uploading and (not zippath or not outputFolder):
        raise NotParameterGivenException("Type --help for more information.")
    if querying and (not outputFolder or not target):
        raise NotParameterGivenException("Type --help for more information.")

    try:
        comparison = Comparison()
        postGISServiceProvider = PostGISServiceProvider()
        spatialPatterns = SpatialPatterns(comparison=comparison, postGISServiceProvider=postGISServiceProvider)
        fileActions = FileActions()



        log_filename = "travel_time_matrix"
        if uploading:
            log_filename = "uploading_" + os.path.basename(zippath).split(".")[-2]
        if querying:
            log_filename = "querying_travel_time_matrix_%s_%s" % (directionality, target)

        print("LOG_NAME: %s" % log_filename)
        Logger.configureLogger(outputFolder, log_filename)
        Logger.getInstance().info("Welcome to the travel time matrix tool")

        columns = getConfigurationProperties(section="ATTRIBUTES_MAPPING")
        tableName = getConfigurationProperties(section="DATABASE_CONFIG")["travel_time_table_name"]

        if uploading:


            fileActions.decompressZipfile(zippath, outputFolder)

            for root, dirs, files in os.walk(outputFolder):
                for filename in files:
                    if filename.endswith("geojson"):
                        f = os.path.join(root, filename)
                        Logger.getInstance().info("Loading: %s" % filename)

                        isExecuted = spatialPatterns.insertData(f, tableName, columns)
                        if isExecuted:
                            os.remove(f)

            Logger.getInstance().info("Uploaded: %s" % zippath)

        if querying:
            traveltimeMatrixFilename = "travel_time_matrix_%s_%s.geojson" % (directionality, target)

            Logger.getInstance().info("Querying %s: %s" % (directionality, target))
            if "TO".__eq__(directionality):
                geodataframe = postGISServiceProvider.getTravelTimeMatrixTo(
                    ykrid=target,
                    tableName=tableName
                )
            else:
                geodataframe = postGISServiceProvider.getTravelTimeMatrixFrom(
                    ykrid=target,
                    tableName=tableName
                )

            geojson = postGISServiceProvider.convertToGeojson(geodataframe)

            fileActions.writeFile(folderPath=outputFolder, filename=traveltimeMatrixFilename, data=geojson)
            Logger.getInstance().info("Find the the travel time matrix geojson file in this path: %s"
                                    % (os.path.join(outputFolder, traveltimeMatrixFilename)))

    except Exception as err:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        Logger.getInstance().exception(''.join('>> ' + line for line in lines))
