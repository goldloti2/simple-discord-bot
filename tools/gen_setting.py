import json

jdata = {}

jdata["DC_TOKEN"] = input("Discord token (required):")
jdata["TWITTER_TOKEN"] = input("Twitter bearer token (required):")
jdata["GAME"] = input("game status (optional):")
jdata["PREFIX"] = input("Prefix (optional):")

with open("settings/setting.json", "w", encoding = "utf-8") as jfile:
    json.dump(jdata, jfile, indent = 4)