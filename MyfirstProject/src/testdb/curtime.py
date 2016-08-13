import calendar
import time

print "RESULT"


cur_time= time.strftime("%m/%d/%Y %I:%M:%S %p")
print "cur timw", cur_time


temp = time.strptime(cur_time, "%m/%d/%Y %I:%M:%S %p")
t = calendar.timegm(temp)
t +=time.timezone
temp = time.gmtime(t)
z= time.strftime("%m/%d/%Y %I:%M:%S %p", temp)

print "GMT Time Value: ", z
