import json
import time

SETTING_FILE = "settings/setting.json"

def load_json(file = SETTING_FILE):
    with open(file, "r", encoding = "utf-8") as jfile:
        data = json.load(jfile)
    return data

def save_json(data, file = SETTING_FILE):
    with open(file, "w", encoding = "utf-8") as jfile:
        json.dump(data, jfile, indent = 4)

def print_cmd(cmd, args, ctx):
    t = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    print(f"[{t}] {cmd} {args}, from {ctx.channel}")

def parse_twitter_msg(isotime, username, id):
    timestr = time.strptime(isotime, "%Y-%m-%dT%H:%M:%S.000Z")
    outtime = time.strftime("%Y/%m/%d, %H:%M", timestr)
    url = f"https://twitter.com/{username}/status/{id}"
    return f"@{username}, {outtime}:\n{url}"