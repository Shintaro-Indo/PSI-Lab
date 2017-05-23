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
import difflib


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


# リストの初期化
url_list = [] # 例：'aichi.html'
name_list = [] # 例："愛知 正温 講師"

# 教員のname_list, url_listを作成
original_url = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/index.html"
html_index = urllib.request.urlopen(original_url)
soup_index = bs4.BeautifulSoup(html_index.read(),"lxml")
a_tag_all = soup_index.find_all('a')
a_tag_list = a_tag_all[2:-1] # スライスで該当箇所のみ抽出
for a_tag in a_tag_list:
    url_list.append(a_tag.attrs['href'])
    name_list.append(a_tag.string)


img_list = ["img/teach_aichi.jpg","img/teach_aoyama.jpg","img/teacher_abe.jpg",
            "img/teach_ihara.jpg","img/teach_ozaki.jpg","img/teach_kageyama.jpg",
            "img/teach_kuriyama.jpg","img/teach_kuriyama.jpg","img/teach_shibanuma.png",
            "img/teach_shirayama.jpg","img/teach_suzuki2.jpg","img/teach_f_takeda.jpg",
            "img/teach_tanaka2.jpg","img/teacher_nawata.jpg","img/teacher_nishino.jpg",
            "img/teacher_hiekata.jpg","img/teach_fujita.jpg","img/teach_matsuo.jpg",
            "img/teach_matsushima2.jpg","img/teach_murayama2.jpg","img/teach_mogi.jpg",
            "img/teach_motohashi2.jpg","img/teach_yoshida2.jpg",
            "img/teach_yamaguchi.jpg","img/teach_rokugawa.jpg"]

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

            # レコードを準備
            contents_list = []

            # 教員名をレコードに追加
            contents_list.append(name_list[teacher_index])

            # タイトルリストを作成
            titles_list = [] # 見出しリスト
            url_text = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[teacher_index]
            html_name = urllib.request.urlopen(url_text)
            soup_name = BeautifulSoup(html_name,"lxml")
            titles_list = soup_name.find_all("th")

            # キーワードが含まれそうな文章を結合
            sentences = ""
            for title in titles_list:
                content = title.nextSibling.nextSibling
                if (title.string in [ u"研究テーマ", u"研究室の紹介", u"備考"]) or ( u"卒業論文" in title.string):
                    sentences += content.get_text() # テキストを取得するにはget_text()が.stringよりも便利．

            # sentencesをMeCabを使って形態素解析
            tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd') # mecab-ipadic-NEologd
            # tagger = MeCab.Tagger() #　デフォルトの辞書(mecab-ipadic-NEologd)バージョン
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
                elif len(types) >= 7 and types[6] == "*": # 記号を削除
                    pass
                elif noun_list[index] in [u"研究", u"研究室", u"科学", u"テーマ"]:
                    pass
                else:
                    keyword_list.append(noun_list[index])


            # tf値を使ってどの研究室にも共通するようなキーワードを排除(手付かず)


            # キーワードと出現回数をディクショナリに保存
            keyword_count = {}
            for keyword in keyword_list:
                keyword_count.setdefault(keyword,0)
                keyword_count[keyword] += 1
            keyword_count = sorted(keyword_count.items(),key=lambda x:x[1],reverse=True) # 出現回数が多い順に並び替え

            # 出現回数が三回以上のキーワードを一文にまとめる．
            keywords = ""
            for word, count in keyword_count:
                if count >= 2:
                    keywords += word + ":" + str(count) + " "

            # キーワードをレコードに追加．
            contents_list.append(keywords)

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

    return render_template('db.html', teachers_table = table)


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

    message_list  = request.form.getlist("message[]") # ユーザーからの入力が配列として格納される

    # 入力がない場合は入力を促す
    if message_list[0] == "":
        error = "興味のある分野を入力してください"
        return render_template('index.html', error_message = error)

    # 入力があった場合
    else:
        score_list = [] # 各教員のキーワードとの類似度

        # 教員ごとのscoreを計算
        for teacher_index in range(len(name_list)):

            score = 0 # 類似度の平均
            similarity_total = 0 # 類似度の合計
            count_total = 0

            # DBからキーワード文全体を抽出
            cur = g.db.execute('select name, keywords from teachers')
            table = [dict(name=row[0],keywords=row[1]) for row in cur.fetchall()]
            sentences = table[teacher_index]["keywords"]

            # キーワード文からキーワードと出現回数を単語ごとに抽出
            keyword_count_list = sentences.split(" ")

            # ユーザーからのメッセージごとのループ
            for message in message_list:

                # 一致判定
                score += sentences.count(message)

                # キーワードごとのループ
                for keyword_count in keyword_count_list:
                    if len(keyword_count.split(":")) == 2:
                        keyword = keyword_count.split(":")[0]
                        count = int(keyword_count.split(":")[1])
                        count_total += count
                        similarity = difflib.SequenceMatcher(None, message, keyword).ratio() * count # 類似度
                        similarity_total += similarity * count

                score += difflib.SequenceMatcher(None, message, keyword).ratio() / count_total


            # score = similarity_total / count_total

            score_list.append(score)

        # レコメンドする研究室のインデックスを取得
        score_array = np.array(score_list)
        recomend_index1 = score_array.argsort()[::-1][0]
        recomend_index2 = score_array.argsort()[::-1][1]
        recomend_index3 = score_array.argsort()[::-1][2]

        return render_template(
            'result.html',

            message = message_list,

            url1 = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[recomend_index1],
            url2 = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[recomend_index2],
            url3 = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[recomend_index3],

            img_url1 = "http://www.si.t.u-tokyo.ac.jp/psi/teachers/"+ img_list[recomend_index1],
            img_url2 = "http://www.si.t.u-tokyo.ac.jp/psi/teachers/"+ img_list[recomend_index2],
            img_url3 = "http://www.si.t.u-tokyo.ac.jp/psi/teachers/"+ img_list[recomend_index3],

            name1 = name_list[recomend_index1],
            name2 = name_list[recomend_index2],
            name3 = name_list[recomend_index3]
        )

# アプリ起動
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
