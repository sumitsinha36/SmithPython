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

# Have to merge with the Select SQL
cHandler.execute("use dynamic_app_data_"+str(app_id))
#for did in result:
sql="SELECT count(*) FROM information_schema.tables WHERE table_schema = 'dynamic_app_data_%s' AND table_name like '%s' and table_name not like '%s'"%(app_id,'dev_journals_%','dev_journals_c%')
cHandler.execute(sql)
number_of_device_assoicated=0

for collection_exist in cHandler.fetchall():
    number_of_device_assoicated= collection_exist[0]

list_table_name=[]
list_did_number=[]
if(number_of_device_assoicated==0):
    message="No CDR Collections Available"
    logging.debug(message)
else:
    sql="select table_name from information_schema.tables WHERE table_schema = 'dynamic_app_data_%s' AND table_name like '%s' and table_name not like '%s'"%(app_id,'dev_journals_%','dev_journals_c%')
    cHandler.execute(sql)
    for table_name in cHandler.fetchall():
            list_table_name.append(table_name[0].__str__())
            list_did_number.append(int(table_name[0][13:]))

#fatch data from each device
# entry_id,obj_id,data,date_update,
for table in list_table_name:
    sql="select entry_id,obj_id,data,date_update from %s"%(table)
    cHandler.execute(sql)
    call_dict=defaultdict(list)
    for data in cHandler.fetchall():
        obj_data={}
        obj_data[data[1]]=data[2]

        call_dict[int(data[0])].append(obj_data)
        #logging.debug(call_dict)
        # we will have diff set of data .. based on dynamic app . and we will have more length of data based on call
        # have to provide logic for mapping like presentation used , call type,

    list_call_dicts.append(call_dict)
    super_dict = {}
    for d in list_call_dicts:
        for k, v in d.iteritems():
            super_dict.setdefault(k, []).append(v)
    logging.debug(super_dict)
    # have to replace Object id with Pres_objId






#for all collection
# we have to look in to the call entry
    #if entry is None:
        #logger.debug("CDR_JOURNAL: no entry found for key %s", k)
        #entry = create_entry(k, JOURNAL_STATE_OPEN)
    #else:
        #if entry.get_state() == JOURNAL_STATE_CLOSED or k in closed_entries:
             #logger.debug("CDR_JOURNAL: call already closed: %s", k)
             #closed_calls.append(k)
             #continue
        #elif entry.get_state() != JOURNAL_STATE_OPEN:
             #halting execution
             #raise TelePresenceCommError("(device id: %s): unknown journal state " + \"for entry key %s" % (tpd.did, k))
             #entry.update_collected_data(v.to_entry())
             #calls.append(entry)

#finally
#if len(calls) > 0:
    #logger.debug("CDR_JOURNAL: saving %d calls", len(calls))
    #EM7_RESULT.extend(calls)
    #logger.debug("CDR_JOURNAL: EM7_RESULT contains %s calls", len(EM7_RESULT))
    #if len(closed_calls) > 0:
         #raise CallAlreadyClosed(str(closed_calls))



