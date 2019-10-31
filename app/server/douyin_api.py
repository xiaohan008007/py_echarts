# coding: utf-8
import threading
from flask import render_template, Blueprint, request, send_file, Flask, jsonify
from .util.utils import init_logger, last_n_days, n_day_ago
from .util import mysql_client, mongo_client, photo_util
from .util import douyinUtil
from .util import douyin_stat

import requests

import time
import pyecharts



import json
import csv
import codecs

from urllib import parse
import re
import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from .douyin.douyinapi_5 import DouYinApi
import datetime
import redis

pool = redis.ConnectionPool(host='10.0.0.93', port=6379)
r = redis.Redis(connection_pool=pool)

pool2 = redis.ConnectionPool(host='10.0.0.93', port=6379, db=3)
r2 = redis.Redis(connection_pool=pool2)
es = Elasticsearch([{'host':'es-cn-v6418omlz000m5fr4.elasticsearch.aliyuncs.com', 'port':9200}], http_auth=('elastic', 'PlRJ2Coek4Y6'))




app = Blueprint('douyin_api', __name__)
root_logger = init_logger()
mysql_client1 = mysql_client.MysqlClient(db='tts_qly_analysis')
mysql_client2 = mysql_client.MysqlClient(db='tts_tob_qly_v2')
mysql_client3 = mysql_client.MysqlClient(db='tts_douyin')


url_set = {'s-bp1ab95be815ccc4.mongodb.rds.aliyuncs.com:3717'}
mongo_client1 = mongo_client.MongodbClient(url_set, "qly_keyword", username="tts_qly", password="qlyrw")
mongo_client2 = mongo_client.MongodbClient(url_set, "qly_industry_168", username="tts_qly", password="qlyrw")
mongo_client3 = mongo_client.MongodbClient({'s-bp1fb86105e14fa4.mongodb.rds.aliyuncs.com:3717'}, "tts_douyin", username="tts_douyin", password="douyinrw")
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()






import codecs


@app.route('/accept_data', methods=['post'])
def accept_data():

    txt_file = request.files.get('txt')
    flag = False
    response = ""
    method = ""

    for line in txt_file.readlines():
        line = line.decode()
        data = parse.unquote((str(line)))
        if data.startswith('GET ') and data.find('GET /aweme/v1/feed') < 0 and data.find('GET /aweme/v1/music/detail') < 0 and data.find('GET /aweme/v1/music/aweme') < 0:
            break
        else:
            # if data.startswith('GET '):
            #     print(data)
            if data.find('GET /aweme/v1/music/detail') > -1:
                method = 'music_detail'
            elif data.find('GET /aweme/v1/music/aweme') > -1:
                method = 'music_aweme'
            elif data.find('GET /aweme/v1/feed') > -1:
                method = 'feed'
            elif data.startswith('GET '):
                print("+++++++++++"+data)

        if data.startswith('{') or flag:
            # print(data)

            if data.startswith('{'):
                flag = True
            if flag:
                # response += \
                # print("====="+data)
                data = data.replace("\"{", "{").replace("}\"", "}")
                response += data.replace("\n", '').replace('\t', '').strip()

        # print(line)

    # print(method)
    # print(response)
    if response != "":
        if method == "music_detail":
            douyinUtil.save_music_detail(response)
        elif method == 'music_aweme':
            print(response)
            douyinUtil.save_music_aweme(response)

        elif method == 'feed':
            # print(response)
            douyinUtil.save_feed(response)
        # if data.startswith('GET ') and (data.find('GET /aweme/v1/music/detail') < 0 and data.find('GET /aweme/v1/music/aweme')<0):
        #     break
        # # if data.find('GET /aweme/v1/music/detail') > -1 or data.find('GET /aweme/v1/music/aweme') > -1:
        # douyin(data)
        # if data.find('mtop.taobao.wsearch.h5search') > -1:
        #     # print(data)
        #     if data.find('GET ') > -1 and data.find('api=mtop.taobao.wsearch.h5search') > -1:
        #         params = data.split("&")
        #         for pa in params:
        #             if pa.startswith('data='):
        #                 q_data = pa.split("=")[1]
        #                 q_data = q_data.replace(' HTTP/1.1', '')
        #                 try:
        #                     data_json = json.loads(q_data)
        #                 except Exception as e:
        #                     print(q_data)
        #                     logging.exception(e)
        #                     return
        #                 keyword = data_json['q']
        #                 page = data_json['page']
        #                 # print(keyword+"\t"+str(page))
        #     if data.find('listItem') > -1:
        #         print_item(data, keyword, page)
            # print(data)
        # print(str(line)+"\n")
    # path = basedir + "/accept/"
    # file_path = path + txt_file.filename
    # txt_file.save(file_path)
    print('hahahaha')
    # print(data)
    return 'ok'
    # return cats_forcast(q)


@app.route('/douyin/daily_set', methods=['get'])
def daily_set():
    uid_set = r.smembers('douyin:doudada:uid:dis')
    print(len(uid_set))
    f = codecs.open('daily_set.txt', 'a+', 'utf-8')
    index_num = 0
    for uid in uid_set:
        index_num+=1
        uid = uid.decode()
        es_result = es.search(index='douyin_sea_user_4', q='uid:"' + uid + '"')
        hits = es_result['hits']['hits']
        result = {}
        result['uid'] = uid
        if len(hits) > 0:
            source = hits[0]['_source']
            result['uid'] = source['uid']
            result['ctime'] = source['ts']
            result['nickname'] = source['nickname']
            result['follower_count'] = source['follower_count']
            if 'douyin_cid' in source:
                result['douyin_cid'] = source['douyin_cid']
            if source['follower_count']<10000:
                print("+++++++<10000++++:"+uid)
                f.write("+++++++<10000++++:"+uid+"\n")
            print(str(index_num)+" "+str(result))
            f.write(str(index_num)+" "+str(result)+"\n")
        else:
            print(str(index_num)+" "+"==============not====:"+uid)
            f.write(str(index_num)+" "+"==============not====:"+uid+"\n")
    f.close()

@app.route('/douyin/push_daily', methods=['get'])
def push_daily():
    param_info = request.values.to_dict()
    result = {}
    if 'author_id' not in param_info:
        result['code'] = '-1'
        result['message'] = 'need param author_id'
        return json.dumps(result)
    user_info = init_push(param_info)
    user_info_json = json.loads(user_info)
    uid = user_info_json['uid']
    print(uid)
    if 'remove' in param_info:
        remove_result = r.srem('douyin:doudada:uid:dis', uid)
        user_info_json['daily_remove'] = remove_result
    else:
        set_result = r.sadd('douyin:doudada:uid:dis', uid)
        user_info_json['daily_set'] = set_result
    user_info_json['daily_set_size'] = r.scard('douyin:doudada:uid:dis')
    return json.dumps(user_info_json)


@app.route('/douyin/get_uid', methods=['get'])
def get_uid():
    param_info = request.values.to_dict()
    result = {}
    if 'author_id' not in param_info:
        result['code'] = '-1'
        result['message'] = 'need param author_id'
        return json.dumps(result)
    author_id = param_info['author_id']
    es_result = es.search(index='douyin_sea_user_4', q='author_id:"' + author_id + '"')
    hits = es_result['hits']['hits']

    if len(hits) > 0:
        source = hits[0]['_source']
        result['code'] = '1'
        result['uid'] = source['uid']
        result['ctime'] = source['ts']
        result['nickname'] = source['nickname']
        result['from'] = 'es'
    else:
        result['code'] = '0'
        result['message'] = 'not found in es'
    return json.dumps(result)


