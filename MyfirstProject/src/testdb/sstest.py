import calendar
import time

print "RESULT"

localtime=time.strptime("11/5/2014  11:30:00 PM", "%m/%d/%Y %I:%M:%S %p")
ltime=time.strftime("%m/%d/%Y %I:%M:%S %p", localtime)
print "cur time Value : ", ltime

temp = time.strptime(ltime, "%m/%d/%Y %I:%M:%S %p")
t = calendar.timegm(temp)
t +=time.timezone
temp = time.gmtime(t)
z= time.strftime("%m/%d/%Y %I:%M:%S %p", temp)

print "GMT Time Value: ", z
