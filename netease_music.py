#! /usr/bin/env python
# -*- coding: utf-8 -*-

import md5
import base64
import urllib2
import urllib
import json
import random
import os
import requests
import sys
import eyed3

reload(sys)
sys.setdefaultencoding('utf-8')
#set cookie
cookie_opener = urllib2.build_opener()
cookie_opener.addheaders.append(('Cookie', 'appver=2.0.2'))
cookie_opener.addheaders.append(('Referer', 'http://music.163.com'))
urllib2.install_opener(cookie_opener)


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


def search_artist_by_name(name):
    search_url = 'http://music.163.com/api/search/get'
    params = {
            's': name,
            'type': 100,
            'offset': 0,
            'sub': 'false',
            'limit': 10
    }
    params = urllib.urlencode(params)
    resp = urllib2.urlopen(search_url, params)
    artists = json.loads(resp.read())
    if artists['code'] == 200 and artists['result']['artistCount'] > 0:
        print(artists)
        return artists['result']['artists'][0]
    else:
        return None


def search_album_by_name(name):
    search_url = 'http://music.163.com/api/search/get'
    params = {
            's': name,
            'type': 10,
            'offset': 0,
            'sub': 'false',
            'limit': 20
    }
    params = urllib.urlencode(params)
    resp = urllib2.urlopen(search_url, params)
    resp_js = json.loads(resp.read())
    if resp_js['code'] == 200 and resp_js['result']['albumCount'] > 0:
        result = resp_js['result']
        album_id = 0
        if result['albumCount'] > 1:
            for i in range(len(result['albums'])):
                album = result['albums'][i]
                print '[%2d]artist:%s\talbum:%s' % (i+1, album['artist']['name'], album['name'])
            select_i = int(raw_input('Select One:'))
            if select_i < 1 or select_i > len(result['albums']):
                print 'error select'
                return None
            else:
                album_id = select_i-1
        return result['albums'][album_id]
    else:
        return None


def search_song_by_name(name):
    search_url = 'http://music.163.com/api/search/get'
    params = {
            's': name,
            'type': 1,
            'offset': 0,
            'sub': 'false',
            'limit': 20
    }
    params = urllib.urlencode(params)
    resp = urllib2.urlopen(search_url, params)

    resp_js = json.loads(resp.read())
    print(json.dumps(resp_js,ensure_ascii=False))
    if resp_js['code'] == 200 and resp_js['result']['songCount'] > 0:
        result = resp_js['result']
        song_id = result['songs'][0]['id']
        # if result['songCount'] > 1:
        #     for i in range(len(result['songs'])):
        #         song = result['songs'][i]
        #         print '[%2d]song:%s\tartist:%s\talbum:%s' % (i+1,song['name'], song['artists'][0]['name'], song['album']['name'])
        #     select_i = int(raw_input('Select One:'))
        #     if select_i < 1 or select_i > len(result['songs']):
        #         print 'error select'
        #         return None
        #     else:
        #         song_id = result['songs'][select_i-1]['id']
        detail_url = 'http://music.163.com/api/song/detail?ids=[%d]' % song_id
        resp = urllib2.urlopen(detail_url)
        song_js = json.loads(resp.read())
        print(json.dumps(song_js, ensure_ascii=False))
        return song_js['songs'][0]
    else:
        return None


def get_artist_albums(artist):
    albums = []
    offset = 0
    while True:
        url = 'http://music.163.com/api/artist/albums/%d?offset=%d&limit=50' % (artist['id'], offset)
        resp = urllib2.urlopen(url)
        print(resp.read())
        tmp_albums = json.loads(resp.read())
        albums.extend(tmp_albums['hotAlbums'])
        if tmp_albums['more'] == True:
            offset += 50
        else:
            break
    return albums


def get_artist_albums2(artist):
    albums = []
    offset = 0
    url = 'http://music.163.com/api/artist/albums/%d?offset=%d&limit=50' % (artist, offset)
    resp = urllib2.urlopen(url)
    print(resp.read())
    tmp_albums = json.loads(resp.read())
    albums.extend(tmp_albums['hotAlbums'])
    if tmp_albums['more'] == True:
        offset += 50
    return albums


