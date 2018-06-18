from psycopg2._psycopg import adapt, AsIs
from shapely.geometry import Point


class Adapters:
    def __init__(self, crs):
        self.crs = crs

    def adaptPoint(self, point):
        return AsIs("ST_GeomFromText('%s', %s)" % (point.wkt, self.crs))

    def adaptLineString(self, line, hasQuotation=True):
        # lineStringCoordinates = [self.adaptPoint(Point(xy), hasQuotation=False) for xy in line.coords]  # xy is a tuple (x, y)

        return AsIs("ST_GeomFromText('%s', %s)" % (line.wkt, self.crs))  # ",".join(lineStringCoordinates))

        # return AsIs("ST_GeomFromText('%s', %s)" % (line.wkt, self.crs))  # ",".join(lineStringCoordinates))
        # return self.adaptPoint(endPoint)

    def adaptLineStringToLastPoint(self, line, hasQuotation=True):
        longitude = line.coords.xy[0][1]
        latitude = line.coords.xy[1][1]
        endPoint = Point(longitude, latitude)

        return self.adaptPoint(endPoint)

    def adaptPolygon(self, polygon):
        return AsIs("ST_GeomFromText('%s', %s)" % (polygon.wkt, self.crs))  # ",".join(lineStringCoordinates))
