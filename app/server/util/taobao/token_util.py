from io import StringIO
from urllib import request
import time


def get_js():
    # f = open("/Users/ludanqing/Downloads/h.js", 'r', encoding='UTF-8')
    s = request.urlopen("http://data.qianliyann.com/download/spider/h.js").read().decode('utf8')  # 1 读取数据串
    f = StringIO(s)  # 2 将字符串转换为 StringIO对象，使其具有文件属性
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    f.close()
    return htmlstr


def get_token(cookies):
    for cookie in cookies:
        # print("%s->%s" % (cookie['name'], cookie['value']))
        if cookie.name == '_tb_token_':
            print(cookie.value)
            token = cookie.value.split("_")[0]
    return token


def init_url(data,  url, appkey, token, ctx):
    i = int(time.time())
    sign = token + "&" + str(i) + "&" + appkey + "&" + data
    en_sign = ctx.call("h", sign)
    url += "&t=" + str(i) + "&sign=" + en_sign + "&appKey=" + appkey + "&data=" + data
    return url