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


@app.route('/douyin/pluginHour', methods=['get'])
def push_plugin():
    bar = read_hour_mysql()
    ret_html = render_template('pycharts.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               script_list=bar.get_js_dependencies())
    return ret_html


@app.route('/douyin/pluginDay', methods=['get'])
def push_pluginday():
    bar = read_day_mysql()
    ret_html = render_template('pycharts.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               script_list=bar.get_js_dependencies())
    return ret_html

def read_hour_mysql():
    stats = mysql_client3.find_plugin_hour()
    installHour = stats['plugin_install']
    pluginPv = stats['plugin_pv']
    webPv = stats['web_pv']
    newUser = stats['new_user']
    rdates = stats['ctime']

    bar = pyecharts.Line("小时趋势图", "数量", width=1000, height=600)
    bar.add("插件安装数", rdates, installHour, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True, is_label_show=True)
    bar.add("插件pv", rdates, pluginPv, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True, is_label_show=True)
    bar.add("主站pv", rdates, webPv, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True, is_label_show=True)
    bar.add("新用户", rdates, newUser, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True, is_label_show=True)
    return bar

def read_day_mysql():
    stats = mysql_client3.find_plugin_day()
    installDay = stats['plugin_install']
    pluginUv = stats['plugin_uv']
    user_action = stats['user_action']
    to_web = stats['to_web']
    intention_user = stats['intention_user']
    click_rate = stats['click_rate']
    webPv = stats['web_pv']
    pluginPv = stats['plugin_pv']
    newUser = stats['new_user']
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



