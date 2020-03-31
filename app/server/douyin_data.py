# coding: utf-8
from gevent import monkey
# 把当前的IO操作，打上标记，以便于gevent能检测出来实现异步(否则还是串行）
monkey.patch_all()
from gevent.pool import Pool
import gevent

import threading
from flask import render_template, Blueprint, request, send_file, Flask, jsonify


import requests

import time
import pyecharts
import codecs



import json
import csv
import codecs

from urllib import parse
import re
import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import datetime

import logging
from logging import handlers
logger = logging.getLogger(__name__)




app = Blueprint('douyin_data', __name__)
# root_logger = init_logger()

es = Elasticsearch([{'host':'es-cn-v641jqyjv000i1mmi.elasticsearch.aliyuncs.com', 'port':9200}], http_auth=('elastic', 'PlRJ2Coek4Y6'))

url_set = {'172.17.0.43:27017'}

# mongo_client = mongo_client.MongodbClient(url_set, "douyin", username="douyin_user", password="douyin@rw")

pool_size = 5
pool = Pool(pool_size)
goup = []



class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,filename,level='info',when='D',backCount=3,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        fmt = '%(message)s'
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        # sh = logging.StreamHandler()#往屏幕上输出
        # sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)#设置文件里写入的格式
        # self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)
# if __name__ == '__main__':
#     log = Logger('all.log',level='debug')
#     log.logger.debug('debug')
#     log.logger.info('info')
#     log.logger.warning('警告')
#     log.logger.error('报错')
#     log.logger.critical('严重')
#     Logger('error.log', level='error').logger.error('error')


log = Logger('all.log', level='info')

@app.route('/douyin/accept', methods=['post'])
def accept():
    param_info = request.values.to_dict()
    json_data = param_info['json_data']
    log.logger.info(json_data)
    # logger.info(json_data)
    return "ok"


def post_data_to_douyin(jsons):
    textmod = {"json_data": jsons}
    r = requests.post("http://49.235.96.25:9963/douyin/accept", data=textmod)

    result = r.text
    return result


def find_es():
    body = {
      "query": {


        "bool": {
          "must": [

              # {
              #     "wildcard": {
              #         "custom_verify": {
              #             "value": "*主持人"
              #         }
              #     }
              # }

              # {
              #   "match": {
              #     "topics": "#萌宠"
              #   }
              # }
              # {
              #           "exists": {
              #             "field": "weixin"
              #           }
              #         },
   #            {
   #          "bool": {
   # "should": [
   #     {
   #         "match": {
   #             "custom_verify": "主持人"
   #         }
   #     },
   #     {
   #         "match": {
   #             "custom_verify": "山东广播电视台主持人"
   #         }
   #     },
   #     {
   #         "match": {
   #             "custom_verify": "辽宁广播电视台主持人"
   #         }
   #     },
   #     {
   #         "match": {
   #             "custom_verify": "山东广播电视台广播文艺频道主持人"
   #         }
   #     }
   #     ,
   #     {
   #         "match": {
   #             "custom_verify": "FM1036福建新闻广播主持人"
   #         }
   #     },
   #     {
   #         "match": {
   #             "custom_verify": "黑龙江广播电视台 主持人"
   #         }
   #     },
   #     {
   #         "match": {
   #             "custom_verify": "广西广播电视台FM104主持人"
   #         }
   #     },
   #     {
   #         "match": {
   #             "custom_verify": "中国教育电视台主持人"
   #         }
   #     },
   #     {
   #         "match": {
   #             "custom_verify": "广西电台970女主播电台主持人"
   #         }
   #     }
   #     ]}}


            # {
            #   "range": {
            #     "follower_count": {
            #       "gte": 1000000,
            #       "lte": 100000000
            #     }
            #   }
            # }
            #   ,
            #   {"range": {
            #       "ts": {
            #           #"lte": "2019-12-06T11:30:00.000Z",
            #           "gte": "2019-12-06T11:30:00.000Z"
            #       }
            #   }}
              # ,
            # {
            #   "match": {
            #     "with_fusion_shop_entry": True
            #   }
            # },
            # {
            #   "exists": {
            #     "field": "author_id_analyze"
            #   }
            # }

          ]
          #   ,
          # "must_not": [
          #   # {"match": {
          #   #   "douyin_cid": ""
          #   # }}
          #     {
          #       "exists": {
          #         "field": "nickname_no_analyze"
          #       }
          #     }
          # ]
        }
      }
    }




    result = es.search(index='douyin_sea_user_6', body=body,size=10000, scroll='1m')


    sid = result['_scroll_id']
    scroll_size = result['hits']['total']
    total=len(result['hits']['hits'])
    push_total = 0
    # Start scrolling
    push_total = deal_s(result, push_total)

    while (scroll_size > 0):
        print("Scrolling...")
        result = es.scroll(scroll_id=sid, scroll='1m')
        # Update the scroll ID
        sid = result['_scroll_id']
        # Get the number of results that we returned in the last scroll
        scroll_size = len(result['hits']['hits'])

        push_total = deal_s(result, push_total)
        total+=scroll_size
        # print("scroll size: " + str(push_total) + " total:" + str(total))
        # if total>=4000:
        #     break

    return "push:"+str(push_total)+"/"+str(total)

def deal_s(result,push_total, writer):
    ACTIONS = []
    for source in result['hits']['hits']:
        my_source = source['_source']
        if 'uid' not in my_source:
            continue
        goup.append(pool.spawn(post_data_to_douyin, jsons=k))
        if k % pool_size == 0:
            gevent.joinall(goup)
            goup = []
        push_total += 1
    return push_total


if __name__ == '__main__':


    pool = Pool(5)
    goup = []
    #
    # goup.append(pool.spawn(set_aweme_to_redis, uid='7351209324'))
    # gevent.joinall(goup)
    #
    # sys.exit()



    for k in range(10):
        goup.append(pool.spawn(post_data_to_douyin, jsons=k))
        if k % pool_size == 0:
            gevent.joinall(goup)
            goup = []


