import hashlib
import requests
import time


list_sort = []
list_sha256 = []
l_account = ['your account', 'your account']
l_iccid = ['your iccid', 'your iccid']
l_password = ['your password', 'your password']
l_sign = ['your sign', 'your sign']


def sha256hex(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode())
    res = sha256.hexdigest()
    print("sha256加密结果:", res)
    list_sha256.append(res)

    return res


def sorted(username, password, secretkey):
    data = username+password+secretkey
    s = data
    l = list(s)
    l.sort()
    s = ''.join(l)
    print(s)
    list_sort.append(s)

    return s


def make_list():
    for i, j, k in zip(l_account, l_password, l_sign):
        print(i, j, k)
        sorted(i, j, k)

    for i in list_sort:
        sha256hex(i)


def api_run():
    url = 'http://112.90.145.10:10929/gprsRealTimeInfo.do'

    make_list()
    while True:
        for account, sign, iccid in zip(l_account, list_sha256, l_iccid):
            form = {
            'account': account,
            'sign': sign,  # "授权签名(account+password+secretkey,以字母升序排列,并使用64位SHA-256算法进行加密)",
            'iccid': iccid}

            res = requests.post(url=url, data=form)
            print(res.text)

        time.sleep(10)


if __name__ == '__main__':
    print(list_sort)
    print(list_sha256)
    api_run()

