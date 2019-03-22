#encoding:utf-8

import os
import ssl
import json
import pymongo
import threading
from queue import Queue
from meituan.setting import *
import requests, time, random
requests.packages.urllib3.disable_warnings()
from project.mt_aes import AESCipher


ssl.match_hostname = lambda cert, hostname: True
class  Meituan_page():
    def __init__(self, wm_latitude=None, wm_longitude=None, city=None, privies=None, models="mysql"):
        self.wm_longitude = str(wm_longitude)
        self.wm_latitude = str(wm_latitude)
        client = pymongo.MongoClient('localhost', 27017)
        self.privies = privies
        self.city = city
        self.db = client[self.privies]
        self.proxie_1 = self.get_proxy()
        self.proxie_2 = self.get_proxy()
        self.client = requests.Session()
        self.mark = True
        self.nums = 0
        self.shop_info_url = 'https://i.waimai.meituan.com/openh5/poi/info?_='

    def get_proxy(self):
        proxy_url = 'http://www.uu-ip.com/Tools/proxyIP.ashx?OrderNumber=tilyp1b06f8651b22cc6e922819c8785d2569&poolIndex=38431&cache=1&qty=1'
        proxies = requests.get(proxy_url).text.strip()
        proxy = {
            'https': proxies,
        }
        return proxy

    def parse_html(self, data):
        try:
            cookies = {'Cookie': 'wm_order_channel=default;_lxsdk_cuid={}; _lxsdk={}; utm_source=0; wx_channel_id=0;_lx_utm=utm_source%3D60066; _lxsdk_s={}; '
                    'terminal=i;'.format(self.random_(), self.random_(), self.random_())
            }
            e = AESCipher("jvzempodf8f9anyt")
            secret_data = '{"ts":1552395870160,"cts":1552395886300,"brVD":[582,238],"brR":[[582,238],[582,238],24,24],"aM":""}'
            enc_str = e.encrypt(secret_data)
            post_url = 'https://i.waimai.meituan.com/openh5/homepage/poilist?_=' + str(str(int(time.time())) + '653')+'0&X-FOR-WITH='+enc_str.decode()
            r = self.client.post(
                post_url,
                headers=headers, verify=False,
                data=data, proxies=self.proxie_1,
                cookies=cookies, timeout=(3, 7)
            )
            self.client.cookies.clear()
            print(self.proxie_1)
            if r.status_code == 200:
                 return r
            else:
                self.proxie_1 = self.get_proxy()
                print(r.status_code)
                return self.parse_html(data)
        except Exception as e:
            print(e)
            self.proxie_1 = self.get_proxy()
            return self.parse_html(data)


    def parse_json_data(self, r):
        try:
            for d in r.json().get('data').get('shopList'):
                infomations={}
                # 店铺id
                infomations['mtWmPoiId']=d.get('mtWmPoiId')
                #配送时间
                infomations['deliverTime']=d.get('deliveryTimeTip')
                #配送费
                infomations['deliverFee']=d.get('shippingFeeTip')
                #起送
                infomations['minPriceTip']=d.get('minPriceTip')
                #图像url
                # infomations['imageUrls']=d.get('picUrl')
                #价格统计
                infomations['avgPrice']=d.get('averagePriceTip')
                #营业时间
                infomations['openingHours']=d.get('shipping_time')
                #销量
                infomations['monthSalesTip'] = d.get('monthSalesTip')
               # 质量评分
                infomations['qualRating']=d.get('wmPoiScore')
               # 综合评分
                infomations['rating']=d.get('wmPoiScore')
               # 餐单meau
                infomations['meau_status']=True
               # 评价
                infomations['elet_status']=True
               # 商家
                infomations['shop_tatus']=True
                #优惠咯
                infomations['promotions']=d.get('discounts2')
                #折扣
                # infomations['discounts2']=d.get('discounts2')
                #地址
                infomations['address']=d.get('address')
                #店铺名
                infomations['shop_name']=d.get('shopName')
                print(infomations)
                data = {
                    'shopId': '0',
                    'source': 'shoplist',
                    'mtWmPoiId': infomations['mtWmPoiId'],
                }
                # res = self.parse_info_html(data)
                try:
                    # 时间
                    # infomations['serTime'] = res.get('data').get('serTime')
                    infomations['serTime'] = ""
                    # phone
                    infomations['shopPhone'] = ""
                    # infomations['shopPhone'] = res.get('data').get('shopPhone')
                except:
                    pass
                lock = threading.Lock()
                lock.acquire()
                print(infomations)
                self.save_to_mongo(infomations)
                lock.release()
        except Exception as e:
            print('parse_json_data:', e)
            # self.proxie_1 = self.get_proxy()

    def parse_info_html(self, data):
        url = self.shop_info_url + str(int(time.time()) * 1000)
        cookies = {'Cookie':
                       'wm_order_channel=default;_lxsdk_cuid={};'
                       ' _lxsdk={};utm_source=0; wx_channel_id=0; '
                       '_lx_utm=utm_source%3D60066;_lxsdk_s={}; '
                       'terminal=i;'.format(self.random_(), self.random_(), self.random_())
                   }
        try:
            res = self.client.post(url, data=data, headers=headers, proxies=self.proxie_2, cookies=cookies,verify=False)
            print('parse_info_html.status_code: {}'.format(res.status_code))
            if res.status_code == 403:
                print("更换代理，更换请求头,请求网址：%s" % url)
                self.proxie_2 = self.get_proxy()
                return self.parse_info_html(data)
            elif res.status_code == 200:
                return res.json()
        except Exception as e:
            print('parse_info_html错误信息: {}'.format(e))
            self.proxie_2 = self.get_proxy()
            time.sleep(2)
            return self.parse_info_html(data)


    def random_(self):
        s = '123456789123456789abcef-'
        ra_ = ''
        for i in range(random.randint(30, 50)):
            ra_ = ra_ + (random.choice(s))
        return ra_

    def parse_food_page(self):
        num = 0
        i = 0
        while True:
            data = {
                'startIndex': str(i),
                'sortId': '0',
                'navigateType': 19,
                'firstCategoryId': 19,
                'secondCategoryId': 19,
                'multiFilterIds': '',
                'sliderSelectCode': '',
                'sliderSelectMin': '',
                'sliderSelectMax': '',
                'geoType': '2',
                'rankTraceId': '724979C6B0E6BED06EDC88E047567CED',
                'wm_latitude': int(self.wm_latitude.replace('.', '')),
                'wm_longitude': int(self.wm_longitude.replace('.', '')),
                'wm_actual_latitude': '',
                'wm_actual_longitude': '',
                '_token': '',
            }
            print(self.wm_latitude, self.wm_longitude)
            try:
                r = self.parse_html(data)
                print(len(r.json().get('data').get('shopList')))
                if type(r.json()) == 'str':
                    break
                if len(r.json().get('data').get('shopList')) == 0:
                    break
                self.parse_json_data(r)
            except Exception as e:
                print('parse_food_page %s' % e)
                break
            num += 1
            i += 1

    def save_to_mongo(self, data):
        if self.db[self.privies].update({"mtWmPoiId": data["mtWmPoiId"]}, {"$set": data}, True):
            print("save to mongo ")
            # print("一共跑了{}条数据".format(sel))
        else:
            print("save to mongo failed ", data["title"])

def thread(city_queue):
    while not city_queue.empty():
        url_info = city_queue.get()
        city = url_info['city']
        poi = url_info['poi']
        lat = poi[1]
        lng = poi[0]
        print(city, poi)
        privies = url_info['province']
        splider = Meituan_page(lat, lng, privies=privies, city=city)
        splider.parse_food_page()


def  main():
    city_queue = Queue()
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'FILES'))
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'FILES')
    with open(os.path.join(path, 'shanghai.json'), mode='r', encoding="utf-8") as f:
        poi_set = json.loads(f.read())
    for key, value in poi_set.items():
        key = key.split(',')
        lat = key[1]
        lng = key[0]
        poi = (lng, lat)
        info = {'poi': poi, 'city': 'shanghai', 'province': 'shanghai'}
        city_queue.put(info)
    threads = []
    for i in range(10):
        t = threading.Thread(target=thread, args=(city_queue,))
        threads.append(t)
    for x in threads:
        x.start()
    for x in threads:
        x.join()

if __name__ == '__main__':
    main()