@app.route('/douyin/update_uid', methods=['get'])
def update_uid():
    list = mongo_client3.find_user_uidnull(1)
    size = 0
    for user in list:
        print(user['authorId'])
        size+=1
        param = {}
        param['author_id']=user['authorId']
        try:
            init_push(param)
        except:
            print("======= "+user['authorId']+" =====not======")
    return str(size)

@app.route('/douyin/del_es', methods=['get'])
def delete_es():
    # param_info = request.values.to_dict()
    # if 'uid' in param_info:
    #     del_es(param_info['uid'])

    uids=['110207550638','110681553200','338275863639191','104339181004','104339181004','101451587839','109020946945','103240935532','3311356577841676','62645582724','110557309933','98217379613','83839355573','106811127431','104902872296','110681553200','98212188339','106200351743','59341887718','60586931248','72711805736','59952519565','76853294490','88276696366','10217606758']
    for uid in uids:
        del_es(uid)
    return 'ok'

def del_es(uid):

    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "uid": uid
                        }
                    }
                    # {
                    #   "range": {
                    #     "follower_count": {
                    #       "gte": 1000000,
                    #       "lte": 100000000
                    #     }
                    #   }
                    # }
                    # ,
                    # {"range": {
                    #     "ts": {
                    #         "lte": "2019-06-03T17:50:00.000Z",
                    #         "gte": "2019-04-01T00:00:00.000Z"
                    #     }
                    # }},
                    # {
                    #   "match": {
                    #     "with_fusion_shop_entry": True
                    #   }
                    # },
                    # {
                    #   "exists": {
                    #     "field": "shoptype"
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
                #         "field": "shoptype"
                #       }
                #     }
                # ]
            }
        }
    }
    es.delete_by_query(index='douyin_sea_relation_item',body=body)
    es.delete_by_query(index='douyin_sea_analyze_aweme_5', body=body)
    # es.delete_by_query(index='douyin_sea_user_4', body=body)
    return 'ok'




@app.route('/douyin/find_es', methods=['get'])
def import_es():
    t = threading.Thread(target=find_es(), name='3')
    t.start()
    return "ok"



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
            #           "lte": "2019-06-13T10:50:00.000Z",
            #           "gte": "2019-04-01T00:00:00.000Z"
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
            #     "field": "shoptype"
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
          #         "field": "douyin_cid"
          #       }
          #     }
          # ]
        }
      }
    }
    csv_file = codecs.open('3000.csv', 'w', 'utf_8_sig')  # 解决写入csv时中文乱码
    writer = csv.writer(csv_file)
    writer.writerow(['昵称', '性别', '省份', '抖音id', '签名', '点赞数',
                     '关注人数', '粉丝数', '作品数', '类目'])



    result = es.search(index='douyin_sea_analyze_aweme_5', body=body,size=10000, scroll='1m')


    sid = result['_scroll_id']
    scroll_size = result['hits']['total']
    total=len(result['hits']['hits'])
    push_total = 0
    # Start scrolling
    push_total = deal_s(result, push_total, writer)

    while (scroll_size > 0):
        print("Scrolling...")
        result = es.scroll(scroll_id=sid, scroll='1m')
        # Update the scroll ID
        sid = result['_scroll_id']
        # Get the number of results that we returned in the last scroll
        scroll_size = len(result['hits']['hits'])

        push_total = deal_s(result, push_total, writer)
        total+=scroll_size
        # print("scroll size: " + str(push_total) + " total:" + str(total))
        # if total>=4000:
        #     break
    csv_file.close()
    return "push:"+str(push_total)+"/"+str(total)


def deal_s(result,push_total, writer):
    ACTIONS = []
    for source in result['hits']['hits']:
        my_source = source['_source']
        if 'signature' in my_source:
            continue
        #item['title_no_analyze'] = item['title']
        # uid = user['uid']
        # if 'signature'  in user:
        #     signature = user['signature']
        #     if signature.find(':')>-1:
        #         signature = signature.replace('\n', ' ')
        #         print(uid+": "+signature)
        #
        #
        #         matchs=re.findall(r'([WwVvXx❤嶶微胃信交流星 心🌟☎🛰|❤️💕✨✉😘😊Ｖ+➕💗🏥📱⭐]+)[\n:： ️ ，]{1,3}([⃣0-9a-zA-Z_\-@]+)',
        #                    signature)
        #         for match in matchs:
        #             if match[0] != '' and len(match[1]) > 5:
        #                 print(match)
        #                 push_total += 1
        #                 break
                # print(matchs)

        # writer.writerow(['昵称', '性别', '省份', '抖音id', '签名', '点赞数',
        #                  '关注人数', '粉丝数', '作品数', '类目'])
        # if 'signature' not in user:
        #     print(uid)
        #     # continue
        # elif push_total < 3000:
        #     gender = '未知'
        #     if user['gender'] == 1:
        #         gender = '男'
        #     elif user['gender'] == 2:
        #         gender = '女'
        #     douyin_cid=''
        #     if user['douyin_cid'] == '10127':
        #         douyin_cid = '美妆'
        #     elif user['douyin_cid'] == '10137':
        #         douyin_cid = '美女'
        #     elif user['douyin_cid'] == '10131':
        #         douyin_cid = '舞蹈'
        #     elif user['douyin_cid'] == '10140':
        #         douyin_cid = '时尚'
        #     elif user['douyin_cid'] == '10136':
        #         douyin_cid = '穿搭'
        #     writer.writerow(
        #         [user['nickname'], gender, user['province'], user['author_id'], user['signature'],
        #          int(user['total_favorited']), int(user['following_count']), int(user['follower_count']), int(user['aweme_count']),
        #          douyin_cid])
        #     push_total+=1
        # nickname = source['_source']['nickname']
        # if nickname == "已重置":
        #     del_es()
        #     print(uid + ":删除信息")
        #     continue
        # set_result = r.sismember('douyin:doudada:uid:dis', uid)
        # set_result = r.sadd('douyin:test14', uid)
        # set_result = r.sadd('douyin:doudada:uid:dis', uid)
        # if set_result == 0:
        #     continue
        # else:
        #     push_total += 1
        # # print(uid+":"+str(set_result))
        # # del_es(uid)
        # author_id=user['author_id']
        # douyin_cid='10148'
        # userFans_list = mongo_client3.get_userfans(author_id)
        # exits = False
        # for userFans in userFans_list:
        #     userFans = init_fans(userFans, uid, author_id, douyin_cid, {})
        #     exits = True
        #
        # if not exits:
        #     userFans = {}
        #     userFans = init_fans(userFans, uid, author_id, douyin_cid, {})
        #
        # mongo_client3.update_userfans(userFans)
        # post_push(uid, '', 'local', '', 0)
        action = {
                     "_index": "douyin_sea_analyze_aweme_5",
                     "_type": "douyinseaaweme5Response",
                    "_id":my_source['aweme_id']  # _id 也可以默认生成，不赋值
                      }
        action['_source'] = my_source
        ACTIONS.append(action)

        push_total+=1
    # success, _ = bulk(es, ACTIONS, index="douyin_sea_analyze_aweme_5", raise_on_error=True)
    # print('Performed %d actions' % success)
    return push_total


