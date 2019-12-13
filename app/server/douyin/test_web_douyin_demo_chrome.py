#!/usr/bin/python
# -*-coding:utf-8-*-
from selenium import webdriver
from time import sleep
import execjs
import time
import json
import logging
import os
import sys
from io import StringIO
from urllib import request


logging.basicConfig(level=logging.INFO)

#import util.douyin_util
# from .util import douyin_util

currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
# print(parentUrl)
sys.path.append(parentUrl)
from util.douyin_util import *


options = init_chrome_option(webdriver)
# options.add_argument('-dump-dom')
driver = webdriver.Chrome(chrome_options=options)
# driver.viewportSize={'width':1024,'height':800}
# driver.maximize_window()

# driver.delete_all_cookies()

driver.get("https://www.douyin.com/share/user/1305874926407576")
# driver.get("https://m.baidu.com")
# driver.implicitly_wait(2)
# sleep(1)
print(driver.page_source)
# driver.save_screenshot('mtaobao.png')


driver.quit()
print("finish")
# print(html)







# load the switch

