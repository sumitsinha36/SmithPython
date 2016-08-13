import urllib2

url= "https://x.x.x.x/status.xml"

username="xxxxx"
password="xxxxx"
password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, url, username, password)
handler = urllib2.HTTPBasicAuthHandler(password_mgr)
opener = urllib2.build_opener(handler)
urllib2.install_opener(opener)

response=urllib2.urlopen(url)
html = response.read()

print html
print "done"
