import json

SETTING_FILE = "setting.json"

def load_setting(file = SETTING_FILE):
    with open(file, "r", encoding = "utf-8") as jfile:
        setting = json.load(jfile)
    return setting

def save_setting(data, file = SETTING_FILE):
    with open(file, "w", encoding = "utf-8") as jfile:
        json.dump(data, jfile)