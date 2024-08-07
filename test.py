import json
import requests
respond = requests.get(url="https://dp4p6x0xfi5o9.cloudfront.net/chunithm/data.json")
content = json.loads(respond.content.decode('utf-8-sig'))  # Decode using 'utf-8-sig'
for song in content["songs"]:
    print(song["title"],f"https://dp4p6x0xfi5o9.cloudfront.net/chunithm/img/cover-m/{song['imageName']}")