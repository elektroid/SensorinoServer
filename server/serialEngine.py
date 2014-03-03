import logging

# create logger with 'spam_application'
logger = logging.getLogger('serial_engine')
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



class SerialEngine:

    linuxPossibleSerialPorts=['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2',
    '/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3',
    '/dev/ttyS0','/dev/ttyS1',
    '/dev/ttyS2','/dev/ttyS3'] # TODO : complete list

    windowsPossibleSerialPorts=['COM1', 'COM2', 'COM3', 'COM4'] # TODO : complete list


    def __init__(self, port=None):
        self.port=port
        if (port==None):
            for device in SerialEngine.linuxPossibleSerialPorts:
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


