import MySQLdb
import re
import logging

#DeviceId=EM7_VALUES['%x']
NodeId=''
AssetId=''

legend_val=[]
logging.basicConfig(filename='/example.log',level=logging.DEBUG)
logging.debug('This is a test message')

#conn = MySQLdb.connect(user=EM7_ACTION_CRED['cred_user'],passwd=EM7_ACTION_CRED['cred_pwd'],host=EM7_ACTION_CRED['cred_host'],port=EM7_ACTION_CRED['cred_port'])
#cur = conn.cursor()

logging.debug('This is a Connection message')

if(NodeId=='' and AssetId==''):
    logging.debug('Inside First If Loop')
    sql="select asset_tag from master_biz.legend_asset where did = (select root_did from master_dev.component_dev_map where component_did=%s);"
    cur.execute(sql,(DeviceId,))
    sql_result=cur.fetchone()
    numrows = int(cur.rowcount)
    logging.debug('Inside First If Loop111')
    logging.debug('numrows::'+str(numrows))
    if numrows!=0:
        logging.debug('Inside numrows')
        logging.debug(sql_result[0])
        legend_val.append(sql_result[0])
        logging.debug("Output Loop1::"+legend_val)

    sql="select ip from master_dev.device_ip_addr where did = (select root_did from master_dev.component_dev_map where component_did=%s);"
    cur.execute(sql,(DeviceId,))
    sql_result=cur.fetchone()
    numrows = int(cur.rowcount)
    if numrows!=0:
        legend_val.append(sql_result[0])
        logging.debug("Output Loop2::"+legend_val)


#EM7_RESULT=legend_val

logging.debug("Output Outside::"+EM7_RESULT)


cur.close()
