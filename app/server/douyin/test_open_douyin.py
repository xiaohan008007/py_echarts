import requests
import redis
import random
import json
pool = redis.ConnectionPool(host='10.0.0.93', port=6379,db=4)

def decryption_douyin(req_url):
    decryption_url = 'http://43.248.105.223:8999/api/douyin?token=158b3aa279684ad3b2e67a73c79a57c8&url=%s&ck=none' % req_url
    print(decryption_url)
    r = requests.get(decryption_url)
    result = r.text
    print(result)
    return result


def read_redis():
    red = redis.Redis(connection_pool=pool)
    return eval(red.srandmember('android7', 1)[0])


# if __name__ == '__main__':
#     USER_AGENT = 'com.ss.android.ugc.aweme/530 (Linux; U; Android 7.1.2; zh_CN; Redmi 5A; Build/N2G47H; Cronet/58.0.2991.0)'
#     url = 'https://aweme-eagle.snssdk.com/aweme/v1/feed/?type=0&max_cursor=0&min_cursor=-1&count=6&volume=0.0&pull_type=2&need_relieve_aweme=0&filter_warn=0&req_from&is_cold_start=0'
#     #url = 'https://api.amemv.com/aweme/v1/aweme/post/?max_cursor=0&user_id=101402041426&count=20&retry_type=no_retry&mcc_mnc=46007&iid=68233090223&device_id=58109720048&ac=wifi&channel=wandoujia_aweme1&aid=1128&app_name=aweme&version_code=551&version_name=5.5.1&device_platform=android&ssmix=a&device_type=SM-G955N&device_brand=samsung&language=zh&os_api=19&os_version=4.4.2&uuid=99001141779389&openudid=7664f16915f04794&manifest_version_code=551&resolution=1280*720&dpi=240&update_version_code=5512'
#     device_info = read_redis()
#     print(device_info['device_id'])
#     url = url+"&device_id="+device_info['device_id']
#     url = url+"&iid="+device_info['iid']
#     url = url + "&uuid=" + device_info['uuid']
#     url = url + "&openudid=" + device_info['openudid']
#     decryption_info = json.loads(decryption_douyin(url))
#     headers = {'X-Khronos': decryption_info['xkhronos'],
#                'X-Gorgon': decryption_info['xgorgon'],
#                'X-Pods': decryption_info['xpods'],
#                'User-Agent': USER_AGENT
#                }
#     res = requests.get(decryption_info['url'], headers=headers)
#     print(res.text)

if __name__ == '__main__':
    randNum = str(random.randint(1, 99999999))
    device_platform ='ios' + randNum,
    video_id = '6722308029779332359'
    headers = {
        'authority': 'aweme-hl.snssdk.com',
        'method': 'GET',
        'path': '/aweme/v1/aweme/detail/?aweme_id=' + str(video_id) + '&app_name=aweme&aid=1128&device_platform=' + str(device_platform),
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    }
    url = "https://aweme-hl.snssdk.com/aweme/v1/aweme/detail/?aweme_id=" + str(video_id) + "&app_name=aweme&aid=1128&device_platform=" + str(device_platform)
    res = requests.get(url=url, headers=headers, verify=False)
    print(res.text)
    print('9999')