@app.route('/douyin/push_fans', methods=['get'])
def push_fans():
    param_info = request.values.to_dict()
    re = push_user_fans(param_info)
    return re


def push_user_fans(param_info):
    douyin_cid = ""
    if 'douyin_cid' in param_info:
        douyin_cid = param_info['douyin_cid']

    jsons = init_push(param_info)
    push_data = json.loads(jsons)
    # 出错了 终止
    if 'uid' not in push_data:
        return json.dumps(push_data)
    textmod = {"author_id": param_info['author_id'], "uid": push_data['uid'], "douyin_cid": douyin_cid}
    r = requests.post("http://192.168.3.140:5002/api/v1/picture", data=textmod)

    result = r.text
    obj = json.loads(r.text)
    # obj['ctime'] = ctime
    # obj['from'] = _from
    # obj['nickname'] = nickname
    # obj['uid'] = uid
    push_data['fans_code']= obj['code']
    push_data['fans_msg'] = obj['msg']

    try:
        return_val = json.dumps(push_data)
    except Exception as e:
        logging.exception(e)

    print("hahhaha=========")
    return return_val


@app.route('/douyin/push_user', methods=['get'])
def push_user():
    param_info = request.values.to_dict()
    return init_push(param_info)


def init_push(param_info):
    ctime = ''
    _from = 'es'
    nickname = ''
    douyin_cid = ''

    if 'douyin_cid' in param_info:
        douyin_cid = param_info['douyin_cid']
    if 'author_id' in param_info:
        author_id = param_info['author_id']
        result = es.search(index='douyin_sea_user_4', q='author_id:"' + author_id + '"')
        hits = result['hits']['hits']
        if len(hits) > 0:
            source = hits[0]['_source']
            uid = source['uid']
            ctime = source['ts']
            nickname = source['nickname']
            _from = 'es'

        else:
            api = DouYinApi('210d096b12055ace')

            device_info = api.get_device_info()
            device_id = device_info['device_id']
            iid = device_info['iid']
            uuid = device_info['uuid']
            openudid = device_info['openudid']
            serial_number = device_info['serial_number']
            clientudid = device_info['clientudid']
            sim_serial_number = device_info['sim_serial_number']
            new_user = device_info['new_user']
            api.init_device_ids(device_id, iid, uuid, openudid, serial_number, clientudid, sim_serial_number)
            api.init_token_id()

            if new_user:
                ret = api.send_xlog("install")
                print('xlog ret:' + api.decrypt_xlog(ret))
            general_search_ret = api.general_search(author_id, 0, 1)
            json_data = json.loads(general_search_ret)
            data = json_data['data']
            if len(data) < 1:
                return "{\"code\":0,\"msg\":\"用户可能不存在，去抖音找一下\",\"from\":\"api\"}"
            usr_list = data[0]['user_list']
            user_info = usr_list[0]['user_info']
            uid = user_info['uid']
            nickname = user_info['nickname']
            _from = 'api'
            print("user from api:" + author_id)
            # print('general_search_ret:' + general_search_ret)

        userFans_list = mongo_client3.get_userfans(uid)
        exits = False
        for userFans in userFans_list:
            userFans = init_fans(userFans, uid, author_id, douyin_cid, param_info)
            exits = True

        if not exits:
            userFans = {}
            userFans = init_fans(userFans, uid, author_id, douyin_cid, param_info)
        try:
            mongo_client3.update_userfans(userFans)
        except Exception as e:
            logging.exception(e)
            return "{\"code\":0,\"msg\":\"更新达人类目mongo出错，操作终止，请联系管理员\",\"from\":\""+_from+"\"}"
    upall = 0
    if 'upall' in param_info:
        upall = 1 ##更新全部历史视频
    return post_push(uid, ctime, _from, nickname, upall)

def init_fans(userFans, uid, author_id, douyin_cid, param_info):
    qq = ''
    weibo = ''
    weixin = ''
    phone = ''
    if 'qq' in param_info:
        qq = param_info['qq']
    if 'weibo' in param_info:
        weibo = param_info['weibo']
    if 'weixin' in param_info:
        weixin = param_info['weixin']
    if 'phone' in param_info:
        phone = param_info['phone']
    if qq:
        userFans['qq'] = qq
    if weibo:
        userFans['weibo'] = weibo
    if weixin:
        userFans['weixin'] = weixin
    if phone:
        userFans['phone'] = phone
    has_contact = False
    if qq or weibo or weixin or phone:
        has_contact = True
        userFans['has_contact'] = has_contact
    userFans['uid'] = uid
    userFans['authorId'] = author_id
    userFans['ctime'] = datetime.datetime.utcnow()
    if douyin_cid:
        userFans['dcatId'] = douyin_cid
    if '_id' in userFans:
        del userFans['_id']
    return userFans


def post_push(uid, ctime, _from, nickname, upall):
    textmod = {"uid": uid,"aweme_id": "", "upall": upall}
    r = requests.post("http://192.168.3.140:5002/api/v1/update", data=textmod)

    result = r.text
    obj = json.loads(r.text)
    obj['ctime'] = ctime
    obj['from'] = _from
    obj['nickname'] = nickname
    obj['uid'] = uid
    return json.dumps(obj)


@app.route('/douyin/pluginPv', methods=['get'])
def push_pluginPv():

    param_info = request.values.to_dict()
    starttime1 = ''
    endTime1 = ''

    starttime2 = ''
    endTime2 = ''
    if 'starttime' in param_info:
        starttime1 = param_info['starttime'] + " 00:00:00"
        endTime1 = param_info['starttime'] + " 23:59:59"
    if 'endtime' in param_info:
        starttime2 = param_info['endtime']
        endTime2 = param_info['endtime'] + " 23:59:59"

    if starttime1 == '' or len(starttime1) < 10:
        starttime1 = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
        endTime1 = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d 23:59:59')

    if starttime2 == '' or len(starttime2) < 10:
        starttime2 = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
        endTime2 = datetime.datetime.now().strftime('%Y-%m-%d 23:59:59')

    beforeStats = mysql_client3.find_plugin_hour(starttime1,endTime1)
    endStats = mysql_client3.find_plugin_hour(starttime2,endTime2)

    bpluginPv = beforeStats['plugin_pv'].tolist()
    for j in range(24):

        if j > len(bpluginPv) - 1:
            bpluginPv.append(0)
    epluginPv = endStats['plugin_pv'].tolist()
    for j in range(24):
        if j > len(epluginPv) - 1:
            epluginPv.append(0)

    rdates = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

    bar = pyecharts.Line("插件Pv趋势图", "数量", width=1000, height=600)
    bar.add(starttime1.split(" ")[0], rdates, bpluginPv, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True,
            is_label_show=True)
    bar.add(starttime2.split(" ")[0], rdates, epluginPv, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True,
            is_label_show=True)

    ret_html = render_template('douyin_plugin.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               myurl='/douyin/pluginPv',
                               script_list=bar.get_js_dependencies())
    return ret_html



