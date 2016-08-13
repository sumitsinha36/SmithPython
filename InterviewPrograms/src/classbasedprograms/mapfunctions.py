def square(x):
    return x*x

def double(x):
    return x+x
lista=[1,2,3,4,5]
s=map(square,lista)
print s

d=map(double,lista)
print d

dd=map(lambda x:x+x,lista)
print dd




