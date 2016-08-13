# for debugging, send logs to /data/logs/silo.log, or
# comment out these two lines for standard logging
from silo_common.logger import minimal_logger
logger = minimal_logger()

COLLECTION_PROBLEM = False
EM7_SNIPPET_EXCEPTION = 519
EM7_SNIPPET_NOTICE = 518

# define function to be added to silo_cursor to get a handle
# for the em7 db, even if the app is running on a collector
def data_db(cls):
    from silo_common import global_definitions as defs
    from silo_common.config import silo_config
    from silo_common.database import active_ha_db, get_dbc
    from silo_common.exceptions import ConfigError, DatabaseError
    from silo_common.misc import ha_state
    import MySQLdb
    import MySQLdb.cursors
    if not (hasattr(cls, "datainstance") and cls.datainstance):
        c = silo_config()
        if c.error == defs.SILO_ERROR:
            raise ConfigError, c.err_msg
        if int(c.get("LOCAL", "model_type")) == defs.SILO_MODEL_AIO:
            if ha_state() == defs.HA_ACTIVE_DB:
                cls.datainstance = cls.local_db()
            else:
                cls.datainstance = active_ha_db()
        else:
            # NOTE: this depends on several assumptions about how the em7
            #       database talks to the collector, including the presence
            #       of a special mysql user (which is currently NOT used
            #       to pick up collection objects!); however, the second
            #       assumption, that the db will be listed in the process
            #       list, is reasonable, since if no em7 db is talking to
            #       a collector, it's probably a symptom of a larger issue
            localdbc = cls.local_db()
            processhosts = dict([(
                    v["Host"].split(":")[0], True
                    ) for v in localdbc.autofetchall_dict("""
                            SHOW PROCESSLIST
                    """)]).keys()
            if len(processhosts) < 1:
                raise DatabaseError, "no connected em7 db host(s) listed"
            synchosts = localdbc.autofetch_column("""
                    SELECT DISTINCT host
                    FROM mysql.user
                    WHERE user = 'db_sync_ssl'
                    """)
            if synchosts is None or len(synchosts) < 1:
                raise DatabaseError, "unable to determine allowed em7 db(s)"
            dbhost = [k for k in processhosts if k in synchosts]
            if len(dbhost) != 1:
                raise DatabaseError, "unable to verify correct em7 db host"
            dbuser=c.get("LOCAL", "dbuser")
            dbpasswd=c.get("LOCAL", "dbpasswd")
            main_conn = MySQLdb.connect (host =dbhost[0],user = dbuser,passwd = dbpasswd,port=7706,db = "",connect_timeout = 60,cursorclass=MySQLdb.cursors.DictCursor)
            cls.datainstance = main_conn.cursor()

    return cls.datainstance

def reporting_db(cls, cred_details, logger=logger):
    from silo_common.credentials import dbc_from_cred_array
    return dbc_from_cred_array(data_dbc, logger)(cred_details)
    #dbc = em7_snippets.dbc_from_cred_id(cred_details['cred_id'])
    #return dbc

# define iterating behaviors for silo_cursor
def iterfetch(self, *args, **kwargs):
    #self.pure_execute(*args, **kwargs)
    #return iter(self)
    data_dbc.execute(self,*args)
    return iter(data_dbc)

def iterfetch_d(self, *args, **kwargs):
    self._fetch_type = 1
    try:
        data_dbc.execute(*args)
        row = data_dbc.fetchone()
        while row is not None:
            yield row
            row = data_dbc.fetchone()
        raise StopIteration
    finally:
        self._fetch_type = 0

# add custom *_db() and iterfetch*() behaviors to silo_cursor
from silo_common.database import silo_cursor
silo_cursor.data_db = classmethod(data_db)
silo_cursor.reporting_db = classmethod(reporting_db)
silo_cursor.iterfetch = iterfetch
silo_cursor.iterfetch_d = iterfetch_d

# define autofetch_value behavior for cx_Oracle.Cursor
def autofetch_value(self, *args, **kwargs):
    self.execute(*args, **kwargs)
    try: return self.fetchall()[0][0]
    except IndexError, TypeError: return None

# add autofetch_value(...) behavior to cx_Oracle.Cursor
from cx_Oracle import Cursor as pl_cursor
#TODO: this won't work (can't set attr of built-in/extension type ...)
#pl_cursor.autofetch_value = autofetch_value

# define an alert handler for exception messages
def API_ALERT(message, did=did, dbc=dbc, logger=logger):
    if logger is not None:
        logger.debug("CDR: (device id: %s): %s", did, message)
    if dbc is not None:
        dbc.execute("""INSERT INTO in_api.messages
    (xtype, xid, message, message_time, ytype, yid, yname)
VALUES
    (1, %s, %s, NOW(), 0, 0, '')""", (did, message))

# some exception types to help determine when to raise which alerts
class CallAlreadyClosed(StandardError):
    def __str__(self):
        return "TelePresence CDR Event: Call Already Closed: %s" % self.args
class DeviceNotAligned(StandardError):
    # should never happen -- app only runs for aligned devices
    def __str__(self):
        return "TelePresence CDR Event: Device Not Aligned: %s" % self.args
class NoCrunchedCalls(StandardError):
    def __str__(self):
        return "TelePresence CDR Event: No Crunched Calls"
class ReportingDBCommError(StandardError):
    def __str__(self):
        return "TelePresence CDR Event: Reporting Communication Error: %s" % self.args
class ReportingDBCredError(StandardError):
    def __str__(self):
        return "TelePresence CDR Event: Reporting Credential Error: %s" % self.args
class TelePresenceCommError(StandardError):
    def __str__(self):
        return "TelePresence CDR Event: Communication Error: %s" % self.args
class TelePresenceCredError(StandardError):
    def __str__(self):
        return "TelePresence CDR Event: Credential Error: %s" % self.args

# include the base db exception classes for capturing data cursor errors
from _mysql_exceptions import MySQLError
from silo_common.exceptions import DatabaseError

# get the data dbc to use for everything except
# API_ALERT and batch_source_collector
try:
    data_dbc = silo_cursor.data_db()
except (DatabaseError, MySQLError) as e:
    API_ALERT(TelePresenceCredError(e))


##############################################################################
#                                                                            #
#  upload snippet -- uploads crunched entries                                #
#                                                                            #
##############################################################################

# set up some vars for the app
CDR_BATCH = "CDR_BATCH"
CDR_BATCH_SEQ = CDR_BATCH + "_SEQ"
CDR_LINE = "CDR_LINE_INTERFACE"
DATE_RANGE = "> DATE_SUB(NOW(), INTERVAL 1 MONTH)"

import datetime, time, traceback

