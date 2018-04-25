import configparser
import datetime
import json
import logging
import logging.config
import os
import shutil
import time
import zipfile

import geopandas as gpd

from codes.src import exceptions


def enum(**enums):
    return type('Enum', (), enums)


carRountingDictionary = {
    "pituus": "distance",
    "digiroa_aa": "speed_limit_time",
    "kokopva_aa": "day_average_delay_time",
    "keskpva_aa": "midday_delay_time",
    "ruuhka_aa": "rush_hour_delay_time"
}

CostAttributes = enum(DISTANCE='pituus', SPEED_LIMIT_TIME='digiroa_aa', DAY_AVG_DELAY_TIME='kokopva_aa',
                      MIDDAY_DELAY_TIME='keskpva_aa', RUSH_HOUR_DELAY='ruuhka_aa')

GeometryType = enum(POINT="Point", MULTI_POINT='MultiPoint', LINE_STRING='LineString', POLYGON="Polygon")

PostfixAttribute = enum(EUCLIDEAN_DISTANCE="EuclideanDistance", AVG_WALKING_DISTANCE="AVGWalkingDistance",
                        WALKING_TIME="WalkingTime", PARKING_TIME="ParkingTime")

GPD_CRS = enum(WGS_84={'init': 'epsg:4326'}, PSEUDO_MERCATOR={'init': 'epsg:3857'})


def getEnglishMeaning(cost_attribute=None):
    return carRountingDictionary[cost_attribute]


def getFormattedDatetime(timemilis=time.time(), format='%Y-%m-%d %H:%M:%S'):
    formattedDatetime = datetime.datetime.fromtimestamp(timemilis).strftime(format)
    return formattedDatetime


def timeDifference(startTime, endTime):
    totalTime = (endTime - startTime) / 60  # min
    return totalTime


def getConfigurationProperties(section="WFS_CONFIG"):
    config = configparser.ConfigParser()
    configurationPath = os.getcwd() + "%codes%resources%configuration.properties".replace("%", os.sep)
    config.read(configurationPath)
    return config[section]


def extractCRS(geojson):
    epsgCode = geojson["crs"]["properties"]["name"].split(":")[-3] + ":" + \
               geojson["crs"]["properties"]["name"].split(":")[-1]
    return epsgCode


def extractCRSFromDataframe(dataframe):
    return dataframe.crs["init"].split(":")[1]


def dgl_timer(func):
    def func_wrapper(*args, **kwargs):
        timerEnabled = "True".__eq__(getConfigurationProperties(section="WFS_CONFIG")["timerEnabled"])
        if timerEnabled:
            functionName = func.__name__
            startTime = time.time()
            Logger.getInstance().info("%s Start Time: %s" % (functionName, getFormattedDatetime(timemilis=startTime)))

            ###############################
            returns = func(*args, **kwargs)
            ###############################

            endTime = time.time()
            Logger.getInstance().info("%s End Time: %s" % (functionName, getFormattedDatetime(timemilis=endTime)))

            totalTime = timeDifference(startTime, endTime)
            Logger.getInstance().info("%s Total Time: %s m" % (functionName, totalTime))

            return returns
        else:
            return func(*args, **kwargs)

    return func_wrapper


class AbstractLinkedList(object):
    def __init__(self):
        self._next = None

    def hasNext(self):
        return self._next is not None

    def next(self):
        self._next

    def setNext(self, next):
        self._next = next


class Node:
    def __init__(self, item):
        """
        A node contains an item and a possible next node.
        :param item: The referenced item.
        """
        self._item = item
        self._next = None

    def getItem(self):
        return self._item

    def setItem(self, item):
        self._item = item

    def getNext(self):
        return self._next

    def setNext(self, next):
        self._next = next


class LinkedList(AbstractLinkedList):
    def __init__(self):
        """
        Linked List implementation.

        The _head is the first node in the linked list.
        _next refers to the possible next node into the linked list.
        And the _tail is the last node added into the linked list.
        """
        self._head = None
        self._next = None
        self._tail = None

    def hasNext(self):
        """
        Veryfy if there is a possible next node in the queue of the linked list.

        :return: True if there is a next node.
        """
        if self._next:
            return True

        return False

    def next(self):
        """
        :return: The next available item in the queue of the linked list.
        """
        item = self._next.getItem()
        self._next = self._next.getNext()
        return item

    def add(self, newItem):
        """
        Add new items into the linked list. The _tail is moving forward and create a new node ecah time that a new item
        is added.

        :param newItem: Item to be added.
        """
        if self._head is None:
            self._head = Node(newItem)
            self._next = self._head
            self._tail = self._head
        else:
            node = Node(newItem)
            self._tail.setNext(node)
            self._tail = node

    def restart(self):
        """
        Move the linked list to its initial node.
        """
        self._next = self._head
        self._tail = self._head


