 def proc_duration_val(val):
        try: seconds = int(val)
        except (TypeError, ValueError): return {"value": val, "str": "00:00:00"}
        hours = seconds / 3600
        seconds -= hours * 3600
        minutes = seconds / 60
        seconds -= minutes * 60
        return {"value": val, "str": "%02d:%02d:%02d" % (
                hours, minutes, seconds
                )}


print proc_duration_val("20:33:33")