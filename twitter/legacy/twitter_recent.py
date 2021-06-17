''' Not in use '''
import requests
import json
from twitter_class import Twitter_Class
from utils import parse_twitter_msg

class Twitter_Recent(Twitter_Class):
    def __init__(self, query, token, channel, loop):
        super.__init__(self, "recent", token, channel)
        self.query = query
        self.params = {"query": query,
                       "max_results": 50,
                       "tweet.fields": "author_id,created_at",
                       "expansions": "author_id",
                       "user.fields": "username"}
        self.request(loop)
    
    def response_proc(self, response):
        messages = []
        users = {}
        for user in response["includes"]["users"]:
            users[user["id"]] = user["username"]
        for data in reversed(response["data"]):
            msg = parse_twitter_msg(data["created_at"],
                                    user[data["author_id"]],
                                    data["id"])
            messages.append(msg)
        self.params["since_id"] = response["meta"]["newest_id"]
        return messages