from flask import Flask, render_template, request, url_for, session, g, redirect, abort, flash
import bs4
from bs4 import BeautifulSoup
import urllib.request
import sqlite3
from contextlib import closing
import numpy as np


# 各種設定
DATABASE = "main.db"
DEBUG = True
SECRET_KEY = 'development key'


# アプリのインスタンスを作成
app = Flask(__name__)
app.config.from_object(__name__) # 与えられたオブジェクトの内で大文字の変数をすべて取得する．
app.config.from_envvar("TEST_SETTINGS", silent=True) # silent=Truel??


# DB接続
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


# DB初期化関数
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource("test.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


# データベースのリクエスト前に呼ばれ，データベース接続などを行う．
@app.before_request
def before_request():
    g.db = connect_db() # g：とりあえず全てを格納する変数．データベースのコネクションやログインしてるユーザ情報など．


# データベースのリクエスト後に呼ばれ，データベースのクローズなどを行う
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, "db", None)
    if db is not None:
        db.close()


# name_list, url_listを作成
original_url = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/index.html" # index
html = urllib.request.urlopen(original_url)
soup = bs4.BeautifulSoup(html.read(),"lxml")
a_tag_all = soup.find_all('a')
a_tag_list = a_tag_all[2:-1] # スライスを利用して該当箇所のみ抽出
url_list = []
name_list = []
for a_tag in a_tag_list:
    url_list.append(a_tag.attrs['href'])
    name_list.append(a_tag.string)


# トップページ
@app.route("/")
def index():
    return render_template('index.html')


# DBに格納・DBから抽出する関数
@app.route("/db")
def db():
    cur = g.db.execute('select name from teachers')
    names = [dict(name=row[0]) for row in cur.fetchall()]
    if len(names) == 0: # テーブルが空の時のみ挿入
        for teacher in range(len(name_list)): #教師のループ
            if (teacher != 15):
                titles_list = [] # 見出しを格納するリスト
                contents_list = [] # 文章を格納するリスト
                url = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[teacher]
                html = urllib.request.urlopen(url)
                soup = BeautifulSoup(html,"lxml")
                titles_list = soup.find_all("th")
                contents_list.append(name_list[teacher])

                for title in titles_list: # 見出しのループ
                    content = title.nextSibling.nextSibling
                    if (title.string in ["研究テーマ","研究室の紹介","備考"]) or ("卒業論文" in title.string): # 後々使えそうな文章だけ抽出
                        contents_list.append(content.get_text()) # get_text()が最強だった

            g.db.execute('insert into teachers (name,research_theme,introduction,remarks1,graduation_thesis_theme,aim,contents_and_plan, remarks2)\
                        values(?,?,?,?,?,?,?,?)',[content for content in contents_list])
            g.db.commit()

            # 抽出
            cur = g.db.execute('select name, research_theme, introduction, remarks1, graduation_thesis_theme, aim, contents_and_plan, remarks2 from teachers')
            table = [dict(name=row[0],research_theme=row[1], introduction=row[2], remarks1=row[3], graduation_thesis_theme=row[4], aim=row[5], contents_and_plan=row[6], remarks2=row[7]) for row in cur.fetchall()]
        return render_template('show_data.html', teachers_table = table)

    else: #テーブルが空でない場合は抽出のみを行う
        cur = g.db.execute('select name, research_theme, introduction, remarks1, graduation_thesis_theme, aim, contents_and_plan, remarks2 from teachers')
        data = [dict(name=row[0],research_theme=row[1], introduction=row[2], remarks1=row[3], graduation_thesis_theme=row[4], aim=row[5], contents_and_plan=row[6], remarks2=row[7]) for row in cur.fetchall()]
        return render_template('show_data.html', teachers_table = data)


# レコメンド
@app.route("/recomend", methods=['POST'])
def recomend():
    url = "http://livedoor.4.blogimg.jp/laba_q/imgs/b/d/bd0839ac.jpg"
    user = request.form["user"]
    message = request.form["message"]

    # DBから抽出するための準備
    cur = g.db.execute('select name, research_theme, introduction, remarks1, graduation_thesis_theme, aim, contents_and_plan, remarks2 from teachers')
    table = [dict(name=row[0],research_theme=row[1], introduction=row[2], remarks1=row[3], graduation_thesis_theme=row[4], aim=row[5], contents_and_plan=row[6],\
            remarks2=row[7]) for row in cur.fetchall()]

    for i in range(len(url_list)):
        link = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[i]
        sentences = table[i]["graduation_thesis_theme"] # 卒論テーマの文章を抽出
        if message in sentences:
            url  = link
            break

    return render_template('result.html', user=user, message = message, url = url)


# アプリ起動
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
