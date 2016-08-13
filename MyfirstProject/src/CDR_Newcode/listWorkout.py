_database="sumit_db"
table="sumit_table"


sql="""select dajm.entry_key,dadj.entry_id,obj_id,data,dajm.state,dajm.date_update from %s.%s dadj, %s.journal_meta dajm
    where dadj.entry_id=dajm.entry_id and dadj.entry_id in (861,862)""" %(_database,table,_database)

print sql