@app.route('/douyin/installHour', methods=['get'])
def push_installHour():
    param_info = request.values.to_dict()
    starttime1 = ''
    endTime1 = ''

    starttime2 = ''
    endTime2 = ''
    if 'starttime' in param_info:
        starttime1 = param_info['starttime'] + " 00:00:00"
        endTime1 = param_info['starttime'] + " 23:59:59"
    if 'endtime' in param_info:
        starttime2 = param_info['endtime'] + " 00:00:00"
        endTime2 = param_info['endtime'] + " 23:59:59"

    if starttime1 == '' or len(starttime1) < 10:
        starttime1 = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
        endTime1 = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d 23:59:59')

    if starttime2 == '' or len(starttime2) < 10:
        starttime2 = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
        endTime2 = datetime.datetime.now().strftime('%Y-%m-%d 23:59:59')

    beforeStats = mysql_client3.find_plugin_hour(starttime1, endTime1)
    endStats = mysql_client3.find_plugin_hour(starttime2, endTime2)

    binstallHour = beforeStats['plugin_install'].tolist()
    for j in range(24):
        if j > len(binstallHour) - 1:
            binstallHour.append(0)
    einstallHour = endStats['plugin_install'].tolist()
    for j in range(24):
        if j > len(einstallHour) - 1:
            einstallHour.append(0)

    rdates = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    bar = pyecharts.Line("插件安装趋势图", "数量", width=1000, height=600)
    bar.add(starttime1.split(" ")[0], rdates, binstallHour, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True,
            is_label_show=True)

    bar.add(starttime2.split(" ")[0], rdates, einstallHour, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True,
            is_label_show=True)

    ret_html = render_template('douyin_plugin.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               myurl='/douyin/installHour',
                               script_list=bar.get_js_dependencies())
    return ret_html

@app.route('/douyin/newUser', methods=['get'])
def push_newUser():
    param_info = request.values.to_dict()
    starttime1 = ''
    endTime1 = ''

    starttime2 = ''
    endTime2 = ''

    if 'starttime' in param_info:
        starttime1 = param_info['starttime'] + " 00:00:00"
        endTime1 = param_info['starttime'] + " 23:59:59"
    if 'endtime' in param_info:
        starttime2 = param_info['endtime'] + " 00:00:00"
        endTime2 = param_info['endtime'] + " 23:59:59"

    if starttime1 == '' or len(starttime1) < 10:
        starttime1 = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
        endTime1 = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d 23:59:59')

    if starttime2 == '' or len(starttime2) < 10:
        starttime2 = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
        endTime2 = datetime.datetime.now().strftime('%Y-%m-%d 23:59:59')

    beforeStats = mysql_client3.find_plugin_hour(starttime1, endTime1)
    endStats = mysql_client3.find_plugin_hour(starttime2, endTime2)

    bnewUser = beforeStats['new_user'].tolist()
    for j in range(24):
        if j > len(bnewUser) - 1:
            bnewUser.append(0)
    enewUser = endStats['new_user'].tolist()
    for j in range(24):
        if j > len(enewUser) - 1:
            enewUser.append(0)

    rdates = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    bar = pyecharts.Line("新用户趋势图", "数量", width=1000, height=600)
    bar.add(starttime1.split(" ")[0], rdates, bnewUser, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True,
            is_label_show=True)
    bar.add(starttime2.split(" ")[0], rdates, enewUser, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True,
            is_label_show=True)
    ret_html = render_template('douyin_plugin.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               myurl='/douyin/newUser',
                               script_list=bar.get_js_dependencies())
    return ret_html


@app.route('/douyin/webPv', methods=['get'])
def push_webPv():
    param_info = request.values.to_dict()
    starttime1 = ''
    endTime1 = ''

    starttime2 = ''
    endTime2 = ''
    if 'starttime' in param_info:
        starttime1 = param_info['starttime'] + " 00:00:00"
        endTime1 = param_info['starttime'] + " 23:59:59"
    if 'endtime' in param_info:
        starttime2 = param_info['endtime'] + " 00:00:00"
        endTime2 = param_info['endtime'] + " 23:59:59"

    if starttime1 == '' or len(starttime1) < 10:
        starttime1 = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
        endTime1 = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d 23:59:59')

    if starttime2 == '' or len(starttime2) < 10:
        starttime2 = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
        endTime2 = datetime.datetime.now().strftime('%Y-%m-%d 23:59:59')

    beforeStats = mysql_client3.find_plugin_hour(starttime1, endTime1)
    endStats = mysql_client3.find_plugin_hour(starttime2, endTime2)

    bwebPv = beforeStats['web_pv'].tolist()
    for j in range(24):
        if j > len(bwebPv) - 1:
            bwebPv.append(0)

    ewebPv = endStats['web_pv'].tolist()
    for i in range(24):
        if i > len(ewebPv) - 1:
            ewebPv.append(0)

    print(ewebPv)

    rdates = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

    bar = pyecharts.Line("主站Pv趋势图", "数量", width=1000, height=600)
    bar.add(starttime1.split(" ")[0], rdates, bwebPv, mark_point=["max", "min"], mark_line=["average"], is_label_show=True, is_more_utils=True, connectNulls=True)
    bar.add(starttime2.split(" ")[0], rdates, ewebPv, mark_point=["max", "min"], mark_line=["average"], is_label_show=True, is_more_utils=True, connectNulls=True)

    ret_html = render_template('douyin_plugin.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               myurl='/douyin/webPv',
                               script_list=bar.get_js_dependencies())
    return ret_html


@app.route('/douyin/pluginDay', methods=['get'])
def push_pluginday():

    param_info = request.values.to_dict()
    starttime = ''
    endtime = ''
    if 'starttime' in param_info:
        starttime = param_info['starttime']
    if 'endtime' in param_info:
        endtime = param_info['endtime']

    if starttime == '':
        starttime = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d 00:00:00')

    if endtime == '':
        endtime = datetime.datetime.now().strftime('%Y-%m-%d 23:59:00')

    bar = read_day_mysql(starttime, endtime)
    ret_html = render_template('douyin_plugin.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               myurl='/douyin/pluginDay',
                               script_list=bar.get_js_dependencies())
    return ret_html


def read_day_mysql(starttime, endtime):
    stats = mysql_client3.find_plugin_day(starttime, endtime)
    installDay = stats['plugin_install']
    pluginUv = stats['plugin_uv']
    user_action = stats['user_action']
    to_web = stats['to_web']
    intention_user = stats['intention_user']
    click_rate = stats['click_rate']
    pluginPv = stats['plugin_pv']
    rdates = stats['ctime']

    bar = pyecharts.Line("日趋势图", "数量", width=1000, height=600)
    bar.add("插件安装数", rdates, installDay, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True, is_label_show=True)
    bar.add("插件UV", rdates, pluginUv, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True, is_label_show=True)
    bar.add("插件用户行为", rdates, user_action, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True, is_label_show=True)
    bar.add("意向点击次数", rdates, to_web, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True, is_label_show=True)
    bar.add("意向点击人数", rdates, intention_user, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True, is_label_show=True)
    bar.add("意向转化率", rdates, click_rate, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True, is_label_show=True)
    bar.add("插件pv", rdates, pluginPv, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True, is_label_show=True)
    return bar


@app.route('/douyin/allData', methods=['get'])
def allData():
    ret_html = render_template('douyin_data.html',
                               mytitle=u"数据演示",
                               host='/static',
                               plugin=pluginData(),
                               web=webData())
    return ret_html

