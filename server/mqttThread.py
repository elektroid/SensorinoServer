import threading
import ConfigParser

class MqttThread(threading.Thread):
    def __init__(self, mqttClient):
        self._mqttClient=mqttClient
        threading.Thread.__init__(self)
        self.daemon = True
    def run (self):
        self._mqttClient.connect("127.0.0.1", 1883, 60)
        self._mqttClient.loop_forever()


