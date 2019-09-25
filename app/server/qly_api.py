# coding: utf-8
import threading
from flask import render_template, Blueprint, request, send_file, Flask, jsonify
from .util.utils import init_logger, last_n_days, n_day_ago
from .util import mysql_client, mongo_client, photo_util
import pyecharts
from pyecharts import Bar
# import Bar, Line, Scatter, EffectScatter, Pie, Grid, Page,Geo, Map
from .util import douyinUtil
from .util import douyin_stat
import pandas as pd
import urllib

from urllib.parse import quote
import json

from collections import defaultdict
import requests
from urllib.parse import quote
import time
from lxml import etree
from aip import AipOcr
import os
import json
import csv
import codecs
from PIL import Image, ImageEnhance
import pytesseract
import base64
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


""" 你的 APPID AK SK """
APP_ID = '15487434'
API_KEY = 'HUoLvBMD8hPbTXYdkjO8QKYh'
SECRET_KEY = 'Nmlxqu5iFhkeGKosZYB8zkWRw8Osds2N'
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

app = Blueprint('api', __name__)
root_logger = init_logger()
mysql_client1 = mysql_client.MysqlClient(db='tts_qly_analysis')
mysql_client2 = mysql_client.MysqlClient(db='tts_tob_qly_v2')


url_set = {'s-bp1ab95be815ccc4.mongodb.rds.aliyuncs.com:3717'}
mongo_client1 = mongo_client.MongodbClient(url_set, "qly_keyword", username="tts_qly", password="qlyrw")
mongo_client2 = mongo_client.MongodbClient(url_set, "qly_industry_168", username="tts_qly", password="qlyrw")
mongo_client3 = mongo_client.MongodbClient({'s-bp1fb86105e14fa4.mongodb.rds.aliyuncs.com:3717'}, "tts_douyin", username="tts_douyin", password="douyinrw")
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

@app.route('/')
def app_0():
    # list = mongo_client2.get_tb_cid()
    #
    # for cid in list:
    #     print(cid['cid'])
    #     catinfo = mongo_client2.get_catinfo(cid['cid'])
    #     print(catinfo['catname']+"\t"+ catinfo['catpath'])
    # list = mongo_client2.get_1688old()
    # ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # items = []
    # for old in list:
    #     item = {}
    #     item['rdate']=str(old['rdate']).split(" ")[0]
    #     item['cid'] = old['cid_name']
    #     item['ctime'] = ctime
    #     item['index_tb'] = old['tb']
    #     item['index_1688_buy'] = old['1688']
    #     item['index_1688_supply'] = old['suppy']
    #     items.append(item)
    #
    # mongo_client2.insert_1688index(items)
    return "<h1>数据演示</h1>  <br> <a href='/one'>qly_pv</a> <br> <a href='/order'>指数99订单</a><br> <a href='/keyword?q=裤子'>关键词查询</a><br> <a href='/keyword_region?q=裤子&start=2018-10-01&end=2018-10-21'>地区关键词查询</a><br> <a href='/guess?q=连衣裙'>类目预测</a><br> <a href='/ocr'>图像识别</a><br> <a href='/static/douyin_user.html'>抖音达人打标</a>"


def label_formatter(params):
    return params.value + '元'

@app.route('/ocr')
def ocr():
    return send_file("templates/upload.html")

basedir = os.path.abspath(os.path.dirname(__file__))

#二值化,输入阈值和文件地址
def binaryzation(threshold,image_address):
    image=Image.open(image_address)#打开图片
    image=image.convert('L')#灰度化
    table=[]
    for x in range(256):#二值化
        if x<threshold:
            table.append(0)
        else:
            table.append(1)
    image=image.point(table,'1')
    return image

def main():
    image=binaryzation(200,'tensorflow.png')
    image.show()#展示二值化后的效果,防止图片二值化效果不佳变成一片白无法识别
    result=pytesseract.image_to_string(image)#变图片为字符串
    print(result)





import codecs















@app.route('/ocr_google', methods=['post'])
def ocr_google():
    img = request.files.get('photo')
    path = basedir + "/photo/"
    file_path = path + img.filename
    img.save(file_path)

    # image = binaryzation(200, file_path)
    image = Image.open(file_path)  # 打开图片
    image = ImageEnhance.Sharpness(image).enhance(2.0)
    # # image.save(path+"hehe.png")
    text = pytesseract.image_to_string(image, lang='chi_sim')  # 使用简体中文解析图片
    print(text)
    text = text.replace('\n', '<br>')
    return text

