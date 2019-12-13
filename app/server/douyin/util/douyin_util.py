import re
import requests
import redis
from io import StringIO
from urllib import request
import execjs
import json
import sys
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
# print(parentUrl)
sys.path.append(parentUrl)


pool = redis.ConnectionPool(host='192.168.3.194', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
USER_DYTK = 'douyin:dytk:user:'
AWEME_DYTK = 'douyin:dytk:aweme:'


def get_dytk(aweme_id, mid, uid, proxies):
    if aweme_id:
        key = AWEME_DYTK + aweme_id
        aweme_info = r.get(key)
        if not aweme_info:
            aweme_info = get_aweme_dytk(aweme_id, mid, proxies)
            r.set(key, aweme_info)

            r.expire(key, 3600*24*3)
        aweme_json = json.loads(aweme_info)
        return aweme_json['dytk'], aweme_json['uid'], aweme_json['authorName']
    elif uid:
        key = USER_DYTK+uid
        dytk = r.get(key)
        if not dytk:
            dytk = get_user_dytk(uid, proxies)
            r.set(key, dytk)
            r.expire(key, 3600 * 24 * 3)
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

    aweme_info = {}

    aweme_info['dytk'] = dytk[0]
    aweme_info['uid'] = uid[0]
    aweme_info['authorName'] = author_name[0]


    return json.dumps(aweme_info, ensure_ascii=False)


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

import sys
def get_sign(uid):
    jsstr = get_js()

    ctx = execjs.compile(jsstr)
    enSign = ctx.call('__M.require("douyin_falcon:node_modules/byted-acrawler/dist/runtime").sign', uid)
    return enSign

def init_chrome_option(webdriver):
    WIDTH = 320
    HEIGHT = 640
    PIXEL_RATIO = 3.0
    UA = 'Mozilla/5.0 (Linux; Android 4.1.1; GT-N7100 Build/JRO03C) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/35.0.1916.138 Mobile Safari/537.36 T7/6.3'

    mimvp_proxy = {

        'ip': '192.168.3.140',  # ip

        'port_https': 8887,  # http, https

        # 'port_socks': 62287,  # socks5

        # 'username': 'mimvp-user',

        # 'password': 'mimvp-pass'

    }
    # mobileEmulation = {'deviceName': 'iPhone X'}
    mobileEmulation = {"deviceMetrics": {"width": WIDTH, "height": HEIGHT, "pixelRatio": PIXEL_RATIO}, "userAgent": UA}
    options = webdriver.ChromeOptions()
    # options.add_argument('user-agent="MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"')
    proxy_https_argument = '--proxy-server=http://{ip}:{port}'.format(ip=mimvp_proxy['ip'], port=mimvp_proxy[
        'port_https'])  # http, https (无密码，或白名单ip授权，成功)

    options.add_argument(proxy_https_argument)
    options.add_experimental_option('mobileEmulation', mobileEmulation)
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-web-security')

    return options

