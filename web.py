import requests
from bs4 import BeautifulSoup

from flask import Flask, render_template,request
from datetime import datetime

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入劉香均的網站20260409</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>現在日期時間</a><hr>"
    link += "<a href=/me>關於我</a><hr>"
    link += "<a href=/welcome?u=香均&d=靜宜資管&c=資訊管理導論>Get傳值</a><hr>"
    link += "<a href=/account>Post傳值</a><hr>"
    link += "<a href=/math2>次方根號計算</a><hr>"
    link += "<a href=/read>讀取Firestore資料</a><hr>"
    link += "<a href=/read2>靜宜資管查詢</a><hr>"
    link += "<a href=/spider1>爬取子青老師本學期課程</a><br>"
    link += "<a href=/movie1>爬取即將上映電影</a><hr>"
    return link

@app.route("/movie1", methods=['GET', 'POST'])
def movie1():
    keyword = ""
    movies = []  # 用來存放篩選後的電影資料
    
    if request.method == 'POST':
        keyword = request.form.get("keyword")
        
        url = "http://www.atmovies.com.tw/movie/next/"
        Data = requests.get(url)
        Data.encoding = "utf-8"
        sp = BeautifulSoup(Data.text, "html.parser")
        result = sp.select(".filmListAllX li")
        
        for item in result:
            title = item.find("img").get("alt") # 電影名稱
            
            # 關鍵字篩選：如果名稱包含關鍵字，才加入清單
            if keyword in title:
                link = "https://www.atmovies.com.tw" + item.find("a").get("href")
                img_src = "https://www.atmovies.com.tw" + item.find("img").get("src")
                
                # 存成字典方便 HTML 讀取
                movies.append({
                    "title": title,
                    "link": link,
                    "img": img_src
                })

    return render_template("movie1.html", movies=movies, keyword=keyword)


@app.route("/spider1")
def spider1():
    R = ""
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box a")

    for i in result:
        R += i.text + i.get("href") + "<br>"
    return R


@app.route("/read2", methods=["GET", "POST"])
def read2():
    # 取得前端 input name="keyword" 的值
    keyword = request.values.get("keyword")
    Result = ""
   
    if keyword:
        db = firestore.client()
        # 讀取集合
        collection_ref = db.collection("靜宜資管2026B")
        docs = collection_ref.get()
       
        for doc in docs:
            teacher = doc.to_dict()
            name = teacher.get("name", "")
            # 比對：如果輸入的姓氏在名字裡面
            if keyword in name:
                Result += f"找到老師：{name}<br>"
       
        if Result == "":
            Result = f"找不到姓氏包含「{keyword}」的老師"
           
    # 將 Result 傳回給 read2.html
    return render_template("read2.html", Result=Result)

             
@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("靜宜資管2026B")    
    docs = collection_ref.get()
    docs = collection_ref.order_by("lab",direction=firestore.Query.DESCENDING).limit(5).get()
    for doc in docs:         
        Result += str(doc.to_dict()) + "<br>"    
    return Result

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime=str(now))

@app.route("/me")
def me():
    return render_template("mis2026b.html")

@app.route("/welcome",methods=["GET"])
def welcome():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")
    return render_template("welcome.html",name = user , dep = d,course = c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/math2")
def math2():
    return render_template("math2.html")

if __name__ == "__main__":
    app.run(debug=True)
