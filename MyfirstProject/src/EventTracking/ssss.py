import re
response=""" <methodResponse>
    <fault>
        <value>
            <struct>
                <member>
                    <name>faultCode</name>
                    <value>
                        <int>14</int>
                    </value>
                </member>
                <member>
                    <name>faultString</name>
                    <value>
                        <string>authorization failed</string>
                    </value>
                </member>
            </struct>
        </value>
    </fault>
</methodResponse> """
reg_ex = re.compile(r'.*<string>authorization failed</string>.*', re.IGNORECASE)
if reg_ex.search(response):
    print reg_ex.search(response).group(0)
    if reg_ex.search(response).group(0).strip() == '<string>authorization failed</string>' :
        print "API,check the credentials",(reg_ex.search(response).group(0).strip())
