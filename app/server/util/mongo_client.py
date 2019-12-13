#!/usr/bin/env python
# -*- coding:utf-8 -*-


from pymongo import MongoClient
from datetime import datetime


class MongodbClient(object):
    def __init__(self, url_set, db_name, username=None, password=None):
        self.url_port_set = self.format_url(url_set)
        self.db_name = db_name
        self.username = username
        self.password = password
        self.client = MongoClient('mongodb://{}/'.format(self.url_port_set), connect=False)
        self.db = self.client["{}".format(db_name)]
        if username:
            self.db.authenticate(self.username, self.password)

    def format_url(self, url_set):
        url = ""
        for url_port in url_set:
            url = url + url_port + ','
        return url[:-1]

    def get_keyword(self, keyword):
        keyword_list = self.db["taobao_keyword_data"].find({"keyword": keyword}).sort('ctime')
        return keyword_list

    def get_1688index(self, cid):
        keyword_list = self.db["index_1688_history"].find({"cid": cid}).sort('rdate')
        return keyword_list

    def get_1688attr(self, cid):
        keyword_list = self.db["attr_1688_history"].find({"cid": cid})
        return keyword_list

    def get_cid(self, cat_name):
        catinfo = self.db['category_1688'].find_one({"catname": cat_name})
        return catinfo

    def get_catinfo(self, cid):
        catinfo = self.db['category_1688'].find_one({"catid": cid})
        return catinfo

    def get_catinfo_in(self, keywords):
        return self.db['category_1688'].find({'catname': {'$in': keywords}})

    def get_tb_cid(self):
        return self.db['index_1688_history'].find({'rdate': '2019-01-09', 'index_tb': {'$gt': 0}})



    def update_userfans(self, userfans):
        self.db['douyin_fans_desc'].update_#!/usr/bin/env python
# -*- coding:utf-8 -*-


from pymongo import MongoClient
from datetime import datetime


class MongodbClient(object):
    def __init__(self, url_set, db_name, username=None, password=None):
        self.url_port_set = self.format_url(url_set)
        self.db_name = db_name
        self.username = username
        self.password = password
        self.client = MongoClient('mongodb://{}/'.format(self.url_port_set), connect=False)
        self.db = self.client["{}".format(db_name)]
        if username:
            self.db.authenticate(self.username, self.password)

    def format_url(self, url_set):
        url = ""
        for url_port in url_set:
            url = url + url_port + ','
        return url[:-1]

    def get_keyword(self, keyword):
        keyword_list = self.db["taobao_keyword_data"].find({"keyword": keyword}).sort('ctime')
        return keyword_list

    def get_1688index(self, cid):
        keyword_list = self.db["index_1688_history"].find({"cid": cid}).sort('rdate')
        return keyword_list

    def get_1688attr(self, cid):
        keyword_list = self.db["attr_1688_history"].find({"cid": cid})
        return keyword_list

    def get_cid(self, cat_name):
        catinfo = self.db['category_1688'].find_one({"catname": cat_name})
        return catinfo

    def get_catinfo(self, cid):
        catinfo = self.db['category_1688'].find_one({"catid": cid})
        return catinfo

    def get_catinfo_in(self, keywords):
        return self.db['category_1688'].find({'catname': {'$in': keywords}})

    def get_tb_cid(self):
        return self.db['index_1688_history'].find({'rdate': '2019-01-09', 'index_tb': {'$gt': 0}})

    def get_userfans(self, uid):
        return self.db['douyin_fans_desc'].find({'uid': uid})

    def get_userfans_uid(self, uid):
        return self.db['douyin_fans_desc'].find({'uid': uid})

    def get_aweme_list_by_uid(self, uid, date1, date2):
        return self.db['douyin_content_data'].find({'uid': uid, "ctime": {"$gte":date1,"$lt":date2}}).limit(500)

    def update_userfans(self, userfans):
        # self.db['douyin_fans_desc'].update_one({'authorId': userfans['authorId']}, {'$set': userfans}, upsert=True)

        self.db['douyin_fans_desc'].update({'uid': userfans['uid']}, {'$set': userfans}, upsert=True)
        # self.db['douyin_fans_desc'].update({'authorId': userfans['authorId']}, {'qq': userfans['qq'], 'weibo': userfans['weibo'], 'weixin': userfans['weixin'], 'phone': userfans['phone'], 'has_contact': userfans['has_contact'], 'ctime': userfans['ctime'], 'dcatId': userfans['dcatId']}, upsert=True)

    def find_user_has_douyincid(self, uids):
        return self.db['douyin_fans_desc'].find({'uid': {'$in': uids}, 'dcatId': {'$ne': ''}})

    def find_user_uidnull(self, type):
        if type=="":
            return self.db['douyin_fans_desc'].find({'uid': ""})
        else:
            return self.db['douyin_fans_desc'].find({'uid':{'$exists':False}})







