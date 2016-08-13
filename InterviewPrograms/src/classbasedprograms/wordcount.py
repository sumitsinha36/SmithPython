str='sumit kumar sinha sumit kumar sinha sumit kumar sinha'
print str

strs=str.split(' ')
print strs

dict={}

for s in strs:
    if(dict.__contains__(s)):
        print 'item already available as key=',s,', Value =',dict.__getitem__(s)
    if(dict.__contains__(s)):
        dict[s]=dict.__getitem__(s)+1;
    else:
        dict[s]=1;



print dict

print dict.keys()
print dict.__contains__('name')

print dict.__len__()
print dict.__str__()







