#! -*- coding:utf-8 -*-

import zlib
import json
import time
import redis
import base64
import requests
from urllib import parse
from bs4 import BeautifulSoup



def get_lat_lng(address):
    sess = requests.session()
    url = "http://api.map.baidu.com/geocoder/v2/?address={0}&output=json&ak=vCnbakxFcgqGpO6Gic4peoF5U0fLB1KO"
    req_url = url.format(address)
    try:
        data = sess.get(req_url)
        print('get_lat_lng status_code [%s]' % data.status_code)
        lat_lng = data.json()["result"]["location"]
        lat, lng = round(lat_lng["lat"], 6), round(lat_lng["lng"], 6)
        return lat, lng
    except Exception as e:
        print(e)


def get_address(pn, nn):
    url = "https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&" \
          "da_par=alamap&pcevaname=pc4.1&qt=con&from=webmap&c=289&wd=%E5%B0%8F%E5%8C%BA%E5%9C%B0%E5%9D%80" \
          "&wd2=&pn={pn}&nn={nn}&db=0&sug=0&addr=0&&da_src=pcmappg.poi.page&on_gel=1&src=7&gr=3&l=11.521823257199848&" \
          "auth=WZdeUVWA71Y3OQDDB2GvLGbDwaWgOGW1uxHHzTRzTVLtykiOxAXXw1GgvPUDZYOYIZuVt1cv3uVtGccZcuVtPWv3GuxtVwi" \
          "04960vyACFIMOSU7ucEWe1GDdw8E62qvSucFC%40B%40ZPuBt0xAwf0wd0vyIIAUSAU7AugjLLwWvrZZWuV&device_ratio=2" \
          "&tn=B_NORMAL_MAP&u_loc=13530215,3627532&ie=utf-8&b=(13448121.468761262,3610167.191531531;13475669.08322072," \
          "3664014.308468469)"
    header = {
        "Cookie": 'BIDUPSID=25F0AB4A048911B179B2981D7FCD3E64; PSTM=1532515760; BAIDUID=A2166345418F04C371D690C2AA88D327:FG=1; BDUSS=UEwNC1McmVtVU1FeXRRd1ZZRDVsfmg2SFhWVTIyNFNqRm54dURCeWtJSGZ1NHhjQUFBQUFBJCQAAAAAAAAAAAEAAAAbHv9GZnlzaF8xOTkxAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN8uZVzfLmVcV; H_PS_PSSID=1456_21118_28720_28558_28607_28585_26350_28604_28627_28605; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; delPer=0; PSINO=5; M_LG_UID=1191124507; M_LG_SALT=0bb45e895a0850176542fed066cb329c; validate=67494',
        "Host": 'map.baidu.com',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    }
    sess = requests.session()
    req_url = url.format(pn=pn, nn=nn)
    data = sess.get(req_url, headers=header)
    print("get_address status_code: [%d]" % data.status_code)
    address = []
    for d in data.json()["content"]:
       address.append(d["area_name"]+d["name"])
    return address


def loop_addres():
    pn = 1
    nn = 10
    rconn = redis.Redis("localhost", 6379)
    while True:
        try:
            address = get_address(pn, nn)
            for add in address:
                lat, lng = get_lat_lng(add)
                get_shop(add, lat, lng)
                print([add, lat, lng])
                line = "----".join([add, str(lat), str(lng)])
                rconn.sadd("baiduLatLng", line)
            #     break
            # break
            pn += 1
            nn += 10
        except Exception as e:
            print(e)
            break


def zipData(formData):
    base = {
        "rId": 100007,
        "ver": "1.0.6",
        "ts": str(int(round(time.time(), 3)*1000)),
        "cts": str(int(round(time.time(), 3)*1000)),
        "brVD": '[369, 603]',
        "brR": '[[1536, 864], [1536, 824], 24, 24]',
        "bI": ["http://waimai.meituan.com/home/wtw3jsxsq4yp", "http://waimai.meituan.com/new/waimaiIndex/?stay=1"],
        "mT": ["508,1835", "508,1835", "511,1835", "513,1835", "517,1835", "524,1835", "529,1835", "540,1833",
               "554,1831", "565,1829", "578,1826", "582,1824", "593,1821", "618,1816", "629,1812", "641,1807",
               "648,1803", "654,1801", "658,1800", "661,1799", "662,1799", "663,1798", "665,1797", "666,1796",
               "668,1795", "676,1789", "688,1782", "704,1774", "717,1767", "716,1955"],
        "kT": [],
        "aT": ["151,336,DIV"],
        "tT": [],
        "aM": "",
        "sign": ""
    }
    lineFrist = [key + "=" + str(value) for key, value in formData.items()]
    joinLine = "&".join(lineFrist)
    base['sign'] = deflate(joinLine.encode()).decode()
    base["cts"] = str(int(round(time.time(), 3)*1000))
    token = deflate(json.dumps(base).encode()).decode()
    return token


