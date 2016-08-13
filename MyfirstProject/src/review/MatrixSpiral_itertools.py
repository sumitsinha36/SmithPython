import itertools
arr = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]
print "\n Original array \n",list(itertools.chain(*arr))
def transpose_and_yield_top(arr):
    while arr:
        yield arr[0]
        arr = list(reversed(zip(*arr[1:])))
print "\n Spiral view of array \n",list(itertools.chain(*transpose_and_yield_top(arr)))