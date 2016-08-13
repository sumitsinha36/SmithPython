import re

text = 'Video Stream Packet Loss Cleared  for Primary Codec. Index: .864.1.2; Message: Trap Received: ctpcStatNotificaion | Trap Detail: ctpcStatEventMonObjectInst: .1.3.6.1.4.1.9.9.644.1.4.10.1.14.864.1.2; ctpcStatEventCrossedValue: 13326653; ctpcStatEventCrosse'
m = re.search('(.*?) Cleared (.*?) Index:(.*?); Message: (.*?);', text)

if m:
    print m.group(1)
    print m.group(2)
    print m.group(3)
    print m.group(4)

str=m.group(1)+ " Occurred " + m.group(2)+ " Index:"+ m.group(3)+ "; "+m.group(4)

print str


