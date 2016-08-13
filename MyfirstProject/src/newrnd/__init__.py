import re
from xml.etree import ElementTree

response="""<?xml version='1.0'?>
<methodResponse>
    <fault>
        <value>
            <struct>
                <member>
                    <name>faultCode</name>
                    <value><int>14</int></value>
                </member>
                <member>
                    <name>faultString</name>
                    <value>
                        <string>Authentication failure</string>
                    </value>
                </member>
            </struct>
        </value>
    </fault>
</methodResponse>"""

xml = ElementTree.fromstring(response)
#print xml

node=ElementTree.fromstring('<a><b>bum</b><b>ear</b><c/></a>')
node.findtext('b')





tree = ElementTree.parse(response)

for network in tree.findall('.//methodResponse'):
    for name in network.findall('.//fault'):
        for value in name.findall('.//value'):
            for struct in value.findall('.//struct'):
                for member in struct.findall('.//member'):
                    for value in member.findall('.//value'):
                        for string in value.findall('.//string'):
                            if string.text is not None and 'Authentication failure' in name.text:
                                print string.text





