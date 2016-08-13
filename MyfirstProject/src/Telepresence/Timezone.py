import calendar
import time

def convert_ts(timestamp, change):
    temp = time.strptime(timestamp, "%m/%d/%Y %I:%M:%S %p")
    t = calendar.timegm(temp)
    t += change
    temp = time.gmtime(t)
    z= time.strftime("%m/%d/%Y %I:%M:%S %p", temp)
    print "GMT Time Value: ", z


print "RESULT"

localtime=time.strptime("11/5/2014  11:30:00 PM", "%m/%d/%Y %I:%M:%S %p")
ltime=time.strftime("%m/%d/%Y %I:%M:%S %p", localtime)
print "cur time Value : ", ltime

convert_ts(ltime, time.timezone)






#ticks = time.time()
#print "Number of ticks since 12:00am, January 1, 1970:", ticks



def convert_ts1(timestamp):
    print "LOcal Time :", timestamp
    t = calendar.timegm(timestamp)

    localss=time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime(t))
    print "in GMT time : ", localss


#cur_time= time.strftime("%m/%d/%Y %I:%M:%S")
#print time.timezone

#convert_ts1(cur_time)



 #   GMTtime = time.asctime(time.gmtime())
#    print "GMT time :",GMTtime
   # gmtss=time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime(GMTtime))
    #print "GMT time :", gmtss






