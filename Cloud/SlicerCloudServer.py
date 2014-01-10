from bottle import Bottle, template

import os
from os.path import basename
from glob import glob

import sqlite3 as lite
import string
import subprocess
import json
import ordereddict
import xml.etree.ElementTree as etree

# compare two xml strings using etree
def xmlstring_compare(xmlString1, xmlString2):
  tree1 = etree.parse(xmlString1)
  tree2 = etree.parse(xmlString2)
  set1 = set(tree1.getroot().itertext())
  set2 = set(tree2.getroot().itertext())

  return set1 == set2

class SlicerCloudServer(object):
  def __init__(self, host, port):
    self.appHome = os.environ['SLICER_HOME']
    self.pathList = os.environ['PATH']
    cliModulePath = ''
    for path in string.split(self.pathList, os.pathsep):
      if string.find(path, 'cli-modules') >= 0:
        cliModulePath = path
        break
    self.cliPath = cliModulePath[:-1]
    self.cliDB = self.appHome + '/Cloud/cloudservice.db';
    self.conn = lite.connect(self.cliDB);
    self.cliCmdPrefix = self.appHome + "/Slicer --launcher-no-splash --launch "
    self._populate_db();
    self._host = host
    self._port = port
    self._app = Bottle()
    self._route()

  def _populate_db(self):
    if self.conn == None:
      print "Error connecting to: %s" % self.cliDB
      return False
    else:
      cur = self.conn.cursor()
      self.conn.text_factory = str
      # update database
      cur.execute(
          "CREATE TABLE IF NOT EXISTS cloudmodules (modulename text, modulexml text)"
          )
      # scan through cli module directory and check whether it is a cloud cli module
      allModules = glob(self.cliPath + "*")
      otherLibs = glob(self.cliPath + "*.*")
      cliModules = list(set(allModules) - set(otherLibs))

      for cliModule in cliModules:
        cliCommand = self.cliCmdPrefix + cliModule + " --xml"
        p = subprocess.Popen(
            cliCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
        xmlString = p.communicate()[0]
        cliModuleName = basename(cliModule)

        # check the existent of this module and whether there is a need to update
        try:
          c = cur.execute(
              'SELECT modulename, modulexml FROM cloudmodules WHERE modulename = ?',
              (cliModuleName,)
              )
          row = c.fetchone()
          dbXmlString = row['modulexml']
          if not xmlstring_compare(xmlString, dbXmlString):
            cur.execute(
                'UPDATE cloudmodules SET xmlstring = ? WHERE modulename = ?',
                 (dbXmlString, cliModuleName)
                 )
            self.conn.commit()
        except:
          cur.execute(
              'INSERT INTO cloudmodules(modulename, modulexml) VALUES(?,?)',
              (cliModuleName, xmlString)
              )
          self.conn.commit()
      return True

  def _route(self):
    self._app.route('/list/', method="GET", callback=self.list_cli)
    self._app.route('/describe/<moduleName>', callback=self.describe_cli)
    self._app.route('/run/<commandString>', callback=self.run_cli)

  def start(self):
    self._app.run(host=self._host, port=self._port, reloader=True, debug=True)


  def list_cli(self):
    moduleList = []
    if self.conn == None:
      print "Error connecting to: %s" % self.cliDB
    else:
      cur = self.conn.cursor()
      self.conn.text_factory = str
      c = cur.execute('SELECT * from cloudmodules')
      modules = c.fetchall()
      print modules
      for module in modules:
        moduleDescription = ordereddict.OrderedDict()
        moduleDescription['modulename'] = module[0]
        moduleDescription['modulexml'] = module[1]
        #moduleDescription['modulename'] = module['modulename']
        #moduleDescription['modulexml'] = module['modulexml']
        moduleList.append(moduleDescription)
    return json.dumps(moduleList)

  def describe_cli(self, moduleName):
    if self.conn == None:
      print "Error connecting to: %s" % self.cliDB
      return ''
    else:
      cur = self.conn.cursor()
      self.conn.text_factory = str
      c = cur.execute('SELECT modulename, modulexml from cloudmodules WHERE modulename = ?', (moduleName,))
      row = c.fetchone()
      return row[1]

  def run_cli(self, commandString):
    print commandString

  def __del__(self):
    if self.conn:
      self.conn.close()

slicerserver = SlicerCloudServer(host='localhost', port=8080)
slicerserver.start()
