a = [1,2,3,4]
b = [17,12,11,10]
c = [-1,-4,5,9]
listvar=map(lambda x,y:x+y, a,b)
print listvar

lista=[1,2,3,4,5,6,7,8,9,10]
paharavar=2
pahara=map(lambda x:x*paharavar,lista)
print pahara

fileredlist=filter(lambda x:x%2,lista)
print fileredlist

reducedvalue=reduce(lambda x,y:x+y,lista)
print reducedvalue



