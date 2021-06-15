import json

jdata = {}

jdata["DC_TOKEN"] = input("Discord token (required):")
jdata["GAME"] = input("game status (optional):")
jdata["PREFIX"] = input("Prefix (optional):")

json.dump("setting.json", jdata)