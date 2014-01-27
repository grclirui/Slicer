
import httplib, urllib
import urllib2
import json
import socket
import getopt

class SlicerCloudClient:
  def __init__(self, cloudHost, cloudPort):
    self._server = cloudHost
    self._port = cloudPort
    self._connection = httplib.HTTPConnection(cloudHost, cloudPort)

  def fetch_cloud_modules(self):
    conn = self._connection
    conn.request("GET", "/list/")
    response = conn.getresponse()
    moduleDescriptionList = json.load(response)
    return moduleDescriptionList

  def fetch_cloud_module_by_name(self, moduleName):
    conn = self._connection
    requestString = "/describe/" + moduleName
    conn.request("GET", requestString)
    response = conn.getresponse()
    moduleDescription = response.read()
    return moduleDescription

  def submit_module_to_cloud(self, commandString):
    opts, args = getopt.getopt(commandString)
    opts
    args

    #conn = self._connection
    #requestString = "/run/" + commandString
    #conn.request("POST", requestString)
    #response = conn.getresponse()
    #print response.read()

  def __del__(self):
    self._connection.close()
    print 'connection closed'

def run_test_fetch_cloud_modules(client):
  cloudModuleList = client.fetch_cloud_modules()
  print ("number of cloud modules %d \n", len(cloudModuleList))
  for module in cloudModuleList:
    print module['modulename']
    print module['modulexml']

def run_test_fetch_cloud_module_by_name(client):
  cloudModule = client.fetch_cloud_module_by_name('DWIToDTIEstimation')
  print cloudModule

def run_test_submit_module_to_cloud(client):
  commandString = "BRAINSFit --fixedVolume /Users/200020387/SlicerTest/testT1.nii.gz"\
  + " --movingVolume /Users/200020387/SlicerTest/testT1Longitudinal.nii.gz"\
  + " --outputVolume /Users/200020387/SlicerTest/testT1LongRegFixed.nii.gz"\
  + " --transformType Rigid"\
  + " --histogramMatch"\
  + " --initializeTransformMode useCenterOfHeadAlign"\
  + " --maskProcessingMode ROIAUTO"\
  + " --ROIAutoDilate 3"\
  + " --interpolationMode Linear"
  message = client.submit_module_to_cloud(commandString)
  print message

if __name__=='__main__':
  server='localhost'
  port=8080
  client = SlicerCloudClient(server, port)
  #run_test_fetch_cloud_modules(client);
  #print 'fetch_cloud_modules ... DONE'
  #run_test_fetch_cloud_module_by_name(client);
  #print 'fetch_cloud_module_by_name ... DONE'
  run_test_submit_module_to_cloud(client);
  print 'submit_module_to_cloud ... DONE'



