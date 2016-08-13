txt = """<?xml version='1.0'?>
<methodResponse>
<fault>
<value><struct>
<member>
<name>faultCode</name>
<value><int>14</int></value>
</member>
<member>
<name>faultString</name>
<value><string>Authentication failure</string></value>
</member>
</struct></value>
</fault>
</methodResponse>"""

print txt.find("Authentication failure")
print txt.find("<string>")

print txt.find("faultCode")

print txt.find("sumit kumar sinha")
print txt.find("s")
print txt.find("sumit")