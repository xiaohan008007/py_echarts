from douyinapi_5 import DouYinApi


def main():

    api = DouYinApi('210d096b12055ace')

    device_info = api.get_device_info()
    print('get_device_info:' + str(device_info))

    device_id = device_info['device_id']
    iid = device_info['iid']
    uuid = device_info['uuid']
    openudid = device_info['openudid']
    serial_number = device_info['serial_number']
    clientudid = device_info['clientudid']
    sim_serial_number = device_info['sim_serial_number']
    new_user = device_info['new_user']

    print('device_id:' + device_id)
    print('iid:' + iid)
    print('uuid:' + uuid)
    print('openudid:' + openudid)
    print('serial_number:' + serial_number)
    print('clientudid:' + clientudid)
    print('sim_serial_number:' + sim_serial_number)
    print('new_user:' + str(new_user))

    api.init_device_ids(device_id, iid, uuid, openudid, serial_number, clientudid, sim_serial_number)
    api.init_token_id()

    if new_user:
        ret = api.send_xlog("install")
        print('xlog ret:' + api.decrypt_xlog(ret))

    # 获取首页推荐列表
    # feed = api.get_feed()
    # print('get_feed:' + feed)

    # 用户搜索
    # user_search_ret = api.user_search('Zbbya666', 0, 10)
    # print('user_search_ret:' + user_search_ret)


    # 获取对应城市的推荐列表
    # nearby_feed = api.get_nearby_feed('110000')
    # print('get_nearby_feed:' + nearby_feed)
    #
    # # 获取用户信息
    for k in range(0,1):
        user_info = api.get_user_info('16752150320')
        print('get_user_info:' + user_info)
    #
    # # 获取用户作品
    user_post = api.get_user_post('75198486940', 0, 20)
    print('get_user_post:' + user_post)
    #
    # # 获取用户动态
    # user_forwards = api.get_user_forward_list('102388086611', 0, 20)
    # print('get_user_forward_list:' + user_forwards)
    #
    # # 获取用户关注列表
    # user_following_list = api.get_user_following_list('102388086611', 0, 20)
    # print('get_user_following_list:' + user_following_list)
    #
    # # 获取用户粉丝
    # user_follower_list = api.get_user_follower_list('102388086611', 0, 20)
    # print('get_user_follower_list:' + user_follower_list)
    #
    # # 获取热搜榜
    # hot_search_list = api.get_hot_search_list()
    # print('get_hot_search_list:' + hot_search_list)
    #
    # # 获取视频榜
    # hot_video_list = api.get_hot_video_list()
    # print('get_hot_video_list:' + hot_video_list)
    #
    # # 获取音乐榜
    # hot_music_list = api.get_hot_music_list()
    # print('get_hot_music_list:' + hot_music_list)
    #
    # # 获取正能量榜
    # hot_positive_list = api.get_hot_positive_energy_list()
    # print('get_hot_positive_energy_list:' + hot_positive_list)
    #
    # # 获取热门分类列表
    # category_list = api.get_hot_category_list(0, 10)
    # print('get_hot_category_list:' + category_list)
    #
    # 综合搜索
    general_search_ret = api.general_search('lovedesign666', 0, 10)
    print('general_search_ret:' + general_search_ret)
    #
    # # 视频搜索
    # video_search_ret = api.video_search('养生', 0, 10)
    # print('video_search_ret:' + video_search_ret)
    #
    #
    #
    # # 获取评论列表
    # comment_list = api.get_video_comment_list('6619905376009587972', 0, 20)
    # print('get_video_comment_list:' + comment_list)
    #
    # # 获取视频详情
    video_detail = api.get_video_detail('6697520923328728333')
    print('get_video_detail:' + video_detail)
    # #
    # # # 获取音乐详情
    # music_detail = api.get_music_detail('6673679720980269831')
    # print('get_music_detail:' + music_detail)
    #
    # # 获取音乐对应的视频列表
    # music_video_list = api.get_music_videos('6673679720980269831', 0, 20)
    # print('music_video_list:' + music_video_list)
    #
    # if new_user:
    #     ret = api.send_xlog("login")
    #     print('xlog ret:' + api.decrypt_xlog(ret))

    # # 用微博登录
    # #weibo_login_result = api.login_with_weibo('2.00FF2YeCGahxaB8c277e301bpt6XID', '2431503295')
    # weibo_login_result = api.login_with_weibo('2.00mdLhFHGahxaB522593474cHvsVXC', '6497104358')
    # print('login_with_weibo:' + weibo_login_result)
    #
    # uid = json.loads(weibo_login_result)['data']['user_id_str']
    # print('uid:' + uid)

    # # 上传头像
    # upload_avatar_result = api.upload_avatar(uid, "/Users/wangmingxing/test_avatar.png")
    # print('upload_avatar_result:' + upload_avatar_result)
    #
    # avatar_uri = json.loads(upload_avatar_result)['data']['uri']
    # print('avatar_uri:' + avatar_uri)
    #
    # # 设置头像
    # set_avatar_result = api.set_avatar(uid, avatar_uri)
    # print('set_avatar_result:' + set_avatar_result)
    #
    # # 设置昵称
    # set_nickname_result = api.set_nickname(uid, 'lalala632')
    # print('set_nickname_result:' + set_nickname_result)

    # # 发送手机登录验证码
    # send_sms_result = api.send_sms_code('18513929936')
    # print('send_sms_code:' + send_sms_result)

    #
    # sms_code = input('请输入短信验证码：')
    # print('sms_code:' + sms_code)
    #
    # # 用短信验证码登录
    # sms_login_result = api.login_with_sms_code('18513929936', sms_code)
    # print('login_with_sms_code:' + sms_login_result)

    #用QQ登录
    # qq_login_result = api.login_with_qq('7D86EBD1A7B4C90BCA1C48FC955C000C', '22C8BE4F391763C6A1612331131A87C0')
    # print('login_with_qq:' + qq_login_result)

    # 点赞
    # like_result = api.like_the_video('6618062576238464269', 1)
    # print('like_the_video:' + like_result)
    #
    # # 关注
    # follow_result = api.follow_the_user('58372667855', 1)
    # print('follow_the_user:' + follow_result)
    #

    # 评论
    #comment_result = api.comment_the_video('6613563972035546375', 'haha', '叨叨', '61292216068')
    # comment_result = api.comment_the_video('6664927575082634499', '牛逼！')
    # print('comment_the_video:' + comment_result)
    # api.send_xlog("comment")

    # # 用手机号和密码登录
    # passwd_login_result = api.login_with_passwd('18513929936', 'w1234567')
    # print('login_with_passwd:' + passwd_login_result)

    # 获取接口使用情况
    api_access_info = api.get_api_access_info()
    print('api_access_info:' + api_access_info)
