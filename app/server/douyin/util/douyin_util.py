import re
import requests
import redis
from io import StringIO
from urllib import request
import execjs

pool = redis.ConnectionPool(host='192.168.3.194', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
USER_DYTK = 'douyin:dytk:user'
AWEME_DYTK = 'douyin:dytk:aweme'


def get_dytk(aweme_id, mid, uid, proxies):
    if aweme_id:
        dytk = r.hget(AWEME_DYTK, aweme_id)
        if not dytk:
            dytk, uid, author_name = get_aweme_dytk(aweme_id, mid, proxies)
            r.hset(AWEME_DYTK, aweme_id, dytk)
        return dytk
    elif uid:
        dytk = r.hget(USER_DYTK, aweme_id)
        if not dytk:
            dytk = get_user_dytk(uid, proxies)
            r.hset(USER_DYTK, aweme_id, dytk)
        return dytk


def get_user_dytk(uid, proxies):
    url = 'https://www.douyin.com/share/user/%s' % uid
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
    }
    if proxies:
        res = requests.get(url=url, headers=header, proxies=proxies, verify=False)
    else:
        res = requests.get(url=url, headers=header, verify=False)

    dytk = re.findall(".*dytk: \'(.*)\'.*", res.text)
    return dytk[0]


def get_aweme_dytk(aweme_id, mid, proxies):
    url = 'https://www.douyin.com/share/video/%s/?mid=%s' % (aweme_id, mid)
    header = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',

        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1'
    }
    if proxies:
        res = requests.get(url, headers=header, proxies=proxies, verify=False)
    else:
        res = requests.get(url, headers=header, verify=False)
    # print(res.text)
    dytk = re.findall(".*dytk: \"(.*)\".*", res.text)
    uid = re.findall(".*uid: \"(.*)\".*", res.text)
    author_name = re.findall(".*authorName: \"(.*)\".*", res.text)
    return dytk[0], uid[0], author_name[0]


def get_js():
    # f = open("D:/WorkSpace/MyWorkSpace/jsdemo/js/des_rsa.js",'r',encoding='UTF-8')
    #f = open("/Users/ludanqing/Downloads/douyin_2.js", 'r', encoding='UTF-8')

    s = request.urlopen("http://data.qianliyann.com/download/spider/douyin/douyin_sign.js").read().decode('utf8')  # 1 读取数据串
    f = StringIO(s)  # 2 将字符串转换为 StringIO对象，使其具有文件属性
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    return htmlstr


def get_sign(uid):
    jsstr = get_js()

    ctx = execjs.compile(jsstr)
    enSign = ctx.call('__M.require("douyin_falcon:node_modules/byted-acrawler/dist/runtime").sign', uid)
    return enSign