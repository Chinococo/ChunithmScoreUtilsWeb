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
RatingConstUpdateDate = None


def UpdateRatingConst():
    global const_rating, RatingConstUpdateDate
    respond = requests.get(url="https://reiwa.f5.si/chunithm_luminous.json")
    content = json.loads(respond.content.decode('utf-8-sig'))  # Decode using 'utf-8-sig'
    const_rating = {}
    for song in content:
        const_rating[song["meta"]["title"]] = {}
        for diffcuilt in song["data"]:
            const_rating[song["meta"]["title"]][diffcuilt] = song["data"][diffcuilt]["const"]
    NowTime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    NonwDate = NowTime.strftime("%Y-%m-%d")
    RatingConstUpdateDate = NonwDate


class PlayerData:
    def __init__(self, playerName, playerRating, playerMaxRating, token):
        self.playerName = playerName
        self.playerRating = playerRating
        self.playerMaxRating = playerMaxRating
        self.token = token


class SegaLogin:
    '''
        初始化 SegaLogin 類的實例。
        @param sega_id: 用戶的 Sega ID
        @param password: 用戶的密碼
    '''
    def __init__(self, sega_id, password):

        self.sega_id = sega_id
        self.password = password
        self.session = requests.Session()
        NowDate = datetime.date.today()
        NowDateTime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
        self.formatted_date = NowDate.strftime("%Y-%m-%d")
        self.formatted_time = NowDateTime.strftime("%Y-%m-%d_%H-%M-%S")
        self.playerData = None

    def Login(self):
        '''
            登入帳號
        '''
        login_web_url = "https://lng-tgk-aime-gw.am-all.net/common_auth/login?site_id=chuniex&redirect_url=https://chunithm-net-eng.com/mobile/&back_url=https://chunithm.sega.com/"
        login_url = "https://lng-tgk-aime-gw.am-all.net/common_auth/login/sid/"
        # Visit the login page to initialize cookies
        self.session.get(login_web_url)
        # Prepare login data and headers
        data = {
            'retention': 1,
            'sid': self.sega_id,
            'password': self.password
        }
        print(self.sega_id,self.password)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "lng-tgk-aime-gw.am-all.net",
            "Origin": "https://lng-tgk-aime-gw.am-all.net",
            "Referer": "https://lng-tgk-aime-gw.am-all.net/common_auth/login?site_id=chuniex&redirect_url=https://chunithm-net-eng.com/mobile/&back_url=https://chunithm.sega.com/",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36"
        }
        # Perform the login
        respond = self.session.post(login_url, data=data, headers=headers)
        print(respond.history)
        if len(respond.history) < 2:
            return False
        next = respond.history[1].url
        self.session.get(next)
        # print(session.cookies.get_dict()["_t"])
        # print(session.cookies.get_dict())
        token = self.session.cookies.get_dict()["_t"]
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
                self.playerData = PlayerData(userName, rating, userMaxRating, token)
                return True
            except Exception as e:
                return False
        else:
            return False

    def GenerateScoreReport(self):
        ...

    def IntoGenere(self):
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
        respond = self.session.get(
            url="https://chunithm-net-eng.com/mobile/record/musicGenre",
            allow_redirects=True,
            headers=headers,
            cookies=self.session.cookies,
            timeout=10  # 设置超时时间（秒）
        )
        # print(respond.status_code)
        if respond.status_code == 200:
            return True
        else:
            return False

    def GetScore(self, diffcult):
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
        respond = self.session.post(
            url=f"{Basic_url}?genre=99&token={self.playerData.token}",
            data={'genre': '99', 'token': self.playerData.token},  # 使用 data 发送表单数据
            allow_redirects=False,
            headers=headers,
            cookies=self.session.cookies,
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
            respond = self.session.get(
                url=redirect_url,
                headers=headers,
                cookies=self.session.cookies,
                allow_redirects=True,
                timeout=10  # 设置超时时间（秒）
            )
            # print(respond.status_code)
            directory = f"webScore/{self.playerData.playerName}"
            if not os.path.exists(directory):
                os.makedirs(directory)
            if respond.status_code == 200:
                with open(f"webScore/{self.playerData.playerName}/GetScore{diffcult}.html", mode="w",
                          encoding="utf-8") as f:
                    f.write(respond.content.decode("utf-8"))
                return True
            else:
                return False

    def ParseWebScore(self):
        all_scores = {}
        all_scores["Player Name"] = self.playerData.playerName
        all_scores["Player Rating"] = self.playerData.playerRating
        for difficulty in ["Basic", 'Advanced', 'Expert', 'Master','Ultima','Recent']:
            all_scores[difficulty]=[]
        for file_name in ["Basic", 'Advanced', 'Expert', 'Master','Ultima','Recent']:

            content = ""
            with open(f"webScore/{self.playerData.playerName}/GetScore{file_name}.html", mode="r",
                      encoding='utf-8') as f:
                content = f.read()
            soup = BeautifulSoup(content, "html.parser")
            pattern = re.compile(r"\bw388 musiclist_box\b.*\bbg_(basic|advanced|expert|master|ultima)\b")
            scores = soup.findAll("div", class_=pattern)

            for score in scores:
                score_classes = score.get("class")  # 拿到他的 class
                song_diffcult = score_classes[2][3:].capitalize() # 打印 class 屬性以便檢查
                music_title = score.find("div", class_="music_title").text.strip()
                try:
                    high_score = score.find("div", class_="play_musicdata_highscore").find("span",
                                                                                           class_="text_b").text.strip()
                except Exception as e:
                    high_score = "0"
                try:
                    diff = song_diffcult[:3].upper()
                    const_rating_song = const_rating[music_title][diff]
                    print(const_rating_song)
                except Exception as e:
                    const_rating_song = 0
                if file_name == "Recent":
                    all_scores[file_name].append({
                        "music_title": music_title,
                        "high_score": high_score,
                        "const": const_rating_song  # const_rating[music_title][diff]["const"]
                    })
                else:
                    all_scores[song_diffcult].append({
                        "music_title": music_title,
                        "high_score": high_score,
                        "const": const_rating_song  # const_rating[music_title][diff]["const"]
                    })

        # 將結果寫入 JSON 文件
        if not os.path.exists(f"score/{self.playerData.playerName}"):
            os.makedirs(f"score/{self.playerData.playerName}")
        with open(f"score/{self.playerData.playerName}/{self.formatted_date}-{self.formatted_time}.json", mode="w",
                  encoding="utf-8") as json_file:
            json.dump(all_scores, json_file, ensure_ascii=False, indent=4)

    def GetScoreReport(self):
        file_path = f"score/{self.playerData.playerName}/{self.formatted_date}-{self.formatted_time}.json"
        # 读取生成的 JSON 文件内容
        with open(file_path, mode="r", encoding="utf-8") as json_file:
            file_content = json.load(json_file)
        return file_content

    def GetRecent(self):
        Basic_url = f"https://chunithm-net-eng.com/mobile/home/playerData/ratingDetailBest/"
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
        respond = self.session.get(
            url=Basic_url,
            allow_redirects=True,
            headers=headers,
            cookies=self.session.cookies,
            timeout=10  # 设置超时时间（秒）
        )
        # print(respond.status_code)
        directory = f"webScore/{self.playerData.playerName}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        if respond.status_code == 200:
            with open(f"webScore/{self.playerData.playerName}/GetScoreRecent.html", mode="w",
                      encoding="utf-8") as f:
                f.write(respond.content.decode("utf-8"))
            return True
        else:
            return False




# 首页，展示登录表单
@app.route('/')
def index():
    content = ""
    with open("template/score.html", mode="r", encoding='utf-8') as f:
        content = f.read()
    return render_template_string(content)


@app.route('/login', methods=['POST'])
def login():
    NowTime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    NonwDate = NowTime.strftime("%Y-%m-%d")
    if RatingConstUpdateDate is None or RatingConstUpdateDate < NonwDate:
        UpdateRatingConst()
    username = request.form['username']
    password = request.form['password']
    segaLogin = SegaLogin(username, password)
    if segaLogin.Login():
        session = segaLogin.IntoGenere()
        if session:
            diffcult = ["Basic", 'Advanced', 'Expert', 'Master','Ultima']
            for diff in diffcult:
                if session is not None:
                    session = segaLogin.GetScore(diff)
            segaLogin.ParseWebScore()
            content = ""
            with open("template/table.html", mode="r", encoding='utf-8') as f:
                content = f.read()
            file_content = segaLogin.GetScoreReport()
            if file_content is not None:
                return render_template_string(content, file_content=file_content)
    return "password or sega_id is not correct", 404
    # 返回文件路径和内容


if __name__ == '__main__':
    #segaLogin = SegaLogin('chinococo', '0317a0317A')
    #segaLogin.Login()
    #segaLogin.GetRecent()
    #segaLogin.ParseWebScore()
    app.run(port=5000)
