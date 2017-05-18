# test.py
from flask import Flask, render_template, url_for, request, session, g, redirect, abort, flash
import numpy as np
import sqlite3

# 各種設定
DATABASE = "test.db"
DEBUG = True
SECRET_KEY = "development key"
USERNAME = "admin"
PASSWORD = "default"

# アプリ作成
app = Flask(__name__) #インスタンス化
app.config.from_object(__name__) # 与えられたオブジェクトの内で大文字の変数をすべて取得する．
app.config.from_envvar("TEST_SETTINGS", silent=True) #silent=True??


# 掲示板に関連する機能＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿
# 何やってるのかわからない変数
# ・curの意味．
# ・g.execute
# ・g.db.execute()
# ・cur.fetchall()
# ・flash

# DB接続
def connect_db():
    return sqlite3.connect(app.config["DATABASE"])


# DB初期化関数
from contextlib import closing
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


# データベースに保存されている全てのポストの一覧のページ．データベースから全てのポストを取り出す．
@app.route("/")
def show_posts():
    cur = g.db.execute("select username, message from test order by id desc") #table test から，usernameとめmessageをとってくる．
    posts_data = [dict(username=row[0], message=row[1]) for row in cur.fetchall()]
    return render_template("test_show_posts.html", posts=posts_data) # ここのurlがtest.htmlではなく．extends先のshow_posts.htmlだった．


# ポストを追加するためのページ．ログインしているユーザしかアクセスできない．
@app.route('/add', methods=['POST']) # POSTリクエストのみが受け付けられる
def add_posts():
    if not session.get('logged_in'): # ユーザがログインしているかどうかの判定には，sessionのlogged_inを使用
        abort(401)
    if request.form["username_post"] == "":
        flash(u"Please enter your name")
    elif request.form["message_post"] == "":
        flash(u"Please enter your message")
    else:
        g.db.execute('insert into test (username, message) values (?, ?)',
                     [request.form["username_post"], request.form["message_post"]])
        g.db.commit()
        flash(u'New message has added')
    return redirect(url_for('show_posts')) #エントリーの追加処理が正常終了するとshow_postsページにリダイレクトされる．これは関数名．


# ポストを削除するための関数
@app.route('/deleted', methods=['POST']) # POSTリクエストのみが受け付けられる
def delete_posts():
    if not session.get('logged_in'): # ユーザがログインしているかどうかの判定には，sessionのlogged_inを使用
        abort(401)
    g.db.execute('delete from test')
    g.db.commit()
    flash(u'All messages have deleted')
    return redirect(url_for('show_posts')) #エントリーの追加処理が正常終了するとshow_postsページにリダイレクトされる．これは関数名．


# ユーザーのログインを行うためのページ
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = u'Wrong username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = u'Wrong password'
        else:
            session['logged_in'] = True #sessionにlogged_inのキーで設定がセットされる．
            flash(u'You are now logged') # 追加メッセージ
            return redirect(url_for('show_posts'))
    return render_template('test_login.html', error=error)


# ユーザーのログアウトを行うためのページ
@app.route('/logout')
def logout():
    session.pop('logged_in', None) #ログアウト処理はsessionからkeyを削除することで行う．
    flash(u'Logged out')
    return redirect(url_for('show_posts'))



# 掲示板以外の機能＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿


# practice for Jinja2
@app.route("/jinja2")
def jinja2():
    dic_jinja2 = {}
    dic_jinja2["name"],dic_jinja2["message"] = "Mr.Aoyama","Nice to meet you"
    array_jinja2 = np.arange(10)
    return render_template('test.html', dic_test = dic_jinja2, array_test = array_jinja2)


# Hello world
@app.route("/hello/") # ユーザーがスラッシュをつけ忘れても自動的にリダイレクトしてくれる．プログラムで/が付いてないのにユーザーがつけた場合はリダイレクトされない．
def hello():
    return "Hello World!"


# variable Rules
@app.route('/user/<user>/<message>/') # http://127.0.0.1:5000/user/Shintaro/18/  #：が全角でmalformed url rule error
def user(user,message): # pass
    return render_template('test.html', u_url = user, m_url = message)


# GET1 (URLに直接入力された情報を得て出力) *from flask import requestが必要
@app.route('/get1/') # getクエリの送り方：GETメソッドはURLの末尾"?"+"パラメーター名=値"でデータ送信．パラメータ追加は"&"でつなげる．get/?name=Shintaro&message=hello
def get1():
    u = request.args.get("name", "No user") # request.argsにクエリパラメータが含まれている
    msg = request.args.get("message", "No message")
    return render_template('test.html', u_get1 = u, m_get1 = msg)


# GET2 (Formに入力された情報を取得して出力)
@app.route('/get2/')
def get2():
    u = request.args.get("user", "No user") # request.argsにクエリパラメータが含まれている
    msg = request.args.get("message", "No message")
    return render_template('test.html', u_get2 = u, m_get2 = msg)


# POST (Formに入力された情報を取得して出力)
@app.route('/post', methods=['POST']) # methodsにPOSTを指定すると、POSTリクエストを受けられる ←/post/とするとリダイレクトエラー．エラー文読むと解決．
def post():
    u = request.form["user"] # request.formにPOSTデータがある # "No user"
    msg = request.form["message"] # "No message"
    return render_template('test.html', u_post = u, m_post = msg)


# POST (Formに入力された情報を取得して出力)
u_list = []
m_list = []
@app.route('/bbs', methods=['POST']) # methodsにPOSTを指定すると、POSTリクエストを受けられる ←/post/とするとリダイレクトエラー．エラー文読むと解決．
def bbs():
    u_list.append(request.form["user"]) # request.formにPOSTデータがある # "No user"
    m_list.append(request.form["message"]) #"No message"
    return render_template('test.html', users = u_list, messages = m_list)


# webのサーバー立ち上げ
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0') # debug=Trueがないと，.pyファイルを再実行しないと反映されない．host =...をつけることで，サーバーを公開できる？