def webData():
    weekTime1 = (datetime.datetime.now() - datetime.timedelta(days=8)).strftime('%Y-%m-%d 00:00:00')
    weekTime2 = (datetime.datetime.now() - datetime.timedelta(days=8)).strftime('%Y-%m-%d 23:00:00')
    weekData = mysql_client3.find_web_report(weekTime1, weekTime2)

    starttime = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y-%m-%d 00:00:00')
    endTime = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d 23:00:00')
    webData = mysql_client3.find_web_report(starttime, endTime)
    webBody = []

    weekDatas1 = weekData['brower_count'].tolist()[0]
    brower_count1 = webData['brower_count'].tolist()[0]
    brower_count2 = webData['brower_count'].tolist()[1]
    upbrower_count = int(brower_count2) - int(brower_count1)
    if brower_count1 == 0:
        ratebrower_count = 0
    else:
        ratebrower_count = round(100 * upbrower_count / brower_count1, 2)
    if weekDatas1 == 0:
        rateWeek1 = 0
    else:
        rateWeek1 = round(100 *(brower_count2 - weekDatas1)/weekDatas1, 2)
    res1 = {'title': "浏览数", 'newCount': brower_count2, 'beforeCount': brower_count1, 'upCount': upbrower_count,'weekData':weekDatas1,
            'rate': ratebrower_count,'rateWeek':rateWeek1}
    webBody.append(res1)

    weekDatas2 = weekData['visitors_count'].tolist()[0]
    visitors_count1 = webData['visitors_count'].tolist()[0]
    visitors_count2 = webData['visitors_count'].tolist()[1]
    upvisitors_count = int(visitors_count2) - int(visitors_count1)
    if visitors_count1 == 0:
        ratevisitors_count = 0
    else:
        ratevisitors_count =round(100 * upvisitors_count / visitors_count1, 2)

    if weekDatas2 == 0:
        rateWeek2 = 0
    else:
        rateWeek2 = round(100 *(visitors_count2 - weekDatas2)/weekDatas2, 2)

    res2 = {'title': "访客数", 'newCount': visitors_count2, 'beforeCount': visitors_count1, 'upCount': upvisitors_count,'weekData':weekDatas2,
            'rate': ratevisitors_count,'rateWeek':rateWeek2}
    webBody.append(res2)


    weekDatas3 = weekData['registe_user_count'].tolist()[0]
    bRe = webData['registe_user_count'].tolist()[0]
    nRe = webData['registe_user_count'].tolist()[1]
    upRe = int(nRe) - int(bRe)
    if bRe == 0:
        rateupRe = 0
    else:
        rateupRe = round(100 * upRe / bRe, 2)

    if weekDatas3 == 0:
        rateWeek3 = 0
    else:
        rateWeek3 = round(100 *(nRe - weekDatas3)/weekDatas3, 2)
    res3 = {'title': "新增注册用户", 'newCount': nRe, 'beforeCount': bRe, 'upCount': upRe,'weekData':weekDatas3,
            'rate': rateupRe, 'rateWeek':rateWeek3}
    webBody.append(res3)

    weekDatas4 = weekData['login_user_count'].tolist()[0]
    blogin = webData['login_user_count'].tolist()[0]
    nlogin = webData['login_user_count'].tolist()[1]
    uplogin = int(nlogin) - int(blogin)
    if blogin == 0:
        ratelogin = 0
    else:
        ratelogin = round(100 * uplogin / blogin, 2)

    if weekDatas4 == 0:
        rateWeek4 = 0
    else:
        rateWeek4 = round(100 *(nlogin - weekDatas4)/weekDatas4, 2)
    res4 = {'title': "日登录用户", 'newCount': nlogin, 'beforeCount': blogin, 'upCount': uplogin,'weekData':weekDatas4,
            'rate': ratelogin,'rateWeek':rateWeek4}
    webBody.append(res4)

    weekDatas5 = weekData['net_login_user_count'].tolist()[0]
    bnet = webData['net_login_user_count'].tolist()[0]
    nnet = webData['net_login_user_count'].tolist()[1]
    upnet = int(nnet) - int(bnet)
    if bnet == 0:
        ratenet = 0
    else:
        ratenet = round(100 * upnet / bnet, 2)
    if weekDatas5 == 0:
        rateWeek5 = 0
    else:
        rateWeek5 = round(100 *(nnet - weekDatas5)/weekDatas5, 2)
    res5 = {'title': "净登陆用户", 'newCount': nnet, 'beforeCount': bnet, 'upCount': upnet,'weekData':weekDatas5,
            'rate': ratenet,'rateWeek':rateWeek5}
    webBody.append(res5)


    weekDatas6 = weekData['active_user_count'].tolist()[0]
    bactive = webData['active_user_count'].tolist()[0]
    nactive = webData['active_user_count'].tolist()[1]
    upactive = int(nactive) - int(bactive)
    if bactive == 0:
        rateactive = 0
    else:
        rateactive = round(100 * upactive / bactive, 2)

    if weekDatas6 == 0:
        rateWeek6 = 0
    else:
        rateWeek6 = round(100 *(nactive - weekDatas6)/weekDatas6, 2)
    res6 = {'title': "日活跃用户", 'newCount': nactive, 'beforeCount': bactive, 'upCount': upactive,'weekData':weekDatas6,
            'rate': rateactive,'rateWeek':rateWeek6}
    webBody.append(res6)

    weekDatas7 = weekData['goto_buypage_count'].tolist()[0]
    bgoto = webData['goto_buypage_count'].tolist()[0]
    ngoto = webData['goto_buypage_count'].tolist()[1]
    upgoto = int(ngoto) - int(bgoto)
    if bgoto == 0:
        rategoto = 0
    else:
        rategoto = round(100 * upgoto / bgoto, 2)
    if weekDatas7 == 0:
        rateWeek7 = 0
    else:
        rateWeek7 = round(100 *(ngoto - weekDatas7)/weekDatas7, 2)
    res7 = {'title': "去购买页人数", 'newCount': ngoto, 'beforeCount': bgoto, 'upCount': upgoto,'weekData':weekDatas7,
            'rate': rategoto,'rateWeek':rateWeek7}
    webBody.append(res7)

    weekDatas8 = weekData['want_buy_count'].tolist()[0]
    bwant = webData['want_buy_count'].tolist()[0]
    nwant = webData['want_buy_count'].tolist()[1]
    upwant = int(nwant) - int(bwant)
    if bwant == 0:
        ratewant = 0
    else:
        ratewant = round(100 * upwant / bwant, 2)
    if weekDatas8 == 0:
        rateWeek8 = 0
    else:
        rateWeek8 = round(100 *(nwant - weekDatas8)/weekDatas8, 2)
    res8 = {'title': "意向购买人数", 'newCount': nwant, 'beforeCount': bwant, 'upCount': upwant,'weekData':weekDatas8,
            'rate': ratewant,'rateWeek':rateWeek8}
    webBody.append(res8)


    weekDatas9 = weekData['want_true_buy_count'].tolist()[0]
    btrue = webData['want_true_buy_count'].tolist()[0]
    ntrue = webData['want_true_buy_count'].tolist()[1]
    uptrue = int(ntrue) - int(btrue)
    if btrue == 0:
        ratetrue = 0
    else:
        ratetrue = round(100 * uptrue / btrue, 2)
    if weekDatas9 == 0:
        rateWeek9 = 0
    else:
        rateWeek9 = round(100 *(ntrue - weekDatas9)/weekDatas9, 2)
    res9 = {'title': "购买次数", 'newCount': ntrue, 'beforeCount': btrue, 'upCount': uptrue,'weekData':weekDatas9,
            'rate': ratetrue,'rateWeek':rateWeek9}
    webBody.append(res9)

    weekDatas10 = weekData['renewal_fee_count'].tolist()[0]
    bfree = webData['renewal_fee_count'].tolist()[0]
    nfree = webData['renewal_fee_count'].tolist()[1]
    upfree = int(nfree) - int(bfree)
    if bfree == 0:
        ratefree = 0
    else:
        ratefree = round(100 * upfree / bfree, 2)
    if weekDatas10 == 0:
        rateWeek10 = 0
    else:
        rateWeek10 = round(100 *(nfree - weekDatas10)/weekDatas10, 2)
    res10 = {'title': "续费次数", 'newCount': ntrue, 'beforeCount': btrue, 'upCount': uptrue,'weekData':weekDatas10,
             'rate': ratefree,'rateWeek':rateWeek10}
    webBody.append(res10)

    weekDatas11 = weekData['registe_retain_rate'].tolist()[0]
    brate = webData['registe_retain_rate'].tolist()[0]
    nrate = webData['registe_retain_rate'].tolist()[1]
    uprate = int(nrate) - int(brate)
    if brate == 0:
        raterate = 0
    else:
        raterate = round(100 * uprate / brate, 2)
    if weekDatas11 == 0:
        rateWeek11 = 0
    else:
        rateWeek11 = round(100 *(nrate - weekDatas11)/weekDatas11, 2)
    res11 = {'title': "新增注册用户留存率", 'newCount': nrate, 'beforeCount': brate, 'upCount': uprate,'weekData':weekDatas11,
             'rate': raterate,'rateWeek':rateWeek11}
    webBody.append(res11)


    weekDatas12 = weekData['order_count'].tolist()[0]
    borderC = webData['order_count'].tolist()[0]
    norderC = webData['order_count'].tolist()[1]
    upOrderC = int(norderC) - int(borderC)
    if borderC == 0:
        rateOrderC = 0
    else:
        rateOrderC = round(100 * upOrderC / borderC, 2)
    if weekDatas12 == 0:
        rateWeek12 = 0
    else:
        rateWeek12 = round(100 *(norderC - weekDatas12)/weekDatas12, 2)
    res12 = {'title': "订单金额数", 'newCount': norderC, 'beforeCount': borderC, 'upCount': upOrderC,'weekData':weekDatas12,
             'rate': rateOrderC,'rateWeek':rateWeek12}
    webBody.append(res12)
    return webBody


