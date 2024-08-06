import datetime
import json
import os
import re
from flask import Flask, request, render_template_string, redirect, url_for, jsonify, render_template
import json
import requests
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
const_rating = {}


class PlayerData:
    def __init__(self, playerName, playerRating, playerMaxRating):
        self.playerName = playerName
        self.playerRating = playerRating
        self.playerMaxRating = playerMaxRating


def Login(sega_id, password):
    login_web_url = "https://lng-tgk-aime-gw.am-all.net/common_auth/login?site_id=chuniex&redirect_url=https://chunithm-net-eng.com/mobile/&back_url=https://chunithm.sega.com/"
    login_url = "https://lng-tgk-aime-gw.am-all.net/common_auth/login/sid/"

    # Create a session object
    session = requests.Session()

    # Visit the login page to initialize cookies
    session.get(login_web_url)

    # Prepare login data and headers
    data = {
        'retention': 1,
        'sid': sega_id,
        'password': password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "lng-tgk-aime-gw.am-all.net",
        "Origin": "https://lng-tgk-aime-gw.am-all.net",
        "Referer": "https://lng-tgk-aime-gw.am-all.net/common_auth/login?site_id=chuniex&redirect_url=https://chunithm-net-eng.com/mobile/&back_url=https://chunithm.sega.com/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36"
    }

    # Perform the login
    respond = session.post(login_url, data=data, headers=headers)
    next = respond.history[1].url
    session.get(next)
    # print(session.cookies.get_dict()["_t"])
    # print(session.cookies.get_dict())
    token = session.cookies.get_dict()["_t"]
    if respond.status_code == 200:
        try:
            soup = BeautifulSoup(respond.content.decode("utf-8"), "html.parser")

            rating = ""
            userName = soup.find("div", class_="player_name_in").text
            userMaxRating = soup.find("div", class_="player_rating_max").text
            rating_div = soup.find("div", class_="player_rating_num_block")
            rating_imgs = rating_div.find_all("img")
            for img in rating_imgs:
                # 使用正則表達式提取數字
                match = re.search(r'(\d+).png', img['src'])
                if match:
                    rating += match.group(1)[1]
                # 檢查是否是逗號
                if 'rating_rainbow_comma' in img['src']:
                    rating += "."
            print("名稱", userName)
            print("目前rating", rating)
            print("最大rating", userMaxRating)
            return session, token, PlayerData(userName, rating, userMaxRating)
        except Exception as e:
            return session,None
    else:
        return session, None


def IntoGenere(session):
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        "Connection": "keep-alive",
        "Host": "chunithm-net-eng.com",
        "Referer": "https://chunithm-net-eng.com/mobile/home/",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    respond = session.get(
        url="https://chunithm-net-eng.com/mobile/record/musicGenre",
        allow_redirects=True,
        headers=headers,
        cookies=session.cookies,
        timeout=10  # 设置超时时间（秒）
    )
    # print(respond.status_code)
    if respond.status_code == 200:
        return session
    else:
        return None


def GetScore(session, token, playerData, diffcult):
    Basic_url = f"https://chunithm-net-eng.com/mobile/record/musicGenre/send{diffcult}"
    headers = {
        "Host": "chunithm-net-eng.com",
        "Origin": "https://chunithm-net-eng.com",
        "Referer": "https://chunithm-net-eng.com/mobile/record/musicGenre/basic",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        "Connection": "keep-alive",
        "Content-Length": "47",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    # print("目前header", headers)
    # session.cookies.setdefault("teamCode", "QQBZY1;")
    # print("目前session cookie", session.cookies.get_dict())
    # print(f"{Basic_url}?genre=99&token={token}")
    respond = session.post(
        url=f"{Basic_url}?genre=99&token={token}",
        data={'genre': '99', 'token': token},  # 使用 data 发送表单数据
        allow_redirects=False,
        headers=headers,
        cookies=session.cookies,
        timeout=10  # 设置超时时间（秒）
    )
    if respond.status_code == 302:
        # 获取重定向 URL
        redirect_url = respond.headers['Location']
        # print(redirect_url)

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
            "Connection": "keep-alive",
            "Referer": "https://chunithm-net-eng.com/mobile/home/",
            "Host": "chunithm-net-eng.com",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36"
        }
        # print("目前header", headers)
        # print("目前session cookie", session.cookies.get_dict())
        respond = session.get(
            url=redirect_url,
            headers=headers,
            cookies=session.cookies,
            allow_redirects=True,
            timeout=10  # 设置超时时间（秒）
        )
        # print(respond.status_code)
        directory = f"webScore/{playerData.playerName}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        if respond.status_code == 200:
            with open(f"webScore/{playerData.playerName}/GetScore{diffcult}.html", mode="w", encoding="utf-8") as f:
                f.write(respond.content.decode("utf-8"))
            return session
        else:
            return None


