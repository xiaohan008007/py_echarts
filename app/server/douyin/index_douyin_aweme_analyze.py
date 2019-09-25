# -*- coding: utf-8 -*-

"""
Created on 10/13/16 10:30 AM
File name   :   index_ttk_show.py
Author      :   jacklone
Email       :   jichenglong1988@gmail.com
Description :

"""

import json
from elasticsearch import Elasticsearch
import logging
import datetime
from copy import deepcopy
import sys
import re
#import geoip2.database

CREATE = True
DELETE = False
# OP_TYPE = sys.argv[0]
READ_TYPE = sys.argv[1]
BULK_NUM = sys.argv[2]
IS_FILTER = sys.argv[3]
#CREATE = True
#DELETE = True

# ES_HOST = [{"host": "10.0.0.213", "port": 9200},
#            {"host": "10.0.0.214", "port": 9200},
#            {"host": "10.0.0.215", "port": 9200},
#            {"host": "10.0.0.216", "port": 9200},
#            {"host": "10.0.0.241", "port": 9200},
#            {"host": "10.0.0.242", "port": 9200},
#            {"host": "10.0.0.243", "port": 9200},
#            {"host": "10.0.0.244", "port": 9200},
#            ]

ES_HOST = [{"host": "10.0.0.243", "port": 9200},
           {"host": "10.0.0.243", "port": 9200},
           ]

INDEX_NAME = 'douyin_sea_analyze_aweme_4'
TYPE_NAME = 'douyinseaaweme4Response'
ID_FIELD = 'repId'

es = Elasticsearch(hosts=ES_HOST, http_auth=('elastic', 'tts_elastic'))
#reader = geoip2.database.Reader("/home/app/tracy/GeoLite2-City.mmdb")

def yield_obj(json_data):
    obj = {}


    ts_info = json_data['ctime']
    obj = json_data

    try:
        ts = datetime.datetime.strptime(ts_info, "%Y-%m-%d %H:%M:%S")

        obj["ts"] = ts
        del obj['ctime']
        #print(obj)
        desc = ""
        if 'desc' in obj:
            desc = obj["desc"]
        pattern = re.compile(r'#\w+')  # 查找数字
        topics = pattern.findall(desc)
        obj["topics"] = topics
        if 'avatar_url' not in obj:
            return 0,0
        if IS_FILTER=='true' and obj['digg_count']<5:
            return 0,0
        if 'play_count' in obj:
            del obj['play_count']
        if len(obj['topics']) <1:
            del obj['topics']
        if 'shoptype' in obj and obj['shoptype']=="":
            del obj['shoptype']
        if 'first_cid' in obj and len(obj['first_cid'])<1:
            del obj['first_cid']
            del obj['second_cid']
        if 'douyin_item' in obj and len(obj['douyin_item'])<1:
            del obj['douyin_item']
        if 'taobao_item' in obj and len(obj['taobao_item'])<1:
            del obj['taobao_item']
        #if obj['have_item'] is False:
           #del obj['douyin_item']
           #del obj['first_cid']
           #del obj['second_cid']
           #del obj['taobao_item']
        #if len(obj['topics'])<1:
           #del obj['topics']
        #if obj['douyin_cid']=="":
           #del obj['douyin_cid']
        #if 'comment_nums' in obj and len(obj['comment_nums'])<1:
        #    del obj['comment_nums']
        #if 'comment_word' in obj and len(obj['comment_word'])<1:
        #    del obj['comment_word']
        if 'comments' in obj:
            del obj['comments']
    except Exception as e:
        print("error: ", e)
        print('dirty', json_data)
        return 0,0
    idx = json_data['aweme_id']
    return idx, obj

def gen_data():
    print('start=====' + READ_TYPE)
    if READ_TYPE == "tail":
        while True:
            oneline = sys.stdin.readline()
            line = oneline.strip()
            try:
                json_data = json.loads(line)
            except Exception as e:
                print("parse_json error =============:" + line)
                continue
            yield yield_obj(json_data)
    else:
        for oneline in sys.stdin.readlines():
            line = oneline.strip()
            try:
                json_data = json.loads(line)
            except Exception as e:
                print("parse_json error =============:" + line)
                continue
            yield yield_obj(json_data)


def index_data():
    bulk_data = []

    for idx, data_dict in gen_data():
        op_dict = {
            "index": {
                "_index": INDEX_NAME,
                "_type": TYPE_NAME,
                "_id": idx
            }
        }
        bulk_data.append(op_dict)
        bulk_data.append(data_dict)

        if len(bulk_data) > int(BULK_NUM):
            try:
                es.bulk(index=INDEX_NAME, body=bulk_data, refresh=False, request_timeout=30)
                print("batch bulk -------"+BULK_NUM)
                bulk_data = []
            except:
                print("es connect timeout...")
                continue

    print("tail -F is killed...")
    if len(bulk_data) > 0:
        print("--------- end --------------")
        es.bulk(index=INDEX_NAME, body=bulk_data, refresh=True, request_timeout=30)
        bulk_data = []


if __name__ == "__main__":
    # reload(sys)
    # sys.setdefaultencoding('utf-8')

    if DELETE and es.indices.exists(INDEX_NAME):
        res = es.indices.delete(index=INDEX_NAME)

    if CREATE and not es.indices.exists(INDEX_NAME):
        request_body = {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 0
            },
            "mappings": {
                TYPE_NAME: {
                    # "_ttl": {
                    #     "enabled": True,
                    #     "default": "15d"
                    # },
                    "_all": {
                        "enabled": False
                    },
                    "dynamic_templates": [
                        {"strnotanalyzed": {
                            "match": "*",
                            "match_mapping_type": "string",
                            "mapping": {
                                "type": "string",
                                "index": "not_analyzed"
                            }
                        }
                        }
                    ],
                    "properties": {
                        "desc":{"type":"text","index":True,"analyzer": "ik_smart"}
                    }
                }
            }
        }

        print("creating '%s' index..." % INDEX_NAME)
        res = es.indices.create(index=INDEX_NAME, body=request_body)
        print(" response: '%s'" % res)

    index_data()
