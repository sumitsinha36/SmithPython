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
import datetime
#import MySQLdb

"""Remove namespace in the passed document in place."""
def remove_namespace(doc, namespace):
    ns = u'{%s}' % namespace
    nsl = len(ns)
    for elem in doc.getiterator():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]


#myDB = MySQLdb.connect(host="10.88.138.251", port=7706, user="root", passwd="em7admin")
#cHandler=myDB.cursor()
#cHandler.execute("select eid from out_messages.spool_mail")
#results1=cHandler.fetchall()
#list1_ip=[]
#for items in results1:
#  list1_ip.append(items[0])
#print(list1_ip)

#GetAllSystems
data="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.tandberg.com/TMS/ManagementService/1.0/"><soapenv:Header/><soapenv:Body><ns:GetAllSystems/></soapenv:Body></soapenv:Envelope>"""

headers = {'Content-Type': 'text/xml; charset=utf-8'}
url='http://10.88.84.57/tms/external/management/managementservice.asmx'


password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, url, "administrator", "TMS4lab")
handler = urllib2.HTTPBasicAuthHandler(password_mgr)

opener = urllib2.build_opener(handler)
opener.open(url)
urllib2.install_opener(opener)


request = urllib2.Request(url, data, headers)
response = urllib2.urlopen(request)
data = response.read()
print data
#<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><GetAllSystemsResponse xmlns="http://www.tandberg.com/TMS/ManagementService/1.0/"><GetAllSystemsResult><ManagedSystem><Id>66</Id><MacAddress>00:50:60:81:56:7C</MacAddress><IPAddress>10.88.85.40</IPAddress><Name>MXP1700</Name><SystemType>TandbergMXP</SystemType><SystemCategory>EndPoint</SystemCategory><SystemTypeDescription>TANDBERG 1700MXP</SystemTypeDescription><Location><ISDNZoneId>-1</ISDNZoneId><IPZoneId>2</IPZoneId><TimeZoneId>8</TimeZoneId></Location><Authentication><Username>admin</Username><Password>********</Password></Authentication><Authentication8021X><Enabled>false</Enabled><Password /></Authentication8021X><Status><SystemStatus>Idle</SystemStatus><ConnectionStatus>OK</ConnectionStatus></Status><SystemCapabilites><SupportsBackup>true</SupportsBackup><SupportsTemplates>true</SupportsTemplates><SupportsRestart>true</SupportsRestart><SupportsIEEE8021x>true</SupportsIEEE8021x></SystemCapabilites><RequestedGatekeeperAddress /><ActiveGatekeeperAddress /><RequestedSIPServerAddress>10.88.84.135</RequestedSIPServerAddress><ActiveSIPServerAddress>10.88.84.135</ActiveSIPServerAddress><H323Id /><E164Alias /><SIPUri>4010@bclab.com</SIPUri></ManagedSystem><ManagedSystem><Id>65</Id><MacAddress>00:50:60:82:F0:5C</MacAddress><IPAddress>10.88.85.42</IPAddress><Name>TANDBERG Codec C90</Name><SystemType>TandbergCSeries</SystemType><SystemCategory>EndPoint</SystemCategory><SystemTypeDescription>TANDBERG Codec C90</SystemTypeDescription><Location><ISDNZoneId>-1</ISDNZoneId><IPZoneId>2</IPZoneId><TimeZoneId>8</TimeZoneId></Location><Authentication><Password>********</Password></Authentication><Authentication8021X><Enabled>false</Enabled><Password /></Authentication8021X><Status><SystemStatus>Unknown</SystemStatus><ConnectionStatus>WrongUsernamePassword</ConnectionStatus></Status><SystemCapabilites><SupportsBackup>true</SupportsBackup><SupportsTemplates>true</SupportsTemplates><SupportsRestart>true</SupportsRestart><SupportsIEEE8021x>true</SupportsIEEE8021x></SystemCapabilites><RequestedGatekeeperAddress>10.88.84.135</RequestedGatekeeperAddress><ActiveGatekeeperAddress /><RequestedSIPServerAddress>10.88.84.133</RequestedSIPServerAddress><ActiveSIPServerAddress>10.88.84.133</ActiveSIPServerAddress><H323Id /><E164Alias>4037</E164Alias><SIPUri>4037@bclab.com</SIPUri></ManagedSystem><ManagedSystem><Id>68</Id><MacAddress>00:10:F3:1E:D2:7C</MacAddress><IPAddress>10.88.84.133</IPAddress><Name>vcs133</Name><SystemType>TandbergVCS</SystemType><SystemCategory>Gatekeeper</SystemCategory><SystemTypeDescription>TANDBERG VCS</SystemTypeDescription><Location><ISDNZoneId>-1</ISDNZoneId><IPZoneId>2</IPZoneId><TimeZoneId>8</TimeZoneId></Location><Authentication><Username>admin</Username><Password>********</Password></Authentication><Status><SystemStatus>Idle</SystemStatus><ConnectionStatus>OK</ConnectionStatus></Status><SystemCapabilites><SupportsBackup>true</SupportsBackup><SupportsTemplates>true</SupportsTemplates><SupportsRestart>true</SupportsRestart><SupportsIEEE8021x>false</SupportsIEEE8021x></SystemCapabilites><RequestedGatekeeperAddress /><ActiveGatekeeperAddress /><RequestedSIPServerAddress /><ActiveSIPServerAddress /></ManagedSystem></GetAllSystemsResult></GetAllSystemsResponse></soap:Body></soap:Envelope>

xml = xml.dom.minidom.parseString(data)
#pretty_xml_as_string = xml.toprettyxml()
#print xml
list_id=[];
list_ipAddr=[];
list_name=[];
list_SystemStatus=[];
list_SystemTypeDescription=[];
list_TimeZoneId=[];
list_H323Id=[];

for s in xml.getElementsByTagName('Id'):
    list_id.append(s.childNodes[0].data)
print "system id: ", list_id

for s in xml.getElementsByTagName('IPAddress'):
    list_ipAddr.append(s.childNodes[0].data)
print "Ip Address : ", list_ipAddr

for s in xml.getElementsByTagName('Name'):
    list_name.append(s.childNodes[0].data)
print "Name:", list_name

for s in xml.getElementsByTagName('SystemStatus'):
    list_SystemStatus.append(s.childNodes[0].data)
print "SystemStatus:", list_SystemStatus

for s in xml.getElementsByTagName('SystemTypeDescription'):
    list_SystemTypeDescription.append(s.childNodes[0].data)
print "SystemTypeDescription:", list_SystemTypeDescription

for s in xml.getElementsByTagName('TimeZoneId'):
    list_TimeZoneId.append(s.childNodes[0].data)
print "TimeZoneId:", list_TimeZoneId

#for s in xml.getElementsByTagName('H323Id'):
#    list_H323Id.append(s.childNodes[0].data)
#print "H323Id:",list_H323Id
#data=
"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:book="http://tandberg.net/2004/02/tms/external/booking/"><soapenv:Header/><soapenv:Body><book:GetConferencesForSystems><book:StartTime>""" +startday +"""</book:StartTime><book:EndTime>"""+ endDay +"""</book:EndTime><book:ConferenceStatus>All</book:ConferenceStatus></book:GetConferencesForSystems></soapenv:Body></soapenv:Envelope>"""
"""
#EndTime,StartTime format:  2014-07-31T23:59:59
endDay=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%S')
startday = datetime.datetime.strftime((datetime.date.today()) - (datetime.timedelta(days=1)), '%Y-%m-%dT%H:%M:%S')
startday = "2014-07-01T00:00:00"
print "\nStart Time ", startday
print "\nEnd Time", endDay

#ConferenceStatus all

data=
headers = {'Content-Type': 'text/xml; charset=utf-8'}
url='http://10.88.84.57/tms/external/Booking/BookingService.asmx'

password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, url, "administrator", "TMS4lab")
handler = urllib2.HTTPBasicAuthHandler(password_mgr)

opener = urllib2.build_opener(handler)
opener.open(url)
urllib2.install_opener(opener)

request = urllib2.Request(url, data, headers)
response = urllib2.urlopen(request)
#response

dataForSystems = response.read()
dataForSystems.replace('&', '&')
if dataForSystems=="":
        logging.info("There is no data available for dataForSystems.xml")
else:
        xmlForSystems = ET.fromstring(dataForSystems)
        print xmlForSystems
        remove_namespace(xmlForSystems.find("."), u'http://www.w3.org/2001/XMLSchema')
        remove_namespace(xmlForSystems.find("."), u'http://schemas.xmlsoap.org/soap/envelope/')
        remove_namespace(xmlForSystems.find("."), u'http://tandberg.net/2004/02/tms/external/booking/')


print "data for system"
print xmlForSystems
print xmlForSystems.findall("./Envelope/Body/GetConferencesForSystemsResponse/GetConferencesForSystemsResult/Conference/Title")
"""
#xmlForSystems = xml.dom.minidom.parseString(dataForSystems)


#pretty_xml_as_string = xmlForSystems.toprettyxml()
#print pretty_xml_as_string

#print "op"
#print xmlForSystems

#for element in tree.findall("Title"):


#print xmlForSystems.find('./Envelope/Body/GetConferencesForSystemsResponse/GetConferencesForSystemsResult/Conference/Title').text

#print xmlForSystems.findall("./Envelope/Body/GetConferencesForSystemsResponse/GetConferencesForSystemsResult/Conference/Title")
#Conference


print "End of code"














