from gevent import monkey
# 把当前的IO操作，打上标记，以便于gevent能检测出来实现异步(否则还是串行）
monkey.patch_all()
from gevent.pool import Pool
import gevent



import json
import codecs
import csv
from elasticsearch import Elasticsearch
import redis
import logging as log
import os
import sys
sys.path.append('../')
import ip_proxy
sys.path.append('../')
import douyin_aweme_list
REDIS_DOUYIN_TEMP = 'douyin:temp:uid'
REDIS_DOUYIN_TEMP_aweme = 'douyin:temp:awemeid'

log.basicConfig(level=log.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                handlers={log.FileHandler(filename='test.log', mode='a', encoding='utf-8')})

pool = redis.ConnectionPool(host='192.168.3.194', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)

es = Elasticsearch([{'host':'es-cn-v6418omlz000m5fr4.elasticsearch.aliyuncs.com', 'port': 9200}], http_auth=('elastic', 'PlRJ2Coek4Y6'))

import requests



def task(url):
    '''
    1、request发起请求
    :param url:
    :return:
    '''
    # response = requests.get(url)
    # print(response.status_code)
    print()






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
        # if index_num<3:
        #     continue
        # if index_num > 3:
        #     break
        # if index_num==3:
        #     print("uid=%s, num=%s" %(uid,num))
        # uid, between_1_5, between_5_10, over_10 = line.strip().split(' ')
        # user_info = r.hget(REDIS_DOUYIN_TEMP, uid)
        # if not user_info:
        #     print(uid)
        #     continue
        # print(uid)
        over_10 = 0
        between_5_10 = 0
        between_1_5 = 0
        for line in f_10_array:
            num, uid_file = line.strip().split(' ')
            # print(num + "+++" + uid_file + "+++")
            if uid_file == '108320481757':
                print('ok')
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

        # print("%s %s %s" %(over_10, between_5_10, between_1_5))
        # break
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
        print(result)
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


import time
def test_t(uid):
    # for i in range(2):
    time.sleep(3)
    print("%s hello %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), uid))


def aweme_play():
    file = codecs.open("douyin_aweme_stat_20191107.txt", 'r', 'utf-8', buffering=True)
    f = codecs.open('aweme_play.txt', 'a+', 'utf-8')
    index_num = 1
    for info in file:
        index_num += 1
        # if index_num>1000:
        #     break
        uid, digg_count, aweme_id = info.strip().split('\t')
        # print(aweme_id)
        aweme_info_str = r.hget(REDIS_DOUYIN_TEMP_aweme, aweme_id)
        if aweme_info_str:
            aweme_info = json.loads(aweme_info_str)

            c = 'uid=%s,aweme_id=%s,digg_count_file=%s,digg_count=%s,play=%s' % (uid, aweme_id, digg_count, aweme_info['digg_count'], aweme_info['play_count'])
            f.write(c+"\n")
            print(c)
    f.close()
    file.close()

def aweme_play_all():
    f = codecs.open('aweme_play_all.txt', 'a+', 'utf-8')
    index_num = 1
    list_all = r.hgetall(REDIS_DOUYIN_TEMP_aweme)
    for aweme_id, aweme_info_str in list_all.items():
        aweme_info = json.loads(aweme_info_str)

        c = 'aweme_id=%s,digg_count=%s,play=%s' % (aweme_id, aweme_info['digg_count'], aweme_info['play_count'])
        f.write(c + "\n")
        print(c)



    f.close()


if __name__ == '__main__':
    print(1)
    # set_aweme_to_redis('80190274850')
    # aweme_play()
    aweme_play_all()
    # read_result('over_10w')
    # print(r.hlen(REDIS_DOUYIN_TEMP_aweme))
    # 控制最多一次向远程提交多少个请求，None代表不限制

    # pool = Pool(5)
    # goup = []
    #
    # goup.append(pool.spawn(set_aweme_to_redis, uid='7351209324'))
    # gevent.joinall(goup)
    #
    # sys.exit()



    # for k in range(10):
    #     goup.append(pool.spawn(set_aweme_to_redis, uid=k))
    #     if k % 3 == 0:
    #         gevent.joinall(goup)
    #         goup = []