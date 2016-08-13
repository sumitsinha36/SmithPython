# include the base db exception classes for capturing data cursor errors
from _mysql_exceptions import MySQLError
from silo_common.exceptions import DatabaseError

# get the data dbc to use for everything except
# API_ALERT and batch_source_collector
try:
    data_dbc = silo_cursor.data_db()
except (DatabaseError, MySQLError):
    API_ALERT(TelePresenceCredError(e))


# define an alert handler for exception messages
def API_ALERT(message, did=did, dbc=dbc, logger=logger):
    if logger is not None:
        logger.debug("CDR: (device id: %s): %s", did, message)
    if dbc is not None:
        dbc.execute("""INSERT INTO in_api.messages (xtype, xid, message, message_time, ytype, yid, yname) VALUES (1, %s, %s, NOW(), 0, 0, '')""", (did, message))

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