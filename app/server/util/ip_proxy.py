import requests
import redis
import socket


pool = redis.ConnectionPool(host='192.168.3.194', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)


def get_proxy():
    # 获取本机电脑名
    myname = socket.gethostname()
    # 获取本机ip
    ip = socket.gethostbyname(myname)
    print('当前ip:%s' % ip)
    if ip.find('192.168.3.') < 0 and ip.find('10.0.0.') < 0:
        print('线下机器不获取代理IP')
        return

    while True:
        proip = r.srandmember('douyin:doudada:proxys', 1)

        if proip:
            proxies = {
                'http': 'http://' + proip[0],
                'https': 'https://' + proip[0]
            }
            return proxies
        # proip = r.blpop('douyin:doudada:proxys', timeout=2)
        # if not proip:
        #     break
        # print('获取代理ip:%s' % proip[1])
        # proxies = {
        #     'http': 'http://' + proip[1],
        #     'https': 'https://' + proip[1]
        # }
        # if not r.exists(f'proxy:{proip[1]}'):
        #     try:
        #         resp = requests.get(url="http://current.ip.16yun.cn:802", proxies=proxies, timeout=2)
        #         if resp.status_code == 200:
        #             r.rpush('douyin:doudada:uid:pool', proip[1])
        #             r.set(f'proxy:{proip[1]}', 1)
        #             r.expire(f'proxy:{proip[1]}', 120)
        #             break
        #     except:
        #         print('IP不可用')
        # else:
        #     break
    # proxies = {
    #     'http': 'http://' + proip[1],
    #     'https': 'https://' + proip[1]
    # }
    # return proxies

def check_response_code(resp):
    if resp.status_code == 200:
        return True
    print('IP不可用')
    return False

if __name__ == '__main__':
     # print(get_proxy())
    ip = '10.0.0.140'
    print(ip.find('10.0.0.'))
    if ip.find('192.168.3.') < 0 and ip.find('10.0.0.') < 0:
        print('线下机器不获取代理IP')
        # return
