from xml.dom import minidom

xmldoc = minidom.parse('japan2.xml')

title = xmldoc.getElementsByTagName('DisplayName')[0].firstChild.data

print title.encode('utf-8')

print title.encode('Shift-JIS')