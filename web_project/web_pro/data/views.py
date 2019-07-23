import time
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import pymongo

client = pymongo.MongoClient(host='127.0.0.1', port=27017)
connection = client['data1']
db = connection['items1']


def test1(request):
    ph_list = []
    ox_list = []
    t_list = []
    for i in range(1, 27):
        ph_list.append('ph-{}'.format(i))
        ox_list.append('ox-{}'.format(i))
        t_list.append('t-{}'.format(i))

    content = {}
    for p, o, t in zip(ph_list, ox_list, t_list):
        p1 = p.replace('-', '')
        o1 = o.replace('-', '')
        t1 = t.replace('-', '')
        content[p1] = db.find_one({'_id': p})['value']
        content[o1] = db.find_one({'_id': o})['value']
        content[t1] = (db.find_one({'_id': t})['value'])

    content['time'] = time.strftime("%Y-%m-%d %X")
    print(content)

    return render(request, 'data/index_test.html', context=content)





