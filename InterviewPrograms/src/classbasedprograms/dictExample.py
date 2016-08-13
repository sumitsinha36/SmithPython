dict={}
dictAddr={}
dictAddr['Father Name']='Subodh Kumar Sinha'
dictAddr['Street']='CHoti Masjid Road'
dictAddr['Area']='Ward No-11'
dictAddr['District']='Supaul'
dictAddr['PinCode']=852131
dictAddr['Country']='India'
dictAddr['Land Mark']='Near Children Park'

List_Education=['10th','12th','BCA','MCA']

dict['Name']='Sumit Kumar Sinha'
dict['Age']=28
dict['Address']=dictAddr
dict['Education']=List_Education

for entrykey in dict.keys():
    print dict[entrykey]

for entrykey in dict.keys():
    if(type(entrykey) == type(dict())):
        for ekey in entrykey.keys():
            print ekey
    else:
        print dict[entrykey]






#print dict.__contains__('name')
#print dict.__getitem__('name')



#print dict.__len__()
#print dict.__str__()







