import json
import requests
respond = requests.get(url="https://reiwa.f5.si/chunithm_luminous.json")
content = json.loads(respond.content.decode('utf-8-sig'))  # Decode using 'utf-8-sig'
const_rating = {}
for song in content:
    const_rating[song["meta"]["title"]] = {}
    for diffcuilt in song["data"]:
        const_rating[song["meta"]["title"]][diffcuilt] = song["data"][diffcuilt]["const"]
print(const_rating)