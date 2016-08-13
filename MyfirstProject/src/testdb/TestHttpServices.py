# simply send a message on HTTP browser ...

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json

PORT_NUMBER = 8080

jsonfiles = []
data={"slno": 2,
"Host Name": "sumitksi-ws",
"IPv4 Address": "10.77.202.107",
"Subnet Mask": "255.255.255.0",
"Physical Address": "44-37-E6-6B-73-13",
"Primary Dns Suffix": "partnet.cisco.com",
"DHCP Enabled": "Yes",
"Autoconfiguration Enabled": "Yes",
"occurrence": 1}

#This class will handles any incoming request from the browser
class myHandler(BaseHTTPRequestHandler):

    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        #self.wfile.write("\nHello Sumit Sinha.. Now You are Here !!!<br>") # Send the html message
        self.wfile.write(data)
        #self.wfile.write("<br>Here I'm Done")
        return

try:
    #Create a web server and define the handler to manage the incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ' , PORT_NUMBER

    #Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()
