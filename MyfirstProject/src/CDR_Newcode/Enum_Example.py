
enum_direction = ["unknown", "Incoming", "Outgoing", "N/A"]

# setting a default - let's simplify it with a small utility function
def proc_array_val(array, val):
        try: return array[int(val)]
        except (IndexError, TypeError, ValueError): return array[0]

 # keep both the numeric and the enum value
def proc_enum_val(array, val):
        return {"value": val, "str": proc_array_val(array, val)}

def proc_state_val(val): return proc_enum_val(enum_direction, val)


print proc_state_val(0)
print proc_state_val(1)
print proc_state_val(2)
print proc_state_val(3)