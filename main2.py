from flask import Flask, render_template, request, url_for, session, g, redirect, abort, flash
import bs4
from bs4 import BeautifulSoup
import urllib.request
import sqlite3
from contextlib import closing

app = Flask(__name__)

original_url = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/index.html" #トップページ
soup = bs4.BeautifulSoup(urllib.request.urlopen(original_url).read(),"lxml")
a_tag = soup.find_all('a')
url_list = []
for link in a_tag:
    if 'href' in link.attrs:
        url_list.append(link.attrs['href']) #教授ごとのリンクをリストに


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

@app.route("/recomend", methods=['POST'])
def recomend():
    url = ""
    user = request.form["user"]
    message = request.form["message"]
    for i in range(2,len(url_list)): #[0],[1]はindex.html(トップページ)
        link = "http://www.si.t.u-tokyo.ac.jp/psi/thesis/thesis16/" + url_list[i]
        key_list = []
        key_list = find_keywords(link)
        for j in range(len(key_list)):
            if message in key_list[j]:
                url  = link #この""は文字列と認識するためのもの
                break
        # if j == len(key_list):
        #     url = "http://livedoor.4.blogimg.jp/laba_q/imgs/b/d/bd0839ac.jpg"
    return render_template('page1.html', user=user, message = message, url = url)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
