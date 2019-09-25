from datetime import datetime, date, timedelta
from collections import Counter
from prettytable import PrettyTable




def get_last_2_week(start, end):
    audit_list = []
    for add_day in range(start, end):
        # print(add_day)
        yesterday = (date.today() + timedelta(days=add_day)).strftime("%Y-%m-%d")  # 昨天日期
        print(yesterday)

        filename="/Users/ludanqing/python/qly_project/pyecharts/pyecharts/app/audit_douyin/audit_douyin_cid.txt." + yesterday
        try:
            for line in open(filename):
                user = line.split("\t")[1].split("=")[1]
                audit_list.append(user)
        except:
            pass
    return audit_list
        # get_file_content("audit_douyin/audit_douyin_cid.txt." + yesterday)

def get_current_week():
    monday, sunday = date.today(), date.today()
    one_day = timedelta(days=1)
    while monday.weekday() != 0:
        monday -= one_day
    while sunday.weekday() != 6:
        sunday += one_day

    return monday





def get_stat_content():
    last_week_start=(date.today() - get_current_week()).days+7
    last_week_end =(date.today() - get_current_week()).days



    yesterday = get_last_2_week(-1, 0)
    lastyesterday = get_last_2_week(-2, -1)
    lastweek = get_last_2_week(-last_week_start, -last_week_end)
    thisweek = get_last_2_week(-last_week_end, 0)

    yesterday_list = Counter(yesterday).items()
    lastyesterday_list = Counter(lastyesterday).items()
    lastweek_list = Counter(lastweek).items()
    thisweek_list = Counter(thisweek).items()

    user_tree={}
    mset = set()
    for ele, v in yesterday_list:
        mset.add(ele)
    for ele, v in lastyesterday_list:
        mset.add(ele)
    for ele, v in thisweek_list:
        mset.add(ele)
    for ele, v in lastweek_list:
        mset.add(ele)
    for user in mset:
        user_tree[str(user)] = []
        yesterday_flag = False
        lastyesterday_flag = False
        lastweek_flag = False
        thisweek_flag = False
        for ele, v in yesterday_list:
            if str(ele) == str(user):
                yesterday_flag = True
                user_tree[str(user)].append(v)
        if not yesterday_flag:
            user_tree[str(user)].append(0)

        for ele, v in lastyesterday_list:
            if str(ele) == str(user):
                lastyesterday_flag = True
                user_tree[str(user)].append(v)
        if not lastyesterday_flag:
            user_tree[str(user)].append(0)


        for ele, v in thisweek_list:
            if str(ele) == str(user):
                thisweek_flag = True
                user_tree[str(user)].append(v)
        if not thisweek_flag:
            user_tree[str(user)].append(0)


        for ele, v in lastweek_list:
            if str(ele) == str(user):
                lastweek_flag = True
                user_tree[str(user)].append(v)
        if not lastweek_flag:
            user_tree[str(user)].append(0)

    x = PrettyTable(["审核人", "昨日", "前日", "本周", "上周"])
    v0_total = 0
    v1_total = 0
    v2_total = 0
    v3_total = 0
    for k, v in user_tree.items():
        x.add_row([k, v[0], v[1], v[2], v[3]])
        v0_total += v[0]
        v1_total += v[1]
        v2_total += v[2]
        v3_total += v[3]
    x.add_row(['总计', v0_total, v1_total, v2_total, v3_total])
    # f = codecs.open('daily_set.txt', 'a+', 'utf-8')
    # f.write(str(x))
    # f.close()
    # print(set)
    # print(get_last_2_week(-1,0))
    return str(x)

import redis
if __name__ == '__main__':
    pool2 = redis.ConnectionPool(host='10.0.0.93', port=6379, db=3)
    r2 = redis.Redis(connection_pool=pool2)
    print(r2.llen("douyin:uid:search:10256625736"))
    # print(hah)
    # if not r2.get("douyin:uid:search:102566257364"):
    #     print("haha")
    # print(get_stat_content())