import pymongo

client = pymongo.MongoClient(host='127.0.0.1', port=27017)
connection = client['data1']
db = connection['items1']

for i in range(14, 27):
    db.update({"_id": 'ox-{}'.format(i)}, {"$set": {"bit2": 0}})



