import requests
import json
import re


def loads_jsonp(_jsonp):
    """
    解析jsonp数据格式为json
    :return:
    """
    try:
        return json.loads(re.match(".*?({.*}).*", _jsonp, re.S).group(1))
    except:
        raise ValueError('Invalid Input')

def handle_product_info(spid, proxies):
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
    }
    url = 'https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?jsv=2.4.8&appKey=12574478&t=1560496829070&sign=a5de8fe882dd17eff8ce157a36cb3fd1&api=mtop.taobao.detail.getdetail&v=6.0&dataType=jsonp&ttid=2017%40taobao_h5_6.6.0&AntiCreep=true&type=jsonp&callback=mtopjsonp2&data=%7B%22itemNumId%22%3A%22'+spid+'%22%7D'
    if proxies:
        response = requests.get(url=url, headers=header, proxies=proxies, verify=False, timeout=3)
    else:
        response = requests.get(url=url, headers=header, verify=False, timeout=3)
    # response = requests.get(url=url, headers=header,  verify=False, timeout=3)
    # if not ip_proxy.check_response_code(response):
    #     raise ProxyLoseException('代理ip失效')
    return parse_productinfo(response.text)


def parse_productinfo(result):

    product_info = {}
    p_result = loads_jsonp(result)
    if 'data' in p_result:
        json_data = p_result['data']
        if 'seller' in json_data:
            seller = json_data['seller']
            product_info['userId'] = seller['userId']
            product_info['shopId'] = seller['shopId']
            product_info['sellerNick'] = seller['sellerNick']
            product_info['shopName'] = seller['shopName']
            product_info['shopType'] = seller['shopType']
            product_info['allItemCount'] = seller['allItemCount']
            product_info['fans'] = seller['fans']
            product_info['creditLevel'] = seller['creditLevel']
        if 'item' in json_data:
            item_simple = json_data['item']
            product_info['title'] = item_simple['title']
            product_info['categoryId'] = item_simple['categoryId']
            product_info['rootCategoryId'] = item_simple['rootCategoryId']
            product_info['commentCount'] = item_simple['commentCount']
            product_info['favcount'] = item_simple['favcount']

            product_info['brandValueId'] = item_simple.get('brandValueId', '')
        if 'props' in json_data:
            brand_info = json_data['props']['groupProps'][0]['基本信息'][0]
            if '品牌' in brand_info:
                product_info['brandName'] = brand_info['品牌']

        if 'apiStack' in json_data:
            apiStack_value = json.loads(json_data['apiStack'][0]['value'])
            if 'item' in apiStack_value:
                item = apiStack_value['item']
                delivery = apiStack_value['delivery']
                skuCore_0 = apiStack_value['skuCore']['sku2info']['0']
                if 'sellCount' in item:
                    product_info['volume'] = item['sellCount']
                else:
                    product_info['volume'] = item['vagueSellCount']
                product_info['quantity'] = skuCore_0['quantity']
                product_info['price'] = skuCore_0['price']['priceMoney']
                # product_info['title'] = item['title']
                product_info['location'] = delivery['from']

    return product_info


if __name__ == '__main__':
    product_info = handle_product_info('595996822862', '')
    print(json.dumps(product_info, ensure_ascii=False))