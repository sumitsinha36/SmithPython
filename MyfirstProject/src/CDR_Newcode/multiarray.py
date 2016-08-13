elements = []

# Append empty lists in first two indexes.


# Add elements to empty lists.
for x in [0,1,2,3,4]:
    elements.append([])
    elements[x].append("roll_no")
    elements[x].append("collecge")
    elements[x].append("sumit_"+x.__str__())
    elements[x].append(25)
    elements[x].append("supaul :: "+x.__str__())


for obj in elements:
    print obj