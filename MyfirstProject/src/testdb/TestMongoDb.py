import pymongo
import datetime

from pymongo import MongoClient
#client=MongoClient("mongodb://localhost:27017/")
client = MongoClient("10.77.202.107", 27017)
db=client["testdb"]
collection=db["mycollection"]

#poll=client.db.mycollection.find({"name" : "sumit"})

####While loop
#while (poll.hasNext() )
#    {
#     print "name :",( poll.next() )
#     }

#### code to fetch data from MongoDB
#for item in db.mycollection.find():
#        print "name:",item["name"]

try:
    #db.mycollection.insert(data, safe=True)

    # do this bellow commmand on Mongo console to make index . which stop inserting duplicate data again on Upsert
    #db.mycollection.ensureIndex( { "slno": 1 }, { "unique": "true" } )

    db.mycollection.update(
         {
         "slno":2,
         "Host Name":"sumitksi-ws",
         "IPv4 Address": "10.77.202.107",
         "Subnet Mask":"255.255.255.0",
         "Physical Address":"44-37-E6-6B-73-13",
         "Primary Dns Suffix":"partnet.cisco.com",
         "DHCP Enabled":"Yes",
         "Autoconfiguration Enabled":"Yes",
         #"occurrence":1
         },
         {"$inc": {"occurrence":1}},
         True)
    print 'Message Successfully written in MongoDB database '
    #break # Exit the retry loop
except pymongo.errors.AutoReconnect, e:
    print 'Warning', e
    time.sleep(5)






