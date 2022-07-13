import hashlib

from pymongo import MongoClient
import certifi
from flask import Flask, render_template,request, jsonify,session, redirect, url_for


app = Flask(__name__)

ca = certifi.where()


client = MongoClient('mongodb+srv://test:sparta@cluster0.xzmedo5.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'
import jwt
import datetime

#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():
    email_receive = request.form['email_give']
    pw_receive = request.form['pw_give']
    pwCheck_receive = request.form['pwCheck_give']
    nickname_receive = request.form['nickname_give']
    birth_receive=request.form['birth_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'email': email_receive, 'pw': pw_hash, 'pwCheck' : pwCheck_receive, 'birth':birth_receive, 'nick': nickname_receive})

    return jsonify({'result': 'success'})



@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"email": payload["email"]})
        return render_template('index_ysw.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/sign')
def sign():
    return render_template('sign_ysw.html')

@app.route('/login')
def login():
   return render_template('login_ysw.html')

@app.route('/createPost')
def createPost():
    return render_template('createPost_ysw.html')

@app.route('/api/savePost', methods=['POST'])
def savePost():
    # 게시글 속성 저장하기
    title_receive = request.form['title_give']
    email_receive = request.form['email_give']
    tag_receive = request.form['tag_give']
    campus_receive = request.form['campus_give']
    body_receive = request.form['body_give']
    photo_receive= request.form['photo_give']
    doc = {"title": title_receive, "email": email_receive,"tag": tag_receive,"campus": campus_receive,"body": body_receive ,"photo":photo_receive}
    db.write.insert_one(doc)
    return jsonify({'result': 'success', 'msg': f' "{title_receive}" saved'})




# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    email_receive = request.form['email_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'email': email_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'email': email_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=360)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
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
        userinfo = db.user.find_one({'email': payload['email']}, {'_id': 0})
        allData_list = list(db.write.find({},{'_id':False}))
        return jsonify({'result': 'success', 'nickname': userinfo['nick'],'allData' : allData_list})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)






###########################################################################
# from pymongo import MongoClient
# import jwt
# import datetime
# import hashlib
# from flask import Flask, render_template, jsonify, request, redirect, url_for
# from werkzeug.utils import secure_filename
# from datetime import datetime, timedelta
#
# app = Flask(__name__)
# app.config["TEMPLATES_AUTO_RELOAD"] = True
# app.config["UPLOAD_FOLDER"] = "./static/profile_pics"
#
# SECRET_KEY = "SPARTA"
#
# # client = MongoClient(
# #     'mongodb+srv://test:sparta@cluster0.6oczs.mongodb.net/?retryWrites=true&w=majority',
# #     27017, username="아이디", password="비밀번호")
# # db = client.dbsparta_plus_week4
# client = MongoClient(
#     "mongodb+srv://test:sparta@cluster0.xzmedo5.mongodb.net/?retryWrites=true&w=majority"
# )
# db = client.dbsparta_campuspot
#
#
#
#
#
#
# @app.route("/")
# def home():
#     token_receive = request.cookies.get("campuspot_token")
#
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
#         user_info = db.users.find_one({"email": payload["email"]})
#         return render_template("main.html", user_info=user_info)
#     except jwt.ExpiredSignatureError:
#         return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
#     except jwt.exceptions.DecodeError:
#         return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
#
#
# @app.route("/login")
# def login():
#     msg = request.args.get("msg")
#     return render_template("login.html", msg=msg)
#
#
# # @app.route("/user/<username>")
# # def user(username):
# #     # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
# #     token_receive = request.cookies.get("campuspot_token")
# #     try:
# #         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
# #         status = username == payload["id"]  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
# #
# #         user_info = db.users.find_one({"username": username}, {"_id": False})
# #         return render_template("user.html", user_info=user_info, status=status)
# #     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
# #         return redirect(url_for("home"))
#
#
# @app.route("/sign_in", methods=["POST"])
# def sign_in():
#     # 로그인
#     email_receive = request.form["email_give"]
#     password_receive = request.form["password_give"]
#
#     pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
#     result = db.users.find_one({"email": email_receive, "password": pw_hash})
#
#     if result is not None:
#         payload = {
#             "email": email_receive,
#             # 로그인 24시간 유지
#             "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
#         }
#         # PyJWT 의 v2.0.0부터 jwt.encode()의 반환값이 바뀌어서 .decode()가 필요 없어졌다.
#         token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
#
#         return jsonify({"result": "success", "token": token})
#     # 찾지 못하면
#     else:
#         return jsonify({"result": "fail", "msg": "이메일/비밀번호가 일치하지 않습니다."})
#
#
# @app.route("/sign_up/save", methods=["POST"])
# def sign_up():
#     email_receive = request.form["email_give"]
#     password_receive = request.form["password_give"]
#     campus_receive = request.form["campus_give"]
#     password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
#     doc = {
#         # 이메일
#         "email": email_receive,
#         # 비밀번호
#         "password": password_hash,
#         # 소속 대학 (기본값은 '')
#         "campus": campus_receive,
#         # # 생년월일
#         # "birth": birth_give,
#     }
#     db.users.insert_one(doc)
#     return jsonify({"result": "success"})
#
#
# @app.route("/sign_up/check_dup", methods=["POST"])
# def check_dup():
#     email_receive = request.form["email_give"]
#     exists = bool(db.users.find_one({"email": email_receive}))
#     return jsonify({"result": "success", "exists": exists})
#
#
# # @app.route("/update_profile", methods=["POST"])
# # def save_img():
# #     token_receive = request.cookies.get("campuspot_token")
# #     try:
# #         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
# #         # 프로필 업데이트
# #         return jsonify({"result": "success", "msg": "프로필을 업데이트했습니다."})
# #     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
# #         return redirect(url_for("home"))
# #
# #
# # @app.route("/posting", methods=["POST"])
# # def posting():
# #     token_receive = request.cookies.get("campuspot_token")
# #     try:
# #         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
# #         # 포스팅하기
# #         return jsonify({"result": "success", "msg": "포스팅 성공"})
# #     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
# #         return redirect(url_for("home"))
# #
# #
# # @app.route("/get_posts", methods=["GET"])
# # def get_posts():
# #     token_receive = request.cookies.get("campuspot_token")
# #     try:
# #         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
# #         # 포스팅 목록 받아오기
# #         return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다."})
# #     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
# #         return redirect(url_for("home"))
# #
# #
# # @app.route("/update_like", methods=["POST"])
# # def update_like():
# #     token_receive = request.cookies.get("campuspot_token")
# #     try:
# #         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
# #         # 좋아요 수 변경
# #         return jsonify({"result": "success", "msg": "updated"})
# #     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
# #         return redirect(url_for("home"))
#
#
# if __name__ == "__main__":
#     app.run("0.0.0.0", port=5000, debug=True)
