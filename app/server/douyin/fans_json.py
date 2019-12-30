import json


def parse_json(j_data):
    uid = j_data['uid']
    fans_list = j_data['fans']
    print("uid:%s fans:%s" % (uid, len(fans_list)))


f = open('test.txt')
for line in f:
    print(line)
    j_data = json.loads(line.strip())
    parse_json(j_data)
    break
f.close()