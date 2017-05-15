from flask import Flask, render_template, request, url_for
import bs4
from bs4 import BeautifulSoup
import urllib.request


app = Flask(__name__)

#システム創成
sys_url = "http://www.sys.t.u-tokyo.ac.jp/research/"
soap = bs4.BeautifulSoup(urllib.request.urlopen(sys_url).read(),"lxml")
sys_keys = soap.find_all('p')
system=[]
for t in sys_keys:
    system.append(t.get_text())


   
tmi =["技術","AI","経営"]

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/add",methods=['POST'])
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
    return render_template('page1.html', user=user, message = message, url = url) #

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
