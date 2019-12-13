from douyinapi8x import DouYinApi
import json
import base64


def main():

    api = DouYinApi('e1fbcf46b2a66597')

    # # device_info = api.register_device('69321125820', '83614046676', '752307a4acd45a0e', '826057530977717')
    # device_info = api.register_device()
    # print('get_device_info:' + str(device_info))
    # return
    #
    # device_id = device_info['device_id']
    # iid = device_info['iid']
    # uuid = device_info['uuid']
    # openudid = device_info['openudid']
    # new_user = device_info['new_user']
    #
    #
    # print('device_id:' + device_id)
    # print('iid:' + iid)
    # print('uuid:' + uuid)
    # print('openudid:' + openudid)
    # print('new_user:' + str(new_user))

    # device_id = '13395663189'
    # iid = '89509767143'
    # uuid = '869437023110566'
    # openudid = 'f85db56bed303289'

    # device_id = '69753491360'
    # iid = '89736073150'
    # uuid = '869876084971619'
    # openudid = 'fa23fbb9db9295f7'

    # device_id = '69753491368'
    # iid = '89738007819'
    # uuid = '869209123716133'
    # openudid = 'fa2364d2b3f6c2aa'

    # device_id = '69753738362'
    # iid = '89739172258'
    # uuid = '869774532313172'
    # openudid = 'fa23c0ebbc2482a1'

    # device_id = '69753832724'
    # iid = '89740342867'
    # uuid = '869962473300954'
    # openudid = 'fa232e97ebba4ddf'

    # device_id = '69753790285'
    # iid = '89739839528'
    # uuid = '869374285974211'
    # openudid = 'fa2314635bc32fd0'

    device_id = '68321684974'
    iid = '89739118707'
    uuid = '869419834103754'
    openudid = 'fa23b26e0af60311'

    api.init_device_ids(device_id, iid, uuid, openudid)

    # 获取首页推荐列表
    # feed = api.get_feed()
    # print('get_feed:' + feed)

    # 获取分享链接的视频信息
    # video_detail = api.get_share_video_detail('http://v.douyin.com/UyrYGY/')
    # print(video_detail)

    # 获取对应城市的推荐列表
    # nearby_feed = api.get_nearby_feed('110000')
    # print('get_nearby_feed:' + nearby_feed)

    # 获取用户信息
    # user_info = api.get_user_info('102388086611')
    # print('get_user_info:' + user_info)

    # 获取用户作品
    # user_post = api.get_user_post('102388086611', 0, 20)
    # print('get_user_post:' + user_post)

    # 获取用户动态
    # user_forwards = api.get_user_forward_list('102388086611', 0, 20)
    # print('get_user_forward_list:' + user_forwards)

    # 获取用户关注列表
    user_id = '58123560683'
    # user_following_list = api.get_user_following_list(user_id, 0, 20)
    # print('get_user_following_list:' + user_following_list)
    # while True:
    #     has_more = json.loads(user_following_list)['has_more']
    #     if not has_more:
    #         break
    #
    #     min_time = json.loads(user_following_list)['min_time']
    #     print('min_time:' + str(min_time))
    #     user_following_list = api.get_user_following_list(user_id, min_time, 20)
    #     print('get_user_following_list:' + user_following_list)


    # 获取用户粉丝
    user_id = '102388086611'
    # user_follower_list = api.get_user_follower_list(user_id, 0, 20)
    # print('get_user_follower_list:' + user_follower_list)
    # while True:
    #     has_more = json.loads(user_follower_list)['has_more']
    #     if not has_more:
    #         break
    #
    #     min_time = json.loads(user_follower_list)['min_time']
    #     print('min_time:' + str(min_time))
    #     user_follower_list = api.get_user_follower_list(user_id, min_time, 20)
    #     print('get_user_follower_list:' + user_follower_list)

    # 获取热搜榜
    # hot_search_list = api.get_hot_search_list()
    # print('get_hot_search_list:' + hot_search_list)

    # 获取视频榜
    # hot_video_list = api.get_hot_video_list()
    # print('get_hot_video_list:' + hot_video_list)

    # 获取音乐榜
    # hot_music_list = api.get_hot_music_list()
    # print('get_hot_music_list:' + hot_music_list)

    # 获取正能量榜
    # hot_positive_list = api.get_hot_positive_energy_list()
    # print('get_hot_positive_energy_list:' + hot_positive_list)

    # 获取热门分类列表
    # category_list = api.get_hot_category_list(0, 10)
    # print('get_hot_category_list:' + category_list)

    # 综合搜索
    general_search_ret = api.general_search('美食', 0, 10)
    print('general_search_ret:' + general_search_ret)

    # 视频搜索
    # video_search_ret = api.video_search('养生', 0, 10)
    # print('video_search_ret:' + video_search_ret)

    # 用户搜索
    # user_search_ret = api.user_search('养生', 0, 10)
    # print('user_search_ret:' + user_search_ret)

    # 获取评论列表
    # comment_list = api.get_video_comment_list('6619905376009587972', 0, 20)
    # print('get_video_comment_list:' + comment_list)

    # 获取视频详情
    # video_detail = api.get_video_detail('6743791024440659211')
    # print('get_video_detail:' + video_detail)

    # 获取音乐详情
    # music_detail = api.get_music_detail('6673679720980269831')
    # print('get_music_detail:' + music_detail)

    # 获取音乐对应的视频列表
    # music_video_list = api.get_music_videos('6673679720980269831', 0, 20)
    # print('music_video_list:' + music_video_list)

    # 获取商品橱窗列表
    # promotion_list = api.get_promotion_list('105621336289', 0, 20)
    # print('promotion_list:' + promotion_list)

    # 获取直播房间信息
    # webcast_room_info = api.get_webcast_room_info('6731613896211188484')
    # print('webcast_room_info:' + webcast_room_info)

    # 获取直播用户信息
    # webcast_user_info = api.get_webcast_user_info('6731613896211188484', '108160072764')
    # print('webcast_user_info:' + webcast_user_info)

    # 获取直播本场榜
    # webcast_ranklist = api.get_webcast_ranklist('6731613896211188484', '108160072764')
    # print('webcast_ranklist:' + webcast_ranklist)

    # 获取接口使用情况
    api_access_info = api.get_api_access_info()
    print('api_access_info:' + api_access_info)


if __name__ == '__main__':
    main()
