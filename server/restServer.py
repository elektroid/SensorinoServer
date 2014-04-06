#!/usr/bin/python
from flask import Flask
from flask.ext import restful
from flask import json
from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.restful.utils import cors

import threading
import logging
import time
import coreEngine



app = Flask(__name__)
api = restful.Api(app)

coreEngine = coreEngine.Core()


class RestSensorinoList(restful.Resource):
    """ Handle sensorinos list and creation"""
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
        args = rparse.parse_args()
        sens=sensorino.Sensorino( args['name'], args['address'], args['description'])
        sens.saveToDb()
        if (coreEngine.addSensorino(sens)==False):
            return 500
        return sens.sid


class RestSensorino(restful.Resource):
    """ Handle sensorino details, update and delete"""
    def get(self, sid):
        try:
            sens=coreEngine.findSensorino(sid)
            return sens.toData()
        except SensorinoNotFoundError:
            abort(404, message="no such sensorino")

    def put(self, sid):
        rparse = reqparse.RequestParser()   
        rparse.add_argument('address', type=str, required=True, help="your sensorino needs an address", location="json")
        rparse.add_argument('name', type=str, required=True, help="your sensorino needs a name", location="json")
        rparse.add_argument('description', type=str, required=True, help="Please give a brief description for your sensorin", location="json")

        args = rparse.parse_args()
        try:
            sens=coreEngine.findSensorino(sid)
            sens.name=args['name']
            sens.address=args['address']
            sens.description=args['description']

            sens.saveToDb()
            return sens.toData()
        except SensorinoNotFoundError:
            abort(404, message="no such sensorino")


    def delete(self, sid):
        return coreEngine.delSensorino(sid)



class ServicesBySensorino(restful.Resource):
    """ List and create services inside a sensorino"""
    def get(self, sid):
        services=[]
        for service in coreEngine.getServicesBySensorino(sid):
            services.append(service)
        return services

    def post(self, sid):
        rparse = reqparse.RequestParser()
        rparse.add_argument('name', type=str, required=True, help="your service needs a name", location="json")
        rparse.add_argument('dataType', type=str, required=True, help="What kind of data ?", location="json")
        rparse.add_argument('location', type=str, required=False, help="Where is your device ?", location="json")
        args =rparse.parse_args()
        
        try:
            coreEngine.createDataService(sid, args['name'], args['dataType'])
            return 201
        except SensorinoNotFoundError:
            abort(404, message="no such sensorino")



class ServiceBySensorino(restful.Resource):
    """ Handle service details, update and delete"""
    def get(self, sid, serviceId):
        sensorinoId=sid
        try:
            return coreEngine.findSensorino(sid=sid).getService(serviceId).toData()
        except SensorinoNotFoundError:
            abort(404, message="no such sensorino")
        except ServiceNotFoundError:
            abort(404, message="no such service")

    def delete(self, sid, serviceId):
        try:
            coreEngine.findSensorino(sid, serviceId)
        except SensorinoNotFoundError:
            abort(404, message="no such sensorino")



class PublishDataServiceBySensorino(restful.Resource):
    """ Handle publish data listing and posting"""
    def get(self, sid, serviceId):
        try:
            sensorinoId=int(sid)
            return coreEngine.findSensorino(sid=sensorinoId).getService(serviceId).getLogs(sid)
        except SensorinoNotFoundError:
            abort(404, message="no such sensorino")
        except ServiceNotFoundError:
            abort(404, message="no such service")


    def post(self, sid, serviceId):
        rparse = reqparse.RequestParser()
        rparse.add_argument('data', type=str, required=True, help="are you loging data ?", location="json")
        args =rparse.parse_args()
        try: 
            sensorinoId=int(sid)
            coreEngine.findSensorino(sid=sensorinoId).getService(serviceId).logData(args['data'])
        except SensorinoNotFoundError:
            abort(404, message="no such sensorino")
        except ServiceNotFoundError:
            abort(404, message="no such service")

      


api.add_resource(RestSensorinoList, '/sensorinos')
api.add_resource(RestSensorino, '/sensorinos/<int:sid>')
api.add_resource(ServicesBySensorino, '/sensorinos/<int:sid>/dataServices')
api.add_resource(ServiceBySensorino, '/sensorinos/<int:sid>/dataServices/<int:serviceId>')
api.add_resource(PublishDataServiceBySensorino, '/sensorinos/<int:sid>/dataServices/<int:serviceId>/data')



if __name__ == '__main__':
    print("sensorino server m0.1")
    coreEngine.start()
    print "engine started"
    app.config['PROPAGATE_EXCEPTIONS'] = True

    app.run(debug=True)
    print "app running"