def pluginData():

    weekTime1 = (datetime.datetime.now() - datetime.timedelta(days=8)).strftime('%Y-%m-%d 00:00:00')
    weekTime2 = (datetime.datetime.now() - datetime.timedelta(days=8)).strftime('%Y-%m-%d 23:00:00')
    weekData = mysql_client3.find_plugin_day(weekTime1, weekTime2)
    print(weekData)

    starttime = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y-%m-%d 00:00:00')
    endTime = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d 23:00:00')

    pluginData = mysql_client3.find_plugin_day(starttime, endTime)

    pluginBody = []

    weekDatas1 = weekData['plugin_install'].tolist()[0]
    bInstall = pluginData['plugin_install'].tolist()[0]
    nInstall = pluginData['plugin_install'].tolist()[1]
    upInstall = int(nInstall) - int(bInstall)
    if bInstall == 0:
        rateInstall = 0
    else:
        rateInstall = round(100 * upInstall / bInstall, 2)
    if weekDatas1 == 0:
        rateWeek1 = 0
    else:
        rateWeek1 = round(100 *(nInstall - weekDatas1)/weekDatas1, 2)
    result1 = {'title':"下载人数", 'newCount': nInstall, 'beforeCount': bInstall, 'upCount':upInstall, 'weekData':weekDatas1,
               'rate':rateInstall, 'rateWeek':rateWeek1}
    pluginBody.append(result1)

    weekDatas2 = weekData['plugin_pv'].tolist()[0]
    bPPv = pluginData['plugin_pv'].tolist()[0]
    nPPv = pluginData['plugin_pv'].tolist()[1]
    upPPv = int(nPPv) - int(bPPv)
    if bPPv == 0:
        ratePPv = 0
    else:
        ratePPv = round(100 * upPPv / bPPv, 2)
    if weekDatas2 == 0:
        rateWeek2 = 0
    else:
        rateWeek2 = round(100 *(nPPv - weekDatas2)/weekDatas2, 2)
    result2 = {'title':"浏览数", 'newCount': nPPv, 'beforeCount': bPPv, 'upCount':upPPv,'weekData':weekDatas2,
               'rate':ratePPv,'rateWeek':rateWeek2}
    pluginBody.append(result2)

    weekDatas3 = weekData['plugin_uv'].tolist()[0]
    bPluginUv = pluginData['plugin_uv'].tolist()[0]
    nPluginUv = pluginData['plugin_uv'].tolist()[1]
    upPluginPv = int(nPluginUv) - int(bPluginUv)
    if bPluginUv == 0:
        ratePluginUv = 0
    else:
        ratePluginUv = round(100 * upPluginPv / bPluginUv, 2)
    if weekDatas3 == 0:
        rateWeek3 = 0
    else:
        rateWeek3 = round(100 * (nPluginUv - weekDatas3) / weekDatas3, 2)
    result3 = {'title':"访客数", 'newCount': nPluginUv, 'beforeCount': bPluginUv, 'upCount':upPluginPv, 'weekData':weekDatas3,
               'rate':ratePluginUv,'rateWeek':rateWeek3}
    pluginBody.append(result3)

    weekDatas4 = weekData['user_action'].tolist()[0]
    bUaction = pluginData['user_action'].tolist()[0]
    nUaction = pluginData['user_action'].tolist()[1]
    upUaction = int(nUaction) - int(bUaction)
    if bUaction == 0:
        rateUaction = 0
    else:
        rateUaction = round(100 * upUaction / bUaction, 2)
    if weekDatas4 == 0:
        rateWeek4 = 0
    else:
        rateWeek4 = round(100 * (nUaction - weekDatas4) / weekDatas4, 2)
    result4 = {'title':"使用行为发生人数", 'newCount': nUaction, 'beforeCount': bUaction, 'upCount':upUaction, 'weekData':weekDatas4,
               'rate':rateUaction,'rateWeek':rateWeek4}
    pluginBody.append(result4)

    weekDatas5 = weekData['to_web'].tolist()[0]
    bToweb = pluginData['to_web'].tolist()[0]
    nToweb = pluginData['to_web'].tolist()[1]
    upToweb = int(nToweb) - int(bToweb)
    if bToweb == 0:
        rateToweb = 0
    else:
        rateToweb = round(100 * upToweb / bToweb, 2)
    if weekDatas5 == 0:
        rateWeek5 = 0
    else:
        rateWeek5 = round(100 * (nToweb - weekDatas5) / weekDatas5, 2)
    result5 = {'title':"主站意向点击次数", 'newCount': nToweb, 'beforeCount': bToweb, 'upCount':upToweb, 'weekData':weekDatas5,
               'rate':rateToweb,'rateWeek':rateWeek5}
    pluginBody.append(result5)

    weekDatas6 = weekData['intention_user'].tolist()[0]
    bIntention = pluginData['intention_user'].tolist()[0]
    nIntention = pluginData['intention_user'].tolist()[1]
    upIntention = int(nIntention) - int(bIntention)
    if bIntention == 0:
        rateIntention = 0
    else:
        rateIntention = round(100 * upIntention / bIntention, 2)
    if weekDatas6 == 0:
        rateWeek6 = 0
    else:
        rateWeek6 = round(100 * (nIntention - weekDatas6) / weekDatas6, 2)
    result6 = {'title':"主站意向点击人数", 'newCount': nIntention, 'beforeCount': bIntention, 'upCount':upIntention,'weekData':weekDatas6,
               'rate':rateIntention,'rateWeek':rateWeek6}
    pluginBody.append(result6)

    weekDatas7 = weekData['click_rate'].tolist()[0]
    bClick = pluginData['click_rate'].tolist()[0]
    nClick = pluginData['click_rate'].tolist()[1]
    upClick = int(nClick) - int(bClick)
    if bClick == 0:
        rateClick = 0
    else:
        rateClick = round(100 * upClick / bClick, 2)
    if weekDatas7 == 0:
        rateWeek7 = 0
    else:
        rateWeek7 = round(100 * (nClick - weekDatas7) / weekDatas7, 2)
    result7 = {'title':"主站意向点击转化率", 'newCount': nClick, 'beforeCount': bClick, 'upCount':upClick, 'weekData':weekDatas7,
               'rate':rateClick,'rateWeek':rateWeek7}
    pluginBody.append(result7)

    return pluginBody

    # bNew = pluginData['new_user'].tolist()[0]
    # nNew = pluginData['new_user'].tolist()[1]
    # upnew = int(nNew) - int(bNew)
    # if nNew == 0:
    #     rateNew = 0
    # else:
    #     rateNew = 100 * upnew / nNew




