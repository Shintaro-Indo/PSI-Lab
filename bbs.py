# -*- coding: utf-8 -*-

from __future__ import with_statement
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

from contextlib import closing

# 各種設定
DATABASE = 'bbs.db' # <- チュートリアルと異なる
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# アプリ生成
app = Flask(__name__) # インスタンス作成
app.config.from_object(__name__) # 与えられたオブジェクトの内で大文字の変数をすべて取得する．→ 各種設定の項目のDATABASEやSECRET_KEYなどがapp.configに登録される．
app.config.from_envvar('FLASKR_SETTINGS', silent=True) # ??

# DB接続
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# DB初期化のためのメソッド．$ python >>> from flaskr import init_db >>> init_db() のように，Pythonシェルから関数を実行することで初期化可能．
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('bbs.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# データベース処理の前後で別処理をするための関数1．リクエスト前に呼ばれるので，ここで，データベース接続などを行う．
@app.before_request
def before_request():
    g.db = connect_db() #g：とりあえず何でも格納しておきたいものを格納しておくもので，データベースのコネクションとか，ログインしてるユーザ情報とかを保持しておくのが良い．

# データベース処理の前後で別処理をするための関数2．before_requestの対のafter_requestは例外発生時に呼ばれる保証がないので，代わりにteardown_requestを使い，ここでデータベースのクローズなどを行う
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# 以下はビュー
# データベースに保存されている全てのエントリーの一覧のページ．ルート．
@app.route('/') #アリケーションルートにアクセスが合った場合
def bbs_show_entries(): # show_entries関数が動作
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()] # データベースから全てのエントリーを取り出し，
    return render_template('bbs_show_entries.html', entries=entries) # ここがサーバーサイドからクライアントサイドへなにかを渡すときのポイント

# エントリーを追加するためのページで，ログインしているユーザしかアクセスできない．
@app.route('/add', methods=['POST']) #POSTリクエストのみが受け付けられ，エントリーの追加処理が正常終了するとshow_entriesページにリダイレクトされる．
def add_entry():
    if not session.get('logged_in'): #ユーザがログインしているかどうかの判定には，sessionのlogged_inを使用している．
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash(u'New entry has added')
    return redirect(url_for('bbs_show_entries')) #リダイレクトのurlは"/"ではなく関数名！


#ユーザのログインを行うためのページ
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = u'WRONG USER NAME'
        elif request.form['password'] != app.config['PASSWORD']:
            error = u'WRONG PASSWORD'
        else:
            session['logged_in'] = True # sessionにlogged_inのキーで設定がセットされる．
            flash(u'WELCOME')
            return redirect(url_for('bbs_show_entries')) #ログイン済みの場合は，ユーザはshow_entriesページにリダイレクトされる
    return render_template('bbs_login.html', error=error) #追加メッセージでユーザにログインが成功した事が通知され，エラーが発生した場合はユーザに再度入力を求める．

# ユーザーのログアウトを行うためのページ．
@app.route('/logout')
def logout():
    session.pop('logged_in', None) # ログアウト処理はsessionからkeyを削除することで行う．
    flash(u'GOOD BYE')
    return redirect(url_for("bbs_show_entries"))



if __name__ == '__main__':
    app.run()


# app.config.from_object()は，与えられたオブジェクトの内で大文字の変数をすべて取得する．
# つまり，各種設定の項目のDATABASEやSECRET_KEYなどがapp.configに登録される．

# こんな感じでセットアップは完了．
# で，実行すると，http://127.0.0.1:5000/にアクセスできる．
# が，404が返ってくる
# なぜなら，Viewが設定されていないから．
