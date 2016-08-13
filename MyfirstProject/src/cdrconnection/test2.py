#import datetime, time, traceback

import cx_Oracle

rows = []
for i in range(1 , 6):
    dateValue = "sumit"
    rows.append(dateValue)

print rows

# insert all of the rows as a batch and commit
ip = '10.88.137.249'
port = 1521
SID = 'qremlg2'
dsn = cx_Oracle.makedsn(ip, port, SID)
connection = cx_Oracle.connect('EM7_INTERFACE', 'EM7_INTERFACE', dsn)
cursor = cx_Oracle.Cursor(connection)
cursor.prepare('insert into testdate (date_field) values (:1)')
cursor.executemany(None, rows)
connection.commit()
cursor.close()
connection.close()



