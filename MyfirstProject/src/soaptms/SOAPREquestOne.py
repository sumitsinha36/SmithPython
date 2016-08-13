import silo_common.logger as dynapp_log
import urllib
import urllib2
import xml.dom.minidom as md
import xml.dom.minidom
from pprint import pprint
import itertools
from itertools import izip
from collections import defaultdict
import json, ast
import re
import xml.etree.ElementTree as ET
import MySQLdb

import logging
logging.basicConfig(filename='/tmp/sumitLogTMS_FIRST.log', level=logging.DEBUG)
app_name = "My App"
logging.info("sumit logging code is working fine.....   ")
logging.info(" sumit Starting Journal App : %s" , app_name)


#myDB = MySQLdb.connect(host="10.40.204.166", port=7706, user="root", passwd="em7admin")
myDB = MySQLdb.connect(host="10.88.138.251", port=7706, user="root", passwd="em7admin")
cHandler=myDB.cursor()


cHandler.execute("select eid from out_messages.spool_mail")
results1=cHandler.fetchall()
list1_ip=[]
for items in results1:
  list1_ip.append(items[0])

logging.info(list1_ip)


my_host_ip = '10.88.138.251'
my_user = 'root'
my_password = 'em7admin'

data="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.tandberg.com/TMS/ManagementService/1.0/"><soapenv:Header/><soapenv:Body><ns:GetAllSystems/></soapenv:Body></soapenv:Envelope>"""

headers = {'Content-Type': 'text/xml; charset=utf-8'}
url='http://10.88.84.57/tms/external/management/managementservice.asmx'

logging.info("sumit 1")
password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, url, "administrator", "TMS4lab")
handler = urllib2.HTTPBasicAuthHandler(password_mgr)

logging.info("sumit  received handler")

opener = urllib2.build_opener(handler)
opener.open(url)
urllib2.install_opener(opener)


request = urllib2.Request(url, data, headers)
logging.info("\nsumit request")
response = urllib2.urlopen(request)
logging.info("\nsumit response %s", response)
data = response.read()
logging.info("\nsumit data %s", data)

getAllSystemsResult = ET.fromstring(data)
logging.info("\ngetAllSystemsResult:  %s",getAllSystemsResult)

for managedSystem in getAllSystemsResult.findall('ManagedSystem'):
    logging.info("\nmanagedSystem.managedSystem:  %s", managedSystem.tag)
    id = managedSystem.find('ID').text
    ipAddress = managedSystem.find('IPAddress').text
    logging.info("\nID :  %s",id)
    logging.info("\nIP Address:  %s",ipAddress)
    
logging.info("\nend of log\n") 
#getManagedSystem = 
#part1=data.split('</ManagedSystem>')
#logging.info("\nsumit part1 %s", part1)
#sid=part1[0].split('<Id>')
#logging.info("\nsumit sid %s", sid)
#sid=part1[0].split('<IPAddress>')
#logging.info("\nsumit IPAddress %s", sid)

























