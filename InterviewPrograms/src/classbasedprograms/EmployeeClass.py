class EmployeeClass:
    'Common base class for all employees'
    #empName="sumit"
    #salary=0
    empCount=0

    '-- sumit'
    def __init__(self, name, salary):
        self.empName=name
        self.salary=salary
        EmployeeClass.empCount+=1

    def displayCount(self):
        print"count =%d"%EmployeeClass.empCount

    def printEmpolyee(self):
        print "Employee Name= %s , Salary=%d"%(self.empName,self.salary)


emp1=EmployeeClass("sumit",30000)
emp1.displayCount()
emp1.printEmpolyee()
emp2=EmployeeClass("prasanna",28000)
emp3=EmployeeClass("baskar",80000)
emp2.displayCount()
emp2.printEmpolyee()
emp3.displayCount()
emp3.printEmpolyee()

print EmployeeClass.__doc__
print EmployeeClass.__name__
print EmployeeClass.__module__
print EmployeeClass.__bases__
print EmployeeClass.__dict__



