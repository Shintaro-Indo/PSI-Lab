from flask import Flask, render_template, request, url_for

app = Flask(__name__)

system =  ["システム","青山","チンパン",]
tmi =["技術","AI","経営"]

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/add", methods=['POST'])
def add():
    user = request.form["user"]
    message = request.form["message"]
    for i in range(len(system)):
        if system[i] in message:
            url = "http://www.sys.t.u-tokyo.ac.jp/" #この""は文字列と認識するためのもの
            break
        elif tmi[i] in message:
            url = "http://tmi.t.u-tokyo.ac.jp/"
            break
        else:
            url = "http://livedoor.4.blogimg.jp/laba_q/imgs/b/d/bd0839ac.jpg"
    return render_template('page1.html', user=user, message = message, url = url) #

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
