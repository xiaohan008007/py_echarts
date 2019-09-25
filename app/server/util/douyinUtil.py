import json
import codecs
import re
import time
from urllib import parse


def save_feed(json_str):
    data_list = json.loads(json_str)
    aweme_list = data_list['aweme_list']
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    f = codecs.open('feed_20190408.txt', 'a+', 'utf-8')
    for data in aweme_list:
        awemeinfo = {}
        awemeinfo['ctime'] = current_time
        awemeinfo['create_time'] = data['create_time']
        awemeinfo['aweme_id'] = data['aweme_id']
        awemeinfo['desc'] = data['desc']
        author = data['author']
        awemeinfo['uid'] = author['uid']
        awemeinfo['short_id'] = author['short_id']
        awemeinfo['unique_id'] = author['unique_id']
        awemeinfo['nickname'] = author['nickname']
        awemeinfo['gender'] = author['gender']
        awemeinfo['birthday'] = author['birthday']
        awemeinfo['signature'] = author['signature']
        awemeinfo['avatar_thumb'] = author['avatar_thumb']['url_list'][0]
        awemeinfo['with_fusion_shop_entry'] = author['with_fusion_shop_entry']

        music = data['music']
        awemeinfo['mid'] = music['mid']
        awemeinfo['music_title'] = music['title']
        awemeinfo['music_author'] = music['author']
        awemeinfo['music_cover'] = music['cover_thumb']['url_list'][0]
        awemeinfo['music_playurl'] = music['play_url']['uri']
        awemeinfo['music_duration'] = music['duration']
        awemeinfo['music_owner_id'] = music['owner_id']

        statistics = data['statistics']
        awemeinfo['comment_count'] = statistics['comment_count']
        awemeinfo['digg_count'] = statistics['digg_count']
        awemeinfo['play_count'] = statistics['play_count']
        awemeinfo['share_count'] = statistics['share_count']
        awemeinfo['forward_count'] = statistics['forward_count']
        awemeinfo['download_count'] = statistics['download_count']

        video = data['video']
        awemeinfo['video_duration'] = video['duration']
        awemeinfo['video_cover'] = video['dynamic_cover']['url_list'][0]
        awemeinfo['video_share_url'] = data['share_url']

        f.write(json.dumps(awemeinfo, ensure_ascii=False) + "\n")
    f.close()

def save_music_detail(json_str):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    f = codecs.open('music_detail_20190408.txt', 'a+', 'utf-8')
    data = json.loads(json_str)
    music_detail = {}
    music_detail['ctime'] = current_time
    musicinfo = data['music_info']
    music_detail['title'] = musicinfo['title']
    music_detail['avatar_thumb'] = musicinfo['avatar_thumb']['url_list'][0]
    music_detail['owner_id'] = musicinfo['owner_id']
    music_detail['owner_nickname'] = musicinfo['owner_nickname']
    music_detail['owner_handle'] = musicinfo['owner_handle']
    music_detail['duration'] = musicinfo['duration']
    music_detail['mid'] = musicinfo['mid']
    music_detail['user_count'] = musicinfo['user_count']
    music_detail['play_url'] = musicinfo['play_url']['uri']

    f.write(json.dumps(music_detail, ensure_ascii=False) + "\n")
    f.close()

def save_music_aweme(json_str):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    f = codecs.open('music_aweme_20190408.txt', 'a+', 'utf-8')
    data_list = json.loads(json_str)
    aweme_list = data_list['aweme_list']
    for data in aweme_list:
        music_aweme = {}
        music_aweme['ctime'] = current_time
        video = data['video']
        music_aweme['dynamic_cover'] = video['dynamic_cover']['url_list'][0]

        # play_addr_list =  video['play_addr']['url_list']
        music_aweme['play_addr'] = data['share_url']
        music_aweme['create_time'] = data['create_time']
        statistics = data['statistics']
        music_aweme['play_count'] = statistics['play_count']
        music_aweme['share_count'] = statistics['share_count']
        music_aweme['forward_count'] = statistics['forward_count']
        music_aweme['aweme_id'] = statistics['aweme_id']
        music_aweme['comment_count'] = statistics['comment_count']
        music_aweme['digg_count'] = statistics['digg_count']
        music_aweme['download_count'] = statistics['download_count']
        author = data['author']
        music_aweme['signature'] = author['signature']
        music_aweme['uid'] = author['uid']
        music_aweme['avatar_url'] = author['avatar_168x168']['url_list'][0]
        music_aweme['share_qrcode'] = author['share_info']['share_qrcode_url']['url_list'][0]
        music_aweme['short_id'] = author['short_id']
        music_aweme['unique_id'] = author['unique_id']
        music_aweme['nickname'] = author['nickname']
        music_aweme['mid'] = data['music']['mid']
        music_aweme['music_title'] = data['music']['title']
        music_aweme['desc'] = data['desc']
        music_aweme['duration'] = data['duration']

        f.write(json.dumps(music_aweme, ensure_ascii=False) + "\n")
    f.close()
