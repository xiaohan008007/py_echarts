import requests
import redis

pool = redis.ConnectionPool(host='192.168.3.194', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)


def get_proxy():
    while True:
        proip = r.blpop('douyin:doudada:uid:pool', timeout=None)
        print('获取代理ip:%s' % proip[1])
        proxies = {
            'http': 'http://' + proip[1],
            'https': 'https://' + proip[1]
        }
        if not r.exists(f'proxy:{proip[1]}'):
            try:
                resp = requests.get(url="http://current.ip.16yun.cn:802", proxies=proxies, timeout=2)
                if resp.status_code == 200:
                    r.rpush('douyin:doudada:uid:pool', proip[1])
                    r.set(f'proxy:{proip[1]}', 1)
                    r.expire(f'proxy:{proip[1]}', 120)
                    break
            except:
                print('IP不可用')
        else:
            break
    proxies = {
        'http': 'http://' + proip[1],
        'https': 'https://' + proip[1]
    }
    return proxies

def check_response_code(resp):
    if resp.status_code == 200:
        return True
    print('IP不可用')
    return False

if __name__ == '__main__':
    print(get_proxy())
