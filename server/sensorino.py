#!/usr/bin/python3
import logging
import sqlite3
import datetime
import json

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
		self.sensorinos=()

	@staticmethod
	def getSensorinos():
		global dbPath
		conn = sqlite3.connect(dbPath)
		conn.row_factory = dict_factory
		c = conn.cursor()
		
		c.execute("SELECT * from sensorinos")
		rows = c.fetchall()
		return rows


	def loadSensorinos(self):
		for row in Core.getSensorinos():
			print(row)
			self.addSensorino(Sensorino(row["sid"], row["name"], row["address"],
					 row["description"], row["owner"], Location(row["location"])))

	def loadSensorino(self, sid):
		global dbPath
		conn = sqlite3.connect(dbPath)
		conn.row_factory = dict_factory
		c = conn.cursor()
		status=c.execute("SELECT * FROM sensorinos WHERE sid=? ",( sid))
		rows = c.fetchall()
		conn.commit()

		if (len(rows)!=1):
			return None
		row=rows[0]
		return Sensorino(row["sid"], row["name"], row["address"],
					 row["description"], row["owner"], Location(row["location"]))


	def addSensorino(self, sensorino):
		if (sensorino in sensorinos):
			logger.debug("not adding sensorino, already present")
			return None
		for sens in self.sensorinos:
			if (sens.sid == sensorino.sid and sens.address==sensorino.address):
				logger.warn("unable to add your server")
				raise Exception("address/id collision")
		
		logger.debug("insert sensorino")
		return self.sensorinos.append(sensorino)			

	def delSensorino(self, sid):
		global dbPath
		conn = sqlite3.connect(dbPath)
		c = conn.cursor()
		status=c.execute("DELETE FROM sensorinos WHERE sid=? ",( self.sid))
		conn.commit()

		return status



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

	def findSensorino(self, sid=None, address=None):
		for sens in self.sensorinos:
			if ((sid!=None and sens.sid == sid) or(address!=None and sens.address==address)):
				return sens
		return None

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

	
	

class SerialEngine:

	linuxPossibleSerialPorts=['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2',
	'/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3',
	'/dev/ttyS0','/dev/ttyS1',
	'/dev/ttyS2','/dev/ttyS3'] # TODO : complete list

	windowsPossibleSerialPorts=['COM1', 'COM2', 'COM3', 'COM4'] # TODO : complete list


	def __init__(self, port=None):
		self.port=port
		if (port==None):
			for device in linuxPossibleSerialPorts:
				try:
					port = Serial(device, 9600) 
				except:
					logger.debug("arduino not on "+device);

	def isReady(self):
		return self.port!=None

	def startParsing(self, messageProcessor):
		while True:
			message=parse(port.readline())	
			if (message!=None):
				messageProcessor.processMessage(message)
						

	def parse(line):
		try:
			message=json.loads(line)
			return message
		except:
			logger.error("fail to parse json message")
			return None

				



class Sensorino:
	def __init__(self, sid, name, address, description="yet another node", owner="default", location="unknown"):
		self.sid=sid
		self.name=name
		self.address=address
		self.description=description
		self.services=()
		self.owner=owner
		self.location=location
		self._alive=None

	def registerService(self, service):
		self.services

	def getService(self, serviceId):
		for service in services:
			if service.serviceId==serviceId:
				return service
		return None



	def persist(self):
		global dbPath
		conn = sqlite3.connect(dbPath)
		c = conn.cursor()

		print(self.sid);
		print(self.name);
		print(self.address);
		print(self.description);
		print(self.owner);
		print(self.location);
	
		status=c.execute("INSERT INTO sensorinos (sid, name, address, description, owner, location) VALUES (?,?,?,?,?,?) ",( self.sid, self.name, self.address, self.description, self.owner, self.location))
		conn.commit()

		# should now persist services ?

	# Rest methods			



		

class Device:
	def __init__(self, name, did, location):
		self.name=name
		self.did=did
		self.location=location


class DataDevice(Device):
	def __init__(self, name, did, location, dataType):
		Device.__init__( self, name, did, location)
		self.dataType=dataType

class ActuatorDevice(Device):
	def __init__(self, name, did, location, actuatorType):
		Device.__init__(self, name, did, location)
		self.actuatorType=actuatorType


class Location:
	def __init__(self, name, position="DEFAULT"):
		self.name=name
		self.position=position

class Position:
	def __init__(self, name):
		self.name=name


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

	def persist(self):
		super(DataService, self).persist()
		conn = sqlite3.connect(dbPath)
		c = conn.cursor()
		status=c.execute("SELECT * FROM services WHERE sid=:sid AND serviceId=:serviceId LIMIT 1", {"sid": self.sid, "serviceId": self.serviceId})
		data = c.fetchone()
		if (data==None):
			logger.debug("INSERT service")
			c.execute("INSERT INTO services (serviceId, name, stype, sid)  VALUES (?,?,?,?)", (self.serviceId, self.name, self.stype, self.sid))
		else:
			logger.debug("UPDATE service")
			c.execute("UPDATE services SET stype=:stype WHERE  sid=:sid AND serviceId=:serviceId LIMIT 1",
				 {"sid": self.sid, "serviceId": self.serviceId, "stype":self.stype})

		conn.commit()
		
	def delete(self):
		conn = sqlite3.connect(dbPath)
		c = conn.cursor()
		logger.debug("DELETE service")
		status=c.execute("DELETE FROM services WHERE sid=:sid AND serviceId=:serviceId LIMIT 1")
		conn.commit()

	def logData(self, value):
		conn = sqlite3.connect(dbPath)
		c = conn.cursor()
		logger.debug("Log data on sensoruino"+str(self.sid)+" service: "+self.name+" data:"+value)

		status=c.execute("INSERT INTO dataServicesLog (sid, serviceId, value, timestamp) VALUES (?,?,?,?) ",
				 (str(self.sid), self.serviceId, value, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
		conn.commit()

	

if __name__ == '__main__':

	core=Core()
	core.loadSensorinos()
	
#	sensorino=Sensorino(str(12), "mySensor", "my first node")

#	s=DataService("toto", "sid123", Device("name", "123", Location("kitchen")))
#	s.sid=555
#	s.persist()

	core.processMessage(SerialEngine.parse(SerialGenerator.generatePublish()))


	


