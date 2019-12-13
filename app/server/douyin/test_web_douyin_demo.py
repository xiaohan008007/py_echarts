import requests
import os
import sys
import json
import urllib3

import redis
#
pool = redis.ConnectionPool(host='192.168.3.194', port=6379, db=5)
rds = redis.Redis(connection_pool=pool)
douyin_uid_signature = 'douyin:web:uid:awemes:signature:'


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#import util.douyin_util
# from .util import douyin_util

currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
# print(parentUrl)
sys.path.append(parentUrl)
from util.douyin_util import *

def get_jdata(uid):
    # res = requests.get('http://49.233.200.77:5001/sign/%s/' % uid)
    # j_data = json.loads(res.text)
    json_str = rds.get(douyin_uid_signature+uid)
    return json.loads(json_str)
def test():
    uid = '1305874926407576'
    # signature =get_sign(uid)
    # print(signature)
    j_data = get_jdata(uid)

    # print(j_data)
    signature = j_data['signature']
    ua = j_data['user-agent']

    # ua ='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'

    headers = {
        "user-agent":ua,
        # "referer": "https://www.iesdouyin.com/share/user/58958068057",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        # "cookie": "_ga=GA1.2.1933718197.1569723451; _gid=GA1.2.574325593.1569723451",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    }

    url = "https://www.iesdouyin.com/web/api/v2/aweme/post/?user_id=%s&sec_uid=&count=21&max_cursor=0&aid=1128&_signature={}" % uid

    response = requests.get(url.format(signature),headers=headers,verify=False)
    print(response.text)


if __name__ == '__main__':
    test()
    # ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    # headers = {
    #     "user-agent": ua,
    #     # "referer": "https://www.iesdouyin.com/share/user/58958068057",
    #     "sec-fetch-mode": "cors",
    #     "sec-fetch-site": "same-origin",
    #     # "cookie": "_ga=GA1.2.1933718197.1569723451; _gid=GA1.2.574325593.1569723451",
    #     "accept": "application/json",
    #     "accept-encoding": "gzip, deflate, br",
    #     "accept-language": "zh-CN,zh;q=0.9"
    # }
    # url = 'https://www.douyin.com/share/user/1305874926407576'
    # res = requests.get(url,headers=headers, verify=False)
    # print(res.text)