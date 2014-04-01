import logging
import serial
import protocol
import httplib2
import json
import time
import datetime
import ConfigParser


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


    def on_publish(prot, address, serviceID, serviceInstanceID, data):
        response, content = http.request( baseUrl+"/address/"+serviceID+"/"+serviceInstanceID, 'POST', json.dumps(data), headers=headers)


    def isReady(self):
        return self.port!=None

    def startParsing(self, messageProcessor):
        while True:
            message=self.parse(self.port.readline())
            if (message!=None):
                messageProcessor.processMessage(message)



