#!/usr/bin/python
import MySQLdb

# connect
#db = MySQLdb.connect(host="10.201.148.115", user="root", passwd="em7admin",db="master")

myDB = MySQLdb.connect(host="10.201.148.115",port=7706,user="root",passwd="em7admin",db="master")
cHandler = myDB.cursor()
cHandler.execute("SHOW DATABASES")
results = cHandler.fetchall()

list_databases = []
for items in results:
    list_databases.append(items[0])

print list_databases

#    list_app_id.append(app_id[0].__int__())

#print list_app_id