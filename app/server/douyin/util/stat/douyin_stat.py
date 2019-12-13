from gevent import monkey
# 把当前的IO操作，打上标记，以便于gevent能检测出来实现异步(否则还是串行）
monkey.patch_all()
from gevent.pool import Pool
import gevent
from elasticsearch import Elasticsearch
import codecs
import redis
import json
import csv
import requests
import time
from threading import Thread
import threadpool
import os
import gevent
from gevent import monkey
from gevent.pool import Pool
import logging as log

import sys
sys.path.append('../')
from util import ip_proxy
sys.path.append('../')
from util import douyin_aweme_list




log.basicConfig(level=log.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                handlers={log.FileHandler(filename='test.log', mode='a', encoding='utf-8')})

pool = redis.ConnectionPool(host='192.168.3.194', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)

es = Elasticsearch([{'host':'es-cn-v6418omlz000m5fr4.elasticsearch.aliyuncs.com', 'port': 9200}], http_auth=('elastic', 'PlRJ2Coek4Y6'))
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

              {
                "match": {
                  "have_item": True
                }
              }
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


            ,{
              "range": {
                "digg_count": {
                  "gte": 10000
                }
              }
            }
              , {
                  "range": {
                      "create_time": {
                          "gte": 1570377630
                      }
                  }
              }
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
    # csv_file = codecs.open('3000.csv', 'w', 'utf_8_sig')  # 解决写入csv时中文乱码
    # writer = csv.writer(csv_file)
    # writer.writerow(['昵称', '性别', '省份', '抖音id', '签名', '点赞数',
    #                  '关注人数', '粉丝数', '作品数', '类目'])



    result = es.search(index='douyin_sea_analyze_aweme_5', body=body,size=10000, scroll='1m')


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
    # csv_file.close()
    return "push:"+str(push_total)+"/"+str(total)

def deal_s(result,push_total):

    f = codecs.open('douyin_aweme_stat_20191107.txt', 'a+', 'utf-8')


    for source in result['hits']['hits']:
        my_source = source['_source']
        # if 'signature' in my_source:
        #     continue

        # f.write("uid=" + str(my_source['uid']) + "\tauthor_id=" + my_source['author_id'] + "\tnickname=" + my_source['nickname'] + "\tdouyin_cid=" + str(my_source['douyin_cid']) + "\tdigg_count=" + str(my_source['digg_count']) + "\n")

        f.write(str(my_source['uid']) + "\t" + str(
            my_source['digg_count']) + "\t" + str(my_source['aweme_id']) + "\n")

        push_total+=1
    f.close()
    return push_total



REDIS_DOUYIN_TEMP = 'douyin:temp:uid'
REDIS_DOUYIN_TEMP_aweme = 'douyin:temp:awemeid'
def get_user(uid):
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
            }
        }
    }


    result = es.search(index='douyin_sea_user_4', body=body, size=10000, scroll='1m')

    sid = result['_scroll_id']
    scroll_size = result['hits']['total']
    total = len(result['hits']['hits'])
    push_total = 0
    for source in result['hits']['hits']:
        my_source = source['_source']
        print(my_source['uid'])
        r.hset(REDIS_DOUYIN_TEMP, my_source['uid'], json.dumps(my_source))

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


def to_array(file_pre):
    module_path = os.path.dirname(__file__)
    f_10 = codecs.open("%s/%s/over_10w.txt" % (module_path, file_pre), 'r', 'utf-8', buffering=True)
    f_5_10 = codecs.open("%s/%s/between_5_10.txt" % (module_path, file_pre), 'r', 'utf-8', buffering=True)
    f_1_5 = codecs.open("%s/%s/between_1_5.txt" % (module_path, file_pre), 'r', 'utf-8', buffering=True)
    f_10_array = []
    f_5_10_array = []
    f_1_5_array = []

    for line in f_10:
        f_10_array.append(line)
    for line in f_5_10:
        f_5_10_array.append(line)
    for line in f_1_5:
        f_1_5_array.append(line)
    f_10.close()
    f_5_10.close()
    f_1_5.close()
    return f_10_array, f_5_10_array, f_1_5_array

def read_result(file_pre):
    module_path = os.path.dirname(__file__)
    f_10_array, f_5_10_array, f_1_5_array = to_array(file_pre)

    cats = douyin_cate_list()
    csv_file = codecs.open('%s/%s.csv' % (module_path, file_pre), 'w', 'utf_8_sig')  # 解决写入csv时中文乱码
    writer = csv.writer(csv_file)
    writer.writerow(['达人昵称', '链接', '达人认证', '达人类目', '达人粉丝数', '10万以上点赞带货视频个数', '5-10万点赞带货视频个数',
                     '1-5万点赞带货视频个数'])

    # # 使用for循环遍历文件对象
    # for line in f:
    list = r.hgetall(REDIS_DOUYIN_TEMP)
    index_num = 0
    for uid, user_info in list.items():
        index_num += 1

        over_10 = 0
        between_5_10 = 0
        between_1_5 = 0
        for line in f_10_array:
            num, uid_file = line.strip().split(' ')
            # print(num + "+++" + uid_file + "+++")

            if uid_file == uid:
                over_10 = int(num)
                break
        for line in f_5_10_array:
            num, uid_file = line.strip().split(' ')
            if uid_file == uid:
                between_5_10 = int(num)
                break
        for line in f_1_5_array:
            num, uid_file = line.strip().split(' ')
            if uid_file == uid:
                between_1_5 = int(num)
                break

        if over_10 == 0 and between_5_10 == 0 and between_1_5 == 0:
            continue
        json_data = json.loads(user_info)
        cat_name = ''
        custom_verify = ''
        if 'custom_verify' in json_data:
            custom_verify = json_data['custom_verify']
        if 'douyin_cid' in json_data and json_data['douyin_cid']:
            for cat in cats:
                if cat['key'] == int(json_data['douyin_cid']):
                    cat_name = cat['value']
        writer.writerow(
                    [json_data['nickname'], 'http://www.99doushang.com/v/rank/star/detail?uid=%s&starName=' % uid, custom_verify, cat_name, json_data['follower_count'], over_10, between_5_10, between_1_5])


    csv_file.close()


