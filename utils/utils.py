import datetime
import json
import os

SETTING_FILE = os.path.join("settings", "setting.json")

def load_json(file: str = SETTING_FILE):
    with open(file, "r", encoding = "utf-8") as jfile:
        data = json.load(jfile)
    return data

def save_json(data: dict, file: str = SETTING_FILE):
    if not os.path.isdir(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))
    with open(file, "w", encoding = "utf-8") as jfile:
        json.dump(data, jfile, indent = 4)

def parse_twitter_msg(isotime: str, username: str, id: str):
    timestr = datetime.datetime.strptime(isotime, "%Y-%m-%dT%H:%M:%S.000Z")
    timestr += datetime.timedelta(hours = 8)
    outtime = timestr.strftime("%Y/%m/%d, %H:%M")
    msg = f"@{username}, {outtime}:\n"
    msg = msg.replace("_", "\\_")
    msg = msg.replace("*", "\\*")
    msg = msg.replace("~", "\\~")
    msg = msg + f"https://twitter.com/{username}/status/{id}"
    return msg
    "2021-06-16T07:41:52.000Z"