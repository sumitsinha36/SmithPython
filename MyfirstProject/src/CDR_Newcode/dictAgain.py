
#dict={list:[]}
dict={}
count =dict.__len__()
print "count 0= ",count
for x in [1,2,3,4]:
    list_a=[x,x+1,x+2]
    dict[count] = list_a
    count=count+1

#dicts={list:[]}
for d in dict:
    print "row number : ",d
    print d,dict[d]
    for x in dict[d]:
        print x

print dict