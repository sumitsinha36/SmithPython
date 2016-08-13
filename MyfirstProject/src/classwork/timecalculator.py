import datetime
import time

print "test: ",time.gmtime(1000000)

datetimestring = 'Mon, 28 Dec 2015 10:52:26'

Check_in_timestamp = time.mktime(time.strptime(datetimestring, '%a, %d %b %Y %H:%M:%S'))
print "Check in Time :",Check_in_timestamp
#print "Check in Time :",datetime.datetime.utctimetuple(Check_in_timestamp,"%a, %d %b %Y %H:%M:%S")
datetimestring = '2015-12-28 18:27:10'

Check_in_timestamp = time.mktime(time.strptime(datetimestring, '%Y %M %DD %H:%M:%S'))
print "Check in Time :",Check_in_timestamp

Check_out_timestamp = datetime.datetime.now()
print "Check out Time:",Check_out_timestamp

print datetime.datetime
#datetimestring = 'Fri, 08 Jun 2012 22:40:26 GMT'
#dt = dateparser.parse(datetimestring)
#timestamp = int(time.mktime(dt.timetuple()))






