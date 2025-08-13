# harman2 폴더/server폴더/exam01.py
# request : client -> server
# response : server -> client

# python으로 server를 만들거임
# 서버에는 두 종류가 있음. 
# 1) flask: 마이크로 웹 프레임워크(코드가 굉장히 짧음.)
# 2) Django: 보안부터 시작해서 모든 기능이 포함되어있음. -> flask보다 10~20배정도 무거움. 
# -> 우리는 flask 서버를 구성할 거임.

# 가상환경 구축하는 법
# 우측 하단에 3.13.5 혹은 가상환경 이름 클릭 or ctrl shift p 누르고 Select interpreter라고 치기
from flask import Flask # route 경로, run 서버 실행
from flask import render_template # html load
from flask import request # 사용자가 보낸 정보
from flask import redirect # 페이지 이동
from flask import make_response  # 페이지 이동 시 정보 유지!!
from aws import detect_labels_local_file 
from aws import compare_faces as cf

# 파일 이름 보안처리 라이브러리
from werkzeug.utils import secure_filename

import os 
# static 폴더가 없다면 만들어라. 
if not os.path.exists("static"):
    os.mkdir("static")


app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")
    # return "관형의 웹페이지"

@app.route("/compare",methods=["POST"])
def compare_faces():
    #/detect를 통해서 한 내용과 거의 동일 (file을 두개 받을 뿐)
    # 1. compare로 오는 file1, file2를 받아서
    if request.method == "POST":
        file1 = request.files["file1"]
        file2 = request.files["file2"]
        #flask 보안 규칙 상 file이름을 secure에서 처리
        file1_filename = secure_filename(file1.filename) 
        file2_filename = secure_filename(file2.filename) 
        #static 폴더에 저장하기
        file1.save("static/"+file1_filename)
        file2.save("static/"+file2_filename)

        r = cf("static/"+file1_filename,"static/"+file2_filename)

    # static폴더에 save
    # 이때 secure_filename을 사용해서 
    # 2. aws.py 얼굴 비교 aws코드!
    # 이 결과를 통해 웹페이지에 "동일한 인물일 확률은  95.34%입니다."
    # 3. aws.py안의 함수를 불러와서 exam01.py 사용!!

    return r

@app.route("/detect",methods=["POST"])
def detect_label():
    
    # flask에서의 보안 규칙상
    # file이름을 secure처리 해야함. 
    if request.method == "POST":
        file = request.files["file"]
        file_name = secure_filename(file.filename)
        file.save("static/"+file_name)
        # file을 static 폴더에 저장하고
        # 해당 경로를 detect_lo~ 함수에 전달
        r = detect_labels_local_file("static/"+file_name)

    return r

@app.route("/secret",methods=["POST"])
def box():
    try:
        #post는 key,value가 뜨지 않으므로 get방식 대비 조금 더 보안유지에 좋음. 
        if request.method == "POST":
            # get으로 오는 data는 args[key], post로 오는 값은 form[key]로, file은 .file[]로 객체를 저장함. 
            hidden = request.form["hidden"]
            return f"비밀 정보: {hidden}"
    except:
        return "데이터 전송 실패!"

#아래와 같이 쓰면 127.0.0.0/login이라는 페이지가 만들어짐. 
@app.route("/login",methods=["GET"])
def login():
    if request.method == "GET":
        login_id = request.args["login_id"]
        login_pw = request.args["login_pw"]

        # 페이지가 이동하더라도 정보를 남겨서 사용하기!!
        # 로그인 성공 여부 확인

        if login_id == "nayeho" and login_pw == "1234":
            #로그인 성공
            response = make_response(redirect("/login/success"))
            # response의 정보를 담을 수 있는 시간을 벌어야함. 
            response.set_cookie("user",login_id)
            return response
        else:
            return redirect("/")
        
    return f"{login_id}님 환영해요~!"
    
@app.route("/login/success",methods=["GET"])
def login_success():
    login_id = request.cookies.get("user")
    return f"{login_id}님 환영합니다."

# 외부에서 import하지 않고 직접 실행할 때만 main을 실행해라. 
if __name__ == "__main__":
    # 나를 바라볼 수 있는 누구나 내 서버에 들어올 수 있음.
    app.run(host="0.0.0.0") 
    #  그냥 app.run()을 하면 다른 사람들이 내 서버를 볼 수 없고 나만 볼 수 있음.
    # 내 ip를 지정해서 서버를 올리면 누구나 들어올 수 있음. 