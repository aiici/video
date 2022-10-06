from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3
import requests
from lxml import etree
import re


UPLOAD_FOLDER = 'static/vedios
app = Flask(__name__)
app.secret_key = '123456'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
data_base = sqlite3.connect('reocords', check_same_thread=False)
cursor = data_base.cursor()
cursor.execute('create table if not exists uploads(info text);')
data_base.commit()


def getrecords():
    cursor.execute('select * from uploads;')
    results = cursor.fetchall()
    records = []
    for r in results:
        records.append(eval(r[0]))
    return records


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',

}


def get_m3u8(Burl):
    url = "https://players.yunque.vip/Json.php"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50",
        "url": Burl,
        "key": "https://v.yunque.vip",
    }
    context = requests.post(url, headers).json()
    url_m3u8 = context["url"]
    return url_m3u8


def get_url(url):
    data = requests.get(url, headers).text
    ex = r'https://play.freeok.vip/OKPlayer/?url=.*'
    out = re.findall(ex, data, re.I)
    return out


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        records = getrecords()
        return render_template('index.html', records=records[::-1])

    else:  # post方法
        name = request.form.get('scon')
        url = "https://v.yunque.vip/index.php/vod/search.html?wd=%s" % name
        context = requests.get(url, headers).text
        ex = r'index.php/vod/detail/id/.*.html'
        data = re.findall(ex, context, re.I)
        flash(name)
        detail = requests.get("https://v.yunque.vip/" + data[0], headers).text
        ji_list = etree.HTML(detail)
        url_list = ji_list.xpath('//*[@id="panel1"]/div/div/a/@href')
        if len(name) > 0:
            num = ji_list.xpath("//*[@id='y-playList']/div[2]/small//text()")[0]
            num = int(num)
            for i in range(0, num):
                # res = requests.get("https://v.yunque.vip" + url_list[i], headers).text
                data_url = "https://v.yunque.vip" + url_list[i]

                record = {"filename": f"第{i + 1}集", "date": data_url}
                cursor.execute('insert into uploads (info) VALUES (\"%s\");' % (record))
        data_base.commit()
        records = getrecords()
        cursor.execute("delete from uploads;")
        return render_template('index.html', records=records)


@app.route("/player", methods=['GET'])
def player(date):
    print(date)
    detail_info = requests.get(date, headers).text
    print(detail_info)
    path = "../" + app.config['UPLOAD_FOLDER'] + "/" + date

    return render_template('player.html', path=path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, port=5000)
