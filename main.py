# -*- coding: utf-8 -*-
CharEncoding = 'utf-8'

from flask import Flask, render_template, request, url_for, session, g, redirect, abort, flash
import bs4
from bs4 import BeautifulSoup
import urllib.request
import sqlite3
from contextlib import closing
import numpy as np
import MeCab


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


# DBに格納する関数
@app.route("/insert")
def db_insert():

    cur = g.db.execute('select name from teachers')
    names = [dict(name=row[0]) for row in cur.fetchall()]
    if len(names) == 0: # テーブルが空の時のみ挿入
        for teacher_index in range(len(name_list)): #教師のループ
            # if(teacher_index == 15): # 稗方研のみHTMLの構造が違う
            if(teacher_index != 15):
                # 教員名をレコードに追加
                titles_list = [] # 見出しリスト
                contents_list = [] # レコード

                url_text = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[teacher_index]
                html = urllib.request.urlopen(url_text)
                soup = BeautifulSoup(html,"lxml")
                titles_list = soup.find_all("th")
                contents_list.append(name_list[teacher_index])

                # キーワードが含まれる文章を
                sentences = ""
                for title in titles_list:
                    content = title.nextSibling.nextSibling
                    if (title.string in [ u"研究テーマ", u"研究室の紹介", u"備考"]) or ( u"卒業論文" in title.string):
                        sentences += content.get_text() # テキストを取得するにはget_text()がstringよりも便利．

                noun_list = []
                type_list = []

                tagger = MeCab.Tagger()
                tagger.parse('')  # これを追記することでUnicodeError解決
                node = tagger.parseToNode(sentences)

                while node:
                    if node.feature.split(",")[0] == u"名詞" and node.surface != None:
                        noun_list.append(node.surface)
                        type_list.append(node.feature)
                    node = node.next

                keyword_list = []
                for index in range(len(noun_list)):
                    types = type_list[index].split(",")
                    if types[1] in [ u"代名詞", u"非自立", u"接尾", u"数", u"副詞可能"]:
                        pass
                    elif len(types) >= 7 and types[6]== "*":
                        pass
                    else:
                        keyword_list.append(noun_list[index])

                # キーワードをレコードに追加
                keyword_count = {}
                for keyword in keyword_list:
                    keyword_count.setdefault(keyword,0)
                    keyword_count[keyword] += 1

                keyword_count = sorted(keyword_count.items(),key=lambda x:x[1],reverse=True)

                keywords = ""
                for word, count in keyword_count:
                    if count >= 2:
                        keywords += word + ":" + str(count) + " "

                contents_list.append(keywords)

                # 画像をレコードに追加(手つかず)

                # レコードをDBに追加
                g.db.execute('insert into teachers (name, keywords) values(?,?)',[content for content in contents_list])
                g.db.commit()

    return redirect(url_for('db_show')) # リダイレクトは関数名を指定


# DB表示のための関数
@app.route("/db")
def db_show():
    # 抽出
    cur = g.db.execute('select name, keywords from teachers')
    table = [dict(name=row[0],keywords=row[1]) for row in cur.fetchall()]

    return render_template('show_data.html', teachers_table = table)


# データ削除のための関数
# @app.route('/deleted', methods=['POST']) # POSTリクエストのみが受け付けられる
# def delete_posts():
#     g.db.execute('delete from teachers ')
#     g.db.commit()
#     return redirect(url_for('index')) #


# レコメンド
@app.route("/recomend", methods=['POST'])
def recomend():
    url = "http://livedoor.4.blogimg.jp/laba_q/imgs/b/d/bd0839ac.jpg"
    user = request.form["user"]
    message1 = request.form["message1"]
    message2 = request.form["message2"]

    # DBから抽出するための準備
    cur = g.db.execute('select name, keywords from teachers')
    keyword_array = [dict(name=row[0], keywords=row[1]) for row in cur.fetchall()]

    suggest1=[]
    suggest2=[]
    suggest3=[]
    recommend=[]

    for i in range(len(url_list)-1): #稗方先生の分無理やり調整してる．あとで直す．
        link = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[i]
        sentences = keyword_array[i]["keywords"] # キーワードを抽出
        if message1 in sentences:
            suggest1.append(link)
    print(suggest1)
    for i in range(len(url_list)-1):
        link = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[i]
        sentences = keyword_array[i]["keywords"]
        if message2 in sentences:
            suggest2.append(link)

    #setに変換して論理演算可能に
    suggest1_set = set(suggest1)
    suggest2_set = set(suggest2)
    suggest3 = list(suggest1_set ^ suggest2_set)
    recommend = list(suggest1_set & suggest2_set)

    #まずmessage1かつmessage2が入っているurlを入れる
    for i in range(len(suggest3)):
        recommend.append(suggest3[i])

    #recommendが少なくとも２つ要素を持つようにチンパンジーの画像で調整
    if len(recommend) ==0:
        recommend.append("http://livedoor.4.blogimg.jp/laba_q/imgs/b/d/bd0839ac.jpg")
        recommend.append("http://livedoor.4.blogimg.jp/laba_q/imgs/b/d/bd0839ac.jpg")
    if len(recommend)==1:
        recommend.append("http://livedoor.4.blogimg.jp/laba_q/imgs/b/d/bd0839ac.jpg")


    return render_template('result.html', user=user,
    message1 = message1, message2 = message2,
    url1 = recommend[0], url2 = recommend[1])


# アプリ起動
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