import requests
def get_redirect_url():
    url = """https://mclick.simba.taobao.com/cc_im?p=INC.redible&s=936271675&k=705&e=cf5Imw38zyT5LeEXLaoxX6gUJlv1pJiLeYS7ah10x8Plp95OWMW%2BVsso8ajx2qSZMHlKHH3GzaQJHiACcFM5PxMDWFwAo9PcY8S1Kuu7YOyaGIYBEZ9QdoMkKz82auCyNZ8bbUQVevFDzlFKxKHX%2Bp%2B%2FHAxpbvW62yiplFhHxAH%2BawzgNyHhNToiFWC%2FBivB3jGPPFqsRTmgWZf7Jshf%2F3NiXmDmL2WTZIU5wKgaeMLtxOLeyKFscBa2Gk%2FOQhS8QXtTBDucRxBcs%2BVbDLrgv3sZMGT3feX36D97LAShJd9MD5XRvHMkUiZ1X4oJf5e8A6wPbXazQ2BhHsqQJmOwW9ar422dxWmq6T1gXauzR9E6oGhtUAciYbZaIvTFPP5WiT5P4ZqSyXv%2FAAyqVXSIM8XLmjd2EBjqrva4CfegCkInOOBujZnCbYEbowsFHgfR4klATU%2BeMdP8aDAcIpvzCSUcQNNzEWczs6wXvWHBKPJKcRl8kP87KeIj1Nss8uZy6C8bX1UJGOX%2FKSRGD7W4PJ8izCG1Zvrbv1PWRmQ4wv%2B2uMM0StYEtjos6rPV5rBcSkwsiLYYrk1N%2BVEWn%2Fpm2D4q1HyKX658ob7TuonqLw7YJdkISO06Ojpj%2BnSXK0fDqKFI84lIBbCoaWX72cFm8FZSwYoxbzwwrE%2FS4mjROCmofgQh%2BXArHCoRdQ2u3FB%2B"""
    url = "http://v.douyin.com/6orwCF/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    # print(response.headers)
    return response.url

if __name__ == '__main__':


    # print(get_redirect_url())


    main()
# import re
# if __name__ == '__main__':
#    si= "vx:   guerfa103   vb：卟噜噜"
#    matchs =re.findall(r'([WwVvXx❤嶶微胃信交流星 心🌟☎🛰|❤️💕✨✉😘😊Ｖ+➕💗🏥📱⭐]+)[\n:： ️ ，]{1,3}([⃣0-9a-zA-Z_\-@]+)',
#                            si)
#    for match in matchs:
#        if match[0] != '' and len(match[1]) > 5:
#            print(match)
#            # push_total += 1
#            break
