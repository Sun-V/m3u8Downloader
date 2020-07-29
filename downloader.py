#!/usr/bin/python
# -*- coding: UTF-8 -*-

from urlparse import urljoin
import requests
import urllib
import os
from xpinyin import Pinyin

_videoName = ''

def get_url_list(url, body):
    lines = body.split('\n')
    ts_url_list = []
    for line in lines:
        if not line.startswith('#') and line != '':
            if line.startswith('http'):
                ts_url_list.append(line)
            else:
                ts_url = urljoin(url, line)
                ts_url_list.append(ts_url)
    return ts_url_list

def get_m3u8_body(url):
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=10)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    r = session.get(url, timeout=10)
    return r.content

def download_ts_file(ts_url_list, download_dir):
    i = 0
    global _videoName
    outfile_path = os.path.join(download_dir, _videoName+'.ts')
    if os.path.isfile(outfile_path):
        print '\n[Warning]: %s already exist!' % (_videoName)
        return
    for ts_url in reversed(ts_url_list):
        i += 1
        file_name = ts_url[ts_url.rfind('/'):]
        curr_path = '%s%s' % (download_dir, file_name)
        print '\n[Downloading]: %s' % (_videoName)
        print '[Processing]: %s/%s' % (i, len(ts_url_list))
        print '[Target]:', curr_path
        if os.path.isfile(curr_path):
            print '\n[Warning]: %s already exist!' % (file_name)
            continue
        urllib.urlretrieve(ts_url, curr_path)
    merge_file(ts_url_list, download_dir)
    print '\n[Downloaded]: %s' % (_videoName)

def merge_file(ts_list, dir):
    index = 0
    outfile = ''
    ts_total = len(ts_list)
    while index < ts_total:
        file_name = ts_list[index].split('/')[-1].split('?')[0]
        infile = open(os.path.join(dir, file_name), 'rb')
        if not outfile:
            global _videoName
            outfile_path = os.path.join(dir, _videoName+'.ts')
            if os.path.isfile(outfile_path):
                print '\n[Warning]: %s already exist!' % (_videoName)
                break
            outfile = open(outfile_path, 'wb')
        outfile.write(infile.read())
        infile.close()
        os.remove(os.path.join(dir, file_name))
        index += 1
    if outfile:
        outfile.close()

def main(url, download_dir):
    body = get_m3u8_body(url)
    ts_url_list = get_url_list(url, body)
    download_ts_file(ts_url_list, download_dir)

if __name__ == '__main__':
    videoNameList=[]
    fi = open('name', 'rb')
    for line in fi.readlines():
        vn = line.decode('utf-8','ignore').strip()
        videoNameList.append(vn)
    fi.close()

    p = Pinyin()
    download_dir='D:/Download/kaishu/'
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    for videoname in videoNameList:
        _videoName = videoname
        py = p.get_pinyin(videoname, '')
        if videoname == u'练字方法':
            py = u'kaishupiantou'
        if videoname == u'左右对称':
            py = u'zuoyouduichen'
        if videoname == u'联撇参差':
            py = u'lianpiecenci'
        url = 'http://www.scwj.net/media/video/changxiao/kaishutongyong/'+py+'.m3u8'
        main(url, download_dir)

    print '\n[Finished].'
