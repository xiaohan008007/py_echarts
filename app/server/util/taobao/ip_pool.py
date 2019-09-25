# IP地址取自国内髙匿代理IP网站：http://www.xicidaili.com/nn/
# 仅仅爬取首页IP地址就足够一般使用

from bs4 import BeautifulSoup
import requests
import random
import urllib
from urllib import request
from lxml import etree
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
'Cookie': 'acw_tc=781bad2015692184811758786e20b2c61ad9c779803cdd09e0db3c3f7eb1ff; ASPSESSIONIDCSBQDSCS=KMPDFFCAGIJIGHLLOJGAJHEN; __51cke__=; Hm_lvt_8fd158bb3e69c43ab5dd05882cf0b234=1569218486; Hm_lvt_96d9d92b8a4aac83bc206b6c9fb2844a=1569218487; acw_sc__v3=5d8871ce9fa9ad6f389673a8a326002ecb417a38; acw_sc__v2=5d8871d6da32acfa9d135e52f3358bb66c1a4537; ASPSESSIONIDAUDRDTCT=ODCIEDDABHFACFHCAKKGENCE; __tins__16949115=%7B%22sid%22%3A%201569223119747%2C%20%22vd%22%3A%203%2C%20%22expires%22%3A%201569224951864%7D; __51laig__=8; Hm_lpvt_8fd158bb3e69c43ab5dd05882cf0b234=1569223152; Hm_lpvt_96d9d92b8a4aac83bc206b6c9fb2844a=1569223153'}


def getHTMLText(url, proxies):
    try:
        r = requests.get(url, proxies=proxies)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
    except:
        return 0
    else:
        return r.text


def get_ip_list(url):
    web_data = requests.get(url,headers)
    soup = BeautifulSoup(web_data.text, 'html')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)
#检测ip可用性，移除不可用ip：（这里其实总会出问题，你移除的ip可能只是暂时不能用，剩下的ip使用一次后可能之后也未必能用）
    for ip in ip_list:
        try:
          proxy_host = "https://" + ip
          proxy_temp = {"https": proxy_host}
          res = urllib.urlopen(url, proxies=proxy_temp).read()
        except Exception as e:
          ip_list.remove(ip)
          continue
    return ip_list


def get_random_ip(ip_list):
    proxy_list = []
    for ip in ip_list:
        proxy_list.append('http://' + ip)
    proxy_ip = random.choice(proxy_list)
    proxies = {'http': proxy_ip}
    return proxies




def spider_detail(url):
    r = requests.get(url, headers=verify_password_headers, verify=False)
    if r.status_code == 200:
        r.encoding = r.apparent_encoding
        # print('爬取成功！！！')
        print(r.text)
        html = etree.HTML(r.text)

        for list_selector in html.xpath('//div[@class="thread_item"]'):
            detail_url = list_selector.xpath('div/h3/a/@href')[0]
            print(detail_url)
            # if detail_url:
            #     break

if __name__ == '__main__':

    # crawl_zhandaye()
    url = 'http://www.zdaye.com/dayProxy.html'
    verify_password_headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'www.zdaye.com',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
    }
    encode_keyword = str('连衣裙'.encode('GBK')).replace('\\x', '%').replace('\'', '')[1:]
    # r = requests.get('https://s.1688.com/selloffer/offer_search.htm?keywords=%s&n=y' % encode_keyword)
    r = requests.get(url, headers=verify_password_headers, verify=False)
    if r.status_code == 200:
        r.encoding = r.apparent_encoding
        # print('爬取成功！！！')
        print(r.text)
        html = etree.HTML(r.text)
        # for cat_selector in html.xpath(
        #         '//div[@class="s-widget-flatcat sm-widget-row sm-sn-items-control sm-sn-items-count-d fd-clr"]/div[@class="sm-widget-items fd-clr"]/ul/li'):
        #     cat_name = cat_selector.xpath('a/span/text()')[0]

        for list_selector in html.xpath('//div[@class="thread_item"]'):
            detail_url = list_selector.xpath('div/h3/a/@href')[0]
            print(detail_url)
            # if detail_url:
            #     break

            # print(str(cat_name))
    # ip_list = get_ip_list(url)
    # proxies = get_random_ip(ip_list)
    # print(proxies)

