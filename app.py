from pymongo import MongoClient
import time
import math
import jwt
import datetime
import hashlib
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import certifi

ca = certifi.where()
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = "SPARTA"

# client = MongoClient(
#     'mongodb+srv://test:sparta@cluster0.6oczs.mongodb.net/?retryWrites=true&w=majority',
#     27017, username="아이디", password="비밀번호")
# db = client.dbsparta_plus_week4
client = MongoClient('mongodb+srv://test:sparta@cluster0.xegtv.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta


@app.route("/")
def home():
    token_receive = request.cookies.get("campuspot_token")

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]})
        return render_template("index_ysw.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route("/login")
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)


@app.route("/mypage")
def mypage():
    # 로그인 한 사용자의 프로필과 글을 모아볼 수 있는 공간(마이페이지)
    token_receive = request.cookies.get("campuspot_token")

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]}, {"_id": False})

        return render_template("mypage.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/createPost')
def createPost():
    token_receive = request.cookies.get("campuspot_token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]}, {"_id": False})

        return render_template("createPost_ysw.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    return render_template('createPost_ysw.html')


@app.route("/sign_in", methods=["POST"])
def sign_in():
    # 로그인
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]

    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one({"email": email_receive, "password": pw_hash})

    if result is not None:
        payload = {
            "email": email_receive,
            # 로그인 24시간 유지
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        # PyJWT 의 v2.0.0부터 jwt.encode()의 반환값이 바뀌어서 .decode()가 필요 없어졌다.
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({"result": "success", "token": token})
    # 찾지 못하면
    else:
        return jsonify({"result": "fail", "msg": "이메일/비밀번호가 일치하지 않습니다."})


@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    ## 회원가입 폼에서 입력값 받아오기
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]
    campus_receive = request.form["campus_give"]
    username_receive = request.form["username_give"]
    birth_receive = request.form["birth_give"]
    # 암호화
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

    doc = {
        # 이메일
        "email": email_receive,
        # 비밀번호
        "password": password_hash,
        # 소속 대학 (기본값은 '')
        "campus": campus_receive,
        # 닉네임
        "username": username_receive,
        # 생년월일
        "birth": birth_receive,
    }
    db.users.insert_one(doc)
    return jsonify({"result": "success"})


@app.route("/sign_up/check_dup", methods=["POST"])
def check_dup():
    email_receive = request.form["email_give"]
    exists = bool(db.users.find_one({"email": email_receive}))
    return jsonify({"result": "success", "exists": exists})


@app.route("/api/myposts", methods=["GET"])
def myposts():
    # 마이페이지 - 내 정보 요청
    token_receive = request.cookies.get("campuspot_token")

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]}, {"_id": False})
        # postlist = list(db.posts.find({"email": user_info["email"]}, {"_id": False}))
        # print(postlist)
        # return jsonify(json.dumps(postlist))
        my_posts = list(db.posts.find({"email": user_info["email"]}, {'_id': False}))
        print(my_posts)

        return jsonify({'result': 'success', 'my_posts': my_posts})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route("/api/delete", methods=["GET"])
def delete_account():
    # 계정 삭제
    token_receive = request.cookies.get("campuspot_token")

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]}, {"_id": False})
        if user_info is not None:
            db.users.delete_one({"email": user_info['email']})

        return jsonify({"result": "success"})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route("/api/editUsername", methods=["POST"])
def edit_username():
    # 계정 삭제
    token_receive = request.cookies.get("campuspot_token")
    username_receive = request.form["username_give"]

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]}, {"_id": False})
        if user_info is not None:
            db.users.update_one({"email": user_info['email']}, {"$set": {"username": username_receive}})

        return jsonify({"result": "success"})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/api/savePost', methods=['POST'])
def savePost():
    # 게시글 속성 저장하기
    num = time.time()
    numId = math.trunc(num)
    title_receive = request.form['title_give']
    email_receive = request.form['email_give']
    tag_receive = request.form['tag_give']
    campus_receive = request.form['campus_give']
    body_receive = request.form['body_give']
    photo_receive = request.form['photo_give']
    doc = {'numId': numId, "title": title_receive, "email": email_receive, "tag": tag_receive, "campus": campus_receive,
           "body": body_receive, "photo": photo_receive}
    db.posts.insert_one(doc)
    return jsonify({'result': 'success', 'msg': f' "{title_receive}" saved'})


@app.route('/api/deletePost', methods=['POST'])
def delete_word():
    # 단어 삭제하기
    num_receive = request.form['numId_give']
    db.posts.delete_one({"numId": int(num_receive)})
    return jsonify({'result': 'success', 'msg': f'word "{num_receive}" deleted'})


@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('campuspot_token')
    # print(request.args.get('campusName'))
    # checkCampus=request.args.get('campusName')
    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.

        # if checkCampus:
        #     userinfo = db.user.find_one({'email': payload['email']}, {'_id': 0})
        #     allData_list = list(db.write.find({'campus':checkCampus}, {'_id': False}))
        #     return jsonify({'result': 'success', 'nickname': userinfo['nick'], 'allData': allData_list})
        #
        # else:
        userinfo = db.users.find_one({'email': payload['email']}, {'_id': 0})
        allData_list = list(db.posts.find({},{'_id':False}))
        print(allData_list)
        return jsonify({'result': 'success', 'user-email': payload['email'], 'allData': allData_list})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
