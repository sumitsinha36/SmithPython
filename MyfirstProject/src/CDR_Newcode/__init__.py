dict={}
list_dict={}

for x in [1,2,3,4,5]:
    dict["name"]="sumit_"+x.__str__()
    dict["age"]=25+x
    dict["address"]="supaul_"+x.__str__()
    print dict
    list_dict[x]=dict


#dict["name"]="Amit"
#dict["age"]=20
#dict["address"]="puna"

#list_dict.append(dict)

#print dict
for obj in list_dict:
    print obj