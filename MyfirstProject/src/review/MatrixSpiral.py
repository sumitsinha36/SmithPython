arr = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]
print "\n Original array \n",arr

def transpose_and_yield_top(arr):
    print "\n arr at function start \t",arr
    while arr:
        print "\n arr at while start \t",arr
        print "\n arr[0]\t",arr[0]
        yield arr[0]
        arr = list(reversed(zip(*arr[1:])))
        print "\n arr final \t",arr

list_value=[]
for item in transpose_and_yield_top(arr):
    for value in item:
        list_value.append(value)
print list_value
