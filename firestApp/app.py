from pymongo import MongoClient
import certifi
from flask import Flask, render_template,request, jsonify

app = Flask(__name__)

ca = certifi.where()


client = MongoClient('mongodb+srv://test:sparta@cluster0.xzmedo5.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

doc = {
    'email':'a@a.com',
    'password':'aaaaa'
}

db.users.insert_one(doc)


@app.route('/')
def home():
   return render_template('login.html')

@app.route('/sign')
def mypage():
    return render_template('sign.html')

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

@app.route('/test', methods=['GET'])
def test_get():
   user_receive = request.args.get('user_give')
   print(user_receive)
   return jsonify({'result':'success', 'msg': '이 요청은 GET!'})