# _*_ coding: utf-8 _*_
from flask import Flask, jsonify, request, render_template
import math
from baidu import savetodb
from models.words import Words, PinYin
from models.keys import Keys
from models.base import db
from sqlalchemy import or_, and_
import random

app = Flask(__name__, static_url_path='/dictionary/static')
# 引用config文件，获取数据库相关配置
import config
app.config.from_object(config)
# 解决跨域问题
from flask_cors import CORS
cors = CORS()
cors.init_app(app, resources={"/*": {"origins": "*"}})
# 连接数据库
db.init_app(app)
with app.app_context():  # 手动将app推入栈
    db.create_all()  # 首次模型映射(ORM ==> SQL),若无则建表; 初始化使用

# 這個方法用來轉變model成字典dict，但是不是依據keys，後append的不會被轉入
# def serialize(model):
#     from sqlalchemy.orm import class_mapper
#     columns = [c.key for c in class_mapper(model.__class__).columns]
#     return dict((c, getattr(model, c)) for c in columns)

@app.route("/dictionary/page/<int:page>/")
def page(page):
    page = '000' + str(page)
    page = page[len(page)-4:len(page)]
    src = "https://jay.thathome.cn/dictionary/static/img/dictionary/%s.png" % page
    pp = "https://jay.thathome.cn/dictionary/page/%s/" % str(int(page) - 1)
    pn = "https://jay.thathome.cn/dictionary/page/%s/" % str(int(page) + 1)
    html = "<div style='width:100%%;padding-top:50px;'><h2><span style='float:left;padding:0 10%%;'>當前頁碼：%s</span>" % page
    html += "<a style='float:right;padding:0 10%%;' href='%s'>下頁</a><a style='float:right;' href='%s'>上頁</a></h2>" % (pn, pp)
    html += "<image style='width:100%%;' src='%s' /></div>" % src
    return html


@app.route("/dictionary/getbaidu/<int:start>/<int:size>/<int:page>/")
def getbaidu(start, page, size):
    # 搜到的字符为0x4e00(19968)到0x9fbf，测试到了0x9fea“鿪”(40938)
    total = 40939 - start
    pages = math.ceil(total / size)
    print('正在执行第 %s 页，一共 %s 页' % (page , pages))
    print('=' * 80)
    text = savetodb(page, size, start)
    return text

@app.route("/dictionary/setpinyin/<int:start>/<int:end>/")
def setpinyin(start, end):
    for i in range(start, end + 1):
        word = Words.query.filter(Words.id == i).first()
        if word and len(word.pinyin) > 0:
            pinyin = word.pinyin.split('_')
            for py in pinyin:
                py = py.replace('ī','i').replace('í','i').replace('ǐ','i').replace('ì','i')
                py = py.replace('ū','u').replace('ú','u').replace('ǔ','u').replace('ù','u')
                py = py.replace('ǖ','ü').replace('ǘ','ü').replace('ǚ','ü').replace('ǜ','ü')
                py = py.replace('ā','a').replace('á','a').replace('ǎ','a').replace('à','a')
                py = py.replace('ē','e').replace('é','e').replace('ě','e').replace('è','e')
                py = py.replace('ō','o').replace('ó','o').replace('ǒ','o').replace('ò','o')
                oldpy = PinYin.query.filter(
                    and_(
                        PinYin.id == str(i), 
                        PinYin.py == py
                    )
                ).first()
                if not oldpy:
                    with db.auto_commit():
                        newpy = PinYin()
                        newpy.id = i
                        newpy.py = py
                        db.session.add(newpy)
    return 'ok'