def list_set():
    list = r.hgetall(REDIS_DOUYIN_TEMP)
    for k, v in list.items():
        # print(k.key())
        print(k)



proxy_ip = ip_proxy.get_proxy()


def get_aweme_list_proxy(uid, proxy_ip):
    try:
        result = douyin_aweme_list.spider_aweme_list(uid, '', proxy_ip, 2)
    except requests.exceptions.ProxyError:
        print('代理ip失效, 无法进行吗 访问，重新获取')
        proxy_ip = ip_proxy.get_proxy()
        result = douyin_aweme_list.spider_aweme_list(uid, '', proxy_ip, 2)
    except requests.exceptions.ConnectTimeout:
        print('代理ip失效，无法进行页面访问，重新获取')
        proxy_ip = ip_proxy.get_proxy()
        result = douyin_aweme_list.spider_aweme_list(uid, '', proxy_ip, 2)
    return result



def set_aweme_to_redis(uid):
    start_time = time.time()
    # urls = 'http://192.168.3.140:9911/douyin_awemelist?uid=%s&max_page=2' % uid
    # try:
    #     res = requests.get(url=urls)
    # except Exception as e:
    #     print(e)
    #     print('%s报错了，终止' % uid)
    #     return
    try:
        result = get_aweme_list_proxy(uid, proxy_ip)
    except Exception as e:
        print(e)
        message = '%s报错了，终止' % uid
        print(message)
        log.info(message)
        return
    json_data = json.loads(result)
    aweme_list = json_data['aweme_list']
    for aweme in aweme_list:
        aweme_info = {}
        aweme_info['aweme_type'] = aweme['aweme_type']
        statistics = aweme['statistics']
        aweme_info['comment_count'] = statistics['comment_count']
        aweme_info['digg_count'] = statistics['digg_count']
        aweme_info['play_count'] = statistics['play_count']
        aweme_info['share_count'] = statistics['share_count']
        aweme_info['forward_count'] = statistics['forward_count']
        r.hset(REDIS_DOUYIN_TEMP_aweme, aweme['aweme_id'], json.dumps(aweme_info))
        r.expire(REDIS_DOUYIN_TEMP_aweme, 3600 * 24 * 7)

    # f = codecs.open('aweme_play.txt', 'a+', 'utf-8')
    p_content = 'uid=%s total_num=%s page=%s sp_times=%s %d second' % (uid, json_data['total'], json_data['sp_info']['page'], json_data['sp_info']['total_sp_times'], (time.time() - start_time))
    # f.write(p_content+"\n")
    print(p_content)
    log.info(p_content)
    # f.close()

def test_t(uid):
    # for i in range(2):
    time.sleep(3)
    print("%s hello %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), uid))




if __name__ == '__main__':

    set_aweme_to_redis('80190274850')
    sys.exit()
    # read_result('between_5_10')
    # read_result('between_1_5')
    # read_result('over_10w')


    # find_es()



    # f = codecs.open("douyin_uid_stat.txt", 'r', 'utf-8', buffering=True)
    # # 使用for循环遍历文件对象
    # for line in f:
    #     get_user(line.strip())
    #     # user = r.hget(REDIS_DOUYIN_TEMP, line)
    # f.close()
    # uid = '59522654679'
    # set_aweme_to_redis(uid)
    # list = r.hgetall(REDIS_DOUYIN_TEMP_aweme)
    # for k, v in list.items():
    #     print(v)

    # 创建线程01，不指定参数
    # for k in range(3):
    #     thread_01 = Thread(target=test_t, args=(k,))
    #       # 启动线程01
    #
    #     thread_01.start()

    exit_uid_set = set(())
    module_path = os.path.dirname(__file__)
    exist_uid_log = "%s/test.log" % module_path
    f = codecs.open(exist_uid_log, 'r', 'utf-8', buffering=True)
    for line in f:
        if line.find('uid') > -1:
            uids = line.split(' ')
            uid = uids[10].split('=')[1]
            exit_uid_set.add(uid)
    f.close()




    name_list = []
    douyin_uid_stat = "%s/douyin_uid_stat.txt" % module_path
    f = codecs.open(douyin_uid_stat, 'r', 'utf-8', buffering=True)
    # 使用for循环遍历文件对象
    for line in f:
        uid = line.strip()
        if uid in exit_uid_set:
            log.info('%s用户已存在' % uid)
            continue
        name_list.append(line.strip())
    f.close()

    start_time = time.time()


    pool = Pool(20)
    goup = []
    uid_index = 0
    for uid in name_list:
        uid_index += 1
        goup.append(pool.spawn(set_aweme_to_redis, uid=uid))
        if uid_index % 10 == 0:
            gevent.joinall(goup)
            goup = []
    # pool = threadpool.ThreadPool(10)
    # req_threads = threadpool.makeRequests(set_aweme_to_redis, name_list)
    # [pool.putRequest(req) for req in req_threads]
    # pool.wait()
    print('%d second' % ((time.time() - start_time)))





