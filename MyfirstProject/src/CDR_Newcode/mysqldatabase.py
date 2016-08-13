#!/usr/bin/python
import MySQLdb
import sys

myDB = MySQLdb.connect(host="10.201.148.67",port=7706,user="root",passwd="em7admin",db="master")
cursor = myDB.cursor()

#cursor.execute("select name from master.dynamic_app")
#data = cursor.fetchone()
#print "Result : %s " % data

cursor.execute("use master")
data = cursor.fetchone()

print "Result : %s " % data


myDB.close()


