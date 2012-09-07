#!/usr/bin/env python

import sys
import struct
import json
from math import floor
from math import sqrt
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from augustus.core.defs import INVALID, MISSING
import augustus.engine.interface
import augustus.core.pmml41 as pmml

import jpype

def tileIndex(depth, longitude, latitude):
    "Inputs a depth and floating-point longitude and latitude, outputs a triple of index integers."
    if abs(latitude) > 90.: raise ValueError("Latitude cannot be %s" % str(latitude))
    longitude += 180.
    latitude += 90.
    while longitude <= 0.: longitude += 360.
    while longitude > 360.: longitude -= 360.
    longitude = int(floor(longitude/360. * 2**(depth+1)))
    latitude = min(int(floor(latitude/180. * 2**(depth+1))), 2**(depth+1) - 1)
    return depth, longitude, latitude

def tileName(depth, longIndex, latIndex):
    "Inputs an index-triple, outputs a string-valued name for the index."
    return "T%02d-%05d-%05d" % (depth, longIndex, latIndex)  # constant length up to depth 15

def fixedWidthHex(number):
    "Represents an 8-byte signed number as a fixed-width hexidecimal string without a minus sign."
    return "%016x" % struct.unpack("Q", struct.pack("q", hash(number)))[0]

class DataStream(augustus.engine.interface.DataStreamInterface):
    def next(self):
        line = sys.stdin.readline()
        if not line: raise StopIteration

        self.key, value = line.strip().split("\t")

        # ultimately, keys would map to different segments, one reducer per segment
        # for now, there is only one key: world
        if self.key != "world": raise Exception

        longitude, latitude, timestamp, intensity = value.split(" ")
        try:
            self.longitude = float(longitude)
        except ValueError:
            self.longitude = INVALID
        try:
            self.latitude = float(latitude)
        except ValueError:
            self.latitude = INVALID
        try:
            self.timestamp = int(timestamp)
        except ValueError:
            self.timestamp = INVALID
        try:
            self.intensity = float(intensity)
        except ValueError:
            self.intensity = INVALID

    def get(self, fieldName):
        if fieldName == "key": return self.key
        elif fieldName == "longitude": return self.longitude
        elif fieldName == "latitude": return self.latitude
        elif fieldName == "timestamp": return self.timestamp
        elif fieldName == "intensity": return self.intensity
        else: return MISSING

class AugustusInterface(augustus.engine.interface.AugustusInterface):
    def begin(self, context):
        self.timestamps = []

    def action(self, context):
        # only one segment will ever match (even when there are multiple segments)
        if len(context.segments) != 1: raise Exception
        segment = context.segments[0]
        self.producer = segment.producer

        self.timestamps.append(self.dataStream.get("timestamp"))
        segment.update()

    def end(self, context):
        totalNumber = {}
        totalIntensity = {}
        maximumIntensity = {}
        distanceSquared = {}
        weightedDistanceSquared = {}
        timestamp = {}

        for i in xrange(len(self.producer.buffer[self.producer.SYNCNUMBER])):
            vector = [self.producer.buffer[field][i] for field in self.producer.model.fields]
            result = self.producer.model.closestCluster(vector)

            if result is not INVALID:
                clusterId, clusterNumber, clusterAffinity = result

                if clusterId not in totalNumber:
                    totalNumber[clusterId] = 0
                    totalIntensity[clusterId] = 0.
                    maximumIntensity[clusterId] = 0.
                    distanceSquared[clusterId] = 0.
                    weightedDistanceSquared[clusterId] = 0.
                    timestamp[clusterId] = 0

                intensity = self.producer.buffer["superintensity"][i]

                totalNumber[clusterId] += 1
                totalIntensity[clusterId] += intensity
                if intensity > maximumIntensity[clusterId]:
                    maximumIntensity[clusterId] = intensity
                distanceSquared[clusterId] += clusterAffinity**2
                weightedDistanceSquared[clusterId] += intensity * clusterAffinity**2
                if self.timestamps[i] > timestamp[clusterId]:
                    timestamp[clusterId] = self.timestamps[i]

        clusters = self.producer.engine.pmmlModel.matches(pmml.Cluster, maxdepth=None)

        for cluster in clusters:
            if cluster["id"] in totalNumber and totalNumber[cluster["id"]] > 0:
                longitude, latitude = cluster.child(pmml.Array).value
                identifier = hash((int(round(1000.*longitude)), int(round(1000.*latitude))))

                key = "%s-%010d-%s" % (tileName(*tileIndex(10, longitude, latitude)), timestamp[cluster["id"]], fixedWidthHex(identifier))

                metadata = {"PMML id": cluster["id"],
                            "num pixels": totalNumber[cluster["id"]],
                            "total intensity": totalIntensity[cluster["id"]],
                            "max intensity": maximumIntensity[cluster["id"]],
                            "RMS distance": sqrt(distanceSquared[cluster["id"]] / totalNumber[cluster["id"]]),
                            "weighted RMS distance": sqrt(weightedDistanceSquared[cluster["id"]] / totalIntensity[cluster["id"]]),
                            }
                self.outputAccumulo.lnglat_write(key, longitude, latitude, json.dumps(metadata))

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(["../../CONFIG.ini", "CONFIG.ini"])

    JAVA_VIRTUAL_MACHINE = config.get("DEFAULT", "lib.jvm")

    ACCUMULO_INTERFACE = config.get("DEFAULT", "accumulo.interface")
    ACCUMULO_DB_NAME = config.get("DEFAULT", "accumulo.db_name")
    ZOOKEEPER_LIST = config.get("DEFAULT", "accumulo.zookeeper_list")
    ACCUMULO_USER_NAME = config.get("DEFAULT", "accumulo.user_name")
    ACCUMULO_PASSWORD = config.get("DEFAULT", "accumulo.password")
    ACCUMULO_TABLE_NAME = config.get("DEFAULT", "accumulo.points_table_name")

    jpype.startJVM(JAVA_VIRTUAL_MACHINE, "-Djava.class.path=%s" % ACCUMULO_INTERFACE)
    AccumuloInterface = jpype.JClass("org.occ.matsu.AccumuloInterface")

    AccumuloInterface.connectForWriting(ACCUMULO_DB_NAME, ZOOKEEPER_LIST, ACCUMULO_USER_NAME, ACCUMULO_PASSWORD, ACCUMULO_TABLE_NAME)

    configuration = """
    <AugustusConfiguration>
        <Logging level="ERROR"><ToStandardOut/><DifferentLevel stage="produce" level="DEBUG"/></Logging>
        <ModelInput fileLocation="clustering.pmml"></ModelInput>
        <DataInput><Interactive/></DataInput>
        <ModelSetup><ProducerAlgorithm model="ClusteringModel" algorithm="kmeans">
            <Parameter name="numberOfClusters" value="10" />
            <Parameter name="seedSource" value="dataWeighted" />
            <Parameter name="numberOfTrials" value="10" />
            <Parameter name="numberToConverge" value="3" />
            <Parameter name="closeEnough" value="0.00001" />
        </ProducerAlgorithm></ModelSetup>
    </AugustusConfiguration>
    """

    augustusInterface = AugustusInterface(configuration, dataStream=DataStream())

    augustusInterface.outputAccumulo = AccumuloInterface

    augustusInterface.run()

    AccumuloInterface.finishedWriting()
    jpype.shutdownJVM()