try:

    # create entry list to pass to data section
    closed_entries = []
    import logging
    logging.basicConfig(filename='/tmp/shak.log',level=logging.DEBUG)
    logger.debug("CDR_UPLOAD: reporting upload snippet entry point")
    try: app_meta = get_app_instance_meta_data()
    except DeserializationError: app_meta = {}
    if app_meta is None: app_meta = {}
    logger.debug("CDR_UPLOAD: %s", app_meta)

    # get crunched calls
    open_entries = bulk_get_open_entries()
    if len(open_entries) <= 0: raise NoCrunchedCalls

    crunch_args = dict(app_id=app_id, did=did, date_range=DATE_RANGE)

    pres_id = list(iterfetch("""SELECT
    journal_presentation_id,name
FROM master.dynamic_app_journal_presentation
WHERE app_id = %(app_id)s""", crunch_args))

    presentation_id=[]
    for k in pres_id:
        presentation_id.append(tuple(k.values()))
    presentation_id=[(t[1], t[0]) for t in presentation_id]
    #logging.debug(tuple(e.entry_key for e in open_entries))
    crunch_args.update(
            pres_map=", ".join("pres_%s AS %s" % p for p in presentation_id),
            open_entries=tuple(e.entry_key for e in open_entries)
            )
    crunched_calls_q = """SELECT
    entry_key, %(pres_map)s
FROM dynamic_app_data_%(app_id)s.dev_journals_crunched_%(did)s AS djc
LEFT JOIN dynamic_app_data_%(app_id)s.journal_meta USING (entry_id)
WHERE entry_key IN %(open_entries)s
    AND djc.date_update %(date_range)s""" % crunch_args
    logger.debug("CDR_UPLOAD: crunched_calls_q(%s)", crunched_calls_q)
    sql="SELECT count(*) as count FROM information_schema.tables WHERE table_schema = 'dynamic_app_data_%s' AND table_name = 'dev_journals_crunched_%s'"%(app_id,did)
    data_dbc.execute(sql)
    check_table_exists=data_dbc.fetchone()
    crunched_calls={}
    if(check_table_exists['count']>0):
        data_dbc.execute(crunched_calls_q)
        crunched_calls=data_dbc.fetchall()

    if len(crunched_calls) > 0:
        logger.debug("CDR_UPLOAD: got %s crunched calls" % (len(crunched_calls), ))
        for k,v in enumerate(crunched_calls):
            crunched_calls[k]["LINE_NUMBER"] = k + 1
            if isinstance(v['CALL_START_DTTM'], datetime.datetime):
               datum=v['CALL_START_DTTM']
            else:
                datum = datetime.datetime.utcfromtimestamp(0)
                datum = datetime.datetime.strftime(datum,'%Y/%m/%d %I:%M:%S')


    data_dbc.execute("""SELECT device FROM master_dev.legend_device WHERE id = %(did)s""", crunch_args)
    device_name=data_dbc.fetchone()
    data_dbc.execute("""SELECT IFNULL(url,'missing stack_id') FROM master.system_settings_core""")
    source_name=data_dbc.fetchone()
    data_dbc.execute("""SELECT IFNULL(name,'missing collector_id') FROM master.system_settings_licenses""")
    collector_name=data_dbc.fetchone()
    listDict = []
    listDict.append((str(device_name['device']) or crunch_args)+"_"+str(int(time.time())))
    listDict.append(source_name["IFNULL(url,'missing stack_id')"] or "missing stack_id")
    listDict.append(collector_name["IFNULL(name,'missing collector_id')"] or "missing collector_id")
    listDict.append(len(crunched_calls))
    collection_times = [int(k['entry_key'].split("_")[0]) for k in crunched_calls]
    try:
        st=datetime.datetime.fromtimestamp(min(collection_times)).strftime('%d/%m/%Y %H:%M:%S')
        listDict.append(st)
        en=datetime.datetime.fromtimestamp(max(collection_times)).strftime('%d/%m/%Y %H:%M:%S')
        listDict.append(en)
    except ValueError:
        logger.debug("CDR_UPLOAD: collection_times: %s" % (collection_times, ))
        logger.debug("CDR_UPLOAD: crunched calls: %s" % (crunched_calls, ))
    # upload crunched calls
    try:
        import cx_Oracle
        ip = cred_details['cred_host']
        port = cred_details['cred_port']
        SID = cred_details['db_sid']
        userName=cred_details['cred_user']
        password=cred_details['cred_pwd']
        dsn_tns = cx_Oracle.makedsn(ip, port, SID)
        rdb=cx_Oracle.connect(userName, password, dsn_tns)
        rdbc = cx_Oracle.Cursor(rdb)
        rdb.autocommit = False
        logger.debug("CDR_UPLOAD: start transaction")
        rdb.begin()
        logger.debug("CDR_UPLOAD: creating batch record")
        cdr_batch_q = "INSERT INTO CDR_BATCH (BATCH_NAME, BATCH_BEGIN_DATE, BATCH_END_DATE, BATCH_SOURCE, BATCH_SOURCE_COLLECTOR, LOAD_DATE,  ROW_COUNT, STATUS, STATUS_DATE) VALUES ('"+listDict[0]+"',to_date('"+listDict[4]+"','dd/mm/yyyy hh24:mi:ss'),to_date('"+listDict[5]+"','dd/mm/yyyy hh24:mi:ss'),'"+listDict[1]+"','"+listDict[2]+"',to_date(to_char(SYSTIMESTAMP, 'mm/dd/yyyy hh24:mi:ss'), 'mm/dd/yyyy hh24:mi:ss'),'"+str(listDict[3])+"','NEW', to_date(to_char(SYSTIMESTAMP, 'mm/dd/yyyy hh24:mi:ss'), 'mm/dd/yyyy hh24:mi:ss'))"
        rdbc.prepare(cdr_batch_q)
        rdbc.execute(cdr_batch_q)
        logger.debug("CDR_UPLOAD: batch_query(%s)", cdr_batch_q)
        logger.debug("CDR_UPLOAD: retrieving newly created batch id")
        cdr_batch_id="""SELECT %s.CURRVAL FROM DUAL""" % (CDR_BATCH_SEQ, )
        rdbc.prepare(cdr_batch_id)
        rdbc.execute(cdr_batch_id)
        id=rdbc.fetchone()[0]
        logging.debug(id)
    except (ValueError,RuntimeError), e:
        COLLECTION_PROBLEM = True
        PROBLEM_STR = e
        raise ReportingDBCommError(traceback.format_exc())
    if id is None:
        raise ReportingDBCommError("unable to retrieve batch id")

    rdb_query_columns = dict(presentation_id).values()
    rdb_query_columns.append("LINE_NUMBER")
    columns=", ".join(rdb_query_columns)
    values=", :".join(rdb_query_columns)
    cdr_line=CDR_LINE
    try:
        for i in range(len(crunched_calls)):
            cdr_line_q="INSERT INTO "+cdr_line+" (BATCH_ID,"+str(columns)+") VALUES (:BATCH_ID,:"+str(values)+")";
            crunched_calls[i].update({'BATCH_ID':id})
            if 'entry_key' in crunched_calls[i]: del crunched_calls[i]['entry_key']
            list=[crunched_calls[i]]
            rdbc.prepare(cdr_line_q)
            rdbc.executemany(cdr_line_q, list)
            logger.debug("CDR_UPLOAD: committing transaction")
            rdb.commit()
            logger.debug("CDR_UPLOAD: executemany(%s)", cdr_line_q)
    except:
        raise ReportingDBCommError(traceback.format_exc())
    date=datetime.datetime.now()
    # close entries
    for entry in open_entries:
        if entry.entry_key in crunched_calls:
            entry.close()
            entry.update_collected_data({
                    "Reporting Batch ID": id,
                    "Reporting Batch Name": listDict[0],
                    "Reporting Upload Time": date
                    })
            EM7_RESULT.append(entry)
    app_meta.update({"last_collection_time": max(collection_times)})
    logger.debug("CDR_UPLOAD: %s", app_meta)
    #set_app_instance_meta_data(app_meta)
    #closed_entries = crunched_calls.keys()

