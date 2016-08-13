from collections import Counter
import collections
#from collections import list

c=Counter(a=4,b=2,c=0,d=0)
print list(c.elements())



cnt=Counter()
lst=['sumit', 'sumit', 'sumit', 'sinha', 'sinha', 'kumar','sumit', 'sumit', 'sumit', 'sinha', 'sinha', 'kumar']

for word in lst:
    cnt[word]+=1

print cnt

for key in cnt:
    print "Word = : ",key," of count= ",cnt[key]

import re
word=re.findall(r'\w+', open('TestFile.txt').read().lower())
#print Counter(word)
#print Counter(word).most_common(2)
#print sum(Counter(word).value())
#print "list(Counter(word)) : ",list(Counter(word))
#print "set(Counter(word)) : ",set(Counter(word))
print "\n dict(Counter(word)) : ",dict(Counter(word))
#print "Counter(word).items() : ",Counter(word).items()

#for key,value in dict(Counter(word)).iteritems():
    #if type(value) is dict:
        #for k,v in value:
            #print "\n k=",k,"\t v",v
    #else:
        #print "\n key= ",key,"\t value : ",value

#wordPattern=re.finditer(r'\w+', open('TestFile.txt').read().lower())
#print Counter(wordPattern)
#print Counter(wordPattern).most_common(2)










