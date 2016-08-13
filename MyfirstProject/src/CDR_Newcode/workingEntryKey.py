collection_entry={}


dict={}
count =dict.__len__()
for x in [1,2,3,4]:
    list_a=[x,x+1,x+2]
    dict[count] = list_a
    count=count+1


for d in dict:
    print d,dict[d]
print "count 1= ",count

count =dict.__len__()
for x in [1,2,3,4]:
    list_a=[x,x+1,x+2]
    dict[count] = list_a
    count=count+1

for d in dict:
    print d,dict[d]
print "count 2= ",count

count =dict.__len__()
for x in [1,2,3,4]:
    list_a=[x,x+1,x+2]
    dict[count] = list_a
    count=count+1

for d in dict:
    print d,dict[d]
print "count 3= ",count