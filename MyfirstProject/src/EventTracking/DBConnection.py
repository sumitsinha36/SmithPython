#!/usr/bin/python
import MySQLdb
from collections import defaultdict
import logging

logging.basicConfig(filename='cdr.log',level=logging.DEBUG)
logging.debug("Sumit has start working here")

myDB = MySQLdb.connect(host="10.201.148.67",port=7706,user="root",passwd="em7admin",db="master")
cHandler = myDB.cursor()

list_call_dicts=[]
app_sql="select aid,name from master.dynamic_app where app_guid='9E9ACD6B19ADD2EB7DA7720D702D454A'"
cHandler.execute(app_sql)

for app_ids in cHandler.fetchall():
    app_id=app_ids[0].__int__()
    app_name=app_ids[1].__str__()