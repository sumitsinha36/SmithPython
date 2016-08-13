import pytz, datetime
import time

a="2015-05-19T00:00:00Z"
naive_a = datetime.datetime.strptime (a, "%Y-%m-%dT%H:%M:%SZ")
print naive_a
b="2015-05-20T10:00:00Z"
naive_b = datetime.datetime.strptime (b, "%Y-%m-%dT%H:%M:%SZ")
print naive_b
delta =naive_b-naive_a

print "Total seconds for less then one day diff ",delta.seconds
print "Total seconds for days diff",delta.days*86400

print "Total seconds diff",delta.days*86400 + delta.seconds