class FileActions:
    def readJson(self, url):
        """
        Read a json file
        :param url: URL for the Json file
        :return: json dictionary data
        """
        with open(url) as f:
            data = json.load(f)
        return data

    def readMultiPointJson(self, url):
        """
        Read a MultiPoint geometry geojson file, in case the file do not be a MultiPoint
        geometry, then an NotMultiPointGeometryException is thrown.

        :param url: URL for the Json file
        :return: json dictionary data
        """
        data = None
        with open(url) as f:
            data = json.load(f)

        self.checkGeometry(data, GeometryType.MULTI_POINT)

        return data

    def readPointJson(self, url):
        """
        Read a MultiPoint geometry geojson file, in case the file do not be a MultiPoint
        geometry, then an NotMultiPointGeometryException is thrown.

        :param url: URL for the Json file
        :return: json dictionary data
        """
        data = None
        with open(url) as f:
            data = json.load(f)

        self.checkGeometry(data, GeometryType.POINT)

        return data

    def checkGeometry(self, data, geometryType=GeometryType.MULTI_POINT):
        """
        Check the content of the Json to verify if it is a specific geoemtry type. By default is MultiPoint.
        In case the geojson do not be the given geometry type then an

        :param data: json dictionary
        :param geometryType: Geometry type (i.e. MultiPoint, LineString)
        :return: None
        """
        for feature in data["features"]:
            if feature["geometry"]["type"] != geometryType:
                raise exceptions.IncorrectGeometryTypeException("Expected %s" % geometryType)

    def writeFile(self, folderPath, filename, data):
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        fileURL = folderPath + "/%s" % filename

        with open(fileURL, 'w+') as outfile:
            json.dump(data, outfile, sort_keys=True)

    def createFile(self, folderPath, filename):
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        with open(folderPath + os.sep + filename, 'w+') as outfile:
            outfile.close()

    def decompressOutputFile(self, zippath, outputFolder):
        zip_ref = zipfile.ZipFile(zippath, 'r')
        zip_ref.extractall(outputFolder)
        zip_ref.close()

    def deleteFolder(self, path):
        print("Deleting FOLDER %s" % path)
        if os.path.exists(path):
            shutil.rmtree(path)
        print("The FOLDER %s was deleted" % path)

    def readShapefile(self, url):
        dataframe = gpd.read_file(url)

    def convertDataFrameToGeojson(self, dataframe):
        jsonResult = dataframe.to_json()
        crs = dataframe.crs
        newJson = json.loads(jsonResult)
        newJson["crs"] = {
            "properties": {
                "name": "urn:ogc:def:crs:%s" % (crs["init"].replace(":", "::"))
            },
            "type": "name"
        }
        return newJson

    @dgl_timer
    def decompressZipfile(self, zippath, outputFolder):
        zip_ref = zipfile.ZipFile(zippath, 'r')
        zip_ref.extractall(outputFolder)
        zip_ref.close()


class Logger:
    __instance = None

    def __init__(self):
        raise Exception("Instances must be constructed with Logger.getInstance()")

    @staticmethod
    def configureLogger(outputFolder, prefix):
        Logger.__instance = None

        log_filename = prefix + "_log - %s.log" % getFormattedDatetime(timemilis=time.time(),
                                                                       format='%Y-%m-%d %H_%M_%S')
        logs_folder = outputFolder + os.sep + "logs"

        FileActions().createFile(logs_folder, log_filename)
        fileHandler = logging.FileHandler(logs_folder + os.sep + log_filename, 'w')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fileHandler.setFormatter(formatter)
        Logger.getInstance().addHandler(fileHandler)

    @staticmethod
    def getInstance():
        if not Logger.__instance:
            configurationPath = os.getcwd() + "%codes%resources%logging.properties".replace("%", os.sep)

            logging.config.fileConfig(configurationPath)

            # create logger
            Logger.__instance = logging.getLogger("CARDAT")
        # "application" code
        # Logger.instance.debug("debug message")
        # Logger.instance.info("info message")
        # Logger.instance.warn("warn message")
        # Logger.instance.error("error message")
        # Logger.instance.critical("critical message")
        return Logger.__instance