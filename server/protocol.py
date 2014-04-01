import logging
import serial
import json

# create logger with 'spam_application'
logger = logging.getLogger('protocol')
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


class Protocol:
    """
    on_publish(self, address, serviceID, serviceInstanceID, data)
    on_set(self, address, serviceID, serviceInstanceID, state)
    on_request(self, address, serviceID, serviceInstanceID)
    on_advert TBSL
    on_ping(self, address)
    on_pong(self, address)
    on_error(self, address, type, data)


    based on json messages:
    { "publish": { "address": [1,2,3,4], "serviceID": 2, "serviceInstanceID": 0, "data": { ..... } } }
    { "set": { "address": [1,2,3,4], "serviceID": 2, "serviceInstanceID": 0, "state": { ..... } } }
    { "request": { "address": [1,2,3,4], "serviceID": 2, "serviceInstanceID": 0, "data": { ..... } } }
    { "control": { "address": [1,2,3,4], "type": "ADVERT", "data": { ..... } }
    { "control": { "address": [1,2,3,4], "type": "PING", "data": { ..... } } }
    { "control": { "address": [1,2,3,4], "type": "PONG", "data": { ..... } } }
    { "error": { "address": [1,2,3,4], "type": "SERVICE_UNAVAILABLE", "data": { ..... } } }

    """

    def __init__(self):
        self.on_publish=None
        self.on_set=None
        self.on_request=None
        self.on_advert=None
        self.on_ping=None
        self.on_pong=None
        self.on_error=None

    @staticmethod
    def serializeAddress(address):
        return  ".".join(str(digit) for digit in address)


    def treatMessage(self, jsonString):
        try:
            message=json.loads(jsonString)
            if("publish" in message):
                msg=message["publish"]
                if(self.on_publish!=None):
                    self.on_publish( SensorinoProtocol.serializeAddress(msg["address"]), msg["serviceId"], msg['serviceInstanceID'], msg["data"])
            elif("set" in message):
                msg=message["set"]
                if(self.on_set!=None):
                    self.on_set(SensorinoProtocol.serializeAddress(msg["address"]), msg["serviceId"], msg['serviceInstanceID'], msg["state"])
            elif("request" in message):
                msg=message["request"]
                if(self.on_request!=None):
                    self.on_request(SensorinoProtocol.serializeAddress(msg["address"]), msg["serviceId"], msg['serviceInstanceID'])
            elif ("control" in message):
                msg=message["control"]
                if ("type" in msg):
                    if("PONG" == msg["type"] and self.on_pong!=None):
                        self.on_pong(SensorinoProtocol.serializeAddress(msg["address"]))
                    elif("PING" == msg["type"] and self.on_ping!=None):
                        self.on_ping(SensorinoProtocol.serializeAddress(msg["address"]))

            elif ("error" in message):
                msg=message["error"]
                if (self.on_error!=None):
                    self.on_error(SensorinoProtocol.serializeAddress(msg["address"]), msg["type"], msg["data"])
            else:
                logger.error("unhandled message "+message)
                    
        except:
            logger.error("fail to parse json message: "+line)
            return None