except MySQLError as e:
    API_ALERT(TelePresenceCommError(e))
except NoCrunchedCalls as e:
    API_ALERT(e)
except (ReportingDBCredError,
        ReportingDBCommError) as e:
    API_ALERT(e)
    try:
        # something broke with the database, try to rollback any work
        rdb.rollback()
    except:
        pass
except:
    COLLECTION_PROBLEM = True
    import traceback
    PROBLEM_STR = traceback.format_exc()
    INTERNAL_ALERTS.append((EM7_SNIPPET_EXCEPTION, PROBLEM_STR))
    logger.debug("CDR_UPLOAD: %s", PROBLEM_STR)
    try:
        # unknown error, we probably should rollback and try again later
        rdb.rollback()
    except:
        pass


##############################################################################
#                                                                            #
#  journal snippet -- records new entries                                    #
#                                                                            #
##############################################################################
##############################################################################
#                                                                            #
#  define the app's primary runtime behavior -- this wrapper function is     #
#  needed to avoid scope issues when defining classes, functions, etc. --    #
#  without it, functions and member methods cannot access locally defined    #
#  variables unless they are explicitly added to the frame                   #
#                                                                            #
##############################################################################

def run_app():

    # stream types
    STR_VIDEO = 1
    STR_AUDIO = 2
    STR_TYPE = [STR_VIDEO, STR_AUDIO]

    # dynamic app object groups
    GRP_CALL = 2
    GRP_STREAM = 3
    GRP_SOURCE = 4
    GRP_MULTI = [GRP_CALL, GRP_STREAM, GRP_SOURCE]

    SRC_SEC1 = 1
    SRC_PRI = 2
    SRC_SEC2 = 3
    SRC_AUX = 4
    SRC_TYPE = [SRC_SEC1, SRC_PRI, SRC_SEC2, SRC_AUX]

    # a lot of the proc_*_val functions like this are just indexing or
    # setting a default - let's simplify it with a small utility function
    def proc_array_val(array, val):
        try: return array[int(val)]
        except (IndexError, TypeError, ValueError): return array[0]

    # keep both the numeric and the enum value
    def proc_enum_val(array, val):
        return {"value": val, "str": proc_array_val(array, val)}

    # set up enum arrays
    enum_state = [
            "unknown",           "Unknown",         "Other",
            "NoMgmtSysConn",     "NoDialTone",      "InvalidNumber",
            "Ringing",           "NoAnswer",        "InProgress",
            "RemoteHold",        "ShareLineActive", "InLocalConference",
            "TerminatedbyError", "LocalHold",       "TerminatedNormally",
            "Answer",            "Resume",          "Busy",
            "Pause",             "Playback",        "Recording"
            ]
    enum_termination = [
            "unknown",                  "unknown",
            "other",                    "internalError",
            "localDisconnected",        "remoteDisconnected",
            "networkCongestion",        "mediaNegotiationFailure",
            "securityConfigMismatched", "incompatibleRemoteEndPt",
            "serviceUnavailable",       "remoteTerminatedWithError"
            ]
    enum_type = ["unknown", "TelePresence", "Audio Only", "unknown"]
    enum_mode = ["No Management System", "No Management System", "Managed"]
    enum_security = [
            "unknown", "Non-Secure", "Authenticated", "Secure", "Unknown"
            ]
    enum_direction = ["unknown", "Incoming", "Outgoing", "unknown"]

    enum_remote_call_type = [
            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A",
            "PTP", "PTP", "MP",  "N/A", "N/A"
            ]

    def proc_state_val(val): return proc_enum_val(enum_state, val)
    def proc_termination_val(val): return proc_enum_val(enum_termination, val)
    def proc_type_val(val): return proc_enum_val(enum_type, val)
    def proc_mode_val(val): return proc_enum_val(enum_mode, val)
    def proc_security_val(val): return proc_enum_val(enum_security, val)
    def proc_direction_val(val): return proc_enum_val(enum_direction, val)
    def proc_direction_val_poly(val): return {"value": val, "str": str([x for x in enum_direction if x.startswith(val)][0])}
    def proc_remote_call_type_val(val):
        return proc_enum_val(enum_remote_call_type, val)

    def proc_bitrate_val(val):
        try: resolution = (float(val) < 4000) and "720P" or "1080P"
        except (TypeError, ValueError): resolution = "N/A"
        return {"value": val, "res": resolution}

    def proc_datetime_val(val):
        if val == "": return "0"
        try:
           val = val.translate(None, ":-/ ")
           val = datetime.datetime.strptime(val,"%Y%m%d%H%M%S")
        except:
            return None
        return val.strftime("%s")

    def proc_datetime_val_poly(val):
        if val == "": return "0"
        try:
            val = val.translate(None, ":-/ ")
            val = datetime.datetime.strptime(val,"%d%b%Y%H%M%S")
        except:
            return None
        return val.strftime("%s")

    def proc_active_val(val): return proc_array_val(["false", "true"], val)

    def proc_attributes_val(val):
        #TODO: change introp back to interop when the presentation display input
        #TODO: is changed to allow longer formulae
        ATTRIBUTE_MASK = {"introp": 192, "webex": 32}
        try:
            attrlist = [(k, (int(val, 16) & v) and "Y" or "N")
                    for k, v in ATTRIBUTE_MASK.iteritems()]
        except (TypeError, ValueError):
            attrlist = [(k, "N") for k in ATTRIBUTE_MASK]
        return dict([("value", val)] + attrlist)

    def proc_remote_device_type_val(val):
        # Cisco TelePresence Recording Server
        CTRS = "9"
        result = proc_remote_call_type_val(val)
        result["ctrs"] = (val == CTRS) and "Y" or "N"
        return result

    def proc_duration_val(val):
        #if val == "%02d:%02d:%02d" %(val):
        #return {"value": val, "str": "%02d:%02d:%02d" %(val)}
        try: seconds = int(val)
        except (TypeError, ValueError): return {"value": val, "str": "00:00:00"}
        hours = seconds / 3600
        seconds -= hours * 3600
        minutes = seconds / 60
        seconds -= minutes * 60
        return {"value": val, "str": "%02d:%02d:%02d" % (
                hours, minutes, seconds
                )}
    def proc_duration_poly_val(val):
        val_in_sec=0
        try: raw_time = str(val)
        except (TypeError, ValueError): return {"value": 0, "str": val}
        if raw_time!='':
            temp = raw_time.split(':')
            val_in_sec = int(temp[0]) * 3600 + int(temp[1]) * 60 + int(temp[2])
        return {"value": val_in_sec, "str": raw_time }

    def proc_poly_val(val):
        return {"value": val, "str": val}

    class tp_stream(dict):
        def __init__(self, *args, **kwargs):
            dict.update(self, dict(
                    (str(i), dict(
                            (str(j), 0) for j in SRC_TYPE
                            )) for i in STR_TYPE
                    ))
            dict.update(self, *args, **kwargs)
        def update(self, value):
            from silo_common.exceptions import ProgrammingError
            if len(value) != 2:
                raise ProgrammingError("tp_stream must update by (index, value)")
            # don't bother testing for keys -- if this class is in use,
            # they should be correct by other logic, and should raise a
            # KeyError when someone adds improper values
            (index, value) = value
            if "Media" in index:
                if "Source" in index:
                    self[index["Media"]][index["Source"]] = value
                else:
                    self[index["Media"]] = value

    class tp_cdr(dict):

        # these objects get some adjustment (x = proc_*_val(x))
        _PROC_MAP = {
                "Attributes": proc_attributes_val,
                "Call Mode": proc_mode_val,
                "Call Termination Reason": proc_termination_val,
                "Direction": proc_direction_val,
                "Duration": proc_duration_val,
                "Initial Bit Rate": proc_bitrate_val,
                "Latest Bit Rate": proc_bitrate_val,
                "Local Start Time": proc_datetime_val,
                "Remote Call Type": proc_remote_call_type_val,
                "Remote Device Type": proc_remote_device_type_val,
                "Rx Active": proc_active_val,
                "Security": proc_security_val,
                "State": proc_state_val,
                "Type": proc_type_val,
                "Tx Active": proc_active_val,
                "Rx Audio Protocol" : proc_poly_val,
                "Rx Avg Latency" : proc_poly_val,
        "Rx Video Protocol" : proc_poly_val,
        "Rx Avg Jitter" : proc_poly_val,
        "Rx Max Jitter" : proc_poly_val,
        "Rx Max Latency" : proc_poly_val,
        "Rx Avg Lost Pkts" : proc_poly_val,
        "Rx Video Format" : proc_poly_val,
        "Disconnect Reason 3rd party" : proc_poly_val

                }




        def __init__(self, *args, **kwargs):
            self.update((k, "") for k in collection_objects)
            self.update((
                    k, tp_stream((str(i), 0) for i in STR_TYPE)
                    ) for k in [
                    "Average Call Latency",
                    "Max Call Latency"
                    ])
            self.update((k, tp_stream()) for k in [
                    "Average Call Jitter",
                    "Max Call Jitter",
                    "Rx Active",
                    "Rx Call Lost Packets",
                    "Rx Duplicate Packets",
                    "Rx Out of Order Packets",
                    "Rx Total Bytes",
                    "Rx Total Packets",
                    "Tx Active",
                    "Tx Total Bytes",
                    "Tx Total Packets"
                    ])
            self["Device"] = dict((k, "") for k in [
                    "co", "device", "loc",
                    "model", "roa_id", "tag"
                    ])
            self.update(dict(*args, **kwargs))

        def __setitem__(self, key, value):
            if isinstance(value, tp_stream):
                dict.__setitem__(self, key, value)
            elif key in self and isinstance(self[key], tp_stream):
                if key in tp_cdr._PROC_MAP:
                    # value is really (index, value), so map [1] only
                    value[1] = tp_cdr._PROC_MAP[key](value[1])
                self[key].update(value)
            elif key in tp_cdr._PROC_MAP:
               dict.__setitem__(self, key, tp_cdr._PROC_MAP[key](value))
            else:
                dict.__setitem__(self, key, value)

        def update(self, *args, **kwargs):
            if len(args) > 1:
                raise TypeError(
                        "update expected at most 1 arguments, got %d" % (
                                len(args),
                                )
                        )
            for k, v in dict(*args, **kwargs).iteritems():
                self[k] = v

        def to_entry(self):
            # get a copy of self in built-in dict form
            v = dict(self)
            v.setdefault(
                    "Call Termination Reason",
                    v.get("State", proc_termination_val(0))
                    )
            # JSON-ify complex types using dict::update vs. tp_cdr::update
            # for use with EM7_RESULT[].update_collected_data()
            import json
            v.update(
                    (i, json.dumps(j)) for i, j in v.iteritems()
                    if isinstance(j, dict) or isinstance(j, list)
                    )
            return v

        def presentation_used(self):
            for obj_name in ["Tx Total Bytes", "Rx Total Bytes"]:
                try:
                    if int(self[obj_name][STR_VIDEO][SRC_AUX]) > 0:
                        # try to return ASAP
                        return "Y"
                except (KeyError, TypeError, ValueError):
                    pass
            return "N"

    class tp_device(object):

        _DEVICE_QUERY = """SELECT DISTINCT
    org.roa_id, org.company, dev.device, snmp.sysdescr,
    IFNULL(asset.asset_tag, '(no asset record)') AS asset_tag,
    IFNULL(loc.location, '(no asset record)') AS location
FROM master_dev.legend_device AS dev
    LEFT JOIN master_dev.device_snmp_data AS snmp ON dev.id=snmp.did
    LEFT JOIN master.dynamic_app_collection AS coll ON dev.id=coll.did
    LEFT JOIN master_biz.organizations AS org on dev.roa_id=org.roa_id
    LEFT JOIN master_biz.legend_asset AS asset ON dev.id=asset.did
    LEFT JOIN master_biz.asset_location AS loc ON asset.id=loc.iid
WHERE coll.app_id = %s AND dev.id = %s"""

        def __init__(self, did, app_id, dbc, logger):

            self._data_loaded = False
            self.app_id       = app_id
            self.date_range   = "< NOW()"
            self.dbc          = dbc
            self.did          = did
            self.local_number = ""
            self.logger       = logger

            self._APP_ID = self._get_app_id(self._APP_GUID)
            self._DEVICE_QUERY %= (self.app_id, self.did)
            # NOTE: this assumes that did is unique across all em7 devices
            #device_row = self.dbc.autofetchrow_dict(self._DEVICE_QUERY)
            self.dbc.execute(self._DEVICE_QUERY)
            device_row=self.dbc.fetchone()
            if device_row is None:
                raise DeviceNotAligned(
                        "no device with did: %s found aligned with this app" %
                        (self.did, )
                        )
            self.__dict__.update(device_row)
            self.model = ""

        def _get_app_id(self, app_guid):
            self.dbc.execute("""SELECT aid
FROM master.dynamic_app
WHERE app_guid = %s""", (app_guid, ))
            aid_val=self.dbc.fetchone()
            return aid_val["aid"]

        def _load_call_data(self):
            from silo_common.exceptions import ProgrammingError
            raise ProgrammingError("_load_call_data() must be overridden")

        def itercalls(self):
            if not self._data_loaded:
                self.call_data = {}
                self._load_call_data()
            self.logger.debug("CDR_JOURNAL: got %d calls", len(self.call_data))
            return self.call_data.iteritems()

        def set_date_range(self, range):
            # it would be nice to check for a valid range
            # here, but for now just check it's a string
            if not isinstance(range, basestring):
                from silo_common.exceptions import ProgrammingError
                raise ProgrammingError("date range must be a string")
            self.date_range = range


    ##########################################################################
    #  Cisco Config App Mappings                                             #
    ##########################################################################

    class cisco_tp_device(tp_device):

        # identify Cisco TelePresence app across systems
        _APP_GUID = "51826B326476F7DB0F97D3A2BD9FBF7F"

        _DATA_QUERY = """SELECT
    collection_time, grp, oid, ind, data
FROM dynamic_app_data_%s.dev_config_%s
LEFT JOIN master.dynamic_app_objects ON object = obj_id
WHERE collection_time %%s
ORDER BY collection_time, grp, object, ind"""

        _INDEX_QUERY = """SELECT DISTINCT
    collection_time, grp, ind, data AS `Call Index`
FROM dynamic_app_data_%%s.dev_config_%%s
LEFT JOIN master.dynamic_app_objects ON object = obj_id
WHERE grp IN %s AND ind > 0 AND oid IN %s
    AND collection_time %%%%s
ORDER BY collection_time, grp, ind""" % (
                tuple(GRP_MULTI),
                ("Call Index", "Call Stream Index", "Call Statistics Index")
                )

        _LOCAL_NUMBER_QUERY = """SELECT data
FROM (
    (
        SELECT collection_time, data
        FROM dynamic_app_data_%(app_id)s.dev_config_%(did)s
        LEFT JOIN master.dynamic_app_objects ON object = obj_id
        WHERE oid = 'Local Number'
            AND data IS NOT NULL
            AND NOT (collection_time %%(date_range)s)
        ORDER BY collection_time DESC
        LIMIT 1
    ) UNION DISTINCT (
        SELECT collection_time, data
        FROM dynamic_app_data_%(app_id)s.dev_config_%(did)s
        LEFT JOIN master.dynamic_app_objects ON object = obj_id
        WHERE oid = 'Local Number'
            AND data IS NOT NULL
            AND collection_time %%(date_range)s
        ORDER BY collection_time
        LIMIT 1
    )
    ORDER BY collection_time
    LIMIT 1
) AS _t"""

        def __init__(self, *args, **kwargs):
            super(cisco_tp_device, self).__init__(*args, **kwargs)
            self._DATA_QUERY %= (self._APP_ID, self.did)
            self._INDEX_QUERY %= (self._APP_ID, self.did)
            self._LOCAL_NUMBER_QUERY %= dict(app_id=self._APP_ID, did=self.did)
            if self.sysdescr == "":
                self.model = "sysdescr missing"
            else:
                import re
                model = re.search("(?P<model>\\d+)", self.sysdescr)
                if model is None:
                    self.model = "model # missing"
                else:
                    self.model = "CTS %s" % (model.group("model"), )

        def _load_call_indices(self):
            from silo_common.exceptions import ProgrammingError
            try:
                self.dbc.execute(self._INDEX_QUERY % (self.date_range, ))
                self.call_index =self.dbc.fetchall()
                t={}
                ind={}
                grp={}
                for i in self.call_index:
                    if i['collection_time'] not in t:
                        t[i['collection_time']]={i['grp']:{i['ind']:{'Call Index':i['Call Index']}}}
                    else:
                        if t[i['collection_time']].has_key(i['grp']):
                            t[i['collection_time']][i['grp']].update({i['ind']:{'Call Index':i['Call Index']}})
                            if(i.has_key('Media')):
                                t[i['collection_time']][i['grp']][i['ind']].update({'Media':i['Media']})
                            if(i.has_key('Source')):
                                t[i['collection_time']][i['grp']][i['ind']].update({'Source':i['Source']}) 
                        else:
                            t[i['collection_time']].update({i['grp']:{i['ind']:{'Call Index':i['Call Index']}}})
                            if(i.has_key('Media')):
                                t[i['collection_time']][i['grp']][i['ind']].update({'Media':i['Media']})
                            if(i.has_key('Source')):
                                t[i['collection_time']][i['grp']][i['ind']].update({'Source':i['Source']})
                self.call_index=t
            except ProgrammingError:
                # if no rows were returned, autofetch_all_assoc raises this...
                self.call_index = {}
            for collection_time, ct in self.call_index.iteritems():
                for grp, ct_grp in ct.iteritems():
                    for ind, ct_grp_ind in ct_grp.iteritems():
                        ct_grp_ind.setdefault("Call Index", "")
                        # zip truncates at the shortest arg count
                        ct_grp_ind.update(zip(
                                ("Call Index", "Media", "Source"),
                                (ct_grp_ind["Call Index"] or "").split(".")
                                ))
        def _load_call_data(self):
            import _mysql_exceptions

            try:
                self._load_call_indices()
                # get last local number before start of data or else the first
                # local number we find if it was missing until somewhere in
                # our range, lastly resorting to the empty string
                self.dbc.execute(self._LOCAL_NUMBER_QUERY % dict(date_range=self.date_range))
                localnumber=self.dbc.fetchone()
                self.local_number=localnumber["data"]
                if self.local_number is None:
                   self.local_number=""
                scalar_data = {}
                call_data = {}
                last_collection_time = ""
                #logging.debug(self._DATA_QUERY % (self.date_range, ))
                # retrieve call data
                for row in dbc.iterfetch_d(
                        self._DATA_QUERY % (self.date_range, )
                        ):
                    try:
                        collection_time = row["collection_time"]
                        obj_name = row["oid"]
                        val = row["data"]
                        grp = row["grp"]
                        ind = row["ind"]
                    except KeyError:
                        # there's something wrong with this row, but this would
                        # mean MySQLdb returned something very strange, in which
                        # case we should probably just move on to the next row
                        continue

                    # python MySQLdb gets DATETIME columns as datetime.datetime
                    # objects, so switch to str(seconds since epoch)
                    ct_str = collection_time.strftime("%s")

                    if obj_name == "Local Number":
                        # update the local number if val is not empty
                        self.local_number = val or getattr(
                                self, "local_number", ""
                                )

                    if ct_str not in scalar_data:
                        if last_collection_time == "":
                            scalar_data[ct_str] = {
                                    "Local Number": self.local_number,
                                    "location": self.location,
                                    "device": self.device,
                                    "model": self.model
                                    }
                        else:
                            scalar_data[ct_str] = scalar_data[last_collection_time]
                        last_collection_time = ct_str

                    if grp in GRP_MULTI:
                        try:
                            index = self.call_index[collection_time][grp][ind]
                            call_index_key = index["Call Index"]
                        except KeyError:
                            # a config object in this group should have a call
                            # index -- if not, we don't know where to put it, so
                            # move to the next one
                            continue
                        if call_index_key:
                            call_data.setdefault(ct_str, {})
                            call_data[ct_str].setdefault(
                                    call_index_key,
                                    tp_cdr({
                                            "collection_time":
                                                    str(collection_time),
                                            "Device": {
                                                    "roa_id": self.roa_id,
                                                    "co": self.company,
                                                    "device": self.device,
                                                    "tag": self.asset_tag,
                                                    "loc": self.location,
                                                    "model": self.model
                                                    }
                                            })
                                    )
                            datum = call_data[ct_str][call_index_key]

                            # this splitting is a little simpler when getting data
                            # from an SNMP walk rather than from a config app
                            if grp in (GRP_STREAM, GRP_SOURCE):
                                if not isinstance(datum[obj_name], tp_stream):
                                    if grp == GRP_STREAM:
                                        datum[obj_name] = tp_stream(
                                            (str(i), 0) for i in STR_TYPE
                                            )
                                    else:
                                        datum[obj_name] = tp_stream()
                                datum[obj_name].update((index, val))
                            else: # grp == GRP_CALL
                                datum[obj_name] = val

                    elif val is not None: # grp not in GRP_MULTI
                        scalar_data[ct_str][obj_name] = val

            except _mysql_exceptions.Error as e:
                if e is None: raise
                from silo_common.database import ER
                if e.args[0] not in (ER.NO_SUCH_TABLE, ER.BAD_DB_ERROR): raise

            # append scalar data to each call and flatten keys
            for ct_str, ct_calls in call_data.iteritems():
                for call_index_key, call_cdr in ct_calls.iteritems():
                    # update every call with values set on the device level
                    if ct_str in scalar_data:
                        call_cdr.update(scalar_data[ct_str])
                    call_cdr["Presentation Used"] = call_cdr.presentation_used()
                    # save this call by key(collection time, call index)
                    self.call_data["%s_%s" % (
                            ct_str, call_index_key
                            )] = call_cdr

            self._data_loaded = True


    ##########################################################################
    #  Tandberg Journal Mappings                                             #
    ##########################################################################

    class tandberg_device(tp_device):

        _DATA_QUERY = """SELECT
    CONCAT(UNIX_TIMESTAMP(djc.date_update), '_', entry_key) AS entry_key, %s
FROM dynamic_app_data_%s.journal_meta
JOIN dynamic_app_data_%s.dev_journals_crunched_%s AS djc USING (entry_id)
WHERE djc.date_update %%s AND state = %s"""
        _OBJ_QUERY = """SELECT data
FROM dynamic_app_data_%%s.dev_config_%s
WHERE object = (
    SELECT obj_id
    FROM master.dynamic_app_objects
    WHERE app_id = %%s AND name = %%s
    LIMIT 1
    ) AND data IS NOT NULL
GROUP BY collection_time
ORDER BY collection_time DESC
LIMIT 1"""

        def __init__(self, *args, **kwargs):
            logging.debug("sumit 1")
            super(tandberg_device, self).__init__(*args, **kwargs)
            self._DATA_QUERY %= (
                    ", ".join("pres_%s AS `%s`" % (
                            k, self._OBJ_MAP[v]
                            ) for k, v in self.dbc.iterfetch(
                                    """SELECT journal_presentation_id, name FROM master.dynamic_app_journal_presentation WHERE app_id = %%s AND name in %s""" % (tuple(self._OBJ_MAP.keys()), ),
                                    args=(self._APP_ID, )
                            )),
                    self._APP_ID,
                    self._APP_ID,
                    self.did,
                    JOURNAL_STATE_CLOSED
                    )
            self._OBJ_QUERY %= (self.did, )
            #self.logger.debug(self._DATA_QUERY)
            # for now, assume any Tandberg devices will have both of these
            self._CONFIG_APP_ID = self._get_app_id(self._CONFIG_APP_GUID)
            self._STATUS_APP_ID = self._get_app_id(self._STATUS_APP_GUID)

        def _load_call_data(self):
            self._load_device_data()
            # ignore proc_*_val for certain objects
            #TODO: give tp_cdr() a way to handle this on its own
            for proc_key in ["Direction", "Security", "State", "Type"]:
                if proc_key in tp_cdr._PROC_MAP:
                    tp_cdr._PROC_MAP[proc_key] = lambda x: {"str": x}
            self.logger.debug(
                    "CDR_JOURNAL: %s calls in source",
                    self.dbc.autofetch_value(
                            """SELECT COUNT(*) FROM dynamic_app_data_%s.journal_meta WHERE did = %s AND state = %s AND date_update %s""" % (
                                    self._APP_ID,
                                    self.did,
                                    JOURNAL_STATE_CLOSED,
                                    self.date_range
                                    )
                            )
                    )
            for row in self.dbc.iterfetch_d(
                    self._DATA_QUERY % (self.date_range, )
                    ):
                entry_key = row["entry_key"]
                del row["entry_key"]
                if entry_key in self.call_data:
                    self.logger.debug("CDR_JOURNAL: entry %s already found, updating" % (entry_key, ))
                else:
                    #self.logger.debug("CDR_JOURNAL: adding entry %s" % (
                    #        entry_key,
                    #        ))
                    self.call_data[entry_key] = tp_cdr({
                            "Device": {
                                    "roa_id": self.roa_id,
                                    "co": self.company,
                                    "device": self.device,
                                    "tag": self.asset_tag,
                                    "loc": self.location,
                                    "model": self.model
                                    },
                            "Local Number": self.local_number,
                            "Presentation Used": "N"
                            })
                if row["Type"] == "Video":
                    row["Presentation Used"] = "Y"
                self.call_data[entry_key].update(row)
            self._data_loaded = True

        def _load_device_data(self):
            # get Local Number and Tandberg Model
            self.__dict__.update(
                    (k, self.dbc.autofetch_value(
                            self._OBJ_QUERY, args=v
                            ) or "N/A") for k, v in self._DEV_OBJ.iteritems()
                    )

    class tandberg_c(tandberg_device):

        _APP_GUID = "9E9ACD6B19ADD2EB7DA7720D702D454A"
        _CONFIG_APP_GUID = "DA8A50E561876A4466C611D7CB326E9A"
        _STATUS_APP_GUID = "335A62A9F7E0787A1FB6A0FF5DD22CE9"
        _OBJ_MAP = {
                "Call ID": ".Call Index",
                "Call Rate": "Initial Bit Rate",
                "Call Type": "Type",
                "Direction": "Direction",
               "Disconnect Cause": "State",
                "Duration": "Duration",
                "Encryption": "Security",
                "Remote Number": "Remote Number",
                "Start Time": "Local Start Time"
                }

        def __init__(self, *args, **kwargs):
            super(tandberg_c, self).__init__(*args, **kwargs)
            self._DEV_OBJ = {
                    "local_number": (
                            self._CONFIG_APP_ID,
                            self._CONFIG_APP_ID,
                            "H323 Alias E164"
                            ),
                    "model": (
                            self._STATUS_APP_ID,
                            self._STATUS_APP_ID,
                            "Product ID"
                            ),
                    "platform": (
                            self._STATUS_APP_ID,
                            self._STATUS_APP_ID,
                            "Product Platform"
                            )
                    }

        def _load_device_data(self):
            super(tandberg_c, self)._load_device_data()
            if self.model == "N/A":
                self.model = self.platform
            else:
                if self.model.lower().find(
                        self.platform.lower()
                        ) == -1 and self.platform != "N/A":
                    self.model += " " + self.platform

    class tandberg_mxp(tandberg_device):

        _APP_GUID = "549F725B75C1BC2E11470D5072BD4166"
        _CONFIG_APP_GUID = "CDD73C4766A2A40E8657EFCE778612A0"
        _STATUS_APP_GUID = "FF51933DC160EAFCC56FCA84095B220E"
        _OBJ_MAP = {
                "Call Rate": "Initial Bit Rate",
                "Call Type": "Type",
                "Direction": "Direction",
                "Disconnect Cause": "State",
                "Duration": "Duration",
                "Encryption In": "Security",
                "Log Tag": ".Call Index",
                "Remote Number": "Remote Number"
                }

        def __init__(self, *args, **kwargs):
            super(tandberg_mxp, self).__init__(*args, **kwargs)
            self._DEV_OBJ = {
                    "local_number": (
                            self._CONFIG_APP_ID,
                            self._CONFIG_APP_ID,
                            "H323 Alias E164"
                            ),
                    "model": (
                            self._STATUS_APP_ID,
                            self._STATUS_APP_ID,
                            "Product ID"
                            )
                    }
  ##########################################################################
  #  Polycom Journal Mappings                                             #
  ##########################################################################

    class polycom_device(tp_device):

        _DATA_QUERY = """SELECT
    CONCAT(UNIX_TIMESTAMP(djc.date_update), '_', entry_key) AS entry_key, %s
FROM dynamic_app_data_%s.journal_meta
JOIN dynamic_app_data_%s.dev_journals_crunched_%s AS djc USING (entry_id)
WHERE djc.date_update %%s AND state = %s"""
        _OBJ_QUERY = """SELECT data
FROM dynamic_app_data_%%s.dev_config_%s
WHERE object = (
    SELECT obj_id
    FROM master.dynamic_app_objects
    WHERE app_id = %%s AND name = %%s
    LIMIT 1
    ) AND data IS NOT NULL
GROUP BY collection_time
ORDER BY collection_time DESC
LIMIT 1"""

        def __init__(self, *args, **kwargs):
            logging.debug("sumit 1 polycom")
            super(polycom_device, self).__init__(*args, **kwargs)
            self._DATA_QUERY %= (
                    ", ".join("pres_%s AS `%s`" % (
                            k, self._OBJ_MAP[v]
                            ) for k, v in self.dbc.iterfetch(
                                    """SELECT journal_presentation_id, name
FROM master.dynamic_app_journal_presentation
WHERE app_id = %%s AND name in %s""" % (tuple(self._OBJ_MAP.keys()), ),
                                    args=(self._APP_ID, )
                            )),
                    self._APP_ID,
                    self._APP_ID,
                    self.did,
                    JOURNAL_STATE_CLOSED
                    )
            self._OBJ_QUERY %= (self.did, )
            #self.logger.debug(self._DATA_QUERY)
            # for now, assume any polycom devices will have config app
            self._CONFIG_APP_ID = self._get_app_id(self._CONFIG_APP_GUID)


        def _load_call_data(self):
            self._load_device_data()
            # ignore proc_*_val for certain objects
            #TODO: give tp_cdr() a way to handle this on its own




            for proc_key in ["Security", "State"]:
                if proc_key in tp_cdr._PROC_MAP:
                    tp_cdr._PROC_MAP[proc_key] = lambda x: {"str": x}

            tp_cdr._PROC_MAP["Duration"] = proc_duration_poly_val

            tp_cdr._PROC_MAP["Direction"] = proc_direction_val_poly
            tp_cdr._PROC_MAP["Local Start Time"] = proc_datetime_val_poly
            self.logger.debug(
                    "CDR_JOURNAL: %s calls in source",
                    self.dbc.autofetch_value(
                            """SELECT COUNT(*)
FROM dynamic_app_data_%s.journal_meta
WHERE did = %s AND state = %s AND date_update %s""" % (
                                    self._APP_ID,
                                    self.did,
                                    JOURNAL_STATE_CLOSED,
                                    self.date_range
                                    )
                            )
                    )

            for row in self.data_dbc.iterfetch_d(
                    self._DATA_QUERY % (self.date_range, )
                    ):
                entry_key = row["entry_key"]
                del row["entry_key"]
                if entry_key in self.call_data:
                    self.logger.debug("CDR_JOURNAL: entry %s already found, updating" % (entry_key, ))
                else:
                    #self.logger.debug("CDR_JOURNAL: adding entry %s" % (
                    #        entry_key,
                    #        ))
                    self.call_data[entry_key] = tp_cdr({
                            "Device": {
                                    "roa_id": self.roa_id,
                                    "co": self.company,
                                    "device": self.device,
                                    "tag": self.asset_tag,
                                    "loc": self.location,
                                    "model": self.model
                                    },
                            "IP Address" : self.local_number

                            })

                row["Local Start Time"] = row["Start Date"]+" "+row["Start Time"]
                self.call_data[entry_key].update(row)
            self._data_loaded = True

        def _load_device_data(self):
            #TODO: should these change based on calls' collection times?
            # get Local Number and Tandberg Model
            self.__dict__.update(
                    (k, self.dbc.autofetch_value(
                            self._OBJ_QUERY, args=v
                            ) or "N/A") for k, v in self._DEV_OBJ.iteritems()
                    )

    class polycom(polycom_device):

        _APP_GUID = "A7585D17B4B100E794B5D0C6EDBBBA2F"
        _CONFIG_APP_GUID = "53F0F4DDD739A3EA09B338BA668DAFB7"

        _OBJ_MAP = {
                "Call ID": ".Call Index",
                "Start Date": "Start Date",
                "Call Rate": "Initial Bit Rate",
                "Start Time": "Start Time",
                "Local Start Time": "Local Start Time",
                "Call Direction": "Direction",
                "Disconnect Reason": "Call Termination Reason",
                "Call Duration (hh:mm:ss)": "Duration",
                "Encryption": "Security",
                "Call Number 1" : "Remote Number",
                "Audio Protocol (Rx)" : "Rx Audio Protocol",
                "Average Latency (Rx)" : "Rx Avg Latency",
                "Video Protocol (Rx)" : "Rx Video Protocol",
            "Average Jitter (Rx)" : "Rx Avg Jitter",
        "Maximum Jitter (Rx)" : "Rx Max Jitter",
        "Maximum Latency (Rx)" : "Rx Max Latency",
        "Average Packets Lost (Rx)" : "Rx Avg Lost Pkts",
        "Video Format (Rx)" : "Rx Video Format",
        "Disconnect Reason" : "Disconnect Reason 3rd party"
                }

        def __init__(self, *args, **kwargs):
            super(polycom, self).__init__(*args, **kwargs)
            self._DEV_OBJ = {

                    "model": (
                            self._CONFIG_APP_ID,
                            self._CONFIG_APP_ID,
                            "System Model"
                            ),
                    "local_number": (
                            self._CONFIG_APP_ID,
                            self._CONFIG_APP_ID,
                            "Host IP Address"
                            ),
                    "Security": (
                            self._CONFIG_APP_ID,
                            self._CONFIG_APP_ID,
                            "Encryption Enable"
                            )
                    }

    #    def _load_device_data(self):
     #       super(polycom, self)._load_device_data()
      #      if self.Security == "False":
       #         self.Security = "Non-Secure"
        #    else:
         #       if self.Security == "True":
          #              self.Security = "Secure"



    ##########################################################################
    #                                                                        #
    #  run_app() Entry Point                                                 #
    #                                                                        #
    #  Classes, constants, and functions are all set, so now we can begin    #
    #  to actually operate on the data.                                      #
    #                                                                        #
    ##########################################################################

    try:

        # set up error handling variables
        calls = []
        closed_calls = []
        try: app_meta = get_app_instance_meta_data() or {}
        except DeserializationError: app_meta = {}
        logger.debug("CDR_JOURNAL: %s", app_meta)

        app = dict((t._APP_GUID, t) for t in (
                cisco_tp_device, tandberg_c, tandberg_mxp,polycom
                ))
        data_dbc.execute("""SELECT app_guid
FROM master.dynamic_app_collection AS dac
LEFT JOIN master.dynamic_app AS da ON dac.app_id = da.aid
WHERE did = %s AND app_guid IN %s
GROUP BY app_guid""" % (did, tuple(app.keys())))
        collect=data_dbc.fetchone()


        if collect is None:
            raise DeviceNotAligned(
                    "no device with did: %s found aligned with this app" %
                    (did, )
                    )
        # set up device with snippet inputs
        tpd = app[collect['app_guid']](did, app_id, data_dbc, logger)
        if "last_collection_time" in app_meta:
            tpd.set_date_range(
                    "> FROM_UNIXTIME(%s)" % app_meta["last_collection_time"]
                    )
        else:
            tpd.set_date_range(DATE_RANGE)

        # convert calls to journal entries
        for k, v in tpd.itercalls():
           # try:
           #     if int(v["Duration"]["value"]) <= 0:
           #         # skip zero-length calls
           #         continue
           # except ValueError:
           #     # or calls with no duration
           #     continue
            entry = get_entry(k)
            if entry is None:
                #logger.debug("CDR_JOURNAL: no entry found for key %s", k)
                entry = create_entry(k, JOURNAL_STATE_OPEN)
            else:
                if entry.get_state() == JOURNAL_STATE_CLOSED or k in closed_entries:
                    logger.debug("CDR_JOURNAL: call already closed: %s", k)
                    closed_calls.append(k)
                    continue
                elif entry.get_state() != JOURNAL_STATE_OPEN:
                    # not closed or open means something strange, probably
                    # requires support or dev examination and warrants
                    # halting execution
                    raise TelePresenceCommError(
                            "(device id: %s): unknown journal state " + \
                            "for entry key %s" % (tpd.did, k)
                            )
            entry.update_collected_data(v.to_entry())
            calls.append(entry)

    except MySQLError as e:
        raise TelePresenceCommError('runapp errorrrrrrrrrr'+str(e))

    finally:
        logger.debug("CDR_JOURNAL: %s", app_meta)
        set_app_instance_meta_data(app_meta)
        if len(calls) > 0:
            logger.debug("CDR_JOURNAL: saving %d calls", len(calls))
            EM7_RESULT.extend(calls)
            logger.debug("CDR_JOURNAL: EM7_RESULT contains %s calls", len(EM7_RESULT))
        if len(closed_calls) > 0:
            raise CallAlreadyClosed(str(closed_calls))


##############################################################################
#                                                                            #
#  Snippet Entry Point                                                       #
#                                                                            #
#  We should be eventing most exceptions that would be collection problems,  #
#  so only set COLLECTION_PROBLEM to True in the catch-all except: block     #
#                                                                            #s
##############################################################################

try:
    #if not isinstance(data_dbc, silo_cursor):
        #raise TelePresenceCredError("unable to get em7 database handle")
    # NOTE: due to the scope provided to apps, the run_app()
    #       environment is altered to include passed values
    app_globals = globals()
    app_globals.update(locals())
    exec "run_app()" in app_globals
except (CallAlreadyClosed,DeviceNotAligned,TelePresenceCommError,TelePresenceCredError) as e:
    API_ALERT('first section'+str(e))
except:
    COLLECTION_PROBLEM = True
    import traceback
    PROBLEM_STR = traceback.format_exc()
    INTERNAL_ALERTS.append((EM7_SNIPPET_EXCEPTION, PROBLEM_STR))
    API_ALERT(PROBLEM_STR, dbc=None)
finally:
    logger.debug("CDR_JOURNAL: EM7_RESULT contains %s calls", len(EM7_RESULT))