def get_album_songs(album):
    url = 'http://music.163.com/api/album/%d/' % album['id']
    resp = urllib2.urlopen(url)
    print resp
    songs = json.loads(resp.read())
    return songs['album']['songs']


def save_song_to_disk(song, folder):
    name = song['name']
    fpath = os.path.join(folder, name+'.mp3')
    if os.path.exists(fpath):
        return

    song_dfsId = str(song['bMusic']['dfsId'])
    url = 'http://m%d.music.126.net/%s/%s.mp3' % (random.randrange(1, 3), encrypted_id(song_dfsId), song_dfsId)
    #print '%s\t%s' % (url, name)
    #return
    resp = urllib2.urlopen(url)
    data = resp.read()
    f = open(fpath, 'wb')
    f.write(data)
    f.close()


def download_song_by_search(name, folder='.'):
    song = search_song_by_name(name)
    if not song:
        print 'Not found ' + name
        return

    if not os.path.exists(folder):
        os.makedirs(folder)
    save_song_to_disk(song, folder)


def download_album_by_search(name, folder='.'):
    album = search_album_by_name(name)
    if not album:
        print 'Not found ' + name
        return
    
    name = album['name']
    folder = os.path.join(folder, name)

    if not os.path.exists(folder):
        os.makedirs(folder)

    songs = get_album_songs(album)
    for song in songs:
        save_song_to_disk(song, folder)


# lyric http://music.163.com/api/song/lyric?os=osx&id= &lv=-1&kv=-1&tv=-1
def song_lyric(music_id):
    action = 'http://music.163.com/api/song/lyric?os=osx&id={}&lv=-1&kv=-1&tv=-1'.format(  # NOQA
        music_id)
    try:
        resp = urllib2.urlopen(action)
        data = json.load(resp)
        if 'lrc' in data and data['lrc']['lyric'] is not None:
            lyric_info = data['lrc']['lyric']
        else:
            lyric_info = '未找到歌词'
        return lyric_info
    except requests.exceptions.RequestException as e:
        print(e)
        return []


def song_tlyric(music_id):
    action = 'http://music.163.com/api/song/lyric?os=osx&id={}&lv=-1&kv=-1&tv=-1'.format(  # NOQA
        music_id)
    try:
        data = json.loads(urllib2.urlopen(action))
        if 'tlyric' in data and data['tlyric'].get('lyric') is not None:
            lyric_info = data['tlyric']['lyric'][1:]
        else:
            lyric_info = '未找到歌词翻译'
        return lyric_info
    except requests.exceptions.RequestException as e:
        print(e)
        return []


def list_files(dir):
    list_dirs = os.walk(dir)
    for root, dirs, files in list_dirs:
        for f in files:
            if f == ".DS_Store":
                continue
            fullpath = os.path.join(root, f)
            print f
            music = eyed3.load(fullpath)
            keyword = f
            if music is not None and music.tag.artist != "" and music.tag.title != "":
                keyword = music.tag.artist + " " + music.tag.title
            save_lyric(keyword,os.path.dirname(fullpath))


def save_lyric(f, path):
    song = search_song_by_name(f)
    lyric = path + "/" + song['name'] + ".lyc"
    with open(lyric, "w+") as f:
        print(song_lyric(song['id']))
        f.write(song_lyric(song['id']))

if __name__ == '__main__':
    # print get_artist_albums({"id": 893259})
    # download_album_by_search('AKB48','/Users/book/Desktop/TS')
    # song = search_song_by_name('成都 赵雷')
    # print("song!", song)
    # lyric = "/Users/book/Desktop/" + song['name'] + ".lyc"
    # with open(lyric, "w+") as f:
    #     print(song_lyric(song['id']))
    #     f.write(song_lyric(song['id']))
    list_files("/Volumes/Macinsh/Music/iTunes/Music/李健/")
    # tag = eyed3.load("/Volumes/Macinsh/Music/iTunes/Music/李健/似水流年/远.mp3")
    # print tag.tag.artist