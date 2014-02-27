#!/usr/bin/python
from flask import Flask
from flask.ext import restful
from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.restful.utils import cors


import logging
import sensorino


app = Flask(__name__)
api = restful.Api(app)
api.decorators=[cors.crossdomain(origin='*')]

parser = restful.reqparse.RequestParser()
parser.add_argument('address', type=str)
parser.add_argument('location', type=str)
parser.add_argument('name', type=str)
parser.add_argument('description', type=str)


coreEngine = sensorino.Core()


class RestSensorinoList(restful.Resource):
    	def get(self):
		for s in coreEngine.getSensorinos():
			print(s)
        	return coreEngine.getSensorinos()
	def post(self):
		args = parser.parse_args()
		print(args)
		sens=sensorino.Sensorino("x", args['name'], args['address'], args['description'])
		sens.persist()
		return sens.sid, 201

class RestSensorino(restful.Resource):
	def put(self, name, address, description, location):
		sensorino=Sensorino(-1, name, address, description)
		sensorino.persist()

	def delete(self, sid):
		coreEngine.delSensorino(sid)
		return sid, 201

	def get(self, sid):
		sens=coreEngine.loadSensorino(sid)
		if (sens==None):
			abort(404, message="no such sensorino")
		return sens
		


api.add_resource(RestSensorinoList, '/sensorinos')
api.add_resource(RestSensorino, '/sensorino/<string:sid>')


if __name__ == '__main__':
	print("hello")
	app.config['PROPAGATE_EXCEPTIONS'] = True
	app.run(debug=True)



