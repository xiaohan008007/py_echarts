# coding: utf-8
import threading
from flask import render_template, Blueprint, request, send_file, Flask, jsonify
from .util.utils import init_logger


import redis

from .douyin.util import douyin_util

from selenium import webdriver


pool5 = redis.ConnectionPool(host='192.168.3.194', port=6379, db=5)
rds5 = redis.Redis(connection_pool=pool5)
douyin_uid_signature = 'douyin:web:uid:awemes:signature:'


app = Blueprint('douyin_chrome', __name__)
root_logger = init_logger()





chrome_driver = ''

@app.route('/douyin/uid_signature')
def uid_signature():
    param_info = request.values.to_dict()
    if 'uid' not in param_info:
        return 'uid required!!'
    uid = param_info['uid']
    r_key = douyin_uid_signature+uid
    if rds5.get(r_key):
        return rds5.get(r_key)

    global chrome_driver
    if not chrome_driver:
        options = douyin_util.init_chrome_option(webdriver)
        # options.add_argument('-dump-dom')
        chrome_driver = webdriver.Chrome(chrome_options=options)
    chrome_driver.get("https://www.douyin.com/share/user/%s" % uid)
    # html = chrome_driver.page_source
    # chrome_driver.quit()
    # if html.find(uid) > -1:
    return rds5.get(r_key)
        # return 'successs'
    return 'fail'

