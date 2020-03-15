# _*_ coding: utf-8 _*_
import requests
import random
import os
import re
import time
import math
from models.words import Words
from models.base import db

def savetodb(page, size, start=19968):
    text = '失败列表：\n'
    # 搜到的字符为0x4e00到0x9fbf，测试到了0x9fea“鿪”(40938)
    for num in range(start + ((page - 1) * size), start + (page * size)):
        if num > 40938:
            break
        info = Baidu(chr(num))
        if info:
            with db.auto_commit():
                newwords = Words()
                newwords.id = num
                newwords.hanzi = info[0]
                newwords.pinyin = info[1]
                newwords.bushou = info[2]
                newwords.bihua = int(info[3])
                newwords.fanti = info[4]
                newwords.shiyi = info[5]
                db.session.add(newwords)
        else:
            text += str(num) + ':' + chr(num) + '\n'
    return text

def Baidu(word):
    url = 'https://hanyu.baidu.com/s?wd=%s&ptype=zici' % word
    r = str(requests.get(url).text)
    # 拼音
    pinyin = re.findall(r'pronounce.*?id="pinyin">([\s\S]*?)</div>', r)
    if not pinyin:
        return None
    pinyin = re.findall('<b>(.*)</b>', pinyin[0])
    word_py = ''
    for py in pinyin:
        word_py += py + '_'
    word_py = word_py[0:len(word_py)-1]
    # 部首
    word_bs = ''
    bushou = re.findall(r'<li id="radical">([\s\S]*?)</li>', r)
    if bushou:
        bushou = re.findall(r'<span>(.*)\n*</span>', bushou[0])
        word_bs = bushou[0]
    # 笔划
    word_bh = 0
    bihua = re.findall(r'<li id="stroke_count">([\s\S]*?)</li>', r)
    if bihua:
        bihua = re.findall('<span>(.*)</span>', bihua[0])
        word_bh = bihua[0]
    # 繁体
    word_ft = ''
    fanti = re.findall(r'<li id="traditional">([\s\S]*?)</li>', r)
    if fanti:
        fanti = re.findall('<span>(.*)</span>', fanti[0])
        word_ft = fanti[0].replace('、','')
    # 释义
    shiyi = re.findall(r'基本释义[\s\S]*?<div class="tab-content">([\s\S]*?)</div>', r)
    word_sy = shiyi[0].replace('\n','').replace('  ', '')
    return word, word_py, word_bs, word_bh, word_ft, word_sy

# # 搜到的字符为0x4e00(19968)到0x9fbf，测试到了0x9fea“鿪”(40938)
# total = 40938 - 19967
# total = 10
# size = 4
# pages = math.ceil(total / size)
# for i in range(1, pages):
#     print('正在执行第 %s 页，一共 %s 页' % (i , pages))
#     print('=' * 80)
#     Unicode(i, size)