import os
import re
import json
import time
import random
import datetime
import requests
import pandas as pd
from retrying import retry
import execjs


import token_util
from login_taobao import UsernameLogin

"""
获取详细教程、获取代码帮助、提出意见建议
关注微信公众号「裸睡的猪」与猪哥联系
@Author  :   猪哥,
"""

# 关闭警告
requests.packages.urllib3.disable_warnings()
# 登录与爬取需使用同一个Session对象
req_session = requests.Session()

# 代理ip，网上搜一个，猪哥使用的是 站大爷：http://ip.zdaye.com/dayProxy.html
# 尽量使用最新的，可能某些ip不能使用，多试几个。后期可以考虑做一个ip池
# 爬取淘宝ip要求很高，西刺代理免费ip基本都不能用，如果不能爬取就更换代理ip
proxies = {'http': '106.75.140.167:8888',
           'https': '106.75.140.167:8888'
                   }
# 请求头
headers = {
    'referer': 'https://www.taobao.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

class GoodsSpider:

    def __init__(self, q, spider_max_page, goods_path):
        self.ctx = execjs.compile(token_util.get_js())
        self.q = q
        self.spider_max_page = spider_max_page
        self.goods_path = goods_path
        # 超时
        self.timeout = 15
        self.goods_list = []

        # 淘宝登录
        # 淘宝用户名
        username = 'xiaohan008007'
        # 淘宝重要参数，从浏览器或抓包工具中复制，可重复使用
        ua = ua = '120#bX1bS97HYSI5d/CutI8aaMpobIGq7PBsCxewdp4g09y60DEjOiwri+4JHVV7HLznzf25kK4goCcbIkIjxo6mXgc+PQ1eE4RYyUz7cAx1q0uUJnXpYgHQHPxlEcHRZWmUiHoHYi/2mNjzFopy0qoAqXsLlR92Ov47Doknih1dJkDLdXvfHA7Jtb1eZpXO9H4viChNYxS0Q4s2wsCKwoaPZolxHG2GebKY3YHhX/VoXhFLLoQ0Zlv11bWSUtT1Vwfdme17Eu7VZVcEKlWl8OwuHDmo2CTE3N0Mac231rJAE1eoDMe5ePTe0ENvXV6r9W2Vqh6W3a1AeFb10rTdFVhH0ZZkM1fGsQ3NGg7KXPM3uAfHIjNtsrgcoI1BnR0QnjJZYRJeHOTPInF+Zg1ZSnc1NxYYUdX9ck72A/h3eUz7Wfm5f+/BPorD6dXJI8YOTy8AK6YX8uNV9Q5R+eRvzPzdb8IqVDV2Yv7nHOdxdDOEq+M0tteQFnWmx1pxPXpbg5MvXqMMGIYbTl9PNWcMbbAt7aPyyEIbbdPn0IUQbOdBJXbVSxtkOyzBzUetJI2S7MOS4SY1tNbmLWaGL8bdsW4lLiT4gJ1cLxYIUfTTERN8tWGngOPQR/Edp991uyVT/okRwEoC9vkPFy4S7ok4QuEfRpLjCXU7guNyzLR6XR5XSfq3OFcgoiDSFnM09lMXk5XXKB8IAB80RXPrplmDRxXBYZNB6ff0iOHJWDFYAirVJVj49BAG4bp8pOusOSL6O8xBlozowzDAN2l+mdxlpm5qJycp9EIqyhiC+xUM16MlDLH2hMyZqriEadwjGH10/3yvS/ARUt0+UJJSOkCyFw7LOedAlObUk6ikRYk3iuUHZOKvn3R/m3y5gQcmhnGpFKB+eEog1gN+48JH6HaGDFsV/W2RuBlxpamYDvHQhKEuufLSRnX6s89BMkB9NzOzuH+WM65/tDgM3fIg+yW7o658FbQ1fFVNnuLIqCWW0xrv14aBkRyM0PjscLkoP5Aex6FOMnkmLq9aoxzkSThV70Zg+1Ss9gfBHwKzh8oL50Cm6uh2O97JwRAmwEVnu2ch8BVVa6JTEgzGrF8WSVG4iVgl1aB1Hfu5u7BW5jJiYhGE/vaQwyKRdJlUAILAC7ZhQp6fr8o3IbOvCGbjDlJBx52w+e88SX9RlrA='
        # 加密后的密码，从浏览器或抓包工具中复制，可重复使用
        TPL_password2 = '219406b145abaad2a216718694f80f95f14e4359c5c9198e5b7b9e93d8276cf5f3f71768af7445fc610a222a7de9efb716278b02cd16efa489f96bddfc446a6cb8e03ed9fbea2bcb202de5ce3cd925a4808dbb1ac03119b9bfe2459707a662dc9a967c6bacee0fb04f26ffc237b867894032e490fd6b56db444b786889f68868'
        ul = UsernameLogin(username, ua, TPL_password2, req_session)
        ul.login()


    @retry(stop_max_attempt_number = 1)
    def spider_goods(self, page):
        """
        :param page: 淘宝分页参数
        :return:
        """
        s = page * 44
        # 搜索链接，q参数表示搜索关键字，s=page*44 数据开始索引
        search_url = f'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q={self.q}&suggest=history_1&_input_charset=utf-8&wq=biyunt&suggest_query=biyunt&source=suggest&bcoffset=4&p4ppushleft=%2C48&s={s}&data-key=s&data-value={s + 44}'
        # search_url = 'http://pv.sohu.com/cityjson%3Fie=utf-8'

        response = req_session.get(search_url, headers=headers, proxies=proxies,
                                   verify=False, timeout=self.timeout)
        # print(response.text)
        # print(response.text)
        goods_match = re.search(r'g_page_config = (.*?)}};', response.text)
        # 没有匹配到数据
        if not goods_match:
            print('提取页面中的数据失败！')
            print(response.text)
            raise RuntimeError
        goods_str = goods_match.group(1) + '}}'
        goods_list = self._get_goods_info(goods_str)
        self._save_excel(goods_list)
        # print(goods_str)

    def _get_goods_info(self, goods_str):
        """
        解析json数据，并提取标题、价格、商家地址、销量、评价地址
        :param goods_str: string格式数据
        :return:
        """
        goods_json = json.loads(goods_str)
        goods_items = goods_json['mods']['itemlist']['data']['auctions']
        goods_list = []
        for goods_item in goods_items:
            goods = {'title': goods_item['raw_title'],
                     'price': goods_item['view_price'],
                     'location': goods_item['item_loc'],
                     'sales': goods_item['view_sales'],
                     'comment_url': goods_item['comment_url']}
            goods_list.append(goods)
        return goods_list

    def _save_excel(self, goods_list):
        """
        将json数据生成excel文件
        :param goods_list: 商品数据
        :param startrow: 数据写入开始行
        :return:
        """
        # pandas没有对excel没有追加模式，只能先读后写
        if os.path.exists(self.goods_path):
            df = pd.read_excel(self.goods_path)
            df = df.append(goods_list)
        else:
            df = pd.DataFrame(goods_list)

        writer = pd.ExcelWriter(self.goods_path)
        # columns参数用于指定生成的excel中列的顺序
        df.to_excel(excel_writer=writer, columns=['title', 'price', 'location', 'sales', 'comment_url'], index=False,
                    encoding='utf-8', sheet_name='Sheet')
        writer.save()
        writer.close()

    def patch_spider_goods(self):
        """
        批量爬取淘宝商品
        如果爬取20多页不能爬，可以分段爬取
        :return:
        """
        # 写入数据前先清空之前的数据
        if os.path.exists(self.goods_path):
            os.remove(self.goods_path)
        # 批量爬取，自己尝试时建议先爬取3页试试
        for i in range(0, self.spider_max_page):
            print('第%d页' % (i + 1))
            self.spider_goods(i)
            # 设置一个时间间隔
            time.sleep(random.randint(10, 15))

    def spider_taobao_address(self):
        url = 'https://h5api.m.taobao.com/h5/mtop.taobao.mbis.getdeliveraddrlist/1.0/?jsv=2.4.2&api=mtop.taobao.mbis.getDeliverAddrList&v=1.0&ecode=1&needLogin=true&dataType=jsonp&type=jsonp&callback=mtopjsonp4'
        appkey = '27769795'
        cookies = req_session.cookies
        token = token_util.get_token(cookies)
        url = token_util.init_url('{}',  url, appkey, token, self.ctx)
        response = req_session.get(url, headers=headers, proxies=proxies,
                                   verify=False, timeout=self.timeout)
        print(response.text)



if __name__ == '__main__':
    nowTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
    spider_max_page = 1
    goods_path = 'taobao_goods_%s.xlsx' % nowTime
    gs = GoodsSpider('避孕套', spider_max_page, goods_path)
    # gs.patch_spider_goods()
    gs.spider_taobao_address()