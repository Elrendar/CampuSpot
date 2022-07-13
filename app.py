from pymongo import MongoClient
import jwt
import datetime
import hashlib
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

SECRET_KEY = "SPARTA"

# client = MongoClient("52.78.26.248", 27017, username="test", password="test")
client = MongoClient(
    "mongodb+srv://test:sparta@cluster0.6oczs.mongodb.net/?retryWrites=true&w=majority"
)
db = client.dbsparta_campuspot


@app.route("/")
def home():
    token_receive = request.cookies.get("campuspot_token")

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]})

        return render_template("main.html", user_info=user_info)
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
        postlist = list(db.posts.find({"email": user_info["email"]}, {"_id": False}))

        return jsonify(json.dumps(postlist))
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


# @app.route("/update_profile", methods=["POST"])
# def save_img():
#     token_receive = request.cookies.get("campuspot_token")
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
#         # 프로필 업데이트
#         return jsonify({"result": "success", "msg": "프로필을 업데이트했습니다."})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))
#
#
# @app.route("/posting", methods=["POST"])
# def posting():
#     token_receive = request.cookies.get("campuspot_token")
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
#         # 포스팅하기
#         return jsonify({"result": "success", "msg": "포스팅 성공"})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))
#
#
# @app.route("/get_posts", methods=["GET"])
# def get_posts():
#     token_receive = request.cookies.get("campuspot_token")
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
#         # 포스팅 목록 받아오기
#         return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다."})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))
#
#
# @app.route("/update_like", methods=["POST"])
# def update_like():
#     token_receive = request.cookies.get("campuspot_token")
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
#         # 좋아요 수 변경
#         return jsonify({"result": "success", "msg": "updated"})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
