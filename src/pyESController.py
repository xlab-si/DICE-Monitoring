from datetime import datetime
from elasticsearch import Elasticsearch
import csv
import unicodedata
import os
import sys


#ouptu dir location
outDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

def queryConstructor(tstart, tstop, queryString, size=500,ordering="desc"):
  '''
      Function generates a query string reprezented by a dictionary/json.
      It has the following arguments:

      tstart      -> unix time representation of required period start
      tstop       -> unix time representation of required period stop
      queryString -> represents the query from the user
      size        -> repreents how many records should be in the output
                  -> default is 500
      ordering    -> can be "asc" or "desc"
                  -> default is "desc"

      Function returns a dictionary of the query body required for elasticsearch.

      TODO:
      - Need more elegant solution, constructor for queryString
  '''
  queryBody= {
  "size": size,
  "sort": {
    "@timestamp": ordering
  },
  "query": {
    "filtered": {
      "query": {
        "query_string": {
          "query": queryString,
          "analyze_wildcard": True
        }
      },
      "filter": {
        "bool": {
          "must": [
            {
              "range": {
                "@timestamp": {
                  "gte": tstart,
                  "lte": tstop
                }
              }
            }
          ],
          "must_not": []
        }
      }
    }
  },
  "fields": [
    "*",
    "_source"
  ],
  "script_fields": {},
  "fielddata_fields": [
    "@timestamp"
  ]
}
  return queryBody


def queryESCore(queryBody, all=True, dMetrics=[ ], debug=False, myIndex="logstash-*"):
  '''
      Function to query the Elasticsearch monitoring (ESM) core.
      It has the following arguments:
      queryBody -> is a dictionary that reprezents the query for ESM Core
                -> it is returned by the function queryConstructor()
      all       -> boolean arguments; if True returns all available metrics from the query
                -> if False must specify list of user defined metrics
                -> default value is True
      dMetrics  -> List of user defined metrics
                -> default is the empty list
                -> if all argument is set to False dMetrics is mandatory
      debug     -> if set to true prints debug information
      myIndex   -> user defined index for ESM Core
                -> default is "logstash-*"

      TODO: 
      - filter by removing terms/metrics from all not only specifying desired metrics

  '''
  #these are the metrics listed in the response JSON under "_source"
  res = es.search(index=myIndex,body=queryBody)
  if debug == True:
    print "%---------------------------------------------------------%"
    print "Raw JSON Ouput"
    print res
    print("%d documents found" % res['hits']['total'])
    print "%---------------------------------------------------------%"
  termsList = []
  termValues = []
  ListMetrics = []
  for doc in res['hits']['hits']:
    if all == False:
      if not dMetrics:
        sys.exit("dMetrics argument not set. Please supply valid list of metrics!")
      for met in metrics:
      #prints the values of the metrics defined in the metrics list
        if debug == True:
          print "%---------------------------------------------------------%"
          print "Parsed Output -> ES doc id, metrics, metrics values."
          print("doc id %s) metric %s -> value %s" % (doc['_id'], met, doc['_source'][met]))
          print "%---------------------------------------------------------%"
        termsList.append(met)
        termValues.append(doc['_source'][met]) 
      dictValues=dict(zip(termsList,termValues))
    else:
      for terms in doc['_source']:
      #prints the values of the metrics defined in the metrics list
        if debug == True:
          print "%---------------------------------------------------------%"
          print "Parsed Output -> ES doc id, metrics, metrics values."
          print("doc id %s) metric %s -> value %s" % (doc['_id'],terms,  doc['_source'][terms]))
          print "%---------------------------------------------------------%"
        termsList.append(terms)
        termValues.append(doc['_source'][terms])
        dictValues=dict(zip(termsList,termValues))
    ListMetrics.append(dictValues)
  return ListMetrics
  

def dict2CSV(ListValues,fileName="output"):
  '''
      Function that creates a csv file from a list of dictionaries.
      It has the arguments:
      ListValues  -> is a list containing dictionaries with individual timestamped metrics.
      fileName    -> name of the ouput csv file
                  -> default is "ouput"

  '''
  if not ListValues:
        sys.exit("listValues argument is empty. Please supply valid input!")
  fileType = fileName+".csv"
  csvOut = os.path.join(outDir,fileType)
  try:
    with open(csvOut,'wb') as csvfile:
      w=csv.DictWriter(csvfile, ListValues[0].keys())
      w.writeheader()
      for dictMetrics in ListValues:
        w.writerow(dictMetrics)
    csvfile.close()
  except EnvironmentError:
    print "ops"





      

if __name__=='__main__':
  if len(sys.argv) == 1:#Elastic search endpoint
    es = Elasticsearch('109.231.126.38')
    testQuery = queryConstructor(1438939155342,1438940055342,"hostname:\"dice.cdh5.s4.internal\" AND serviceType:\"dfs\"")
    metrics = ['type','@timestamp','host','job_id','hostname','AvailableVCores']
    test = queryESCore(testQuery, debug=True)
    dict2CSV(test)
    #queryESCoreCSV(test, True)