@app.route('/up_ocr', methods=['post'])
def up_ocr():
    img = request.files.get('photo')
    b64_photo = request.form.get('b64_photo')
    high = request.form.get('high')
    form = request.form.get('form')
    merge = request.form.get('merge')
    photo_type = request.form.get('photo_type')
    # username = request.form.get("name")
    # basedir = os.path.abspath(os.path.dirname(__file__))
    path = basedir+"/photo/"
    file_path = path + img.filename
    img.save(file_path)
    # print
    # '上传头像成功，上传的用户是：' + username
    # return render_template('index.html')

    image = get_file_content(file_path)
    # client.
    if high and high == "1":
        jsons = client.basicAccurate(image)
        j_data = json.dumps(jsons)
        # """ 调用高清文字识别, 图片参数为本地图片 """
        return j_data
    elif form and form == "1":
        jsons = client.tableRecognitionAsync(image)
        # j_data = json.dumps(jsons)
        reqid = jsons['result'][0]['request_id']

        print(reqid)
        # print(jsons['result']['ret_msg'])
        """ 如果有可选参数 """
        options = {}
        options["result_type"] = "json"
        time.sleep(3)
        """ 带参数调用表格识别结果 """
        jsons = client.getTableRecognitionResult(reqid, options)
        j_data = json.dumps(jsons)
        # """ 调用表格文字识别, 图片参数为本地图片 """
        return j_data
    elif merge and merge == "1":
        return parse_photo_batch(photo_type, path, img.filename)
    else:
        jsons = client.basicGeneral(image)
        j_data = json.dumps(jsons)
        # """ 调用通用文字识别, 图片参数为本地图片 """
        return j_data



@app.route('/guess')
def cats_guess():
    param_info = request.values.to_dict()
    if 'q' in param_info:
        q = param_info['q']
    else:
        q = '半身裙'
    return cats_forcast(q)





def print_item(data, keyword, page):
    # 将已编码的json字符串解码为python对象
    objs = jsonpToJson(data)
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # data = objs['data']['listItem']
    current_hour = time.strftime("%Y-%m-%d %H", time.localtime())
    if 'data' in objs:
        data = objs['data']
        if 'listItem' in data:
            # f = codecs.open('taobao1.txt_' + current_hour, 'a+', 'utf-8')
            datas = data['listItem']
            # f.write(current_time + "\t" + keyword+"\t"+str(page)+"\n")
            # pipe = conn.pipeline()
            page_site = 1
            for data in datas:
                title = data['name']
                itemid = data['item_id']
                cid = '0'
                if 'category' in data:
                    cid = data['category']
                userId = data['userId']
                spid = itemid
                rank = str(page) + "-" + str(page_site)
                pay = data['sold']
                sellerCredit = '0'
                userType = data['isB2c']
                pprice = data['price']
                nick = data['nick']
                imgUrl = data['pic_path']
                imgUrl_sub = imgUrl.split('/')
                imgUrl = imgUrl_sub[len(imgUrl_sub) - 1].replace('_60x60.jpg', '')
                type = '0'
                if 'true' == data['isP4p']:
                    type = '1'
                itemLoc = data['sellerLoc']
                if itemLoc == '':
                    itemLoc = data['location']
                # cid、userId、keyword、spid、rank、pay、title、sellerCredit、userType、pprice、nick、imgUrl、type、itemLoc
                if keyword != 'haha':
                    print(
                        cid + "\t" + userId + "\t" + keyword + "\t" + spid + "\t" + rank + "\t" + pay + "\t" + title + "\t" + sellerCredit + "\t" + userType + "\t" + pprice + "\t" + nick + "\t" + imgUrl + "\t" + type + "\t" + itemLoc + "\n")
                page_site += 1
                # pipe.lpush('key', itemid + "@" + title + "\n")
            # pipe.execute()
            # f.write(tips)
            # print("=====my data==========:"+tips)
            # f.write("\n")
            print(current_time + "\t" + keyword + "\t" + str(page))
            # f.close()
        else:
            print(current_time + "\t" + keyword + "\t" + str(page) + " ==========no listItem")
    else:
        print(current_time + "\t" + keyword + "\t" + str(page) + " ==========no data")

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

