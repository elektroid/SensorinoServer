import logging
import serial
import protocol
import httplib2
import json
import time
import datetime
import ConfigParser
import mosquitto


# create logger with 'spam_application'
logger = logging.getLogger('serial_gateway')
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

config=ConfigParser.ConfigParser()
config.read("sensorino.ini")


# we want to receive order events
mqttc=mosquitto.Mosquitto()
mqttc.on_message = mqtt_on_message
mqttc.on_connect = mqtt_on_connect
mqttc.on_publish = mqtt_on_publish
mqttc.on_subscribe = mqtt_on_subscribe
# Uncomment to enable debug messages
#mqttc.on_log = on_log
mqttc.connect(self.config.get("Mqtt", "ServerAddress"), 1883, 60)
mqttc.subscribe("commands", 0)




httplib2.debuglevel     = 0
http                    = httplib2.Http()
content_type_header     = "application/json"
baseUrl                 = config.get("RestServer", "ServerAddress")+"/sensorinos/"



class SerialGateway:

    linuxPossibleSerialPorts=['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2',
    '/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3',
    '/dev/ttyS0','/dev/ttyS1',
    '/dev/ttyS2','/dev/ttyS3'] # TODO : complete list

    windowsPossibleSerialPorts=['\\.\COM1', '\\.\COM2', '\\.\COM3', '\\.\COM4'] # TODO : complete list


    def __init__(self, port=None):
        self.protocol=protocol.Protocol()
        self.protocol.on_publish=on_publish
        self.mqtt=mqtt
        self.mqtt.on_message=on_mqtt_message
        self.port=port
        if (port==None):
            for device in SerialEngine.windowsPossibleSerialPorts:
                try:
                    self.port = serial.Serial(device, 57600)
                    break
                except:
                    logger.debug("arduino not on "+device)
        else:
            self.port = serial.Serial(port, 57600)


    def on_mqtt_message(mqtt, obj, msg):
        logger.debug("msg from mosquitto: "+json.dumps(msg))
        if ("commands" == msg.topic):
            command=msg.payload
            if ("request" in command):
                self.port.write(json.dumps(msg.payload))


    def on_publish(prot, address, serviceID, serviceInstanceID, data):
        response, content = http.request( baseUrl+"/address/"+serviceID+"/"+serviceInstanceID, 'POST', json.dumps(data), headers=headers)


    def isReady(self):
        return self.port!=None

    def start(self, messageProcessor):
        while True:
            self.protocol.treatMessage(self.port.readline())



