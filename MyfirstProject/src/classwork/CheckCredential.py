import urllib2
import libxml2
import libxslt

url= "https://10.88.84.62/RPC2/"

username="admin"
#password="CC4lab"
password="CC4"
password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, url, username, password)
handler = urllib2.HTTPBasicAuthHandler(password_mgr)
opener = urllib2.build_opener(handler)
urllib2.install_opener(opener)

response=urllib2.urlopen(url)
response = response.read()
stylesheetArgs = {}
doc = libxml2.parseDoc(response)
print doc
print "done"