def jsonpToJson(_jsonp):
    if _jsonp.startswith('b'):
        data_len = len(_jsonp)
        # print(data_len)

        # _jsonp = _jsonp[3, data_len-1]
        _jsonp = _jsonp.replace("b' ", "").replace("'","")
    # print(_jsonp)
    try:
        _jsonp = _jsonp.strip()
        return json.loads(re.match(".*?({.*}).*", _jsonp, re.S).group(1))
    except Exception as e:

        logging.exception(e)
        print("原始jsonp:"+_jsonp)
        return ""



@app.route('/douyin_user_search', methods=['POST', 'GET'])
def infos():
    """
     请求的数据源，该函数模拟数据库中存储的数据，返回以下这种数据的列表：
    {'name': '香蕉', 'id': 1, 'price': '10'}
    {'name': '苹果', 'id': 2, 'price': '10'}
    """
    data = []
    names = ['香', '草', '瓜', '果', '桃', '梨', '莓', '橘', '蕉', '苹']
    for i in range(1, 1001):
        d = {}
        d['id'] = i
        d['name'] = "披萨店" # 随机选取汉字并拼接
        d['price'] = '10'
        data.append(d)
    if request.method == 'POST':
        print('post')
    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        print('get', limit)
    print('get  offset', offset)
    return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
    # 注意total与rows是必须的两个参数，名字不能写错，total是数据的总长度，rows是每页要显示的数据,它是一个列表
    # 前端根本不需要指定total和rows这俩参数，他们已经封装在了bootstrap table里了


@app.route('/douyin_user_list')
def hi():
    return render_template('douyin_table.html')




def get_last_aweme(uid, count):
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "uid": uid
                        }
                    }
                ]
                # ,
                # "must_not": [
                #     # {"match": {
                #     #   "douyin_cid": ""
                #     # }}
                #     {
                #         "exists": {
                #             "field": "douyin_cid"
                #         }
                #     }
                # ]
            }
        }
        , "sort":
            [
             {"create_time": {"order": "desc"}}

             ]
    }
    result = es.search(index='douyin_sea_analyze_aweme_5', body=body, size=count, scroll='1m')
    return parse_es_aweme_page(result)


def get_from_es(show_all, author_id, fans_max_count, fans_min_count, from_index, page_size):

    body = {
        "query": {
            "bool": {
                "must": [

                    {
                      "range": {
                        "follower_count": {
                          "gte": fans_min_count,
                          "lte": fans_max_count
                        }
                      }
                    }


                ]

            }
        }
        , "sort":
            [{"_score": {"order": "desc"}},
             {"follower_count": {"order": "desc"}}

             ]
        , "from": from_index
        , "size": page_size
    }
    if author_id:

        match = {}
        match['author_id'] = author_id
        add_match={}
        add_match['match'] = match
        body['query']['bool']['must'].append(add_match)

    must_not_list = []
    if show_all == "false":

        not_match_douyincid = {}
        exists = {}
        exists['field']='douyin_cid'
        not_match_douyincid['exists']=exists

        must_not_list.append(not_match_douyincid)

    not_match_nickname = {}
    nickname = {}
    nickname['nickname'] = '已重置'
    not_match_nickname['match'] = nickname
    must_not_list.append(not_match_nickname)

    body['query']['bool']['must_not'] = must_not_list

    result = es.search(index='douyin_sea_user_4', body=body)
    # sid = result['_scroll_id']
    scroll_size = result['hits']['total']


    return parse_es_page(show_all, result, scroll_size)


def parse_es_aweme_page(result):
    objs = []
    for source in result['hits']['hits']:
        aweme = source['_source']
        if 'top_pic' in aweme and not aweme['top_pic'].startswith('http'):
            aweme['top_pic'] = "https://p3.pstatp.com/obj/"+aweme['top_pic']
        if 'top_pic' not in aweme:
            aweme['top_pic'] = ""
        aweme['link_url'] = "https://www.iesdouyin.com/share/video/"+aweme['aweme_id']+"/?mid="+aweme['mid']
        # uid = user['uid']
        # user['user_info'] = "<pre>"+user['author_id']+"\n"+user['nickname']+"</pre>"
        objs.append(aweme)

    return objs


def parse_es_page(show_all, result, total, need_aweme=True):
    objs = []
    uids = []
    for source in result['hits']['hits']:
        user = source['_source']
        uids.append(user['uid'])
    hascat_list = mongo_client3.find_user_has_douyincid(uids)
    hascat_user_set = set()
    for user in hascat_list:
        hascat_user_set.add(user['uid'])

    for source in result['hits']['hits']:
        user = source['_source']
        # uid = user['uid']
        # user['user_info'] = "<pre>"+user['author_id']+"\n"+user['nickname']+"</pre>"
        if not user['avatar_url'].startswith('http'):
            user['avatar_url'] = "https://p3.pstatp.com/aweme/100x100/" + user['avatar_url']
        comment_word = ""
        if 'comment_word' in user and len(user['comment_word']) > 0:
            for word in user['comment_word']:
                comment_word += word + ","
        if 'signature' in user and len(user['signature']) > 24:
            user['signature'] = user['signature'][0:24]+".."

        user['comment_word'] = comment_word
        verify = ""
        if 'custom_verify' in user and "" != user['custom_verify']:
            verify = user['custom_verify']
        if 'enterprise_verify_reason' in user and "" != user['enterprise_verify_reason']:
            verify = user['enterprise_verify_reason']
        user['verify'] = verify
        user['douyin_catename'] = ''
        if 'douyin_cid' in user and ""!=user['douyin_cid']:
            for cate in douyin_cate_list():
                if str(cate['key']) == user['douyin_cid']:
                    user['douyin_catename'] = cate['value']
        if need_aweme:
            aweme_list = get_last_aweme(user['uid'], 3)
            user['aweme1_pic'] = ""
            user['aweme1_link'] = ""
            user['aweme2_pic'] = ""
            user['aweme2_link'] = ""
            user['aweme3_pic'] = ""
            user['aweme3_link'] = ""

            if len(aweme_list) > 0:
                user['aweme1_pic'] = aweme_list[0]['top_pic']
                user['aweme1_link'] = aweme_list[0]['link_url']
            if len(aweme_list) > 1:
                user['aweme2_pic'] = aweme_list[1]['top_pic']
                user['aweme2_link'] = aweme_list[1]['link_url']
            if len(aweme_list) > 2:
                user['aweme3_pic'] = aweme_list[2]['top_pic']
                user['aweme3_link'] = aweme_list[2]['link_url']
        set_result = r.sismember('douyin:doudada:uid:dis', user['uid'])
        user['update_daily'] = 'NO'
        if set_result == 1:
            user['update_daily'] = '是'
        user['fans_pic'] = "NO"
        if 'age_max' in user:
            user['fans_pic'] = '有'
        if show_all == 'false':
            if user['uid'] not in hascat_user_set:
                objs.append(user)
            elif r2.llen("douyin:uid:search:"+user['uid']) == 0:
                objs.append(user)

        else:
            objs.append(user)

    return objs, total