@app.route("/dictionary/setkeys/<types>/", methods=['GET', 'POST'])
@app.route("/dictionary/setkeys/<types>/<page>/", methods=['GET', 'POST'])
def setkeys(types, page = None):
    key = ''
    keys = ''
    if request.method == 'POST': 
        page = request.form['page']
        oldkeys = Keys.query.filter(Keys.page == page).first()
        if not oldkeys:
            key = request.form['key']
            keys = request.form['keys']
            keys2 = request.form['keys2']
            if keys2 and keys2 != '':
                keys += '_' + keys2
            if types == 'pinyin':
                keys = keys.replace('i1','ī').replace('i2','í').replace('i3','ǐ').replace('i4','ì')
                keys = keys.replace('u1','ū').replace('u2','ú').replace('u3','ǔ').replace('u4','ù')
                keys = keys.replace('v1','ǖ').replace('v2','ǘ').replace('v3','ǚ').replace('v4','ǜ').replace('v','ü')
                keys = keys.replace('a1','ā').replace('a2','á').replace('a3','ǎ').replace('a4','à')
                keys = keys.replace('e1','ē').replace('e2','é').replace('e3','ě').replace('e4','è')
                keys = keys.replace('o1','ō').replace('o2','ó').replace('o3','ǒ').replace('o4','ò')
            elif types == 'bihua':
                keys = keys.replace('_', '至')
                if '畫' not in keys:
                    keys += '畫'
            keylist = key.split(',')
            for item in keylist:
                oldkeys = Keys.query.filter(Keys.key == item).first()
                if len(keylist) == 1 or not oldkeys:
                    with db.auto_commit():
                        newkeys = Keys()
                        newkeys.page = page
                        newkeys.keyword = item
                        newkeys.pagetitle = keys
                        db.session.add(newkeys)
            page = int(page) + 1
            keys = keys.replace('至', '_').replace('畫', '')
            if '_' in keys:
                ks = keys.split('_')
                keys = ks[len(ks) - 1]
    resp_data = dict(
        page='setkeys',
        thispage=page if page else '5353',
        thiskey='',
        thiskeys=keys if keys else '',
        types=types,
        name='目录索引创建'
    )
    return render_template('input.html', **resp_data)

@app.route("/dictionary/setword/", methods=['GET', 'POST'])
@app.route("/dictionary/setword/<auto>/", methods=['GET', 'POST'])
def setword(auto = ''):
    wordlist = []
    lastinput = []
    if request.method == 'POST': 
        word = request.form['word']
        page = request.form['page']
        forced = True if '!' in page else False
        page = page.replace('!', '').replace('！', '')
        if len(word) >= 2 and len(word) <=5 and len(page) == 0:
            page = word[1:5]
            word = word[0:1]
        if len(word) > 0 and len(page) > 0:
            words = Words.query.filter(Words.hanzi == word).first()
            page = '000' + str(page)
            page = page[len(page)-4:len(page)]
            if words and page != '000 ' and ( words.page == '' or words.page == '0000' or forced ):
                with db.auto_commit():
                    words.page = page
                    words.check = 8
                page += ' 成功'
            else:
                page += ' 失敗'
        lastinput += [[page, "最近錄入「%s」" % word]]
    if auto == 'auto':
        text = 'newlist.txt'
        import os
        with open(text, "r", encoding='utf-8') as f:
            text = f.read()
            f.close()
        items = text.split('\n')
        count = 0
        for i in range(0, len(items)):
            ws = items[i].split(',')
            if len(ws) > 2 and len(ws[1]) == 1:
                thisw = Words.query.filter(Words.hanzi == ws[1]).first()
                if thisw and thisw.page == '':
                    count += 1
                    wordlist += [[ws[0],ws[1]]]
            if count == 4:
                wordlist += [[len(items) - i , "剩余字数"]]
                break
        auto = wordlist[0][1]
    resp_data = dict(
        page='setword',
        word=auto,
        wordlist=wordlist + lastinput,
        name='錄入漢字檢索索引' + (' 「%s(%s)」' % (auto, wordlist[0][0]) if auto != '' else '')
    )
    return render_template('input.html', **resp_data)

@app.route("/dictionary/setwords/")
def setwords():
    success = 0
    text = 'list.txt'
    import os
    if os.path.exists(text):
        with open(text, "r", encoding='utf-8') as f:
            text = f.read()
            f.close()
    items = text.split('\n')
    for item in items:
        ws = item.split(',')
        if len(ws) > 3 and len(ws[1]) == 1 and len(ws[2]) > 1:
            words = Words.query.filter(Words.hanzi == ws[1]).first()
            if words and words.page == '':
                page = '000' + ws[2]
                page = page[len(page)-4:len(page)]
                with db.auto_commit():
                    words.page = page
                    words.check = 8
                success += 1
    return "总共有%s条数据，成功录入%s条数据！" % (str(len(items)), str(success))
    

