from xml.dom import minidom

xmldoc = minidom.parse('japanlang.xml')

title = xmldoc.getElementsByTagName('title')[0].firstChild.data

print title.encode("utf-8")


