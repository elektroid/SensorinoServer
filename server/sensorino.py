#!/usr/bin/python3
import logging
import threading
import sqlite3
import mosquitto
import datetime
import json
import ConfigParser

# create logger with 'spam_application'
logger = logging.getLogger('sensorino_application')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

dbPath="db/example.db"

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Core:
    def __init__(self):
        self.readConfig()
        self.sensorinos=[]
        self.loadSensorinos()
        self.mqttClient = self._createMqttClient()

    def readConfig(self, filename="sensorino.ini"):
        self.config = ConfigParser.ConfigParser()
        self.config.read(filename)


    def _createMqttClient(self):
        def mqtt_on_connect(mosq, obj, rc):
            mqttc.subscribe("sensorino", 0)
            mqttc.publish("sensorino", "heuu", 0)
            print("rc: "+str(rc))

        def mqtt_on_message(mosq, obj, msg):
            print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

        def mqtt_on_publish(mosq, obj, mid):
            print("mid: "+str(mid))

        def mqtt_on_subscribe(mosq, obj, mid, granted_qos):
            print("Subscribed: "+str(mid)+" "+str(granted_qos))

        def mqtt_on_log(mosq, obj, level, string):
            print(string)

        mqttc=mosquitto.Mosquitto()
        mqttc.on_message = mqtt_on_message
        mqttc.on_connect = mqtt_on_connect
        mqttc.on_publish = mqtt_on_publish
        mqttc.on_subscribe = mqtt_on_subscribe
        # Uncomment to enable debug messages
        #mqttc.on_log = on_log
        mqttc.connect(self.config.get("Mqtt", "ServerAddress"), 1883, 60)
        
        return mqttc


    def getSensorinos(self):
        return self.sensorinos

    def loadSensorinos(self):
        global dbPath
        conn = sqlite3.connect(dbPath)
        conn.row_factory = dict_factory
        c = conn.cursor()

        c.execute("SELECT * from sensorinos")
        rows = c.fetchall()

        for row in rows:
            sens=Sensorino( row["name"], row["address"], row["description"], row["owner"], row["location"], row["sid"])
                     #row["description"], row["owner"], Location(row["location"])))
            self.addSensorino(sens)
            servicesRows=self.getServicesBySensorino(sens.sid)
            for srow in servicesRows:
                sens.registerService(DataService(srow['name'], srow['dataType'], sens.sid, srow['serviceId']))

    def addSensorino(self, sensorino):
        if (sensorino in self.sensorinos):
            logger.debug("not adding sensorino, already present")
            return None
        for sens in self.sensorinos:
            if (sens.sid == sensorino.sid and sens.address==sensorino.address):
                logger.warn("unable to add your sensorino")
                return None
        return self.sensorinos.append(sensorino)

    def delSensorino(self, sid):
        s = self.findSensorino(sid=sid)
        if s == None:
            logger.debug("not deleting sensorino as already missing")
            return True
        else:
            self.sensorinos.remove(s)

    def findSensorino(self, sid=None, address=None):
        for sens in self.sensorinos:
            if ((sid!=None and sens.sid == sid) or(address!=None and sens.address==address)):
                return sens
        return None

    def getServicesBySensorino(self, sid):
        global dbPath
        conn = sqlite3.connect(dbPath)
        conn.row_factory = dict_factory
        c = conn.cursor()
        status=c.execute("SELECT * FROM services WHERE sid=:sid ",   {"sid": sid})

        rows = c.fetchall()
        conn.commit()

        return rows

    # TODO generate exception on failures, this will allow rest server to translate them into http status

    # the core should read serial port and generate events
    def publish(self, sid, serviceId, data):
        sens=findSensorino(sid)
        if (sens==None):
            logger.warn("logging data from unknown sensorino is not allowed (yet)")
            return 
        service=sens.getService(serviceId)
        if (service==None):
            logger.warn("logging data from unknown sensorino is not allowed (yet)")
            return
        return service.logData(data)

    def onSetState(self, sid, serviceId, sensorinoAddress, state):
        self.mqttClient.publish("commands",  { "set" : {"address":sensorinoAddress, "serviceID":}        



class Sensorino:
    def __init__(self, name, address, description="yet another node", owner="default", location="unknown", sid=None):
        self.sid=sid
        self.name=name
        self.address=address
        self.description=description
        self.services=[]
        self.owner=owner
        self.location=location
        self._alive=None

    def registerService(self, service):
        if (self.getService(service.serviceId)==None):
            self.services.append(service)

    def removeService(self, serviceId):
        for service in self.services:
            if (service.serviceId == serviceId):
                self.remove(service)
                break


    def getService(self, serviceId):
        for service in self.services:
            if service.serviceId==serviceId:
                return service
        return None


    def toData(self):
        return {
            'name': self.name,
            'sid': self.sid,
            'name': self.name,
            'address': self.address,
            'description': self.description,
            'owner': self.owner,
            'location': self.location
        }

    def saveToDb(self):
        logger.debug("insert/update sensorino in db")
        status=None
        try:
            global dbPath
            conn = sqlite3.connect(dbPath)
            c = conn.cursor()
            status=None
            if (self.sid==None):
                logger.debug("insert")
                status=c.execute("INSERT INTO sensorinos ( name, address, description, owner, location) VALUES (?,?,?,?,?) ",(  self.name, self.address, self.description, self.owner, self.location))
                self.sid=c.lastrowid
            else:
                status=c.execute("UPDATE sensorinos SET name=:name, address=:address, description=:description, owner=:owner, location=:location WHERE sid=:sid", self.toData())
            conn.commit()
        except Exception as e:
            print(e)
            # Roll back any change if something goes wrong
            conn.rollback()
        return status

    def deleteFromDb(self):
        status=None
        try:
            global dbPath
            conn = sqlite3.connect(dbPath)
            c = conn.cursor()
            status=c.execute("DELETE FROM sensorinos WHERE sid=? ",( self.sid))
            conn.commit()
        except Exception as e:
            print(e)
            # Roll back any change if something goes wrong
            conn.rollback()

        return status



class Device:
    def __init__(self, name, location, did):
        self.name=name
        self.did=did
        self.location=location
        self.type=None

    def toData(self):
        return {
            'name': self.name,
            'did': self.did,
            'location': self.location.toData(),
            'type': self.type
        }


class DataDevice(Device):
    def __init__(self, name, dataType, location=None, did=None):
        Device.__init__( self, name, location, did)
        self.type="data"
        self.dataType=dataType

    def toData(self):
        data=super(Device, self).toData()
        data['dataType']=self.dataType
        return data

class ActuatorDevice(Device):
    def __init__(self, name, did, location, actuatorType):
        Device.__init__(self, name, location, did)
        self.type="action"
        self.actuatorType=actuatorType


class Location:
    def __init__(self, name, position="DEFAULT"):
        self.name=name
        self.position=position

    def toData(self):
        return {
            'name': self.name,
            #'position': self.position.toData(),
            'position': self.position,
        }

class Position:
    def __init__(self, name):
        self.name=name

    def toData(self):
        return {
            'name': self.name
        }


# Services can be linked to a sensor, an actuator or be a network protocol handler (Ping?)

class Service():
    def __init__(self, name, serviceId):
        self.name=name
        self.serviceId=serviceId
        self.sid=None
        self.stype=None

    def setSensorino(self, s):
        self.sid=s.sid

    def persist(self):
        if (self.sid==None):
            raise(Exception("Can't persist orphan service"))

    def saveToDb(self):
        if (self.sid==None):
            logger.critical("unable to save service without sensorino")
            return None

        try:
            global dbPath
            conn = sqlite3.connect(dbPath)
            c = conn.cursor()
            status=None
            if (self.serviceId==None):
                logger.debug("INSERT service")
                status=c.execute("INSERT INTO services ( name, stype, dataType, sid)  VALUES (?,?,?,?)",
                    ( self.name, self.stype, self.dataType, self.sid))
                self.serviceId=c.lastrowid
            else:
                logger.debug("UPDATE service")
                status=c.execute("UPDATE services SET stype=:stype WHERE sid=:sid AND serviceId=:serviceId LIMIT 1",
                     self.toData())
            conn.commit()
        except Exception as e:
            print(e)
            # Roll back any change if something goes wrong
            conn.rollback()

        return status

    def deleteFromDb(self):

        status=None
        try:
            global dbPath
            conn = sqlite3.connect(dbPath)
            c = conn.cursor()
            logger.debug("DELETE service")
            status=c.execute("DELETE FROM services WHERE sid=:sid AND serviceId=:serviceId LIMIT 1", self.toData())
            conn.commit()
        except Exception as e:
            print(e)
            # Roll back any change if something goes wrong
            conn.rollback()
        return status

    def toData(self):
        return {
            'name': self.name,
            'serviceId' : self.serviceId,
            'sid': self.sid,
            'dataType' : self.dataType,
            'stype' : self.stype
        }




class DataService(Service):
    def __init__(self, name, dataType, sid, serviceId=None):
        Service.__init__( self, name, serviceId)
        self.dataType=dataType
        self.sid=sid
        self.stype="DATA"

    def logData(self, value):
        status=None
        try:
            global dbPath
            conn = sqlite3.connect(dbPath)
            c = conn.cursor()
            logger.debug("Log data on sensorino"+str(self.sid)+" service: "+self.name+" data:"+value)

            status=c.execute("INSERT INTO dataServicesLog (sid, serviceId, value, timestamp) VALUES (?,?,?,?) ",
                     (str(self.sid), self.serviceId, value, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
        except Exception as e:
            print(e)
            # Roll back any change if something goes wrong
            conn.rollback()
        return status

    def getLogs(self, sid):
        global dbPath
        conn = sqlite3.connect(dbPath)
        conn.row_factory = dict_factory
        c = conn.cursor()

        c.execute("SELECT value, timestamp FROM dataServicesLog WHERE serviceId=:serviceId AND sid=:sid", self.toData())
        rows = c.fetchall()
        return rows



class ActuatorService(Service):

    def __init__(self, name, dataType, sid, serviceId=None):
        Service.__init__( self, name, serviceId)
        self.dataType=dataType
        self.sid=sid
        self.stype="ACTUATOR"

    def setState(self, state):
        self.state=state