@app.route('/douyin_data')
def dou_data():
    param_info = request.values.to_dict()
    page = 1
    page_size = 20
    fans_max_count = 9000000000
    fans_min_count = 10000
    author_id = ""
    if 'page' in param_info:
        page = int(param_info['page'])

        page_size = int(param_info['page_size'])
        max_page = 10000/page_size
        if page > max_page:
            page = max_page
    page -= 1
    if 'fans_max' in param_info and "" != param_info['fans_max']:
        fans_max_count = int(param_info['fans_max'])
    if 'fans_min' in param_info and "" != param_info['fans_min']:
        fans_min_count = int(param_info['fans_min'])
    if 'author_id' in param_info and "" != param_info['author_id']:
        author_id = param_info['author_id']
    data={}

    objs=[]
    return_list, total=get_from_es(param_info['show_all'], author_id, fans_max_count, fans_min_count, page_size*page, page_size)
    data['datalist'] = return_list
    data['douyin_cate_list'] = douyin_cate_list()
    data['total'] = total
    return json.dumps(data)


@app.route('/douyin_change_cate')
def dou_chanage():
    param_info = request.values.to_dict()
    author_id=''
    douyin_cid=''
    audit_user = ''
    nickname= ''

    if 'author_id' in param_info:
        author_id = param_info['author_id']
    if 'douyin_cid' in param_info:
        douyin_cid = param_info['douyin_cid']
    if 'audit_user' in param_info:
        audit_user = param_info['audit_user']
    if 'nickname' in param_info:
        nickname = param_info['nickname']


    param_info = {}
    param_info['douyin_cid'] = douyin_cid
    param_info['author_id'] = author_id
    return_msg = push_user_fans(param_info)

    json_data = json.loads(return_msg)
    if json_data['msg'] == 'Success':
        today = time.strftime("%Y-%m-%d", time.localtime())
        f = codecs.open('audit_douyin/audit_douyin_cid.txt.' + today, 'a+', 'utf-8')
        f.write(time.strftime("%Y-%m-%d %H:%M:%S",
                              time.localtime()) + "\t" + "audit_user=" + audit_user + "\tauthor_id=" + author_id + "\tnickname=" + nickname + "\tdouyin_cid=" + douyin_cid + "\n")
        f.close()
    # obj={}
    # obj['message'] = "成功"
    # obj['code'] = "200"
    # print(return_msg)
    # print(return_msg)
    return return_msg


def douyin_cate_list():

    cates = [{"key": 10117, "value": "生活"},
             {"key": 10126, "value": "娱乐"},
             {"key": 10124, "value": "美食"},
             {"key": 10127, "value": "美妆"},
             {"key": 10132, "value": "文化"},
             {"key": 10125, "value": "政务"},
             {"key": 10130, "value": "音乐"},
             {"key": 10137, "value": "美女"},
             {"key": 10135, "value": "帅哥"},
             {"key": 10129, "value": "游戏"},
             {"key": 10131, "value": "舞蹈"},
             {"key": 10139, "value": "剧情"},
             {"key": 10136, "value": "穿搭"},
             {"key": 10144, "value": "宠物"},
             {"key": 10154, "value": "汽车"},
             {"key": 10138, "value": "旅行"},
             {"key": 10142, "value": "动漫"},
             {"key": 10151, "value": "科技"},
             {"key": 10157, "value": "种草"},
             {"key": 10118, "value": "才艺"},
             {"key": 10119, "value": "搞笑"},
             {"key": 10120, "value": "情感"},
             {"key": 10121, "value": "明星"},
             {"key": 10122, "value": "萌娃"},
             {"key": 10123, "value": "健康"},
             {"key": 10133, "value": "体育"},
             {"key": 10134, "value": "创意"},
             {"key": 10140, "value": "时尚"},
             {"key": 10141, "value": "母婴育儿"},
             {"key": 10143, "value": "教育"},
             {"key": 10145, "value": "职场"},
             {"key": 10146, "value": "家居"},
             {"key": 10147, "value": "摄影教学"},
             {"key": 10148, "value": "资讯"},
             {"key": 10149, "value": "科普"},
             {"key": 10150, "value": "文学"},
             {"key": 10152, "value": "艺术"},
             {"key": 10155, "value": "农产品"}]
    return cates



@app.route('/douyin_stat_email')
def douyin_stat_email():
    param_info = request.values.to_dict()
    toUser = "danqing@taotaosou.com"
    if 'toUser' in param_info:
        toUser = param_info['toUser']

    email_content = douyin_stat.get_stat_content()
    textmod = {"address": toUser.split(","), "datas": email_content, "title": '抖音达人每日打标汇总'}
    r = requests.post("http://192.168.3.140:5002/api/v1/send_email", data=textmod)

    result = r.text

    return result


@app.route('/douyin_test')
def douyin_test():
    body = {
        "query": {
            "bool": {
                "must": [

                    {
                        "range": {
                            "follower_count": {
                                "gte": 10000,
                                "lte": 100000000000000
                            }
                        }
                    }

                ]

            }
        }
        , "sort":
            [{"_score": {"order": "desc"}},
             {"follower_count": {"order": "desc"}}

             ]

    }

    show_all="false"
    author_id="111"
    if author_id:
        match = {}
        match['comment_word'] = "牛仔裤"
        add_match = {}
        add_match['match'] = match
        body['query']['bool']['must'].append(add_match)

        match2 = {}
        match2['comment_word'] = "裙子"
        add_match2 = {}
        add_match2['match'] = match2
        body['query']['bool']['must'].append(add_match2)

    must_not_list = []

    if show_all == "false":
        not_match_douyincid = {}
        exists = {}
        exists['field'] = 'douyin_cid'
        not_match_douyincid['exists'] = exists

        must_not_list.append(not_match_douyincid)

    not_match_nickname = {}
    nickname = {}
    nickname['nickname'] = '已重置'
    not_match_nickname['match'] = nickname
    must_not_list.append(not_match_nickname)

    body['query']['bool']['must_not'] = must_not_list

    result = es.search(index='douyin_sea_user_4', body=body, size=100)
    # sid = result['_scroll_id']
    scroll_size = result['hits']['total']

    list,total = parse_es_page(show_all, result, scroll_size, False)
    print(total)
    for k in list:
        sig = ''
        if 'signature' in k:
            sig = k['signature']
        print(k['uid']+"\t"+k['nickname']+"\t"+sig+"\t"+k['comment_word'])
    return str(total)



