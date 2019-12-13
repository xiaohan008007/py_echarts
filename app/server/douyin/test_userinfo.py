import re
import requests
import time
import sys
from lxml import etree
import redis
from .util.proxy_exception import ProxyLoseException

pool = redis.ConnectionPool(host='192.168.3.194', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
'''
                         抖音用户基本信息 -> 请求share来获取数据 
'''

def handle_decode(input_data):
    # 匹配icon font
    regex_list = [
        {'name': [' &#xe603; ', ' &#xe60d; ', ' &#xe616; '], 'value': 0},
        {'name': [' &#xe602; ', ' &#xe60e; ', ' &#xe618; '], 'value': 1},
        {'name': [' &#xe605; ', ' &#xe610; ', ' &#xe617; '], 'value': 2},
        {'name': [' &#xe604; ', ' &#xe611; ', ' &#xe61a; '], 'value': 3},
        {'name': [' &#xe606; ', ' &#xe60c; ', ' &#xe619; '], 'value': 4},
        {'name': [' &#xe607; ', ' &#xe60f; ', ' &#xe61b; '], 'value': 5},
        {'name': [' &#xe608; ', ' &#xe612; ', ' &#xe61f; '], 'value': 6},
        {'name': [' &#xe60a; ', ' &#xe613; ', ' &#xe61c; '], 'value': 7},
        {'name': [' &#xe60b; ', ' &#xe614; ', ' &#xe61d; '], 'value': 8},
        {'name': [' &#xe609; ', ' &#xe615; ', ' &#xe61e; '], 'value': 9},
    ]

    for i1 in regex_list:
        for i2 in i1['name']:
            input_data = re.sub(i2, str(i1['value']), input_data)       # 把正确value替换到自定义字体上

    html = etree.HTML(input_data)
    douyin_info = {}
    # 获取头像
    douyin_info['avatar'] = html.xpath("//div[@class='personal-card']/div[@class='info1']//span[@class='author']/img/@src")[0]
    # 获取个人认证
    douyin_info['verify'] = ""
    verify = html.xpath("//div[@class='personal-card']/div[@class='info2']/div")
    if verify:
        douyin_info['verify'] = verify[0].xpath('string(.)').strip()
    # 获取昵称
    douyin_info['nick_name'] = html.xpath("//div[@class='personal-card']/div[@class='info1']//p[@class='nickname']/text()")[0]
    # 获取抖音ID
    douyin_id_html = html.xpath("//div[@class='personal-card']/div[@class='info1']/p[@class='shortid']")[0]

    douyin_id = douyin_id_html.xpath('string(.)').replace('抖音ID：', '').strip()
    # douyin_id = ''.join(html.xpath("//div[@class='personal-card']/div[@class='info1']/p[@class='shortid']/i/text()"))
    douyin_info['douyin_id'] = douyin_id
    # douyin_info['douyin_id'] = re.sub(search_douyin_str, '', html.xpath("//div[@class='personal-card']/div[@class='info1']//p[@class='nickname']/text()")[0]).strip() + douyin_id
    # # 职位类型
    # try:
    #     douyin_info['job'] = html.xpath("//div[@class='personal-card']/div[@class='info2']/div[@class='verify-info']/span[@class='info']/text()")[0].strip()
    # except:
    #     pass
    # 描述
    douyin_info['describe'] = html.xpath("//div[@class='personal-card']/div[@class='info2']/p[@class='signature']/text()")[0].replace('\n', ',')
    # 关注
    douyin_info['follow_count'] = html.xpath(
        "//div[@class='personal-card']/div[@class='info2']/p[@class='follow-info']//span[@class='focus block']")[0].xpath('string(.)').replace('关注', '').strip()
    # douyin_info['follow_count'] = html.xpath("//div[@class='personal-card']/div[@class='info2']/p[@class='follow-info']//span[@class='focus block']//i[@class='icon iconfont follow-num']/text()")[0].strip()
    # 粉丝
    fans_value = ''.join(html.xpath("//div[@class='personal-card']/div[@class='info2']/p[@class='follow-info']//span[@class='follower block']//i[@class='icon iconfont follow-num']/text()"))
    unit = html.xpath("//div[@class='personal-card']/div[@class='info2']/p[@class='follow-info']//span[@class='follower block']/span[@class='num']/text()")
    if unit[-1].strip() == 'w':
        douyin_info['fans'] = str(float(fans_value) / 10) + 'w'
    else:
        douyin_info['fans'] = fans_value
    # 点赞
    digg = ''.join(html.xpath("//div[@class='personal-card']/div[@class='info2']/p[@class='follow-info']//span[@class='liked-num block']//i[@class='icon iconfont follow-num']/text()"))
    unit = html.xpath("//div[@class='personal-card']/div[@class='info2']/p[@class='follow-info']//span[@class='liked-num block']/span[@class='num']/text()")
    if unit[-1].strip() == 'w':
        douyin_info['digg'] = str(float(digg) / 10) + 'w'
    else:
        douyin_info['digg'] = digg
    #作品数
    aweme_like_count = html.xpath('//div[@class="video-tab"]/div')[0].xpath('string(.)')
    aweme_count = aweme_like_count.split('喜欢')[0].replace('作品', '').strip()
    like_count = aweme_like_count.split('喜欢')[1].strip()
    douyin_info['like'] = like_count
    douyin_info['aweme_count'] = aweme_count
    return douyin_info



def handle_douyin_info(url, proxies):
    for k in range(50):
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
        }
        if proxies:
            response = requests.get(url=url, headers=header, proxies=proxies, verify=False, timeout=3)
        else:
            response = requests.get(url=url, headers=header, verify=False, timeout=3)
        # response = requests.get(url=url, headers=header,  verify=False, timeout=3)
        # if not ip_proxy.check_response_code(response):
        #     raise ProxyLoseException('代理ip失效')
        result = response.text.strip()
        if result:
            break
        else:
            time.sleep(1)

    return handle_decode(result)


if __name__ == '__main__':
    url = 'https://www.douyin.com/share/user/81939158402'
    res = requests.get(url,verify=False)
    print(res.text)
    # proxies = ip_proxy.get_proxy()
    # try:
    #     result = handle_douyin_info(url, proxies)
    # except ProxyLoseException as e:
    #     print(e)
    #     print('===============')
    #     proxies = ip_proxy.get_proxy()
    #     result = handle_douyin_info(url, proxies)

