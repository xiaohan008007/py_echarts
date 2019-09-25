from pymongo import MongoClient
import json
from datetime import datetime


def format_url(url_set):
    url = ""
    for url_port in url_set:
        url = url + url_port + ','
    return url[:-1]


url_set = {'s-bp1ab95be815ccc4.mongodb.rds.aliyuncs.com:3717'}

# mongo_client3 = mongo_client.MongodbClient(url_set, "tts_douyin", username="tts_douyin", password="douyinrw")

url_port_set = format_url(url_set)
db_name = "weiyou_deploy"
username = "tts_weiyou"
password = "weiyourw"
client = MongoClient('mongodb://{}/'.format(url_port_set), connect=False)
db = client["{}".format(db_name)]
if username:
    db.authenticate(username, password)

i=1
for content in db["orders_detail"].find().batch_size(1000):
    # print(i++)
    content.pop('_id', 0)
    try:
        if 'time_payment' in content and content['time_payment']:
            content['time_payment'] = content['time_payment'].strftime('%Y-%m-%d %H:%M:%S')
        if 'time_create' in content and content['time_create']:
            content['time_create'] = content['time_create'].strftime('%Y-%m-%d %H:%M:%S')
        if 'end_time' in content and content['end_time']:
            content['end_time'] = content['end_time'].strftime('%Y-%m-%d %H:%M:%S')
        if 'consign_time' in content and content['consign_time']:
            content['consign_time'] = content['consign_time'].strftime('%Y-%m-%d %H:%M:%S')
        if 'firstInsertTime' in content and content['firstInsertTime']:
            content['firstInsertTime'] = content['firstInsertTime'].strftime('%Y-%m-%d %H:%M:%S')
        c = json.dumps(content, ensure_ascii=False)
        print(c)
    except Exception as e:
        print("ERROR LINE:")
        print(content)
