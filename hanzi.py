import random
import os
import re

def Unicode():
    val = random.randint(0x4e00, 0x9fbf)
    return chr(val)

def savelist():
    src = 'word.txt'
    with open(src, "r") as f:
        words = f.read()
        f.close()
    w = str(words)
    daxie = re.findall('([a-z]+) +(.+)',w)
    lists = []
    i = 0
    for dx in daxie:
        for d in dx[1]:
            lists += [[dx[0],d]]
            i += 1
    for l in lists:
        count = 0
        for item in lists:
            if l[1] == item[1]:
                count += 1
            if count > 1:
                l[0] += '_' + item[0]
                item[0] = '[重]'
                count -= 1
    text = 'list_new\n'
    for items in lists:
        text += items[0] + ',' + items[1] + ',\n'
    # print(lists)
    with open('list_new.xls', "a+") as f:
        f.write(text)
        f.close()

savelist()