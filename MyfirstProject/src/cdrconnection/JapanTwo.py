# -*- coding: utf-8 -*-

print "Sumit Kumar Sinha"
import sys
print sys.getdefaultencoding()

from xml.dom import minidom

xmldoc = minidom.parse('japan2.xml')

title = xmldoc.getElementsByTagName('title')[0].firstChild.data

print title.encode("utf-8")



#from lxml import etree
#from lxml import objectify
#content = u'<?xml version="1.0" encoding="utf-8"?><div>Order date : 05/08/2013 12:24:28</div>'
#mail.replace('\xa0',' ')
#xml = etree.fromstring(mail)

