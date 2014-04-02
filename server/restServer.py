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
        sensorinoId=int(sid)
        sens=coreEngine.findSensorino(sid=sensorinoId)
        if (sens==None):
            abort(404, message="no such sensorino")
        service=sensorino.DataService(args['name'], args['dataType'], sens.sid)
        #TODO: who should handle db call ?
        status=service.saveToDb()
        sens.registerService(service)
        return service.serviceId, 201



class ServiceBySensorino(restful.Resource):
    """ Handle service details, update and delete"""
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
        #TODO: who should handle db call ?
        sens.removeService(service)
        service.deleteFromDb()

        return service.serviceId


class PublishDataServiceBySensorino(restful.Resource):
    """ Handle publish data listing and posting"""
    def get(self, sid, serviceId):
        sensorinoId=int(sid)
        sens=coreEngine.findSensorino(sid=sensorinoId)
        if (sens==None):
            abort(404, message="no such sensorino")
        service=sens.getService(serviceId)
        if (service==None):
            abort(404, message="no such service")
        return service.getLogs(sid)


    def post(self, sid, serviceId):
        rparse = reqparse.RequestParser()
        rparse.add_argument('data', type=str, required=True, help="are you loging data ?", location="json")
        args =rparse.parse_args()
        sensorinoId=int(sid)
        sens=coreEngine.findSensorino(sid=sensorinoId)
        if (sens==None):
            abort(404, message="no such sensorino")
        service=sens.getService(serviceId)
        if (service==None):
            abort(404, message="no such service")

        service.logData(args['data']);
        return service.toData()
      


api.add_resource(RestSensorinoList, '/sensorinos')
api.add_resource(RestSensorino, '/sensorinos/<int:sid>')
api.add_resource(ServicesBySensorino, '/sensorinos/<int:sid>/dataServices')
api.add_resource(ServiceBySensorino, '/sensorinos/<int:sid>/dataServices/<int:serviceId>')
api.add_resource(PublishDataServiceBySensorino, '/sensorinos/<int:sid>/dataServices/<int:serviceId>/data')



if __name__ == '__main__':
    print("sensorino server m0.1")
    coreEngine.start()
    app.config['PROPAGATE_EXCEPTIONS'] = True

    app.run(debug=True)


