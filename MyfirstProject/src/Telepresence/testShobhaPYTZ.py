#for x in xrange(1, 11):
#    for y in xrange(1, 11):
#                print  "SUMIT 0"
#                print '%d * %d = %d' % (x, y, x*y)
#    print "sumit 1"
#print "sinha"




def proc_bitrate_val(val):
        try: resolution = (float(val) < 4000) and "720P" or "1080P"
        #except (TypeError, ValueError): resolution = " "
        except (TypeError, ValueError): resolution = "N/A"
        return {"value": val, "res": resolution}

proc_bitrate_val(5000)

print proc_bitrate_val(1000)

print proc_bitrate_val(5000)

print proc_bitrate_val(' ')




