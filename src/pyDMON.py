'''

Copyright 2015, Institute e-Austria, Timisoara, Romania
    http://www.ieat.ro/
Developers:
 * Gabriel Iuhasz, iuhasz.gabriel@info.uvt.ro

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#!flask/bin/python


from flask.ext.restplus import Api, Resource, fields
from flask import Flask, jsonify
from flask import request
from flask import redirect
from flask import make_response
from flask import abort
from flask import url_for
from flask import render_template
from flask import Response
from flask import send_file
from flask import send_from_directory
import os
import sys
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
#DICE Imports
from pyESController import *
#from dbModel import *


app = Flask("D-MON")
api = Api(app, version='0.1', title='DICE MOnitoring API',
    description='RESTful API for the DICE Monitoring Platform  (D-MON)',
)

db = SQLAlchemy(app)
#%--------------------------------------------------------------------%
class dbNodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nodeFQDN = db.Column(db.String(64), index=True, unique=True)
    nodeIP = db.Column(db.String(64), index=True, unique=True)
    nodeOS = db.Column(db.String(120), index=True, unique=False)
    nUser = db.Column(db.String(64), index=True, unique=False)
    nPass = db.Column(db.String(64), index=True, unique=False)
    nkey = db.Column(db.String(120), index=True, unique=False)
    nRoles = db.Column(db.String(120), index=True, unique=False) #hadoop roles running on server
    nStatus = db.Column(db.Boolean, unique=False)
    nMonitored = db.Column(db.Boolean, unique=False)
    nCollectdState = db.Column(db.String(64), index=True, unique=False) #Running, Pending, Stopped, None
    nLogstashForwState = db.Column(db.String(64), index=True, unique=False) #Running, Pending, Stopped, None
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    #ES = db.relationship('ESCore', backref='nodeFQDN', lazy='dynamic')

    def __repr__(self):
        return '<dbNodes %r>' % (self.nickname)


class dbESCore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostFQDN = db.Column(db.String(64), index=True, unique=True)
    hostIP = db.Column(db.String(64), index=True, unique=True)
    hostOS = db.Column(db.String(120), index=True, unique=False)
    nodeName = db.Column(db.String(64), index=True, unique=True)
    nodePort = db.Column(db.Integer, index=True, unique=False,default = 9200)
    clusterName = db.Column(db.String(64), index=True, unique=False)
    conf = db.Column(db.String(140), index=True, unique=False)
    ESCoreStatus = db.Column(db.String(64), index=True, unique=False)#Running, Pending, Stopped, None
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<dbESCore %r>' % (self.body)

class dbSCore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostFQDN = db.Column(db.String(64), index=True, unique=True)
    hostIP = db.Column(db.String(64), index=True, unique=True)
    hostOS = db.Column(db.String(120), index=True, unique=False)
    inLumberPort = db.Column(db.Integer, index=True, unique=False,default = 5000)
    sslCert = db.Column(db.String(120), index=True, unique=False)
    sslKey = db.Column(db.String(120), index=True, unique=False)
    udpPort = db.Column(db.Integer, index=True, unique=False,default = 25826) #collectd port same as collectd conf
    outESclusterName = db.Column(db.String(64), index=True, unique=False )# same as ESCore clusterName
    outKafka = db.Column(db.String(64), index=True, unique=False) # output kafka details
    outKafkaPort = db.Column(db.Integer, index=True, unique=False)
    conf = db.Column(db.String(140), index=True, unique=False)
    LSCoreStatus = db.Column(db.String(64), index=True, unique=False)#Running, Pending, Stopped, None
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<dbLSCore %r>' % (self.body)

class dbKBCore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostFQDN = db.Column(db.String(64), index=True, unique=True)
    hostIP = db.Column(db.String(64), index=True, unique=True)
    hostOS = db.Column(db.String(120), index=True, unique=False)
    kbPort = db.Column(db.Integer, index=True, unique=False,default = 5601)
    conf = db.Column(db.String(140), index=True, unique=False)
    KBCoreStatus = db.Column(db.String(64), index=True, unique=False)#Running, Pending, Stopped, None
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<dbKBCore %r>' % (self.body)

#Not Used Yet
class dbApp(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	appName = db.Column(db.String(64), index=True, unique=False)
	appVersion = db.Column(db.String(64), index=True, unique=False)
	jobID = db.Column(db.String(64), index=True, unique=True)
	startTime = db.Column(db.String(64), index=True, unique=False)
	stopTime = db.Column(db.String(64), index=True, unique=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)
	def __repr__(self):
		return '<dbApp %r>' % (self.body)


#%--------------------------------------------------------------------%

#changes the descriptor on the Swagger WUI and appends to api /dmon and then /v1
dmon = api.namespace('dmon', description='D-MON operations')

#argument parser
pQueryES = api.parser() 
#pQueryES.add_argument('task',type=str, required=True, help='The task details', location='form')


#descripes universal json @api.marshal_with for return or @api.expect for payload model
queryES = api.model('query details Model', {
	'fname': fields.String(required=False,default="output", description='Name of output file.'),
    'size': fields.Integer(required=True,default=500, description='Number of record'),
    'ordering': fields.String(required=True,default='desc', description='Ordering of records'),
    'queryString': fields.String(required=True,default = "hostname:\"dice.cdh5.s4.internal\" AND serviceType:\"dfs\""
    	,description='ElasticSearc Query'),
    'tstart': fields.Integer(required=True,default=1438939155342,description='Start Date'),
    'tstop': fields.Integer(required=True,default=1438940055342,description='Stop Date'),
    'metrics': fields.List(fields.String(required=False, default = ' ', description = 'Desired Metrics'))

})
#Nested JSON input 
dMONQuery = api.model('queryES Model',{
	'DMON':fields.Nested(queryES, description="Query details")
	})


# monNodes = api.model('Monitored Nodes',{
# 	'Node':fields.List(fields.Nested(nodeDet, description="FQDN and IP of nodes"))
# 	})
# nodeDet = api.model('Node Info',{
# 	'FQDN' : field
# 	})#[{'FQDN':'IP'}]


# def abort_if_todo_doesnt_exist(todo_id):
#     if todo_id not in TODOS:
#         api.abort(404, "Todo {} doesn't exist".format(todo_id))

#getGateway = dbNodes.query.filter_by(name = gateway).first()
@dmon.route('/v1/observer/nodes')
class NodesMonitored(Resource):
	#@api.marshal_with(monNodes) # this is for response
	def get(self):
		nodeList = []
		nodesAll=db.session.query(dbNodes.nodeFQDN,dbNodes.nodeIP).all()
		if nodesAll is None:
			response = jsonify({'Status':'No monitored nodes found'})
			response.status_code = 404
			return response
		for nl in nodesAll:
			nodeDict= {}
			print >>sys.stderr, nl[0]
			nodeDict.update({nl[0]:nl[1]})
			nodeList.append(nodeDict)
		response = jsonify({'Nodes':nodeList})
		response.status_code=200
		return response


@dmon.route('/v1/observer/nodes/<nodeFQDN>')
@api.doc(params={'nodeFQDN':'Nodes FQDN'})
class NodeStatus(Resource):
	def get(self, nodeFQDN):
		qNode = dbNodes.query.filter_by(nodeFQDN = nodeFQDN).first()
		if qNode is None:
			response = jsonify({'Status':'Node ' +nodeFQDN+' not found!'})
			response.status_code = 404
			return response
		else:
			response = jsonify({nodeFQDN:{
				'Status':qNode.nStatus,
				'IP':qNode.nodeIP,
				'Monitored':qNode.nMonitored,
				'OS':qNode.nodeOS}})
			response.status_code = 200	
		return response


@dmon.route('/v1/observer/nodes/<nodeFQDN>/services')
@api.doc(params={'nodeFQDN':'Nodes FQDN'})
class NodeStatusServices(Resource):
	def get(self,nodeFQDN):
		return "Node " + nodeFQDN +" status of services!"		

@dmon.route('/v1/observer/query/<ftype>')
@api.doc(params={'ftype':'output type'})
class QueryEsCore(Resource):
	#@api.doc(parser=pQueryES) #inst parser
	#@api.marshal_with(dMONQuery) # this is for response
	@api.expect(dMONQuery)# this is for payload
	def post(self, ftype):
		#args = pQueryES.parse_args()#parsing query arguments in URI
		supportType = ["csv","json","plain"]
		if ftype not in supportType:
			response = jsonify({'Supported types':supportType, "Submitted Type":ftype })
			response.status_code = 415
			return response
		query = queryConstructor(request.json['DMON']['tstart'],request.json['DMON']['tstop'],
			request.json['DMON']['queryString'],size=request.json['DMON']['size'],ordering=request.json['DMON']['ordering'])
		#return query
		if not 'metrics'  in request.json['DMON'] or request.json['DMON']['metrics'] == " ":
			ListMetrics, resJson = queryESCore(query, debug=False)
			if ftype == 'csv':
				if not 'fname' in request.json['DMON']:
					fileName = 'output'+'.csv'
					dict2CSV(ListMetrics)
				else:
					fileName = request.json['DMON']['fname']+'.csv'
					dict2CSV(ListMetrics,request.json['DMON']['fname'])

				csvOut = os.path.join(outDir,fileName)
				try:
					csvfile=open(csvOut,'r')
				except EnvironmentError:
					response = jsonify({'EnvError':'file not found'})
					response.status_code = 500
					return response
				return send_file(csvfile,mimetype = 'text/csv',as_attachment = True)
			if ftype == 'json':
				response = jsonify({'DMON':resJson})
				response.status_code = 200
				return response
			if ftype == 'plain':
				return Response(str(ListMetrics),status=200 ,mimetype='text/plain')

		else:
			metrics = request.json['DMON']['metrics']
			ListMetrics, resJson = queryESCore(query, allm=False,dMetrics=metrics, debug=False)
			#repeated from before create function
			if ftype == 'csv':
				if not 'fname' in request.json['DMON']:
					fileName = 'output'+'.csv'
					dict2CSV(ListMetrics)
				else:
					fileName = request.json['DMON']['fname']+'.csv'
					dict2CSV(ListMetrics,request.json['DMON']['fname'])
				csvOut = os.path.join(outDir,fileName)
				try:
					csvfile=open(csvOut,'r')
				except EnvironmentError:
					response = jsonify({'EnvError':'file not found'})
					response.status_code = 500
					return response
				return send_file(csvfile,mimetype = 'text/csv',as_attachment = True)
			if ftype == 'json':
				response = jsonify({'DMON':resJson})
				response.status_code = 200
				return response
			if ftype == 'plain':
				return Response(str(ListMetrics),status=200 ,mimetype='text/plain')


@dmon.route('/v1/overlord')
class OverlordInfo(Resource):
	def get(self):
		return "Overlord Information"

@dmon.route('/v1/overlord/core')
class OverlordBootstrap(Resource):
	def post(self):
		return "Deploys all monitoring core components with default configuration"

@dmon.route('/v1/overlord/core/status')
class OverlordCoreStatus(Resource):
	def get(self):
		return "Monit Core Status!"

@dmon.route('/v1/overlord/chef')
class ChefClientStatus(Resource):
	def get(self):
		return "Monitoring Core Chef Client status"

@dmon.route('/v1/overlord/nodes/chef')
class ChefClientNodes(Resource):
	def get(self):
		return "Chef client status of monitored Nodes"


@dmon.route('/v1/overlord/nodes')
class MonitoredNodes(Resource):
	def get(self):
		return "Current monitored Nodes"

	def post(self):
		return "Submit Nodes for monitoring"


@dmon.route('/v1/overlord/nodes/<nodeFQDN>')
class MonitoredNodeInfo(Resource):
	def get(self, nodeFQDN):
		return "Return info of specific monitored node."

	def put(self, nodeFQDN):
		return "Change info of specific monitored node."

@dmon.route('/v1/overlord/core/es/config')
class ESCoreConfiguration(Resource):
	def get(self):
		return "Returns current configuration of ElasticSearch"

	def put(self):
		return "Changes configuration of ElasticSearch"

@dmon.route('/v1/overlord/core/es')
class ESCoreController(Resource):
	def post(self):
		return "Deploys (Start/Stop/Restart/Reload args not json payload) configuration of ElasticSearch"

@dmon.route('/v1/overlord/core/kb/config')
class KBCoreConfiguration(Resource):
	def get(self):
		return "Retruns Kibana current configuration"

	def put(self):
		return "Changes configuration of Kibana"

@dmon.route('/v1/overlord/core/kb')
class KKCoreController(Resource):
	def post(self):
		return "Deploys (Start/Stop/Restart/Reload args not json payload) configuration of Kibana"

@dmon.route('/v1/overlord/core/ls/config')
class LSCoreConfiguration(Resource):
	def get(self):
		return "Returns current logstash server configuration"

	def put(self):
		return "Changes configuration fo logstash server"

@dmon.route('/v1/overlord/core/ls')
class LSCoreController(Resource):
	def post(self):
		return "Deploys (Start/Stop/Restart/Reload args not json payload) configuration of Logstash Server"



@dmon.route('/v1/overlord/aux')
class AuxInfo(Resource):
	def get(self):
		return "Returns Information about AUX components"


@dmon.route('/v1/overlord/aux/deploy')
class AuxDeploy(Resource):
	def get(self):
		return "List of deployed aux monitoring components"

	def post(self):
		return "Deploy currently configured aux monitoring components"

@dmon.route('/v1/overlord/aux/<auxComp>/<nodeFQDN>')
class AuxDeploySelective(Resource):
	def post(self, auxComp, nodeFQDN):
		return "Deploys auxiliary monitoring components on a node by node basis."

@dmon.route('/v1/overlord/aux/<auxComp>/config')
class AuxConfigSelective(Resource):
	def get(self, auxComp):
		return "Returns current configuration of aux components"

	def put(self,auxComp):
		return "Sets configuration of aux components use parameters (args) -unsafe"

"""
Custom errot Handling

"""	


@app.errorhandler(403)
def forbidden(e):
    response = jsonify({'error': 'forbidden'})
    response.status_code = 403
    return respons


@app.errorhandler(404)
def page_not_found(e):
    response = jsonify({'error': 'not found'})
    response.status_code = 404
    return response
   


@app.errorhandler(500)
def internal_server_error(e):
    response = jsonify({'error': 'internal server error'})
    response.status_code = 500
    return response
   

@app.errorhandler(405)
def meth_not_allowed(e):
	response=jsonify({'error':'method not allowed'})
	response.status_code=405
	return response

@api.errorhandler(400)
def bad_request(e):
	response=jsonify({'error':'bad request'})
	response.status_code=400
	return response

@app.errorhandler(415)
def bad_mediatype(e):
	response=jsonify({'error':'unsupported media type'})
	response.status_code = 415
	return response



#109.231.126.38

if __name__ == '__main__':
	#directory Location
	outDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
	tmpDir  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
	cfgDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
	baseDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')

	app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(baseDir,'dmon.db')
	app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
	db.create_all()

	#print >>sys.stderr, "Running as: %s:%s" % (os.getuid(), os.getgid())
	# testQuery = queryConstructor(1438939155342,1438940055342,"hostname:\"dice.cdh5.s4.internal\" AND serviceType:\"dfs\"")
	# metrics = ['type','@timestamp','host','job_id','hostname','AvailableVCores']
	# test, test2 = queryESCore(testQuery, debug=False)
	# print >>sys.stderr, test2
	app.run(debug=True)