@app.route('/1688')
def index_1688():


    param_info = request.values.to_dict()
    if 'cat_name' in param_info:
        cat_name = param_info['cat_name']
    else:
        cat_name = '半身裙'

    cat_info = mongo_client2.get_cid(cat_name)
    if cat_info is None:
        cats = spider_1688_catinfo(cat_name)
        catinfos = mongo_client2.get_catinfo_in(cats)
        cat_link = "该类目不存在，可能属于以下类目：<br>"
        for cat in catinfos:
            cat_link += "<a href='/1688?cat_name="+cat['catname']+"'>"+cat['catname']+"</a>\t"
            # print(cat['catname'])
        # cats_str = '\t'.join(cats)
        return cat_link
    # bar = read_1688_index(cat_info['catid'], cat_name)
    bar = read_1688_all(cat_info['catid'], cat_name)
    # bar = read_keyword(q)
    ret_html = render_template('pycharts.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               script_list=bar.get_js_dependencies())
    return ret_html


@app.route('/keyword_region')
def keyword_region():
    param_info = request.values.to_dict()
    if 'q' in param_info:
        q = param_info['q']
    else:
        q = '裤子'
    if 'start' in param_info:
        start_date = param_info['start']
        end_date = param_info['end']
    else:
        start_date = n_day_ago(7)
        end_date = n_day_ago(1)
    bar = read_region(q, start_date, end_date)
    # bar = read_keyword(q)
    ret_html = render_template('pycharts.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               script_list=bar.get_js_dependencies())
    return ret_html


@app.route('/keyword')
def keyword():
    param_info = request.values.to_dict()
    if 'q' in param_info:
        q = param_info['q']
    else:
        q = '裤子'
    bar = read_keyword(q)
    ret_html = render_template('pycharts.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               script_list=bar.get_js_dependencies())
    return ret_html


@app.route('/order')
def order():
    bar = read_order()
    ret_html = render_template('pycharts.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               script_list=bar.get_js_dependencies())
    return ret_html


@app.route('/one')
def app_1():

    # bar = read_csv()
    bar = read_mysql()
    ret_html = render_template('pycharts.html',
                               myechart=bar.render_embed(),
                               mytitle=u"数据演示",
                               host='/static',
                               script_list=bar.get_js_dependencies())
    return ret_html

def spider_1688_catinfo(keyword):
    cats = []
    encode_keyword = str(keyword.encode('GBK')).replace('\\x', '%').replace('\'', '')[1:]
    r = requests.get('https://s.1688.com/selloffer/offer_search.htm?keywords=%s&n=y' % encode_keyword)
    if r.status_code == 200:
        r.encoding = r.apparent_encoding
        # print('爬取成功！！！')
        # print(r.text)
        html = etree.HTML(r.text)
        for cat_selector in html.xpath(
                '//div[@class="s-widget-flatcat sm-widget-row sm-sn-items-control sm-sn-items-count-d fd-clr"]/div[@class="sm-widget-items fd-clr"]/ul/li'):
            cat_name = cat_selector.xpath('a/span/text()')[0]
            cats.append(str(cat_name))
            # print(str(cat_name))
    return cats


def cats_forcast(q):
    keyword = q
    q = quote(q, 'utf-8')
    request_url = 'http://47.92.145.108:30003/youche/getInsightCatsforecastnew.do?bidwordList=' + q
    s = urllib.request.urlopen(request_url).read().decode('utf8')
    json_data = json.loads(s)
    cat_list = json_data['simba_insight_catsforecastnew_get_response']['category_forecast_list'][
        'insight_category_forcast_d_t_o']
    # for cat in cat_list:
    return json.dumps(cat_list)
    # return cat_list


def read_region(q, star_date, end_date):
    # q = '11'
    keyword = q
    q = quote(q, 'utf-8')
    request_url = 'http://47.92.145.108:30003/youche/wordsArea.do?keyword='+q+'&startDate='+star_date+'&endDate='+end_date
    s = urllib.request.urlopen(request_url).read().decode('utf8')
    json_data = json.loads(s)
    region_list = json_data['simba_insight_wordsareadata_get_response']['word_areadata_list']['insight_words_area_distribute_data_d_t_o']
    regions = []
    values = []
    min_num = 100000000
    max_num = 0
    for region in region_list:
        if 'cityname' in region:
            region_name = region['cityname']
            if region_name == '内蒙':
                region_name = '内蒙古'
            if region_name.find('中国其它') > -1 or region_name.find('国外') > -1:
                continue
            regions.append(region_name)
            pv = int(region['impression'])
            if pv < min_num:
                min_num = pv
            if pv > max_num:
                max_num = pv
            values.append(region['impression'])
            # print(region['cityname'])



    geo = pyecharts.Geo(keyword+"--全国主要城市访问量", star_date+"~"+end_date, title_color="#fff",
              title_pos="center", width=1000,
              height=600, background_color='#404a59')
    # attr, value = geo.cast(data)
    geo.add("流量", regions, values, visual_range=[min_num, max_num], maptype='china', visual_text_color="#fff",
            symbol_size=10, is_visualmap=True)



    # map = Map(keyword+"~全国主要城市访问量", star_date+"~"+end_date, width=1200, height=600)
    # map.add("", regions, values, visual_range=[min_num, max_num], maptype='china', is_visualmap=True, is_label_show=True,
    #         visual_text_color='#000')
    return geo
    # print(s)


def read_keyword(q):

    keyword_list = mongo_client1.get_keyword(q)
    pvs = []
    amounts = []
    pays = []
    favs = []
    rdates = []
    for keyword in keyword_list:
        pvs.append(keyword['impression'])
        amounts.append(keyword['transactiontotal'])
        pays.append(keyword['transactionshippingtotal'])
        favs.append(keyword['favtotal'])
        ctime = str(keyword['ctime']).split(" ")[0]
        rdates.append(last_n_days(ctime, 1)[0])
    bar = pyecharts.Line(q, "关键词数据走势")
    bar.add("搜索量", rdates, pvs, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True)
    bar.add("成交金额", rdates, amounts, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True)
    bar.add("成交笔数", rdates, pays, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True)
    bar.add("收藏数", rdates, favs, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True)
    return bar


def read_1688_all(cid, cat_name):
    page = pyecharts.Page()  # 实例化page类

    bar = read_1688_index(cid, cat_name)
    page.add(bar)
    attr_list = mongo_client2.get_1688attr(cid)
    # attrs = []
    # for attr in attr_list:
    #     attrs.append(attr)
    rows_by_type = defaultdict(list)

    for attr in attr_list:
        rows_by_type[attr['attr_type']].append(attr)
    for attr_type in rows_by_type.items():
        # print(attr_type[1]['attr_value'])
        attr_value_index_group = []
        attr_value_group = []
        for attr in attr_type[1]:
            attr_value_index_group.append(attr['attr_value_index'])
            attr_value_group.append(attr['attr_value'])
            # print(attr_type[0]+"\t"+attr['attr_value'])
        # attr = ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]
        # v1 = [11, 12, 13, 10, 10, 10]
        pie = pyecharts.Pie(attr_type[0], title_pos='50%')
        pie.add(attr_type[0], attr_value_group, attr_value_index_group, radius=[40, 75], label_text_color=None,
                is_label_show=True, legend_orient='vertical', legend_pos='left')
        page.add(pie)
    # print(rows_by_type)
    # pie
    # attr = ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]
    # v1 = [11, 12, 13, 10, 10, 10]
    # pie = Pie("饼图-圆环图示例", title_pos='50%')
    # pie.add("", attr, v1, radius=[40, 75], label_text_color=None,
    #         is_label_show=True, legend_orient='vertical', legend_pos='left')

    # TODO 配置Grid类
    # grid = Grid(height=720, width=1200)  # 初始化，参数可传page_title,width,height
    # grid.add(bar, grid_bottom="60%", grid_left="60%")  # 添加要展示的图表，并设置显示位置
    # # grid.add(line, grid_bottom="60%", grid_right="60%")  # 添加要展示的图表，并设置显示位置
    # grid.add(pie, grid_bottom="60%", grid_right="60%")
    # grid.add(scatter, grid_top="60%", grid_left="60%")  # 添加要展示的图表，并设置显示位置
    # grid.add(es, grid_top="60%", grid_right="60%")  # 添加要展示的图表，并设置显示位置

    # grid.render("Grid_并行显示多张图表.html")
    # return grid



    return page


def read_1688_index(cid, cat_name):
    index_list = mongo_client2.get_1688index(cid)
    rdates = []
    index_tbs = []
    index_1688_buy = []
    for index in index_list:
        rdates.append(index['rdate'])
        index_tbs.append(index['index_tb'])
        index_1688_buy.append(index['index_1688_buy'])
    bar = pyecharts.Line(cat_name, "行业数据走势")
    bar.add("淘宝交易指数", rdates, index_tbs, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True)
    bar.add("1688收购指数", rdates, index_1688_buy, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True)
    return bar

def read_csv():
    pddata = pd.read_csv('/Users/ludanqing/Desktop/test3.csv')

    # 返回全部列名
    # cols = pddata.columns
    # print(pddata['日期'][1])
    bar = pyecharts.Line("一周访问量", "千里眼")
    time = pddata['日期']
    today = pddata['数据1']
    yesterday = pddata['数据2']
    # time = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    # today = [5, 20, 36, 10, 75, 90, 28]
    # yesterday = [25, 10, 56, 70, 25, 40, 88]
    bar.add("这周", time, today, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True)
    bar.add("上周", time, yesterday, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True)
    return bar


def read_order():
    orders = mysql_client2.find_order()
    pays = orders['sum_pay']
    counts = orders['count']
    rdates = orders['rdate']
    # for order in orders:
    #     pays.append(int(order['sum_pay'])/100)
    #     rdates.append(order['rdate'])
    #     counts.append(order['count'])
    bar = Bar("成交量", "zhishu99")
    bar.add("单数", rdates, counts, mark_point=["max", "min"], mark_line=["average"], is_label_show=True,  is_more_utils=True)
    bar.add("金额", rdates, pays, mark_point=["max", "min"], mark_line=["average"],is_label_show=True, label_formatter=label_formatter, is_more_utils=True)
    return bar


def read_mysql():
    stats = mysql_client1.find_qlypv_history()
    pvs = stats['num']
    rdates = stats['rdate']

    bar = pyecharts.Line("历史访问量", "千里眼")
    time = rdates
    today = pvs
    # bar.add("这周", time, today, mark_point=["max", "min"], mark_line=["average"], is_label_show=True, label_formatter=label_formatter, is_more_utils=True)
    bar.add("pv", time, today, mark_point=["max", "min"], mark_line=["average"], is_more_utils=True)
    return bar
# def read_csv(file_path):
#     with open(file_path, 'r') as fr:
#         rows = csv.DictReader(fr)
#         for row in rows:
#             print(row)


def parse_photo_batch(photo_type, local_path, file_name):
    im = Image.open(local_path + file_name)  # 打开图片
    start = time.time()
    g1, g2, g3 = photo_util.get_3column(1, im, local_path)
    t2 = time.time()
    print("google:"+str(t2-start))
    g0 = photo_util.parse_first_column(photo_type, client, im, local_path)
    print("baidu:"+str(time.time()-t2))
    result = {}
    result['first_column'] = g0
    result['data'] = g1
    jsonStr = json.dumps(result)

    return jsonStr

def parse_base64(str):
    str = str.replace('%2B', "+").replace('%3D', '=').replace('%2F', '/')
    imgdata =  base64.b64decode(str)

    f = open('okk.jpg', 'rb')
    baseimg = base64.b64encode(f.read())
    f.close()





@app.route('/check_ad')
def check_ad():
    hour = time.strftime("%H", time.localtime())
    if int(hour) < 9:
        return 'true'
    r = requests.get("http://showkc.taotaosou.com/qly.do?adType=0,0,1,0&adSize=0,0,1000*50,0&itemSize=0,0,1,0&pid=702&keyword=0,0,%E5%A5%B3%E7%AB%A5%E5%87%89%E9%9E%8B_%E6%B7%98%E5%AE%9D%E6%90%9C%E7%B4%A2,0&locationHref=https%3A%2F%2Fs.taobao.com%2Fsearch%3Fq%3D%25E5%25A5%25B3%25E7%25AB%25A5%25E5%2587%2589%25E9%259E%258B%26refpid%3D430269_1006%26source%3Dtbsy%26style%3Dgrid%26tab%3Dall%26pvid%3Df01a3f06ba812a556e1a5b6cb1dc56b5%26clk1%3Dc40e943e8b64b0aaf3321006ec8622e4%26spm%3Da21bo.2017.201856-sline.4.5af911d97O4x0X&cate=#")
    result = r.text
    if result.find('title') > -1:
        return 'true'
    return 'false'





