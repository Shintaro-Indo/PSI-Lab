from flask import Flask, render_template, request, url_for, session, g, redirect, abort, flash
import bs4
from bs4 import BeautifulSoup
import urllib.request
import sqlite3
from contextlib import closing


# # 各種設定
# DATABASE = "main.db"
# DEBUG = True
# SECRET_KEY = 'development key'
# # USERNAME = 'admin'
# # PASSWORD = 'default'


app = Flask(__name__)
app.config.from_object(__name__) # 与えられたオブジェクトの内で大文字の変数をすべて取得する．
app.config.from_envvar("TEST_SETTINGS", silent=True) # silent=Truel??


# # DB接続
# def connect_db():
#     return sqlite3.connect(app.config['DATABASE'])


# # DB初期化関数
# def init_db():
#     with closing(connect_db()) as db:
#         with app.open_resource("test.sql", mode="r") as f:
#             db.cursor().executescript(f.read())
#         db.commit()


# # データベースのリクエスト前に呼ばれ，データベース接続などを行う．
# @app.before_request
# # def before_request():
# #     g.db = connect_db() # g：とりあえず全てを格納する変数．データベースのコネクションやログインしてるユーザ情報など．


# # データベースのリクエスト後に呼ばれ，データベースのクローズなどを行う
# @app.teardown_request
# def teardown_request(exception):
#     db = getattr(g, "db", None)
#     if db is not None:
#         db.close()


#システム創成
sys_url = "http://www.sys.t.u-tokyo.ac.jp/research/"
soap_system = bs4.BeautifulSoup(urllib.request.urlopen(sys_url).read(),"lxml")
sys_keys = soap_system.find_all('p')
system=[]
for t in sys_keys:
    system.append(t.get_text())

#TMI
tmi_url = "http://tmi.t.u-tokyo.ac.jp/staff/staff1.htm"
soap_tmi = bs4.BeautifulSoup(urllib.request.urlopen(tmi_url).read(),"lxml")
tmi_keys = soap_tmi.find_all('table')
tmi=[]
for t in tmi_keys:
    text = t.get_text()
    text2 = text.replace("●","  ").replace("／","  ")
    tmi.append(text2)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/add", methods=['POST'])
def add():
    user = request.form["user"]
    message = request.form["message"]
    for i in range(len(system)):
        if message in system[i]:
            url = "http://www.sys.t.u-tokyo.ac.jp/" #この""は文字列と認識するためのもの
            break
        elif i<len(tmi):
            if message in tmi[i]:
                url = "http://tmi.t.u-tokyo.ac.jp/"
                break
        else:
            url = "http://livedoor.4.blogimg.jp/laba_q/imgs/b/d/bd0839ac.jpg"
    return render_template('page1.html', user=user, message = message, url = url, tmi = tmi, system = system)


@app.route("/data")
def data():
    for p in system:
        g.db.execute('insert into system (paragraph) values (?)', [p])
        g.db.commit()
    cur = g.db.execute('select paragraph from system order by id desc')
    data = [dict(paragraph=row[0]) for row in cur.fetchall()]
    return render_template('data.html',tmi = tmi, system = system, system_table = data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
