import datetime
endDay=datetime.datetime.strftime(datetime.date.today(), '%Y-%m-%dT%H:%M:%S')
#      datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%S')
print endDay

startday = datetime.datetime.strftime((datetime.date.today()) - (datetime.timedelta(days=1)), '%Y-%m-%dT%H:%M:%S')

print startday

#print "2014-07-31T23:59:59"

print datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%S')

#tendDay=datetime.datetime.strftime(datetime.datetime.time(), '%Y-%m-%dT%H:%M:%S')

#print tendDay