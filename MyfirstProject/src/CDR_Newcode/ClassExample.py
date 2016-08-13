class ref:
    def __init__(self,obj): self.obj=obj
    def set(self,obj):self.obj=obj
    def get(self):return self.obj
    def delete(self): del self.obj


a=ref([1,2])
print(a.get())

a.set([5,3])
print(a.get())

