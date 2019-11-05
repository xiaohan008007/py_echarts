import requests
import re
import json
import codecs
import os
import time
from .util import douyin_util


def get_aweme_list(s, uid, max_cursor, sign, dytk, proxies):
    url = 'https://www.douyin.com/web/api/v2/aweme/post/?user_id=%s&sec_uid=&count=21&max_cursor=%s&aid=1128&_signature=%s&dytk=%s' %(uid, max_cursor, sign, dytk)
    header = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'referer': 'https://www.douyin.com/share/user/%s' % uid,
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1'
    }
    # header['cookie'] = '_ba=BA0.2-20190326-5199e-930dCDjV6al6oNlc2MxL; _ga=GA1.2.2028148563.1553573854;_gid=GA1.2.240070870.1571821079'

    # print(url)
    if proxies:
        res = s.get(url, headers=header, proxies=proxies, verify=False)
    else:
        res = s.get(url, headers=header, verify=False)
    return res.text


def create(file_name):
    if not os.path.exists(file_name):
        f = open(file_name, 'w')

        f.close()
        print(file_name + " created.")
    else:
        os.remove(file_name)
        create(file_name)
    return


def spider_aweme_list(uid, aweme_id, proxies):
    s = requests.session()
    # create('aweme_%s.txt' % uid)
    aweme_list = []

    spider_info = {'page': 0, 'max_sp_page': 5, 'total_sp_times': 0}
    the_aweme = {}
    sign = douyin_util.get_sign(uid)
    dytk = douyin_util.get_dytk('', '', uid, proxies)
    fetch_page(aweme_list, spider_info, s, uid, 0, sign, dytk, aweme_id, proxies)

    # f_page = codecs.open('aweme_%s.txt' % uid, 'a+', 'utf-8')

    if aweme_id:
        for aweme in aweme_list:
            if aweme['aweme_id'] == aweme_id:
                the_aweme = aweme
                break

        content = json.dumps(the_aweme, ensure_ascii=False)
    else:
        content = json.dumps(aweme_list, ensure_ascii=False)

    # f_page.write(content)
    # f_page.write("\n")
    # f_page.close()

    print('total aweme:%s' % len(aweme_list))

    result = {}
    result['total'] = len(aweme_list)
    result['sp_info'] = spider_info
    if aweme_id:
        result['aweme_info'] = the_aweme
    else:
        result['aweme_list'] = aweme_list
    return json.dumps(result, ensure_ascii=False)

def fetch_page(aweme_list, spider_info, s, uid, max_cursor, sign, dytk, aweme_id, proxies):
    times = 0
    total_aweme = 0


    while True:
        times += 1
        spider_info['total_sp_times'] += 1
        print(times)
        result = get_aweme_list(s, uid, max_cursor, sign, dytk, proxies)
        json_data = json.loads(result)
        if json_data['aweme_list']:
            spider_info['page'] += 1
            aweme_list += json_data['aweme_list']
            total_aweme += len(json_data['aweme_list'])
            content = json.dumps(json_data, ensure_ascii=False)
            print(content)
            if aweme_id and content.find(aweme_id) > -1:
                break
                # max page :8
            if spider_info['page'] >= spider_info['max_sp_page']:
                break

            if json_data['has_more']:
                print("========")
                print(json_data['has_more'])
                max_cursor = json_data['max_cursor']
                fetch_page(aweme_list, spider_info, s, uid, max_cursor, sign, dytk, aweme_id, proxies)

            break
    print(total_aweme)




if __name__ == '__main__':

    tic = time.time()


    # uid = '81939158402'
    uid = '88166986029'
    # aweme_id = '6751993255207931143'
    aweme_id = ''




    spider_aweme_list(uid, aweme_id, '')
    toc = time.time()
    print(toc - tic)
        # result = get_aweme_list(s, uid, max_cursor, sign, dytk)
        # json_data = json.loads(result)
        # if json_data['aweme_list']:
        #
        #     print(json.dumps(json_data, ensure_ascii=False))
        #     break
