import pytz, datetime

local = pytz.timezone ("America/Chicago")
endPointTime="2015-04-27T06:16:30Z"
#2015-04-20T16:18:46Z

#naive = datetime.datetime.strptime ("2015-04-20T16:18:46Z", "%Y-%m-%dT%H:%M:%SZ")
naive = datetime.datetime.strptime (endPointTime, "%Y-%m-%dT%H:%M:%SZ")
local_dt = local.localize(naive, is_dst=None)
print "Local time : ",local_dt
utc_dt = local_dt.astimezone (pytz.utc)
print "UTC time : ",utc_dt

#IST_dt = local_dt.astimezone (pytz.ist)
#print "IST time : ",utc_dt
local = pytz.timezone ("Indian/Antananarivo")
local_dt = local.localize(naive, is_dst=None)
print "Indian/Antananarivo time : ",local_dt

#for timezones in pytz.all_timezones:
#    print  timezones




#import datetime
#time='2015-04-20T16:18:46Z'
#time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seconds))
#"2015-04-20T16:18:46Z".strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seconds))

#from time import strftime, gmtime, localtime
#time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seconds))