def deflate(data):
    try:
        return base64.b64encode(zlib.compress(data))
    except zlib.error:
        print(zlib.error)
        return None


def test_token():
    sign = "eJxNjstqwzAURP8lC+8aO7bTkoIW2aWQQglNG7oRqizbN9arV1dR7K+vS6BkN+cwDLOQWoQA7chp9IpJQYoLrTNDAXjrLHEZAr8oDOAsKwvRPG4235lD6MAeUbOeyD/neRJgBCyNAorCLqUzee+MyhOl6ox+PdUyZV50iru2DYpYubphgEnNuzMgWYWszrwW1Do0bG4gSHV7VmTBIf3n6P0fgr24uXJntOsgEMg75awGq7gX4yxjhIYd0+vTHstTFfXwIIc+9C/8Y594oWJx9aft+6o5FLhutm+fg9H19bw77BBTBV9XNHL6WfwCpLhy3w=="
    sign_decode = base64.b64decode(sign)
    sign_string = zlib.decompress(sign_decode).decode()
    print(sign_string)
    jw = "eJx1kktzokAUhf8LWyil32BVFiiJYhAfQdGksgBF0KggoKhT89+nu2vCTE3VsOmP2+eePn3hh1I4G6UDdP4wTbnGhdJRQEtvUUVTqpLvEIIAMRjFhk40Zf1XzcSQlzUlKha20vkA1NSojj5FYcbfPwBBVDMo/tR+I+QIsSYWJXK4REmrKu+023W4O4a71jHeVZfw1Fpnx3aaHeN2XdVoX+Tkgdc1z/N/tcIdj75wxNDQgIEQl2NoNoh0gVgi/INIIJVIBDKJTKDZINYlCjMMBGJhhqFE4YDlEQQIlL7E+AelL8Ycid5kINIMsAZ19I3IFAIsMiBDZjAEssYXUXk3WaXNhRARt4CyjYiQUCRDMiQUByP+GYABiESRF0gBFAJdtgEh0A0x0C8xUL6GzWAhH6PtLMRm9b054j8Mbyx3yYlTPLx5+7I61w9rPpsYh55qhGMW+V+ZE8AwmE6Tg9dn2ey8e0SeGRYLsJmxV/X6RrtfnrqubXc8DbKpxdZpbjr5cLrK3ML3bGu5L9zB87tVGJk9tsrX+jqb9DFE5GDTkRXPo3F8t9uneDZMur27Z2VFzz3PH3Gsju7p+ECzmzrZzO/vC6Lvigu0V/nqEuVp8nzyLo9REqyC8lHUAbAzPerj5G2wYIuj33W26EQn+jYpIL4sh6dqXCbPo4SRsO6fWbLE99s+dVYbXb36g7LyX7bL2nHWqtlrGyti4iwY3sxwW6k0Iy9ueqmO6jYxB8CMasa6Xb+7MJfewKXBtu7lbnpH9dOT8vMXaNPxMw=="
    sign_decode = base64.b64decode(jw)
    sign_string = zlib.decompress(sign_decode).decode()
    print(sign_string)