@app.route("/dictionary/getwordlist/<pinyin>/<int:bihua>/<int:bhrange>/<int:jianti>/<int:fanti>/<int:bushou>/<int:page>/")
def getwordlist(pinyin, bihua, bhrange, jianti, fanti, bushou, page):
    param = []
    if bihua > 0:
        if bhrange > 0:
            param.append(Words.bihua >= bihua - bhrange)
            param.append(Words.bihua <= bihua + bhrange)
        else:
            param.append(Words.bihua == bihua)
    if jianti > 0:
        param.append(Words.jianti.like("%" + chr(jianti) + "%"))
    if fanti > 0:
        param.append(Words.fanti.like("%" + chr(fanti) + "%"))
    if bushou > 0:
        param.append(Words.bushou.like("%" + chr(bushou) + "%"))
    if pinyin != 'empty':
        param.append(PinYin.py == pinyin,)
        wordlist = Words.query.join(PinYin).filter(*param).paginate(
            page=page, per_page=60,error_out=False, max_per_page=None
        )
    else:
        wordlist = Words.query.filter(*param).paginate(
            page=page, per_page=60,error_out=False, max_per_page=None
        )
    if not wordlist:
        word_dict = {'code': 0, 'msg': '沒有找到數據！'}
    else:
        word_dict = []
        for word in wordlist.items:
            word_dict += [ word.hanzi ]
        word_dict = {'code': 100, 'data': {'total': wordlist.total, 'has_next': wordlist.has_next, 'page': page, 'items': word_dict } }
    return jsonify(word_dict)

@app.route("/dictionary/getword/<int:num>/")
def getword(num):
    if num == 0:
        num = random.randint(19968, 40892)
    word = Words.query.filter(Words.id == num).first()
    if not word:
        word_dict = {'code': 0, 'msg': '沒有找到數據！'}
    else:
        word_dict = {'code': 100, 'data': dict(word)}
        word_dict['data']['page'] = str(word_dict['data']['page'])
    return jsonify(word_dict)

@app.route("/dictionary/getkeys/<types>/<value>/")
def getkeys(types, value):
    if types == 'pinyin':
        keys = Keys.query.filter(Keys.keyword == value.lower()).first()
    if types == 'bihua' and int(value) > 0:
        keys = Keys.query.filter(Keys.keyword == value).first()
        while not keys:
            value = str(int(value) - 1)
            keys = Keys.query.filter(Keys.keyword == value).first()
    if types == 'page':
        keys = Keys.query.filter(Keys.page == value).first()
    if not keys:
        keys_dict = {'code': 0, 'msg': '沒有找到數據！'}
    else:
        keys_dict = {'code': 100, 'data': dict(keys)}
        keys_dict['data']['keys'] = keys.pagetitle
    return jsonify(keys_dict)

@app.route("/dictionary/setpage/<types>/<int:num>/<page>/")
def setpage(types, num, page):
    word = Words.query.filter(Words.id == num).first()
    if word:
        if word.page.replace(' ', '') == '' or word.page == page:
            check = word.check
            if types == "up" and check < 9:
                check += 1
            elif types == "down" and check > 0:
                check -= 1
            with db.auto_commit():
                word.page = page if check > 0 else ''
                word.check = check
    return jsonify({'code': 100, 'msg': '感謝您的反饋！'})

@app.route("/dictionary/notice/")
def notice():
    title = '<h2 style="font-size:24px;padding:80px 10px 0;font-weight:100;">今日詩句：</h2>'
    import requests
    text = requests.get('https://v1.jinrishici.com/all.txt').text
    # text = text.replace('，', '，<br />')
    text = '<p style="font-size:16px;color:#8F8F8F;padding:4px 10px;font-weight:200;">%s</p>' % text
    return jsonify({'code': 100, 'msg': title + text})

@app.route("/dictionary/")
def index():
    return '<h1>Welcome!</h1>Dictionary<br />Yuan is the best!'

@app.errorhandler(404)
def page_miss(e):
    return '<h1>PAGE 404 ! </h1>Dictionary<br />Yuan is the best!'

@app.errorhandler(500)
def page_error(e):
    return '<h1>PAGE 500 ! </h1>Dictionary<br />Yuan is the best!'

if __name__ == "__main__":
    app.run(debug=True)