#!/usr/bin/python3
import logging
import threading
import datetime
import ConfigParser
import sensorino
import common
import mqttThread

# create logger with 'spam_application'
logger = logging.getLogger('sensorino_coreEngine')
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



class Core:
    def __init__(self):
        self.sensorinos=[]
        self.loadSensorinos()
        self.mqtt = None


    def getSensorinos(self):
        """return all the sensorinos that are registered"""
        return self.sensorinos

    def loadSensorinos(self):
        """load all sensorinos stored in db """
        for senso in sensorino.Sensorino.loadAllSensorinos():
            self.addSensorino(senso)
        

    def addSensorino(self, sensorino):
        """create and add a new sensorino unless there is an id/address conflict """
        if (sensorino in self.sensorinos):
            logger.debug("not adding sensorino, already present")
            return None
        for sens in self.sensorinos:
            if (sens.sid == sensorino.sid and sens.address==sensorino.address):
                logger.warn("unable to add your sensorino, id or address duplication")
                return None
        self.sensorinos.append(sensorino)
        return True

    def delSensorino(self, sid):
        """delete and remove a new sensorino"""
        s = self.findSensorino(sid=sid)
        if s == None:
            logger.debug("not deleting sensorino as already missing")
            return True
        else:
            s.deleteFromDb()
            self.sensorinos.remove(s)
            return True

    def findSensorino(self, sid=None, address=None):
        """return sensorino with given address or id"""
        for sens in self.sensorinos:
            if ((sid!=None and sens.sid == sid) or(address!=None and sens.address==address)):
                return sens
        return None

    def getServicesBySensorino(self, sid):
        """return all services registered in sensorino with given id"""
        s = self.findSensorino(sid=sid)
        if s == None:
            logger.debug("not returning services as unable to find sensorino")
            return True
        return s.services 

        
    # TODO generate exception on failures, this will allow rest server to translate them into http status

    
    def publish(self, sid, serviceId, data):
        """publish some data on dataService with given id"""
        sens=findSensorino(sid)
        if (sens==None):
            logger.warn("logging data from unknown sensorino is not allowed (yet)")
            return None
        service=sens.getService(serviceId)
        if (service==None):
            logger.warn("logging data from unknown sensorino is not allowed (yet)")
            return None
        return service.logData(data)

    def setState(self, sid, serviceId, state):
        """to setState we should send command and wait for the publish back"""
        sens=findSensorino(sid)
        if (sens==None):
            logger.warn("logging data from unknown sensorino is not allowed (yet)")
            return None
        service=sens.getService(serviceId)
        if (service==None):
            logger.warn("logging data from unknown sensorino is not allowed (yet)")
            return None
        
        self.mqtt.mqttc.publish("commands",  { "set" : {"address":sensorinoAddress, "serviceID":serviceId, "state":state}})
        return True

    
    def request(self, sid, serviceId):
        """will launch a request to service"""
        sens=findSensorino(sid)
        if (sens==None):
            logger.warn("logging data from unknown sensorino is not allowed (yet)")
            return None
        service=sens.getService(serviceId)
        if (service==None):
            logger.warn("logging data from unknown sensorino is not allowed (yet)")
            return None
        self.mqtt.mqttc.publish("commands",  { "request": { "address":sens.address, "serviceID":service.serviceId, "serviceInstanceID":service.sid}})
        return True


    def _createMqttClient(self):
        """confire mqtt client and create thread for it"""
        def mqtt_on_connect(mosq, obj, rc):
            mosq.subscribe("sensorino", 0)
            print("rc: "+str(rc))

        def mqtt_on_message(mosq, obj, msg):
            print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

        def mqtt_on_publish(mosq, obj, mid):
            print("mid: "+str(mid))

        def mqtt_on_subscribe(mosq, obj, mid, granted_qos):
            print("Subscribed: "+str(mid)+" "+str(granted_qos))

        def mqtt_on_log(mosq, obj, level, string):
            print(string)

        mqtt=mqttThread.MqttThread()

        mqtt.mqttc.on_message = mqtt_on_message
        mqtt.mqttc.on_connect = mqtt_on_connect
        mqtt.mqttc.on_publish = mqtt_on_publish
        mqtt.mqttc.on_subscribe = mqtt_on_subscribe
        # Uncomment to enable debug messages
        #mqtt.mqttc.on_log = on_log
        
        self.mqtt = mqtt
        return mqtt


    def start(self):
        self._createMqttClient().run()

