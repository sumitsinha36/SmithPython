import pycurl
import urllib
import StringIO
c = pycurl.Curl()

c.setopt(pycurl.URL, "https://10.88.84.120")
c.setopt(pycurl.SSL_VERIFYPEER, 0)
c.setopt(pycurl.SSL_VERIFYHOST, 0)
pf = {'userName' : 'admin', 'password.password' : 'cisco!123' }
fields = urllib.urlencode(pf)
c.setopt(pycurl.URL, "https://10.88.84.120/adminui/loginAction.do?buttonAction=login")
c.setopt(pycurl.POSTFIELDS, fields)
import StringIO
b = StringIO.StringIO()
c.setopt(pycurl.WRITEFUNCTION, b.write)
c.setopt(pycurl.FOLLOWLOCATION, 1)
c.setopt(pycurl.MAXREDIRS, 5)
