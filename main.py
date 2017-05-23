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
app.config.from_envvar("TEST_SETTINGS", silent=True) # silentは設定されていない環境変数をFlaskに伝えないように切り替わる．


# DB接続
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


# DB初期化関数
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource("test.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


# DBのリクエスト前に呼ばれ，DB接続などを行う．
@app.before_request
def before_request():
    g.db = connect_db() # g：とりあえず全てを格納する変数．データベースのコネクションやログインしてるユーザ情報など．


# DBのリクエスト後に呼ばれ，DBのクローズなどを行う
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, "db", None)
    if db is not None:
        db.close()


# 教員のname_list, url_listを作成
url_list = []
name_list = []
original_url = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/index.html"
html_index = urllib.request.urlopen(original_url)
soup_index = bs4.BeautifulSoup(html_index.read(),"lxml")
a_tag_all = soup_index.find_all('a')
a_tag_list = a_tag_all[2:-1] # スライスで該当箇所のみ抽出
for a_tag in a_tag_list:
    url_list.append(a_tag.attrs['href'])
    name_list.append(a_tag.string)


# トップページ
@app.route("/")
def index():
    return render_template('index.html')


# DBに挿入
@app.route("/insert", methods=['POST'])
def db_insert():

    # テーブルが空の時のみ挿入
    cur = g.db.execute('select name from teachers')
    names = [dict(name=row[0]) for row in cur.fetchall()]
    if len(names) == 0:

        # 各教師のループ
        for teacher_index in range(len(name_list)):

            contents_list = [] # レコードとして使用
            titles_list = [] # 見出しリスト

            # 教員名をレコードに追加
            url_text = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[teacher_index]
            html_name = urllib.request.urlopen(url_text)
            soup_name = BeautifulSoup(html_name,"lxml")
            titles_list = soup_name.find_all("th")
            contents_list.append(name_list[teacher_index])

            # キーワードが含まれそうな文章を結合
            sentences = ""
            for title in titles_list:
                content = title.nextSibling.nextSibling
                if (title.string in [ u"研究テーマ", u"研究室の紹介", u"備考"]) or ( u"卒業論文" in title.string):
                    sentences += content.get_text() # テキストを取得するにはget_text()が.stringよりも便利．

            # sentencesをMeCabを使って形態素解析
            tagger = MeCab.Tagger()
            tagger.parse('')  # これを追記することでUnicodeError解決
            node = tagger.parseToNode(sentences)

            noun_list = [] # 名詞リスト
            type_list = [] # 品詞等の情報
            while node:
                if node.feature.split(",")[0] == u"名詞":
                    noun_list.append(node.surface)
                    type_list.append(node.feature)
                node = node.next

            # キーワードになり得ない名詞を排除．
            keyword_list = []
            for index in range(len(noun_list)):
                types = type_list[index].split(",")
                if types[1] in [ u"代名詞", u"非自立", u"接尾", u"数", u"副詞可能"]:
                    pass
                elif len(types) >= 7 and types[6]== "*":
                    pass
                else:
                    keyword_list.append(noun_list[index])

            # キーワードと出現回数をディクショナリに保存
            keyword_count = {}
            for keyword in keyword_list:
                keyword_count.setdefault(keyword,0)
                keyword_count[keyword] += 1
            keyword_count = sorted(keyword_count.items(),key=lambda x:x[1],reverse=True) # 出現回数が多い順に並び替え

            # 出現回数が三回以上のキーワードを一文にまとめる．
            keywords = ""
            for word, count in keyword_count:
                if count >= 3:
                    keywords += word + ":" + str(count) + " "

            # キーワードをレコードに追加．
            contents_list.append(keywords)


            # 画像をレコードに追加(手つかず)




            # レコードをDBに追加
            g.db.execute('insert into teachers (name, keywords) values(?,?)',[content for content in contents_list])
            g.db.commit()

    return redirect(url_for('db_show')) # リダイレクトは関数名を指定


# DBを表示
@app.route("/db")
def db_show():
    # 抽出
    cur = g.db.execute('select name, keywords from teachers')
    table = [dict(name=row[0],keywords=row[1]) for row in cur.fetchall()]

    return render_template('show_data.html', teachers_table = table)


# データ削除
@app.route('/deleted', methods=['POST']) # POSTリクエストのみが受け付けられる
def delete():
    g.db.execute('delete from teachers ')
    g.db.commit()
    return redirect(url_for('db_show'))


# レコメンド
@app.route("/recomend", methods=['POST'])
def recomend():
    url = "http://livedoor.4.blogimg.jp/laba_q/imgs/b/d/bd0839ac.jpg"
    user = request.form["user"]
    message_list  = request.form.getlist("message[]")
    # message1 = message_list[0]
    # message2 = message_list[1]

    # DBから抽出するための準備
    cur = g.db.execute('select name, keywords from teachers')
    keyword_array = [dict(name=row[0], keywords=row[1]) for row in cur.fetchall()]

    suggest1=[]
    suggest2=[]
    suggest3=[]
    recommend=[]

    for message_index in range(len(message_list)):
        message = message_list[message_index]
        for teacher_index in range(len(url_list)):
            link = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[teacher_index]
            sentences = keyword_array[teacher_index]["keywords"] # キーワードを抽出
            if message in sentences:
                suggest1.append(link)
                
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

    # message_list = []
    # message_list.append(message1)
    # if message2:
    #     message_list.append(message2)
    return render_template('result.html', user=user,
    message = message_list,
    url1 = recommend[0], url2 = recommend[1])


# アプリ起動
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
