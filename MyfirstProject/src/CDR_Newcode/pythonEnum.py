def proc_array_val(array, val):
        try: return array[int(val)]
        except (IndexError, TypeError, ValueError): return array[0]

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
def proc_remote_call_type_val(val): return proc_enum_val(enum_remote_call_type, val)






print proc_state_val(0)
print proc_termination_val(0)
print proc_type_val(0)
print proc_mode_val(0)
print proc_security_val(0)
print proc_direction_val(0)
print proc_remote_call_type_val(0)









