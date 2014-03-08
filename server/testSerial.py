#-------------------------------------------------------------------------------
# Name:        modulo1
# Purpose:
#
# Author:      Dario
#
# Created:     08/03/2014
# Copyright:   (c) Dario 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import serialEngine

class MessageParser:
    def processMessage(self, message):
        print("in pm:")
        print(message)
        if(message["internals"]!=None):
            msg=message["internals"]

            self.onDataLog(1, 1, msg["temp"])

    def onDataLog(self, sensoId, serviceId, data):
        print("should log "+str(data)+" on senso "+str(sensoId)+" "+str(serviceId))


def main():
    parser=MessageParser()
    engine=serialEngine.SerialEngine("\\.\COM3")
    engine.startParsing(parser)





if __name__ == '__main__':
    main()