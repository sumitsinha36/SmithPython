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


#print data
#<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><GetAllSystemsResponse xmlns="http://www.tandberg.com/TMS/ManagementService/1.0/"><GetAllSystemsResult><ManagedSystem><Id>66</Id><MacAddress>00:50:60:81:56:7C</MacAddress><IPAddress>10.88.85.40</IPAddress><Name>MXP1700</Name><SystemType>TandbergMXP</SystemType><SystemCategory>EndPoint</SystemCategory><SystemTypeDescription>TANDBERG 1700MXP</SystemTypeDescription><Location><ISDNZoneId>-1</ISDNZoneId><IPZoneId>2</IPZoneId><TimeZoneId>8</TimeZoneId></Location><Authentication><Username>admin</Username><Password>********</Password></Authentication><Authentication8021X><Enabled>false</Enabled><Password /></Authentication8021X><Status><SystemStatus>Idle</SystemStatus><ConnectionStatus>OK</ConnectionStatus></Status><SystemCapabilites><SupportsBackup>true</SupportsBackup><SupportsTemplates>true</SupportsTemplates><SupportsRestart>true</SupportsRestart><SupportsIEEE8021x>true</SupportsIEEE8021x></SystemCapabilites><RequestedGatekeeperAddress /><ActiveGatekeeperAddress /><RequestedSIPServerAddress>10.88.84.135</RequestedSIPServerAddress><ActiveSIPServerAddress>10.88.84.135</ActiveSIPServerAddress><H323Id /><E164Alias /><SIPUri>4010@bclab.com</SIPUri></ManagedSystem><ManagedSystem><Id>65</Id><MacAddress>00:50:60:82:F0:5C</MacAddress><IPAddress>10.88.85.42</IPAddress><Name>TANDBERG Codec C90</Name><SystemType>TandbergCSeries</SystemType><SystemCategory>EndPoint</SystemCategory><SystemTypeDescription>TANDBERG Codec C90</SystemTypeDescription><Location><ISDNZoneId>-1</ISDNZoneId><IPZoneId>2</IPZoneId><TimeZoneId>8</TimeZoneId></Location><Authentication><Password>********</Password></Authentication><Authentication8021X><Enabled>false</Enabled><Password /></Authentication8021X><Status><SystemStatus>Unknown</SystemStatus><ConnectionStatus>WrongUsernamePassword</ConnectionStatus></Status><SystemCapabilites><SupportsBackup>true</SupportsBackup><SupportsTemplates>true</SupportsTemplates><SupportsRestart>true</SupportsRestart><SupportsIEEE8021x>true</SupportsIEEE8021x></SystemCapabilites><RequestedGatekeeperAddress>10.88.84.135</RequestedGatekeeperAddress><ActiveGatekeeperAddress /><RequestedSIPServerAddress>10.88.84.133</RequestedSIPServerAddress><ActiveSIPServerAddress>10.88.84.133</ActiveSIPServerAddress><H323Id /><E164Alias>4037</E164Alias><SIPUri>4037@bclab.com</SIPUri></ManagedSystem><ManagedSystem><Id>68</Id><MacAddress>00:10:F3:1E:D2:7C</MacAddress><IPAddress>10.88.84.133</IPAddress><Name>vcs133</Name><SystemType>TandbergVCS</SystemType><SystemCategory>Gatekeeper</SystemCategory><SystemTypeDescription>TANDBERG VCS</SystemTypeDescription><Location><ISDNZoneId>-1</ISDNZoneId><IPZoneId>2</IPZoneId><TimeZoneId>8</TimeZoneId></Location><Authentication><Username>admin</Username><Password>********</Password></Authentication><Status><SystemStatus>Idle</SystemStatus><ConnectionStatus>OK</ConnectionStatus></Status><SystemCapabilites><SupportsBackup>true</SupportsBackup><SupportsTemplates>true</SupportsTemplates><SupportsRestart>true</SupportsRestart><SupportsIEEE8021x>false</SupportsIEEE8021x></SystemCapabilites><RequestedGatekeeperAddress /><ActiveGatekeeperAddress /><RequestedSIPServerAddress /><ActiveSIPServerAddress /></ManagedSystem></GetAllSystemsResult></GetAllSystemsResponse></soap:Body></soap:Envelope>
document = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><GetAllSystemsResponse xmlns="http://www.tandberg.com/TMS/ManagementService/1.0/">
                <GetAllSystemsResult>
                    <ManagedSystem><Id>66</Id>
                        <MacAddress>00:50:60:81:56:7C</MacAddress>
                        <IPAddress>10.88.85.40</IPAddress>
                        <Name>MXP1700</Name>
                        <SystemType>TandbergMXP</SystemType>
                        <SystemCategory>EndPoint</SystemCategory>
                        <SystemTypeDescription>TANDBERG 1700MXP</SystemTypeDescription>
                        <Location>
                            <ISDNZoneId>-1</ISDNZoneId>
                            <IPZoneId>2</IPZoneId>
                            <TimeZoneId>8</TimeZoneId>
                        </Location>
                        <Authentication>
                            <Username>admin</Username>
                            <Password>********</Password>
                        </Authentication>
                        <Authentication8021X>
                            <Enabled>false</Enabled>
                            <Password />
                        </Authentication8021X>
                        <Status>
                            <SystemStatus>Idle</SystemStatus>
                            <ConnectionStatus>OK</ConnectionStatus>
                        </Status>
                        <SystemCapabilites>
                            <SupportsBackup>true</SupportsBackup>
                            <SupportsTemplates>true</SupportsTemplates>
                            <SupportsRestart>true</SupportsRestart>
                            <SupportsIEEE8021x>true</SupportsIEEE8021x>
                        </SystemCapabilites>
                        <RequestedGatekeeperAddress />
                        <ActiveGatekeeperAddress />
                        <RequestedSIPServerAddress>10.88.84.135</RequestedSIPServerAddress>
                        <ActiveSIPServerAddress>10.88.84.135</ActiveSIPServerAddress>
                        <H323Id />
                        <E164Alias />
                        <SIPUri>4010@bclab.com</SIPUri>
                    </ManagedSystem>
                    <ManagedSystem><Id>65</Id><MacAddress>00:50:60:82:F0:5C</MacAddress><IPAddress>10.88.85.42</IPAddress><Name>TANDBERG Codec C90</Name><SystemType>TandbergCSeries</SystemType><SystemCategory>EndPoint</SystemCategory><SystemTypeDescription>TANDBERG Codec C90</SystemTypeDescription><Location><ISDNZoneId>-1</ISDNZoneId><IPZoneId>2</IPZoneId><TimeZoneId>8</TimeZoneId></Location><Authentication><Password>********</Password></Authentication><Authentication8021X><Enabled>false</Enabled><Password /></Authentication8021X><Status><SystemStatus>Unknown</SystemStatus><ConnectionStatus>WrongUsernamePassword</ConnectionStatus></Status><SystemCapabilites><SupportsBackup>true</SupportsBackup><SupportsTemplates>true</SupportsTemplates><SupportsRestart>true</SupportsRestart><SupportsIEEE8021x>true</SupportsIEEE8021x></SystemCapabilites><RequestedGatekeeperAddress>10.88.84.135</RequestedGatekeeperAddress><ActiveGatekeeperAddress /><RequestedSIPServerAddress>10.88.84.133</RequestedSIPServerAddress><ActiveSIPServerAddress>10.88.84.133</ActiveSIPServerAddress><H323Id /><E164Alias>4037</E164Alias><SIPUri>4037@bclab.com</SIPUri></ManagedSystem><ManagedSystem><Id>68</Id><MacAddress>00:10:F3:1E:D2:7C</MacAddress><IPAddress>10.88.84.133</IPAddress><Name>vcs133</Name><SystemType>TandbergVCS</SystemType><SystemCategory>Gatekeeper</SystemCategory><SystemTypeDescription>TANDBERG VCS</SystemTypeDescription><Location><ISDNZoneId>-1</ISDNZoneId><IPZoneId>2</IPZoneId><TimeZoneId>8</TimeZoneId></Location><Authentication><Username>admin</Username><Password>********</Password></Authentication><Status><SystemStatus>Idle</SystemStatus><ConnectionStatus>OK</ConnectionStatus></Status><SystemCapabilites><SupportsBackup>true</SupportsBackup><SupportsTemplates>true</SupportsTemplates><SupportsRestart>true</SupportsRestart><SupportsIEEE8021x>false</SupportsIEEE8021x></SystemCapabilites><RequestedGatekeeperAddress /><ActiveGatekeeperAddress /><RequestedSIPServerAddress /><ActiveSIPServerAddress /></ManagedSystem></GetAllSystemsResult></GetAllSystemsResponse></soap:Body></soap:Envelope>


"""

xml = xml.dom.minidom.parseString(document)
#pretty_xml_as_string = xml.toprettyxml()
#print pretty_xml_as_string

for s in xml.getElementsByTagName('Id'):
    print s.childNodes[0].data

print "Today"


























