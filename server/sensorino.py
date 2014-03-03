#!/usr/bin/python3
import logging
import sqlite3
import datetime
import json
import serialEngine

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
        self.sensorinos=[]
        self.loadSensorinos()

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
            self.addSensorino(Sensorino( row["name"], row["address"], 
                     row["description"], row["owner"], row["location"], row["sid"]))
                     #row["description"], row["owner"], Location(row["location"])))

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
        print(sid)
        status=c.execute("SELECT * FROM services WHERE sid=:sid ",   {"sid": sid})

        rows = c.fetchall()
        conn.commit()

        return rows
 

    # the core should read serial port and generate events
    def onDataLog(self, sid, serviceId, data):
        sens=findSensorino(sid)
        if (sens==None):
            logger.warn("logging data from unknown sensorino is not allowed (yet)")
            return
        service=sens.getService(serviceId)
        if (service==None):
            logger.warn("logging data from unknown sensorino is not allowed (yet)")
            return
        return service.logData(data)


    def start(self):
        serial=SerialEngine()
        serial.start()

    def processMessage(self, message):
        if (message["command"] == "publishData"):
            sens=self.findSensorino(address=message['srcAddress'])
            if (sens==None):
                logger.error("received message from unknown sensorino")
            else:
                self.onDataLog(sens.sid, message["srcService"], message["data"])


class SerialGenerator:

    def generatePublish():
        return '{ "srcAddress": "123", "srcService": "temp1", "command": "publishData", "data": "12.6"}'

    
    



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

    def getService(self, serviceId):
        for service in services:
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
        return status

    def deleteFromDb(self):
        global dbPath
        conn = sqlite3.connect(dbPath)
        c = conn.cursor()
        status=c.execute("DELETE FROM sensorinos WHERE sid=? ",( self.sid))
        conn.commit()
        return status

        

class Device:
    def __init__(self, name, did, location):
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
    def __init__(self, name, did, location, dataType):
        Device.__init__( self, name, did, location)
        self.type="data"
        self.dataType=dataType

    def toData(self):
        data=super(Device, self).toData()
        data['dataType']=self.dataType
        return data

class ActuatorDevice(Device):
    def __init__(self, name, did, location, actuatorType):
        Device.__init__(self, name, did, location)
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
    def setSensorino(self, sid):
        self.sid=sid
    def persist(self):
        if (self.sid==None):
            raise(Exception("Can't persist orphan service"))
    

class DataService(Service):
    def __init__(self, name, serviceId, device):
        Service.__init__( self, name, serviceId)
        self.device=device
        self.stype="DATA"

    def saveToDb(self):
        if (self.sid==None):
            logger.critical("unable to save service without sensorino")
            return None
        if (self.sid==None):
            logger.debug("INSERT service")
            c.execute("INSERT INTO services ( name, stype, sid)  VALUES (?,?,?)", (self.serviceId, self.name, self.stype, self.sid))
        else:
            logger.debug("UPDATE service")
            c.execute("UPDATE services SET stype=:stype WHERE  sid=:sid AND serviceId=:serviceId LIMIT 1",
                 self.toData())

        conn.commit()
        
    def deleteFromDb(self):
        conn = sqlite3.connect(dbPath)
        c = conn.cursor()
        logger.debug("DELETE service")
        status=c.execute("DELETE FROM services WHERE sid=:sid AND serviceId=:serviceId LIMIT 1")
        conn.commit()

    def logData(self, value):
        conn = sqlite3.connect(dbPath)
        c = conn.cursor()
        logger.debug("Log data on sensorino"+str(self.sid)+" service: "+self.name+" data:"+value)

        status=c.execute("INSERT INTO dataServicesLog (sid, serviceId, value, timestamp) VALUES (?,?,?,?) ",
                 (str(self.sid), self.serviceId, value, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return status

    def toData(self):
        return {
            'name': self.name,
            'serviceId' : self.serviceId,
            'device' : self.device.toData()
        } 

    
    


