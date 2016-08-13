str="sdjh"
#str="0"
print "value for str :", str
print "TYPE OF str :", type(str).__name__

#print int("0")
#print str.__str__()
#print "str=", (str).__str__()
if not str:
    print "str is null"
else:
    print "string is not null"
    #if ((str != '') & (len('str')> 0)):
    try:
        if (int(str)> 0):
            print "data is true with no space value and no 0 value"
        else:
            print "it has zero value"
    except ValueError:
        print ValueError.__class__
        print ValueError.__doc__
#print int(str)
print int("0")
print type(int("0")).__name__

