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
api.decorators=[cors.crossdomain(origin='*')]


def json_type(data):
    try:
        return json.loads(data)
    except:
        raise ValueError('Malformed JSON')


coreEngine = sensorino.Core()


class RestSensorinoList(restful.Resource):

    #def __init__(self):
        #self.reqparse = reqparse.RequestParser()   
        #self.reqparse.add_argument('newSensorino', type=json_type, required=False, help='Tracking data should be JSON')

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
        return sens.sid, 201

class RestSensorino(restful.Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()   
        self.reqparse.add_argument('newSensorino', type=json_type, required=False, help='Tracking data should be JSON')
        self.reqparse.add_argument('address', type=str)
        self.reqparse.add_argument('location', type=str)
        self.reqparse.add_argument('name', type=str)
        self.reqparse.add_argument('description', type=str)

    def get(self, sid):
        sens=coreEngine.loadSensorino(sid)
        if (sens==None):
            abort(404, message="no such sensorino")
        return sens.toData()

    def put(self, id):
        sensorino=Sensorino(-1, name, address, description)
        sensorino.persist()
        return sensorino.toData()


    def delete(self, sid):
        coreEngine.delSensorino(sid)
        return sid, 201




class ServicesBySensorino(restful.Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()   
        self.reqparse.add_argument('newSensorino', type=json_type, required=False, help='Tracking data should be JSON')

    def get(self, sid):
        return coreEngine.getServicesBySensorino(sid)
    def post(self):
        args = self.reqparse.parse_args()
        print(args)
        sens=sensorino.Sensorino("x", args['name'], args['address'], args['description'])
        sens.persist()
        return sens.sid, 201
   
class ServicesDataBySensorino(restful.Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()   
        self.reqparse.add_argument('newSensorino', type=str, required=False, help='Tracking data should be JSON')

    def post(self):
        args = self.reqparse.parse_args()
        print(args)
        sens=sensorino.Sensorino("x", args['name'], args['address'], args['description'])
        sens.persist()
        return sens.sid, 201
 

class SerialThread(threading.Thread):
    def __init__(self):
        self._engine = serialEngine.SerialEngine()
        threading.Thread.__init__(self)
    def run (self):
        while True:
            print("serial thread")
            time.sleep(10)


api.add_resource(RestSensorinoList, '/sensorinos')
api.add_resource(RestSensorino, '/sensorino/<string:sid>')



if __name__ == '__main__':
    print("hello")
    #serial=SerialThread()
    #serial.start()
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.run(debug=True)


