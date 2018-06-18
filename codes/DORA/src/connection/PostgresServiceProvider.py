import json

import geopandas as gpd
import psycopg2
from joblib import Parallel, delayed
from psycopg2.extensions import register_adapter
from shapely.geometry import LineString, Point, Polygon
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

from codes.src.util import getConfigurationProperties, extractCRSFromDataframe, GPD_CRS, GeometryType, dgl_timer
from codes.src.geometries.adapters import Adapters


def verifyPairOfPointsExistence(self, ykr_from_id, ykr_to_id, sql):
    geoDataFrame = self.executePostgisQuery(sql % (ykr_from_id, ykr_to_id))
    if len(geoDataFrame) > 0:
        self.travelTimeMatrixCopy = self.travelTimeMatrixCopy[
            ~(
                (self.travelTimeMatrixCopy.ykr_from_id == ykr_from_id) &
                (self.travelTimeMatrixCopy.ykr_to_id == ykr_to_id)
            )
        ]
    return self.travelTimeMatrixCopy


class PostGISServiceProvider(object):
    # engine = create_engine('postgresql://<yourUserName>:postgres@localhost:5432/postgres', echo=False)
    # Session = sessionmaker(bind=engine)
    # session = Session()
    # meta = MetaData(engine, schema='cldmatchup')
    def __init__(self):
        self.__engine = None

    def getConnection(self):
        """
        Creates a new connection to the pg_database

        :return: New connection.
        """
        config = getConfigurationProperties(section="DATABASE_CONFIG")
        con = psycopg2.connect(database=config["database_name"], user=config["user"], password=config["password"],
                               host=config["host"])
        return con

    def getEngine(self):
        if not self.__engine:
            config = getConfigurationProperties(section="DATABASE_CONFIG")
            # engine = create_engine('postgresql://<yourUserName>:postgres@localhost:5432/postgres', echo=False)
            self.__engine = create_engine(
                'postgresql://%s:%s@%s/%s' % (
                    config["user"], config["password"], config["host"], config["database_name"]),
                echo=False
            )

        return self.__engine

    def executePostgisQuery(self, sql):
        """
        Given a PG_SQL execute the query and retrieve the attributes and its respective geometries.

        :param sql: Postgis SQL sentence.
        :return: Sentence query results.
        """

        con = self.getConnection()

        try:
            geoDataFrame = gpd.GeoDataFrame.from_postgis(sql, con, geom_col='geometry', crs=GPD_CRS.PSEUDO_MERCATOR)
        finally:
            con.close()

        return geoDataFrame

    def insertableTravelTimeMatrixGeoDataFrame(self, travelTimeMatrix, tableName, column1, column2):

        sql = "select * from %s where %s = %s and %s = %s" % (tableName, column1, "%s", column2, "%s")

        self.travelTimeMatrixCopy = travelTimeMatrix.copy()

        ################################################################################################################
        # for index, row in travelTimeMatrix.iterrows():
        #     travelTimeMatrixCopy = verifyPairOfPointsExistence(row, sql, travelTimeMatrixCopy)
        ################################################################################################################

        with Parallel(n_jobs=int(getConfigurationProperties(section="PARALLELIZATION")["jobs"]),
                      backend="threading",
                      verbose=int(getConfigurationProperties(section="PARALLELIZATION")["verbose"])) as parallel:
            returns = parallel(
                delayed(verifyPairOfPointsExistence)(self, row[column1], row[column2], sql) for index, row in
                travelTimeMatrix.iterrows())

        return self.travelTimeMatrixCopy

    @dgl_timer
    def insert(self, dataFrame, tableName, isTableExist="append", geometryType=GeometryType.LINE_STRING):
        """
        Insert each dataframe row data into the given table name. Parse all the dataframe columns name into the given in the dictionary 'columns' if any.

        :param dataFrame: geoDataframe
        :param tableName: Table name with defined 'geometry' column
        :param isTableExist: {'fail', 'replace', 'append'}, default 'fail'
            - fail: If table exists, do nothing.
            - replace: If table exists, drop it, recreate it, and insert data.
            - append: If table exists, insert data. Create if does not exist.
        :return: True if the statement was executed.
        """
        try:
            Session = sessionmaker(bind=self.getEngine())
            session = Session()

            crs = extractCRSFromDataframe(dataFrame)
            adapters = Adapters(crs=crs)

            if geometryType == GeometryType.POINT:
                register_adapter(Point, adapters.adaptPoint)
            elif geometryType == GeometryType.LINE_STRING:
                register_adapter(LineString, adapters.adaptLineStringToLastPoint)
            elif geometryType == GeometryType.POLYGON:
                register_adapter(Polygon, adapters.adaptPolygon)

            schema = 'public'
            meta = MetaData(self.__engine, schema=schema)

            travelTimeMatrixTable = Table(tableName, meta, autoload=True, schema=schema, autoload_with=self.getEngine())
            dataFrame.to_sql(
                travelTimeMatrixTable.name,
                self.getEngine(),
                if_exists=isTableExist,
                schema=schema,
                index=False
            )
        finally:
            session.close()

        return True

    @dgl_timer
    def copyData(self, csvData, tableName, columns, separator=';'):
        try:
            connection = self.getConnection()
            cursor = connection.cursor()
            cursor.copy_from(csvData, tableName, sep=separator, null='-1', columns=tuple(columns))
            connection.commit()
        except Exception as err:
            connection.rollback()
            raise err
        finally:
            connection.close()

        return True

    @dgl_timer
    def renameColumnsAndExtractSubSet(self, travelTimeMatrix, columns, geometryColumn="geometry"):
        if columns:
            keys = [key for key in columns]

            # keys.append(geometryColumn) # the geometry is removed, it will be used the join with the grid centroid table

            travelTimeMatrix = travelTimeMatrix[keys]
            travelTimeMatrix = travelTimeMatrix.rename(index=str, columns=columns)
        return travelTimeMatrix

    @dgl_timer
    def getTravelTimeMatrixTo(self, ykrid, tableName):
        sql = "SELECT matrix.ykr_from_id, matrix.ykr_to_id, matrix.travel_time, grid.geometry " \
              "FROM %s AS matrix " \
              "INNER JOIN ykr_gridcells AS grid ON grid.ykr_id = matrix.ykr_from_id " \
              "AND matrix.ykr_to_id = %s " \
              "ORDER BY matrix.travel_time ASC " % (tableName, ykrid)
        return self.executePostgisQuery(sql)

    @dgl_timer
    def getTravelTimeMatrixFrom(self, ykrid, tableName):
        sql = "SELECT matrix.ykr_from_id, matrix.ykr_to_id, matrix.travel_time, grid.geometry " \
              "FROM %s AS matrix " \
              "INNER JOIN ykr_gridcells AS grid ON grid.ykr_id = matrix.ykr_to_id " \
              "AND matrix.ykr_from_id = %s " \
              "ORDER BY matrix.travel_time ASC " % (tableName, ykrid)
        return self.executePostgisQuery(sql)

    def getTravelTimeMatrixDifferences(self, ykrid, tableName):
        # sql = "select * from %s where %s = %s" % (tableName, column, ykrid)
        sql = "SELECT matrix.ykr_from_id, matrix.ykr_to_id, matrix.travel_time, matrix.travel_time_difference, grid.geometry " \
              "FROM %s AS matrix " \
              "INNER JOIN ykr_gridcells AS grid ON grid.ykr_id = matrix.ykr_to_id " \
              "AND matrix.ykr_from_id = %s " \
              "ORDER BY matrix.travel_time ASC " % (tableName, ykrid)
        return self.executePostgisQuery(sql)

    @dgl_timer
    def convertToGeojson(self, dataframe):
        jsonResult = dataframe.to_json()
        newJson = json.loads(jsonResult)
        newJson["crs"] = {
            "properties": {
                "name": "urn:ogc:def:crs:%s" % (GPD_CRS.PSEUDO_MERCATOR["init"].replace(":", "::"))
            },
            "type": "name"
        }
        return newJson
