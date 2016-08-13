import logging
logging.basicConfig(filename='cdr.log',level=logging.DEBUG)
logging.debug("Sumit has start working here")

dict={}
count =dict.__len__()
logging.debug("count 0 =")
logging.debug(count)

for x in [1,2,3,4]:
    list_a=[x,x+1,x+2]
    dict[count] = list_a
    count=count+1

for d in dict:
    logging.debug(d)
    logging.debug(dict[d])

logging.debug("count 1= ")
logging.debug(count)




