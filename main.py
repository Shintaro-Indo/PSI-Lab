from flask import Flask
from flask import render_template,request


app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/add",methods=['POST'])
def add():
    user = request.form["user"]
    message = request.form["message"]
    if message == "システム創成学":
        url = "http://www.sys.t.u-tokyo.ac.jp/admissions/" #この""は文字列と認識するためのもの
    elif message == "技術経営戦略学":
        url = "http://tmi.t.u-tokyo.ac.jp/examinfo/examinfo.htm"
    return render_template('page1.html', user=user, message = message, url = url) #

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
