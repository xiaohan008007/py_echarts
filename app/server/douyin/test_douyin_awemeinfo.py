import requests
from util import douyin_util
import json


def get_aweme_info(aweme_id, mid, proxies):
    dytk, uid, authorName = douyin_util.get_dytk(aweme_id, mid, '', proxies)
    url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=%s&dytk=%s' % (aweme_id, dytk)
    if proxies:
        res = requests.get(url, verify=False, proxies=proxies)
    else:
        res = requests.get(url, verify=False)
    json_data = json.loads(res.text)
    json_data['uid'] = uid
    json_data['authorName'] = authorName
    json_data['aweme_list'] = json_data['item_list']
    del json_data['item_list']
    return json.dumps(json_data, ensure_ascii=False)



headers_video = {
        "Range": "bytes=0-163840",
        "Vpwp-Type": "preloader",
        # "Vpwp-Raw-Key": "v0200f840000bf5svk8ckqbibu1vt8jg_h264_540p",
        "Vpwp-Flag": "0",
        "Accept-Encoding": "identity",
        "Host": "aweme.snssdk.com",
        # "Connection": "Keep-Alive",
        "User-Agent": "okhttp/3.10.0.1"
    }

def getRealPlayAddress(url):
    res = requests.get(url, headers=headers_video, allow_redirects=False)
    if res.status_code == 302:
        long_url = res.headers['Location']
        headers_video['Referer'] = long_url
        return long_url
    return None

def download(video_src):
    vid = video_src.split("?video_id=")[1].split("&")[0]
    dl_url = getRealPlayAddress(video_src)
    r = requests.get(dl_url)
    with open( vid + ".mp4", "wb") as code:
        code.write(r.content)

def get_video_no_watermark(aweme_id, mid, proxies):
    info = json.loads(get_aweme_info(aweme_id, mid, ''))
    url = info["video"]["play_addr"]["url_list"][0]
    return getRealPlayAddress(url)

if __name__ == '__main__':
    aweme_id = '6772102552432430349'
    mid = '6772047033906907911'
    # dytk='71cfc9c2cb062d09b18719b96a7733fad2f7673a72cf2fb3238e47b2a09fd448'
    print(douyin_util.getRealPlayAddress(aweme_id, mid, ''))

