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
    return render_template('page1.html', user=user, message = message)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
