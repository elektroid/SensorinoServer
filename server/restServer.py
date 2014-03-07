#!/usr/bin/python
from flask import Flask
from flask.ext import restful
from flask import json
from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.restful.utils import cors

import threading
import logging
import time

import sensorino
import serialEngine


app = Flask(__name__)
api = restful.Api(app)
#api.decorators=[cors.crossdomain(origin='*')]


def json_type(data):
    try:
        return json.loads(data)
    except:
        raise ValueError('Malformed JSON')


coreEngine = sensorino.Core()


class RestSensorinoList(restful.Resource):

    def get(self):
        sensorinos=[]
        for s in coreEngine.getSensorinos():
            sensorinos.append(s.toData())
        return sensorinos

    def post(self):
        rparse = reqparse.RequestParser()   
        rparse.add_argument('address', type=str, required=True, help="your sensorino needs an address", location="json")
        rparse.add_argument('name', type=str, required=True, help="your sensorino needs a name", location="json")
        rparse.add_argument('description', type=str, required=True, help="Please give a brief description for your sensorin", location="json")
        print("lets parse")
        args = rparse.parse_args()
        print(args)
        sens=sensorino.Sensorino( args['name'], args['address'], args['description'])
        sens.saveToDb()
        coreEngine.addSensorino(sens)
        print(sens.toData())
        return sens.sid

class RestSensorino(restful.Resource):

    def get(self, sid):
        sens=coreEngine.findSensorino(sid)
        if (sens==None):
            abort(404, message="no such sensorino")
        return sens.toData()

    def put(self, sid):
        rparse = reqparse.RequestParser()   
        rparse.add_argument('address', type=str, required=True, help="your sensorino needs an address", location="json")
        rparse.add_argument('name', type=str, required=True, help="your sensorino needs a name", location="json")
        rparse.add_argument('description', type=str, required=True, help="Please give a brief description for your sensorin", location="json")

        args = rparse.parse_args()
        sens=coreEngine.findSensorino(sid)
        sens.name=args['name']
        sens.address=args['address']
        sens.description=args['description']

        sens.saveToDb()
        return sens.toData()

    def delete(self, sid):
        coreEngine.delSensorino(sid)
        return sid




class DataServicesBySensorino(restful.Resource):

    def get(self, sid):
        services=[]
#        print(coreEngine.getServicesBySensorino(sid))
        for service in coreEngine.getServicesBySensorino(sid):
            services.append(service)
        return services

    def post(self, sid):
        print("who dares awakening the planet smasher ?")
        rparse = reqparse.RequestParser()
        print("who dares awakening the planet smasher 1?")
        rparse.add_argument('name', type=str, required=True, help="your service needs a name", location="json")
        rparse.add_argument('dataType', type=str, required=True, help="What kind of data ?", location="json")
        rparse.add_argument('location', type=str, required=False, help="Where is your device ?", location="json")
        print("who dares awakening the planet smasher 2?")
        args =rparse.parse_args()
        print("who dares awakening the planet smasher 3?")
        print(args)
        sensorinoId=int(sid)
        sens=coreEngine.findSensorino(sid=sensorinoId)
        print("sens is")
        print(sens)
        if (sens==None):
            abort(404, message="no such sensorino")
        service=sensorino.DataService(args['name'], args['dataType'], sens.sid)
        status=service.saveToDb()
        sens.registerService(service)
        print(service)
        print(service.serviceId)
        return service.serviceId, 201



class DataServiceBySensorino(restful.Resource):

    def get(self, sid, serviceId):
        sensorinoId=sid
        sens=coreEngine.findSensorino(sid=sid)
        if (sens==None):
            abort(404, message="no such sensorino")

        service=sens.getService(serviceId)
        if (service==None):
            abort(404, message="no such service")

        return service.toData()


    def delete(self, sid, serviceId):
        sens=coreEngine.findSensorino(sid=sid)
        if (sens==None):
            abort(404, message="no such sensorino")
   
        service=sens.getService(serviceId)
        if (service==None):
            abort(404, message="no such service")

        print("fuck this service")
        print(service)
        sens.removeService(service)
        service.deleteFromDb()

        return service.serviceId

class PublishDataServiceBySensorino(restful.Resource):

    def get(self, sid, serviceId):
        services=[]
#        print(coreEngine.getServicesBySensorino(sid))
        for service in coreEngine.getServicesBySensorino(sid):
            services.append(service)
        return services

    def post(self, sid):
        print("who dares awakening the planet smasher ?")
        rparse = reqparse.RequestParser()
        print("who dares awakening the planet smasher 1?")
        rparse.add_argument('name', type=str, required=True, help="your service needs a name", location="json")
        rparse.add_argument('dataType', type=str, required=True, help="What kind of data ?", location="json")
        rparse.add_argument('location', type=str, required=False, help="Where is your device ?", location="json")
        print("who dares awakening the planet smasher 2?")
        args =rparse.parse_args()
        print("who dares awakening the planet smasher 3?")
        print(args)
        sensorinoId=int(sid)
        sens=coreEngine.findSensorino(sid=sensorinoId)
        print("sens is")
        print(sens)
        if (sens==None):
            abort(404, message="no such sensorino")
        service=sensorino.DataService(args['name'])
        service.setDataType(args['dataType'])
        service.setSensorino(sens)
        status=service.saveToDb()
        sens.registerService(service)
        print(service)
        print(service.serviceId)
        return service.serviceId, 201

      


 



class SerialThread(threading.Thread):
    def __init__(self):
        self._engine = serialEngine.SerialEngine()
        threading.Thread.__init__(self)
    def run (self):
        while True:
            print("serial thread")
            time.sleep(10)


api.add_resource(RestSensorinoList, '/sensorinos')
api.add_resource(RestSensorino, '/sensorinos/<int:sid>')
api.add_resource(DataServicesBySensorino, '/sensorinos/<int:sid>/dataServices')
api.add_resource(DataServiceBySensorino, '/sensorinos/<int:sid>/dataServices/<int:serviceId>')
#api.add_resource(PublishDataServiceBySensorino, '/sensorino/<int:sid>/dataService/<int:serviceId>/data')



if __name__ == '__main__':
    print("hello")
    #serial=SerialThread()
    #serial.start()
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.run(debug=True)


