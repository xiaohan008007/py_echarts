import json
import time
import uuid
import random
import base64
from urllib import parse

import requests


class DouYinApi:

    USER_AGENT = 'com.ss.android.ugc.aweme/530 (Linux; U; Android 7.1.2; zh_CN; Redmi 5A; Build/N2G47H; Cronet/58.0.2991.0)'

    COMMON_DEVICE_PARAMS = {
        'retry_type': 'no_retry',
        'app_type': 'normal',
        'ssmix': 'a',
        'mcc_mnc': '46011',
        'ac': 'wifi',
        'channel': 'aweGW',
        'aid': '1128',
        'app_name': 'aweme',
        'version_code': '530',
        'version_name': '5.3.0',
        'device_platform': 'android',
        'device_type': 'Redmi 5A',
        'device_brand': 'Xiaomi',
        'language': 'zh',
        'os_api': '25',
        'os_version': '7.1.2',
        'manifest_version_code': '530',
        'resolution': '720*1280',
        'dpi': '320',
        'update_version_code': '5302',
        'js_sdk_version': '1.10.4',
        'tt_data': 'a'
    }

    URL_BASE = "http://47.105.204.39/douyinapi/"

    def __init__(self, cid):
        """
        :param cid: client id
        """
        self.__cid = cid
        self.__device_id = ''
        self.__iid = ''
        self.__uuid = ''
        self.__openudid = ''
        self.__device_params = {}
        self.__cookie = {}
        self.__serial_number = ''
        self.__openudid = ''
        self.__clientudid = ''
        self.__sim_serial_number = ''
        self.__token_id = ''

    def get_api_access_info(self):
        """获取接口使用情况
        :return:
        """
        querys = {
            'cid': self.__cid
        }

        response = requests.get(DouYinApi.URL_BASE + "getApiAccessInfo?" + parse.urlencode(querys))
        return response.text

    def init_device_ids(self, device_id, iid, uuid, openudid, serial_number, clientudid, sim_serial_number):
        """ 初始化设备id参数
        :param device_id 设备ID
        :param iid install id
        :param uuid imei
        :param openudid
        """
        self.__device_id = device_id
        self.__iid = iid
        self.__uuid = uuid
        self.__openudid = openudid
        self.__serial_number = serial_number
        self.__clientudid = clientudid
        self.__sim_serial_number = sim_serial_number

        device_ids = {
            'device_id': device_id,
            'iid': iid,
            'uuid': uuid,
            'openudid': openudid
        }
        self.__device_params = self.COMMON_DEVICE_PARAMS.copy()
        self.__device_params.update(device_ids)

    def get_device_info(self):
        """获取设备信息
        :return:
        """
        serial_number = str(uuid.uuid1())[-12:]
        openudid = '7664' + str(uuid.uuid1())[-12:]
        clientudid = str(uuid.uuid1())
        device_id = '661' + self.__get_random(8)
        _uuid = '99' + self.__get_random(12)
        sim_serial_number = '89861' + self.__get_random(15)

        register_info = {
            "magic_tag": "ss_app_log",
            "header": {
                "display_name": "抖音短视频",
                "update_version_code": int(self.COMMON_DEVICE_PARAMS['update_version_code']),
                "manifest_version_code": int(self.COMMON_DEVICE_PARAMS['manifest_version_code']),
                "aid": int(self.COMMON_DEVICE_PARAMS['aid']),
                "channel": self.COMMON_DEVICE_PARAMS['channel'],
                "appkey": "57bfa27c67e58e7d920028d3",
                "package": "com.ss.android.ugc.aweme",
                "app_version": self.COMMON_DEVICE_PARAMS['version_name'],
                "version_code": int(self.COMMON_DEVICE_PARAMS['version_code']),
                "sdk_version": "2.5.5.8",
                "os": "Android",
                "os_version": self.COMMON_DEVICE_PARAMS['os_version'],
                "os_api": int(self.COMMON_DEVICE_PARAMS['os_api']),
                "device_model": self.COMMON_DEVICE_PARAMS['device_type'],
                "device_brand": self.COMMON_DEVICE_PARAMS['device_brand'],
                "device_manufacturer": self.COMMON_DEVICE_PARAMS['device_brand'],
                "cpu_abi": "armeabi-v7a",
                "build_serial": serial_number,
                "release_build": "1337f79_20190228",
                "density_dpi": int(self.COMMON_DEVICE_PARAMS['dpi']),
                "display_density": "xhdpi",
                "resolution": "1280x720",
                "language": "zh",
                "mc": "02:00:00:00:00:00",
                "timezone": 8,
                "access": "4g",
                "not_request_sender": 0,
                "carrier": "中国电信",
                "mcc_mnc": "46011",
                "rom": "MIUI-V9.6.2.0.NCKCNFD",
                "rom_version": "miui_V9_V9.6.2.0.NCKCNFD",
                "sig_hash": "aea615ab910015038f73c47e45d21466",
                "device_id": device_id,
                "openudid": openudid,
                "udid": _uuid,
                "clientudid": clientudid,
                "serial_number": serial_number,
                "sim_serial_number": [
                    {
                        "sim_serial_number": sim_serial_number
                    }
                ],
                "region": "CN",
                "tz_name": "Asia/Shanghai",
                "tz_offset": 28800,
                "sim_region": "cn"
            },
            "_gen_time": int(round(time.time() * 1000))
        }

        register_body = self.encrypt_tt(json.dumps(register_info))
        params = {
            'uuid': _uuid,
            'openudid': openudid,
            '_rticket': str(int(round(time.time() * 1000)))
        }

        params.update(self.COMMON_DEVICE_PARAMS)
        device_register_url = 'https://log.snssdk.com/service/2/device_register/?' + parse.urlencode(params)

        sign_params = {
            'url': device_register_url,
            'nosign': '1'
        }

        sign = json.loads(requests.post(self.__get_sign_url(), data=sign_params, headers={}).text)
        if 'ret' in sign and sign['ret'] == -1:
            print(sign)
            exit()

        headers = {
            'User-Agent': DouYinApi.USER_AGENT,
            'X-Khronos': sign['xkhronos'],
            'X-Gorgon': sign['xgorgon'],
            'X-Pods': sign['xpods']
        }

        resp = json.loads(requests.post(device_register_url, data=register_body, headers=headers).text)
        ids = {
            'device_id': str(resp['device_id']),
            'iid': str(resp['install_id']),
            'uuid': _uuid,
            'openudid': openudid,
            'serial_number': serial_number,
            'clientudid': clientudid,
            'sim_serial_number': sim_serial_number,
            'new_user': resp['new_user']
        }
        return ids

    def init_token_id(self):
        """ 初始化token_id， xlog用
        :return:
        """
        content = {
            "k0": "JDRbRqkWbSN5ILxz+Uc7f+DF/0DcGd7eTxvVdhWFdXxi2fA0LB7KZv0xYC3j3Lzp5nTqBqI4Qu/W9R4iPeh49E6p18iKn8o=",
            "k6": "",
            "k7": "",
            "k8": "",
            "k5": self.__uuid,
            "k1": self.__openudid,
            "k9": self.__serial_number,
            "k2": self.COMMON_DEVICE_PARAMS['device_brand'],
            "k4": self.COMMON_DEVICE_PARAMS['device_type'],
            "k3": self.COMMON_DEVICE_PARAMS['device_brand'],
            "k12": "N2G47H",
            "k17": "Xiaomi/riva/riva:7.1.2/N2G47H/V9.6.2.0.NCKCNFD:user/release-keys",
            "k11": self.COMMON_DEVICE_PARAMS['os_version'],
            "k16": "1529574654",
            "k18": "Linux 3.18.31-perf-g26ceb89 armv8l localdomain localhost #1 SMP PREEMPT Thu Jun 21 18:00:23 CST 2018",
            "k10": int(self.COMMON_DEVICE_PARAMS['os_api']),
            "k14": "10390511616",
            "k15": "10390511616",
            "k13": "1901676",
            "k19": 0,
            "k20": 0,
            "k21": 0,
            "k22": {
                "env": 3,
                "en": {
                    "sig": 0,
                    "cb": 10,
                    "cid": 0,
                    "br": "",
                    "file": [

                    ],
                    "prop": [

                    ]
                }
            }
        }

        encrypted_body = self.encrypt_xlog(json.dumps(content))
        params = {
            'app_id': self.COMMON_DEVICE_PARAMS['aid'],
            'version_code': '2',
            'time': str(int(round(time.time() * 1000))),
            'version': '1.0.0'
        }

        url = 'https://sdfp.snssdk.com/v1/getInfo?' + parse.urlencode(params)
        resp = requests.post(url, data=encrypted_body).text
        print(resp)
        self.__token_id = json.loads(resp)['token_id']

    def send_xlog(self, action):
        """ send xlog
        :param action: install/login/comment
        :return:
        """
        grilock = {
            "os": "Android",
            "version": "1.0.0",
            "token_id": self.__token_id,
            "code": 102
        }

        xlog = {
            "dpod": {
                "pod": ""
            },
            "p1": self.__device_id,
            "p2": self.__iid,
            "ut": 8124,
            "ait": 1553503111,
            "pkg": "com.ss.android.ugc.aweme",
            "fp": "Xiaomi/riva/riva:7.1.2/N2G47H/V9.6.2.0.NCKCNFD:user/release-keys",
            "vc": int(self.COMMON_DEVICE_PARAMS['version_code']),
            "vpn": 0,
            "wifisid": "<unknown ssid>",
            "wifimac": "",
            "wifip": "0.0.0.0",
            "aplist": [

            ],
            "route": {
                "iip": "",
                "gip": "",
                "ghw": "",
                "type": ""
            },
            "location": "",
            "apps": [

            ],
            "mdi_if": {
                "ui": "8" + self.__uuid,
                "mc": "02:00:00:00:00:00",
                "mid": "3757e51db14ea1f74707bd7746f6" + self.__serial_number,
                "ts": 1548519571390
            },
            "extra": action,
            "hw": {
                "brand": self.COMMON_DEVICE_PARAMS['device_brand'],
                "model": self.COMMON_DEVICE_PARAMS['device_type'],
                "board": "QC_Reference_Phone",
                "device": "riva",
                "product": "riva",
                "display": "720*1280",
                "dpi": int(self.COMMON_DEVICE_PARAMS['dpi']),
                "bat": 0,
                "cpu": {
                    "core": 4,
                    "hw": "Qualcomm Technologies, Inc MSM8917",
                    "max": "1401000",
                    "min": "960000",
                    "ft": "half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt lpae evtstrm aes pmull sha1 sha2 crc32"
                },
                "mem": {
                    "ram": "1947316224",
                    "rom": "10390511616"
                }
            },
            "id": {
                "i": int(self.COMMON_DEVICE_PARAMS['os_api']),
                "r": self.COMMON_DEVICE_PARAMS['os_version'],
                "imei": self.__uuid,
                "imsi": "4" + self.__uuid,
                "adid": self.__openudid,
                "adid_ex": self.__openudid,
                "mac": "",
                "serial": self.__serial_number
            },
            "emulator": {
                "sig": 0,
                "cb": 10,
                "cid": 0,
                "br": "",
                "file": [

                ],
                "prop": [

                ]
            },
            "env": {
                "ver": "0.6.01.03",
                "tag": "default",
                "pkg": "com.ss.android.ugc.aweme",
                "tz": "GMT+08:00",
                "ml": "zh_CN",
                "uid": 10223,
                "rebuild": -1,
                "jd": 0,
                "dbg": 0,
                "tid": 0,
                "xposed": 0,
                "hk": [

                ],
                "su": 0,
                "sp": "",
                "ro.secure_s": "1",
                "ro.debuggable_s": "0",
                "click": "",
                "hph": "",
                "hpp": "",
                "mc": 2454853734,
                "fc": 946933748,
                "jexp": 0,
                "frida": 0,
                "cydia": 0,
                "vapp": ""
            },
            "extension": {
                "bt": -1,
                "notify": 1258375024,
                "sign": "NA",
                "bytes64": "AT7vnWUeTiCN0kUm+UVuvssVgkW2uH1GmXAOCeaCia5BVgSy80D5ID5UbH6x6xcSHsdjXqljImqg/LxoSbAeyqYZ67ZUTE23KmeyzHjTOeTtrAZ7xAQoclOl66ocIC0IuGprBuiVYAODz/HXtrx7kpnXUUgoCNZD+vFye2tW15m1wtzrW6g+WC5Z3Ad7VcBPoDjr2bIfcy/tNgiLOpJHbPUfILwWn4vyoXVFXFalV8ijYiakfOj8OF0Yp11Yl50Kyn24ALPu+7+VCfzpN1L9hzkxc7Rfwuws4KDObWrG3P3vbS6oG9VBSppHi8H2jvQIHixGCdICvABAFrt+1Qoaj7idJNwEEAvfvhLLUNIC3xj11W/WpVZ6nYwig4HqNol5p1aW3f9UAQUUnbhf/ESqqmD7onHa8I2sgQnIec61CsagRu/5mhoiXFHQqMZOwKV2VWK/P1sH6RZDN2awx/FBwbBtiTO6WKUC1/gCfufaVvvkgzd4+F+I2SD/ycrlh72rLMw8M/2TDmbgRevf/i6B6cAaK6VSWGLVuNLDCvieM1jES7JlR1suSH3OCxIqI67RxxEzSc01fF87Ybmfb/6P3ey8/cos67/fqbcr52G3+j4oY818tVXixXeTOg5lfBPa7YoIycNuCxCD20z/h6iohVyuR7MLDHdRK3mLLgg2CoPu3KddXCaxtIU79Oa3X7H2675ERFxEtuZE"
            },
            "rl": {

            },
            "ssp": {

            },
            "grilock": str(base64.b64encode(bytes(json.dumps(grilock), 'utf-8')))
        }

        headers = {
            'User-Agent': DouYinApi.USER_AGENT,
        }

        params = {
            'os': '0',
            'ver': '0.6.01.03',
            'm': '1',
            'app_ver': self.COMMON_DEVICE_PARAMS['version_name'],
            'region': 'CN',
            'aid': self.COMMON_DEVICE_PARAMS['aid'],
            'did': self.__device_id
        }

        url = 'https://xlog.snssdk.com/v2/r?' + parse.urlencode(params)
        return requests.post(url, headers=headers, data=self.encrypt_xlog(json.dumps(xlog))).content

    def get_feed(self):
        """获取首页推荐列表
        """
        douyin_url = 'https://aweme-eagle.snssdk.com/aweme/v1/feed/?type=0&max_cursor=0&min_cursor=-1&count=6&volume=0.0&pull_type=2&need_relieve_aweme=0&filter_warn=0&req_from&is_cold_start=0'
        return self.__http_get(self.__make_get_url(douyin_url))

    def get_nearby_feed(self, city_id):
        """获取对应城市的推荐列表
        :param cityid: 城市代码, 从https://wenku.baidu.com/view/af4281bafd0a79563c1e7287.html获取
        :return:
        """
        params = {
            'city': city_id,
        }

        douyin_url = 'https://api.amemv.com/aweme/v1/nearby/feed/?max_cursor=0&min_cursor=0&count=20&feed_style=1&filter_warn=0&poi_class_code=0'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def get_user_info(self, user_id):
        """获取用户信息
        :param user_id: 用户ID
        :return:
        """
        params = {
            'user_id': user_id
        }

        douyin_url = 'https://aweme-eagle.snssdk.com/aweme/v1/user/?'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def get_user_post(self, user_id, max_cursor, count):
        """获取用户作品
        :param user_id: 用户ID
        :param max_cursor: 用于分页，第1页是0，后1页是上1页请求的时候返回的max_cursor
        :param count: 返回视频的条数
        :return:
        """
        params = {
            'user_id': user_id,
            'max_cursor': str(max_cursor),
            'count': str(count)
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/aweme/post/'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def get_user_forward_list(self, user_id, max_cursor, count):
        """获取用户动态
        :param user_id: 用户ID
        :param max_cursor: 用于分页，第1页是0，后1页是上1页请求的时候返回的max_cursor
        :param count: 每次返回的动态条数
        :return:
        """
        params = {
            'user_id': user_id,
            'max_cursor': str(max_cursor),
            'count': str(count)
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/forward/list/'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def get_user_following_list(self, user_id, max_time, count):
        """获取用户关注列表 注意：关注列表请求太频繁会导致不返回数据
        :param user_id: 用户ID
        :param max_time: 用于分页，第1页是0，后1页是上1页请求时返回的max_time
        :param count: 每次返回的条数
        :return:
        """
        params = {
            'user_id': user_id,
            'max_time': str(int(time.time()) if max_time == 0 else max_time),
            'count': str(count)
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/user/following/list/'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def get_user_follower_list(self, user_id, max_time, count):
        """获取用户粉丝列表
        :param user_id: 用户ID
        :param max_time: 用于分页，第1页是0，后1页是上1页请求时返回的min_time
        :param count: 每次返回的条数
        :return:
        """
        params = {
            'user_id': user_id,
            'max_time': str(int(time.time()) if max_time == 0 else max_time),
            'count': str(count)
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/user/follower/list/'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def get_hot_search_list(self):
        """获取抖音热搜榜
        :return:
        """
        douyin_url = 'https://api.amemv.com/aweme/v1/hot/search/list/?detail_list=1'
        return self.__http_get(self.__make_get_url(douyin_url))

    def get_hot_video_list(self):
        """获取抖音视频榜
        :return:
        """
        douyin_url = 'https://aweme.snssdk.com/aweme/v1/hotsearch/aweme/billboard/'
        return self.__http_get(self.__make_get_url(douyin_url))

    def get_hot_music_list(self):
        """获取抖音音乐榜
        :return:
        """
        douyin_url = 'https://aweme.snssdk.com/aweme/v1/hotsearch/music/billboard/'
        return self.__http_get(self.__make_get_url(douyin_url))

    def get_hot_positive_energy_list(self):
        """获取抖音正能量榜
        :return:
        """
        douyin_url = 'https://aweme.snssdk.com/aweme/v1/hotsearch/positive_energy/billboard/'
        return self.__http_get(self.__make_get_url(douyin_url))

    def get_hot_category_list(self, cursor, count):
        """获取热门分类列表
        :param cursor: 分页用，第1页是0，下一页是上1页请求返回的cursor
        :param count: 每次返回的条数
        :return:
        """
        params = {
            'cursor': str(cursor),
            'count': str(count)
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/category/list/'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def general_search(self, keyword, offset, count):
        """综合搜索
        :param keyword: 关键词
        :param offset: 分页，第1页是0，下1页是上1页请求返回的cursor
        :param count: 每次返回的条数
        :return:
        """
        params = {
            'keyword': keyword,
            'offset': str(offset),
            'count': str(count),
            'is_pull_refresh': '0',
            'hot_search': '0',
            'latitude': '0.0',
            'longitude': '0.0'
        }

        douyin_url = 'https://aweme-hl.snssdk.com/aweme/v1/general/search/single/?'
        return self.__http_post(self.__make_post_url(douyin_url, params), params)

    def video_search(self, keyword, offset, count):
        """ 视频搜索
        :param keyword: 关键词
        :param offset: 分页，第1页是0，下1页是上1页请求返回的cursor
        :param count: 每次返回的条数
        :return:
        """
        params = {
            'keyword': keyword,
            'offset': str(offset),
            'count': str(count),
            'is_pull_refresh': '0',
            'hot_search': '0',
            'source': 'video_search'
        }

        douyin_url = 'https://aweme-hl.snssdk.com/aweme/v1/search/item/?'
        return self.__http_post(self.__make_post_url(douyin_url, params), params)

    def user_search(self, keyword, offset, count):
        """ 用户搜索
        :param keyword: 关键词
        :param offset: 分页，第1页是0，下1页是上1页请求返回的cursor
        :param count: 每次返回的条数
        :return:
        """
        params = {
            'keyword': keyword,
            'cursor': str(offset),
            'count': str(count),
            'type': '1',
            'is_pull_refresh': '0',
            'hot_search': '0',
            'source': ''
        }

        douyin_url = 'https://aweme-hl.snssdk.com/aweme/v1/discover/search/?'
        return self.__http_post(self.__make_post_url(douyin_url, params), params)

    def get_video_comment_list(self, aweme_id, cursor, count):
        """获取视频评论列表
        :param awemeId: 视频ID
        :param cursor: 分页, 第1页是0, 下1页是上1页请求返回的cursor
        :param count: 每次返回的条数
        :return:
        """
        params = {
            'aweme_id': aweme_id,
            'cursor': str(cursor),
            'count': str(count)
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v2/comment/list/'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def get_video_detail(self, aweme_id):
        """获取视频详情
        :param aweme_id: 视频ID
        :return:
        """
        params = {
            'aweme_id': aweme_id
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/aweme/detail/'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def get_music_detail(self, music_id):
        """获取音乐详情
        :param music_id: 音乐id
        :return:
        """
        params = {
            'music_id': str(music_id),
            'click_reason': '0'
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/music/detail/'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def get_music_videos(self, music_id, cursor, count):
        """获取音乐对应的视频列表
        :param music_id: 音乐id
        :param cursor: 分页，首页是0，下一页是上一页请求返回的cursor
        :param count: 每次返回的视频条数
        :return:
        """
        params = {
            'music_id': str(music_id),
            'cursor': str(cursor),
            'count': str(count),
            'type': '6'
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/music/aweme/'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def login_with_qq(self, access_token, uid):
        """用QQ登录
        :param access_token: 抓包获取
        :param uid: 抓包获取
        :return:
        """
        params = {
            'access_token': access_token,
            'expires_in': str(7776000),
            'uid': uid
        }

        douyin_url = 'https://iu.snssdk.com/passport/auth/login/?platform=qzone_sns'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def login_with_weibo(self, access_token, uid):
        """用微博登录
        :param access_token: 抓包获取
        :param uid: 抓包获取
        :return:
        """
        params = {
            'access_token': access_token,
            'expires_in': str(int(time.time() + 30 * 24 * 60 * 60)),
            'uid': uid
        }

        douyin_url = 'https://iu.snssdk.com/passport/auth/login/?platform=sina_weibo'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def send_sms_code(self, phone_num):
        """发送手机登录验证码
        :param phone_num: 接收验证码的手机号, 11位
        :return:
        """
        form_params = {
            'type': '3731',
            'mix_mode': '1',
            'mobile': self.encrypt_phone_num(phone_num),
            'auto_read': '0',
            'unbind_exist': '35',
            'account_sdk_source': 'app'
        }

        douyin_url = 'https://iu.snssdk.com/passport/mobile/send_code/v1/?account_sdk_version=350'
        return self.__http_post(self.__make_post_url(douyin_url, form_params), form_params)

    def login_with_sms_code(self, phone_num, code):
        """用手机短信验证码登录
        :param phone_num: 11位手机号
        :param code: 短信验证码
        :return:
        """
        form_params = {
            'code': self.encrypt_param(code),
            'mobile': self.encrypt_phone_num(phone_num),
            'mix_mode': '1',
            'captcha': ''
        }

        douyin_url = 'https://iu.snssdk.com/passport/mobile/sms_login/'
        return self.__http_post(self.__make_post_url(douyin_url, form_params), form_params)

    def login_with_passwd(self, phone_num, passwd, captcha=''):
        """密码登录
        :param phone_num: 11位手机号
        :param passwd: 密码
        :param captcha: 图片验证码
        :return:
        """
        form_params = {
            'mobile': self.encrypt_phone_num(phone_num),
            'mix_mode': '1',
            'password': self.encrypt_param(passwd),
            'captcha': str(captcha)
        }

        douyin_url = 'https://is.snssdk.com/passport/mobile/login/'
        return self.__http_post(self.__make_post_url(douyin_url, form_params), form_params)

    def like_the_video(self, aweme_id, types):
        """视频点赞, 需要先登录
        :param aweme_id: 视频ID
        :param types: 0 取消点赞， 1 点赞
        :return:
        """
        params = {
            'aweme_id': aweme_id,
            'type': str(types),
            'channel_id': '0'
        }

        douyin_url = 'https://aweme-hl.snssdk.com/aweme/v1/commit/item/digg/?'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def follow_the_user(self, user_id, types):
        """关注用户,需要先登录
        :param user_id: 要关注的用户ID
        :param types: 0 取消关注， 1 关注
        :return:
        """
        params = {
            'user_id': user_id,
            'type': str(types),
            'channel_id': '0',
            'from': '0'
        }

        douyin_url = 'https://aweme-hl.snssdk.com/aweme/v1/commit/follow/user/?'
        return self.__http_get(self.__make_get_url(douyin_url, params))

    def comment_the_video(self, aweme_id, comment, at_user_name='', at_user_id=''):
        """评论视频 需要先登录
        :param aweme_id: 视频ID
        :param comment: 评论内容
        :param at_user_name 关注用户的名字
        :param at_user_id 关注用户id
        :return:
        """
        text_extra = []
        if at_user_name and at_user_id:
            text_extra = [{
                'at_user_type': '',
                'end': len(at_user_name) + 2,
                'start': 0,
                'type': 0,
                'user_id': at_user_id
            }]
            comment = '@' + at_user_name + ' ' + comment

        form_params = {
            'aweme_id': aweme_id,
            'text': comment,
            'text_extra': json.dumps(text_extra),
            'is_self_see': '0',
            'channel_id': '0'
        }

        douyin_url = 'https://aweme-hl.snssdk.com/aweme/v1/comment/publish/'
        return self.__http_post(self.__make_post_url(douyin_url, form_params), form_params)

    def encrypt_phone_num(self, phone_num):
        """加密手机号码
        :param phone_num: 手机号码（eg:13501336789）
        :return:
        """
        resp = requests.get(DouYinApi.URL_BASE + 'encryptPhoneNum?' + 'phone_num=' + phone_num)
        return self.__get_msg(resp)

    def encrypt_param(self, param):
        """加密验证码
        :param param:
        :return:
        """
        resp = requests.get(DouYinApi.URL_BASE + 'encryptParam?' + 'param=' + param)
        return self.__get_msg(resp)

    def encrypt_xlog(self, xlog):
        """加密xlog
        :param xlog: xlog内容
        :return:
        """
        querys = {
            'cid': self.__cid
        }

        url = DouYinApi.URL_BASE + 'encryptXlog?' + parse.urlencode(querys)
        return requests.post(url, data=xlog, headers={}).content

    def encrypt_tt(self, tt):
        """加密device register info或者app log
        :param tt:
        :return:
        """
        querys = {
            'cid': self.__cid
        }

        url = DouYinApi.URL_BASE + 'encryptTT?' + parse.urlencode(querys)
        return requests.post(url, data=tt, headers={}).content

    def decrypt_xlog(self, xlog):
        """解密xlog
        :param xlog: 加密的xlog内容
        :return:
        """
        querys = {
            'cid': self.__cid
        }

        url = DouYinApi.URL_BASE + 'decryptXlog?' + parse.urlencode(querys)
        return requests.post(url, data=xlog, headers={}).text

    def upload_avatar(self, uid, avatar_file):
        """上传头像
        :param uid: 用户uid
        :param avatar_file: 头像(png格式，分辨率为720*720，位深8)
        :return:
        """
        files = {
            'file': ('profileHeaderCrop.png', open(avatar_file, 'rb'), 'application/octet-stream', {'Expires': '0'})
        }

        params = {
            'uid': uid,
            '_rticket': str(int(round(time.time() * 1000)))
        }
        params.update(self.COMMON_DEVICE_PARAMS)

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/upload/image/?' + parse.urlencode(params)
        sign_params = {
            'url': douyin_url,
            'cookie': self.__cookie,
            'nosign': 1
        }

        sign_url = self.__get_sign_url()
        signatue = requests.post(sign_url, data=sign_params, headers={}).text
        sign = json.loads(signatue)

        headers = {
            'User-Agent': DouYinApi.USER_AGENT,
            'X-Khronos': sign['xkhronos'],
            'X-Gorgon': sign['xgorgon'],
            'X-Pods': sign['xpods']
        }
        return requests.post(douyin_url, files=files, headers=headers, cookies=self.__cookie).text

    def set_avatar(self, uid, avatar_uri):
        """设置头像
        :param uid: 用户id
        :param avatar_uri: 头像uri, 由upload_avatar返回
        :return:
        """
        form_params = {
            'uid': uid,
            'avatar_uri': avatar_uri
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/commit/user/'
        return self.__http_post(self.__make_post_url(douyin_url, form_params), form_params)

    def set_nickname(self, uid, nickname):
        """设置昵称
        :param uid: 用户id
        :param nickname: 昵称
        :return:
        """
        form_params = {
            'uid': uid,
            'nickname': nickname
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/commit/user/'
        return self.__http_post(self.__make_post_url(douyin_url, form_params), form_params)

    def set_signature(self, uid, signature):
        """ 设置签名
        :param uid: 用户id
        :param signature: 签名
        :return:
        """
        form_params = {
            'uid': uid,
            'signature': signature
        }

        douyin_url = 'https://aweme.snssdk.com/aweme/v1/commit/user/'
        return self.__http_post(self.__make_post_url(douyin_url, form_params), form_params)

    def __get_random(self, len):
        return ''.join(str(random.choice(range(10))) for _ in range(len))

    def __get_msg(self, resp):
        return json.loads(resp.text)['msg']

    def __add_other_params(self, douyin_url, params={}):
        if not douyin_url.__contains__('?'):
            douyin_url = douyin_url + '?'

        common_params = parse.urlencode(self.__device_params)
        if douyin_url.endswith('?') or douyin_url.endswith('&'):
            douyin_url = douyin_url + common_params
        else:
            douyin_url = douyin_url + '&' + common_params

        if len(params) > 0:
            douyin_url = douyin_url + '&' + parse.urlencode(params)
        douyin_url = douyin_url + "&_rticket=" + str(int(round(time.time() * 1000))) + "&ts=" + str(int(time.time()))
        return douyin_url

    def __get_sign_url(self):
        querys = {
            'cid': self.__cid
        }

        sign_url = DouYinApi.URL_BASE + 'getSignature?' + parse.urlencode(querys)
        return sign_url

    def __make_get_url(self, douyin_url, params={}):
        douyin_url = self.__add_other_params(douyin_url, params)
        sign_url = self.__get_sign_url()
        form_params = {
            'url': douyin_url,
            'cookie': self.__cookie
        }
        signature = requests.post(sign_url, data=form_params, headers={}).text
        sign = json.loads(signature)
        return self.__make_sign_url(douyin_url, sign)

    def __make_post_url(self, douyin_url, form_params):
        douyin_url = self.__add_other_params(douyin_url)
        sign_url = self.__get_sign_url()
        params = form_params.copy()
        params['url'] = douyin_url
        params['cookie'] = self.__cookie
        signature = requests.post(sign_url, data=params, headers={}).text
        sign = json.loads(signature)
        return self.__make_sign_url(douyin_url, sign)

    def __make_sign_url(self, douyin_url, sign):
        if 'as' not in sign:
            print(sign)
            return douyin_url

        as_param = sign['as']
        cp_param = sign['cp']
        mas_param = sign['mas']
        self.__xkhronos = sign['xkhronos']
        self.__xgorgon = sign['xgorgon']
        self.__xpods = sign['xpods']
        return douyin_url + '&as=' + as_param + '&cp=' + cp_param + '&mas=' + mas_param

    def __http_get(self, url):
        headers = {
            'User-Agent': DouYinApi.USER_AGENT,
            'X-Khronos': self.__xkhronos,
            'X-Gorgon': self.__xgorgon,
            'X-Pods': self.__xpods
        }

        resp = requests.get(url, headers=headers, cookies=self.__cookie)
        if len(self.__cookie) == 0 or resp.cookies.get_dict().__contains__('sessionid'):
            self.__cookie = resp.cookies.get_dict()
        return resp.text

    def __http_post(self, url, form_params):
        headers = {
            'User-Agent': DouYinApi.USER_AGENT,
            'X-Khronos': self.__xkhronos,
            'X-Gorgon': self.__xgorgon,
            'X-Pods': self.__xpods
        }

        resp = requests.post(url, headers=headers, data=form_params, cookies=self.__cookie, allow_redirects=False)
        if len(self.__cookie) == 0 or resp.cookies.get_dict().__contains__('sessionid'):
            self.__cookie = resp.cookies.get_dict()
        if resp.status_code == 307:
            return self.__http_post(resp.headers['Location'], form_params)
        return resp.text








