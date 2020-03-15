# _*_ coding: utf-8 _*_
import requests
import os
import time

def save_img(name, imgformat):
    name = name + '.' + imgformat
    print('正在下载 %s' % name)
    url = "http://s3.cn-north-1.amazonaws.com.cn/lqhanzi-images/dictionaries/zh-dict/" + name
    if not os.path.exists(name):
        r = requests.get(url,stream=True)
        with open(name, 'wb') as fd:
            for chunk in r.iter_content():
                fd.write(chunk)
        # time.sleep(4)

save_img('A01', 'jpg')
save_img('A02', 'jpg')
for j in range(3, 26):
    if j < 10:
        j = 'A0' + str(j)
    else:
        j = 'A' + str(j)
    save_img(j, 'png')

for i in range(1, 5727):
    if i < 10:
        i = '000' + str(i)
    elif i < 100:
        i = '00' + str(i)
    elif i < 1000:
        i = '0' + str(i)
    else:
        i = str(i)
    save_img(i, 'png')