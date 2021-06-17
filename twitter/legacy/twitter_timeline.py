''' Not in use '''
import requests
import json
from twitter_class import Twitter_Class
from utils import parse_twitter_msg

class Twitter_Timeline(Twitter_Class):
    def __init__(self, username, id, token, channel, loop):
        super.__init__(self, "timeline", token, channel)
        self.url = self.url % id
        self.username = username
        self.params = {"exclude": "retweets",
                       "max_results": 50,
                       "tweet.fields": "created_at"}
        self.request(loop)
    
    def response_proc(self, response):
        messages = []
        for data in reversed(response["data"]):
            msg = parse_twitter_msg(data["created_at"],
                                    self.username,
                                    data["id"])
            messages.append(msg)
        self.params["since_id"] = response["meta"]["newest_id"]
        return messages