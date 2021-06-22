import json
import datetime
import os

SETTING_FILE = os.path.join("settings", "setting.json")

def load_json(file = SETTING_FILE):
    with open(file, "r", encoding = "utf-8") as jfile:
        data = json.load(jfile)
    return data

def save_json(data, file = SETTING_FILE):
    with open(file, "w", encoding = "utf-8") as jfile:
        json.dump(data, jfile, indent = 4)

def parse_twitter_msg(isotime, username, id):
    timestr = datetime.datetime.strptime(isotime, "%Y-%m-%dT%H:%M:%S.000Z")
    timestr += datetime.timedelta(hours = 8)
    outtime = timestr.strftime("%Y/%m/%d, %H:%M")
    url = f"https://twitter.com/{username}/status/{id}"
    return f"@{username}, {outtime}:\n{url}"
    "2021-06-16T07:41:52.000Z"