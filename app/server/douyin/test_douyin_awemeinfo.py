import requests
from .util import douyin_util
import json


def get_aweme_info(aweme_id, mid, proxies):
    dytk = douyin_util.get_dytk(aweme_id, mid, '', proxies)
    url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=%s&dytk=%s' % (aweme_id, dytk)
    if proxies:
        res = requests.get(url, verify=False, proxies=proxies)
    else:
        res = requests.get(url, verify=False)
    json_data = json.loads(res.text)
    return json.dumps(json_data['item_list'][0], ensure_ascii=False)


if __name__ == '__main__':
    aweme_id = '6751233447093603588'
    mid = '6751200837449747204'
    # dytk='71cfc9c2cb062d09b18719b96a7733fad2f7673a72cf2fb3238e47b2a09fd448'
    print(get_aweme_info(aweme_id, mid))