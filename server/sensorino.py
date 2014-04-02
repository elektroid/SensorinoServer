#!/usr/bin/python3
import logging
import threading
import sqlite3
import mosquitto
import datetime
import json
import common

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

    def loadServices(self):
        for service in Service.getServicesBySensorino(sid=self.sid):
            self.registerService(service) 
 

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
            conn = sqlite3.connect(common.Config.getDbFilename())
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
            conn = sqlite3.connect(common.Config.getDbFilename())
            c = conn.cursor()
            status=c.execute("DELETE FROM sensorinos WHERE sid=? ",( self.sid))
            conn.commit()
        except Exception as e:
            print(e)
            # Roll back any change if something goes wrong
            conn.rollback()

        return status

    @staticmethod
    def loadAllSensorinos(loadServices=False):

        sensorinos=[]

        conn = sqlite3.connect(common.Config.getDbFilename())
        conn.row_factory = common.dict_factory
        c = conn.cursor()

        c.execute("SELECT * from sensorinos")
        rows = c.fetchall()

        for row in rows:
            sens=Sensorino( row["name"], row["address"], row["description"], row["owner"], row["location"], row["sid"])
            sensorinos.append(sens)
            if(loadServices):
                sens.loadServices()

        return sensorinos
            



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
            conn = sqlite3.connect(common.Config.getDbFilename())
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
            conn = sqlite3.connect(common.Config.getDbFilename())
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

    @staticmethod
    def getServicesBySensorino(sid):
        conn = sqlite3.connect(common.Config.getDbFilename())
        conn.row_factory = common.dict_factory
        c = conn.cursor()
        status=c.execute("SELECT * FROM services WHERE sid=:sid ",   {"sid": sid})

        rows = c.fetchall()
        conn.commit()

        services=[]
        for srow in rows:
            service=None
            if("DATA" == srow["stype"]):
                service=DataService(srow['name'], srow['dataType'], sens.sid, srow['serviceId'])
            elif("ACTUATOR" == srow["stype"]):
                service=ActuatorService(srow['name'], srow['dataType'], sens.sid, srow['serviceId'])
            if(None==service):
                logger.error("failed to load service for sensorino :"+srow)
            else:
                services.append(service)

        return services




class DataService(Service):
    def __init__(self, name, dataType, sid, serviceId=None):
        Service.__init__( self, name, serviceId)
        self.dataType=dataType
        self.sid=sid
        self.stype="DATA"

    def logData(self, value):
        status=None
        try:
            conn = sqlite3.connect(common.Config.getDbFilename())
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
        conn = sqlite3.connect(common.Config.getDbFilename())
        conn.row_factory = common.dict_factory
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

