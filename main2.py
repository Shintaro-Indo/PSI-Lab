from flask import Flask, render_template, request, url_for, session, g, redirect, abort, flash
import bs4
from bs4 import BeautifulSoup
import urllib.request
import sqlite3
from contextlib import closing



app = Flask(__name__)

#DB用
# # 各種設定
# DATABASE = "main.db"
# DEBUG = True
# SECRET_KEY = 'development key'
# # USERNAME = 'admin'
# # PASSWORD = 'default'
# app.config.from_object(__name__) # 与えられたオブジェクトの内で大文字の変数をすべて取得する．
# app.config.from_envvar("TEST_SETTINGS", silent=True) # silent=Truel??

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
# def before_request():
#     g.db = connect_db() # g：とりあえず全てを格納する変数．データベースのコネクションやログインしてるユーザ情報など．
#
# # データベースのリクエスト後に呼ばれ，データベースのクローズなどを行う
# @app.teardown_request
# def teardown_request(exception):
#     db = getattr(g, "db", None)
#     if db is not None:
#         db.close()



original_url = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/index.html"　#トップページ
soup = bs4.BeautifulSoup(urllib.request.urlopen(original_url).read(),"lxml")
a_tag = soup.find_all('a')
url_list = []
for link in a_tag:
    if 'href' in link.attrs:
        url_list.append(link.attrs['href'])　#教授ごとのリンクをリストに


#各教授のページからキーワードリストを作成
def find_keywords(url):
    soup = bs4.BeautifulSoup(urllib.request.urlopen(url).read(),"lxml")
    keys = soup.find_all('li')
    key_list = []
    for t in keys:
        key_list.append(t.get_text())
    return key_list


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/add", methods=['POST'])
def add():
    user = request.form["user"]
    message = request.form["message"]
    for i in range(2,len(url_list)):　#[0],[1]はindex.html(トップページ)
        link = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[i]
        key_list = []
        key_list = find_keywords(link)
        for j in range(len(key_list)):
            if message in key_list[j]:
                url = link #この""は文字列と認識するためのもの
                break
        
        # else:
        #     url = "http://livedoor.4.blogimg.jp/laba_q/imgs/b/d/bd0839ac.jpg"
    return render_template('page1.html', user=user, message = message, url = url)

#
# @app.route("/data")
# def data():
#     for p in system:
#         g.db.execute('insert into system (paragraph) values (?)', [p])
#         g.db.commit()
#     cur = g.db.execute('select paragraph from system order by id desc')
#     data = [dict(paragraph=row[0]) for row in cur.fetchall()]
#     return render_template('data.html',tmi = tmi, system = system, system_table = data)
#

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