def get_shop(address, lat, lng):
    mei_url = "http://waimai.meituan.com/geo/geohash?lat={lat}&lng={lng}&addr={add}&from=m"
    add = parse.quote(address)
    req_mei = mei_url.format(add=add, lng=lng, lat=lat)
    if False:
        req_mei = "http://waimai.meituan.com/geo/geohash?lat=31.132904&lng=121.54854&addr=%E4%B8%8A%E6%B5%B7%E5%B8%82%E6%B5%A6%E4%B8%9C%E6%96%B0%E5%8C%BA%E4%B8%AD%E5%9B%BD%E7%94%B5%E4%BF%A1%E4%BF%A1%E6%81%AF%E5%9B%AD%E5%8C%BA&from=m"
    sesss = requests.session()
    headers = {
        "Cookie": '_lxsdk_cuid=16987da1bfac8-05578dda9e94fa-9333061-144000-16987da1bfab3; w_utmz="utm_campaign=(direct)&utm_source=(direct)&utm_medium=(none)&utm_content=(none)&utm_term=(none)"; w_uuid=UwM7Lr2X3ulk-ckhshI_VLw_0eu0xpXAT1dR0r5dAPWkml4xjHRHrrw3iZxrmczq; w_visitid=f271cdb5-8908-4b9c-9e6f-fa3669f28cc6; _lxsdk=16987da1bfac8-05578dda9e94fa-9333061-144000-16987da1bfab3; _ga=GA1.3.1096036169.1552906553; _gid=GA1.3.1175728288.1552906553; uuid=31c412ba39eb455f92be.1552906594.1.0.0; mtcdn=K; n=eiX401982443; lt=vbpko65ISoYMSuE6YOwvQJg_YUgAAAAAEggAAFAiT2T-ifGWsHpp54PPVeNFQugQTJubS5KxZOSut4uynYySmP-sxwyu3HJI83gNiw; lsu=; cookie_phone=17301609198; _lx_utm=utm_source%3Dbaidu%26utm_medium%3Dorganic%26utm_term%3D%25E7%25BE%258E%25E5%259B%25A2; __mta=45986203.1552908192633.1552908192633.1552908290847.2; waddrname="%E4%BF%9D%E5%88%A9%C2%B7%E6%9E%97%E8%AF%AD%E6%BA%AA"; w_geoid=wtw3ju3mwg15; w_cid=310115; w_cpy=pudongxinqu; w_cpy_cn="%E6%B5%A6%E4%B8%9C%E6%96%B0%E5%8C%BA"; w_ah="31.137587931007147,121.54375568032265,%E4%BF%9D%E5%88%A9%C2%B7%E6%9E%97%E8%AF%AD%E6%BA%AA|40.01470198854804,116.49476073682308,%E7%BE%8E%E5%9B%A2%E7%82%B9%E8%AF%84%E5%8C%97%E4%BA%AC%E6%80%BB%E9%83%A8"; _ga=GA1.2.1096036169.1552906553; _gid=GA1.2.1175728288.1552906553; JSESSIONID=1ctun8gxndy0h9pugt33kja7z; _lxsdk_s=169907183e8-45-88b-345%7C%7C29',
        "Host": "waimai.meituan.com",
        "Referer": "http://waimai.meituan.com/new/waimaiIndex/?stay=1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    }
    mei_data = sesss.get(req_mei, headers=headers)
    print("get_shop status_code [%d]" % mei_data.status_code)
    soup = BeautifulSoup(mei_data.text, "lxml")
    restaurant = soup.find("div", {"class": "rest-list"}).find_all("div", {"class": "restaurant"})
    for rest in restaurant:
        send_time = rest.find("span", {"class": "send-time"}).text.strip().strip("分钟")
    next_paeg(sesss, mei_data)


def next_paeg(sesss, data):
    uuid = data.cookies.get("w_uuid")
    originUrl = parse.quote(data.url)
    headers = {
        "Cookie": data.headers["Set-Cookie"],
        "Host": "waimai.meituan.com",
        "Referer": "http://waimai.meituan.com/new/waimaiIndex/?stay=1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    }
    formData = {"classify_type": "cate_all", "sort_type": "0", "price_type": "0", "support_online_pay": "0",
                "support_invoice": "0", "support_logistic": "0", "page_offset": 21, "page_size": 20,
                "mtsi_font_css_version": "20ad699b", "uuid": uuid, "platform": "1", "partner": "4",
                "originUrl": originUrl}
    token = zipData(formData)
    post_url = "http://waimai.meituan.com/ajax/poilist?_token={}"
    req_url = post_url.format(token)
    post_dta = sesss.post(req_url, data=formData, headers=headers)
    print(post_dta.url)
    print(post_dta.text)


if __name__ == "__main__":
    address = "上海市浦东新区中国电信信息园区"
    # lat, lng = get_lat_lng(address)
    # get_shop(address, lat, lng)
    # get_shop("", "", "")
    loop_addres()
    # test_token()
    # zipData("s", "s")
