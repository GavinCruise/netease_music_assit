#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from urllib import urlencode
import md5
import base64
import urllib2
import json
import random
import os

# proxies = {
#   "http": "http://10.10.1.10:3128",
#   "https": "http://10.10.1.10:1080",
# }
# requests.get("http://example.org", proxies=proxies)

cookies = {"os": "osx"}
header = {
    "Host": "music.163.com", "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "orpheus://orpheus",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.78.2 (KHTML, like Gecko)"
}


def search_song_by_name(name):
    search_url = 'http://music.163.com/api/search/get'
    params = {
        's': name,
        'type': 1,
        'offset': 0,
        'sub': 'false',
        'limit': 10
    }
    resp = requests.post(search_url, urlencode(params), cookies=cookies, headers=header)

    resp_js = resp.json()
    print(json.dumps(resp_js, ensure_ascii=False))
    if resp_js['code'] == 200 and resp_js['result']['songCount'] > 0:
        result = resp_js['result']
        #默认选中返回的第一个
        song_id = result['songs'][0]['id']
        detail_url = 'http://music.163.com/api/song/detail?ids=[%d]' % song_id
        resp = requests.get(detail_url)
        song_js = resp.json()
        print(json.dumps(song_js,ensure_ascii=False))
        return song_js['songs'][0]
    else:
        return None

#歌曲，路径，音质(取值 h，m，l)
def save_song_to_disk(song, folder, timbre='h'):
    name = song['name']
    if song[timbre+'Music'] == None :
        song_dfsId = str(song['bMusic']['dfsId'])
        ext = song['bMusic']['extension']
    else:
        song_dfsId = str(song[timbre+'Music']['dfsId'])
        ext = song[timbre+'Music']['extension']

    fpath = os.path.join(folder, name+"-"+song['artists'][0]['name']+"."+ext)
    if os.path.exists(fpath):
        return

    url = 'http://m%d.music.126.net/%s/%s.mp3' % (random.randrange(1, 3), encrypted_id(song_dfsId), song_dfsId)

    print("正在保存======> ")
    r = requests.get(url)
    with open(fpath, "wb") as code:
        code.write(r.content)
    print("OK")

def encrypted_id(id):
    byte1 = bytearray('3go8&$8*3*3h0k(2)2')
    byte2 = bytearray(id)
    byte1_len = len(byte1)
    for i in xrange(len(byte2)):
        byte2[i] = byte2[i]^byte1[i%byte1_len]
    m = md5.new()
    m.update(byte2)
    result = m.digest().encode('base64')[:-1]
    result = result.replace('/', '_')
    result = result.replace('+', '-')
    return result


if __name__ == '__main__':
    save_song_to_disk(search_song_by_name("美"),"/Users/book/Desktop")