def ParseWebScore(playerData, formatted_date, formatted_time):
    difficulties = ["Basic", 'Advanced', 'Expert', 'Master']
    all_scores = {}
    all_scores["Player Name"] = playerData.playerName
    all_scores["Player Rating"] = playerData.playerRating
    for difficulty in difficulties:
        content = ""
        with open(f"webScore/{playerData.playerName}/GetScore{difficulty}.html", mode="r", encoding='utf-8') as f:
            content = f.read()
        soup = BeautifulSoup(content, "html.parser")
        scores = soup.findAll("div", class_=f"w388 musiclist_box bg_{difficulty.lower()}")
        difficulty_scores = []

        for score in scores:
            music_title = score.find("div", class_="music_title").text.strip()
            try:
                high_score = score.find("div", class_="play_musicdata_highscore").find("span",class_="text_b").text.strip()
            except Exception as e:
                high_score = "0"
            try:
                diff = difficulty[:3].upper()
                const_rating_song=const_rating[music_title][diff]
                print(const_rating_song)
            except Exception as e:
                print("沒定數")
                const_rating_song = 0
            difficulty_scores.append({
                "music_title": music_title,
                "high_score": high_score,
                "const": const_rating_song#const_rating[music_title][diff]["const"]
            })

        all_scores[difficulty] = difficulty_scores
    # 將結果寫入 JSON 文件
    if not os.path.exists(f"score/{playerData.playerName}"):
        os.makedirs(f"score/{playerData.playerName}")
    with open(f"score/{playerData.playerName}/{formatted_date}-{formatted_time}.json", mode="w",
              encoding="utf-8") as json_file:
        json.dump(all_scores, json_file, ensure_ascii=False, indent=4)


# 首页，展示登录表单
@app.route('/')
def index():
    content = ""
    with open("template/score.html", mode="r", encoding='utf-8') as f:
        content = f.read()
    return render_template_string(content)


@app.route('/login', methods=['POST'])
def login():
    UpdateRatingConst()
    username = request.form['username']
    password = request.form['password']
    # print(username,password)
    session, token, playerData = Login(username, password)
    # 獲取當前日期和時間，並設置時區為UTC+8
    NowDate = datetime.date.today()
    NowDateTime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))

    # 格式化日期和時間以用於文件名
    formatted_date = NowDate.strftime("%Y-%m-%d")
    formatted_time = NowDateTime.strftime("%Y-%m-%d_%H-%M-%S")
    if token is not None:
        session = IntoGenere(session)
        if session:
            diffcult = ["Basic", 'Advanced', 'Expert', 'Master']
            for diff in diffcult:
                if session is not None:
                    session = GetScore(session, token, playerData, diff)
            ParseWebScore(playerData, formatted_date, formatted_time)
    file_path = f"score/{playerData.playerName}/{formatted_date}-{formatted_time}.json"
    # 读取生成的 JSON 文件内容
    with open(file_path, mode="r", encoding="utf-8") as json_file:
        file_content = json.load(json_file)

    # 返回文件路径和内容
    content = ""
    with open("template/table.html", mode="r", encoding='utf-8') as f:
        content = f.read()
    return render_template_string(content, file_content=file_content)


def UpdateRatingConst():
    global const_rating
    respond = requests.get(url="https://reiwa.f5.si/chunithm_luminous.json")
    content = json.loads(respond.content.decode('utf-8-sig'))  # Decode using 'utf-8-sig'
    const_rating = {}
    for song in content:
        const_rating[song["meta"]["title"]] = {}
        for diffcuilt in song["data"]:
            const_rating[song["meta"]["title"]][diffcuilt] = song["data"][diffcuilt]["const"]


if __name__ == '__main__':
    app.run(port=5000)
