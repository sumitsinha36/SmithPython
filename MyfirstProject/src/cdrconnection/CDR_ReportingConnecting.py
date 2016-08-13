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