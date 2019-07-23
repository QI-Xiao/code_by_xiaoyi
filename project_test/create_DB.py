import pymongo
import bson.objectid


client = pymongo.MongoClient(host='127.0.0.1', port=27017)
connection = client['data1']
db = connection['items1']

ph_list = []
ox_list = []
t_list = []

for i in range(1, 27):
    ph_list.append('ph-{}'.format(i))
    ox_list.append('ox-{}'.format(i))
    t_list.append('t-{}'.format(i))

print(ph_list, ox_list, t_list)
# db.insert({'_id':_id, 'value':0})

for i in ph_list:
    db.insert({'_id': i, 'value':'0'})

for i in ox_list:
    db.insert({'_id': i, 'value':'0'})

for i in t_list:
    db.insert({'_id': i, 'value': '18.6'})

