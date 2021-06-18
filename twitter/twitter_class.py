import requests
import json
import asyncio
from utils import parse_twitter_msg

import warnings
warnings.filterwarnings("ignore", category = RuntimeWarning)

url_factory = {"timeline": "https://api.twitter.com/2/users/%s/tweets",
               "recent": "https://api.twitter.com/2/tweets/search/recent"}

class Twitter_Class():
    def __init__(self, api, headers, channel):
        self.url = url_factory[api]
        self.__headers = headers
        self.channel = channel
        self.ini = True
    
    def response_proc(self, response):
        raise NotImplementedError
    
    async def request(self):
        def req():
            return requests.get(self.url,
                                headers = self.__headers,
                                params = self.params)
        loop = asyncio.get_running_loop()
        response = loop.run_in_executor(None, req)
        if response.status_code != 200:
            print(self.console_msg + ":" + response.status_code)
            return
        messages = self.response_proc(response.json())
        if self.ini == True:
            self.ini = False
            return
        for msg in messages:
            await self.channel.send(msg)
            print(self.console_msg + "\n" + msg)



class Twitter_Timeline(Twitter_Class):
    def __init__(self, username, id, headers, channel):
        super().__init__("timeline", headers, channel)
        self.url = self.url % id
        self.username = username
        self.params = {"exclude": "retweets",
                       "max_results": 50,
                       "tweet.fields": "created_at"}
        self.console_msg = f"@{username} in {channel}"
        self.request()
    
    def response_proc(self, response):
        messages = []
        for data in reversed(response["data"]):
            msg = parse_twitter_msg(data["created_at"],
                                    self.username,
                                    data["id"])
            messages.append(msg)
        self.params["since_id"] = response["meta"]["newest_id"]
        return messages



class Twitter_Recent(Twitter_Class):
    def __init__(self, query, headers, channel):
        super().__init__("recent", headers, channel)
        self.query = query
        self.params = {"query": query,
                       "max_results": 50,
                       "tweet.fields": "author_id,created_at",
                       "expansions": "author_id",
                       "user.fields": "username"}
        self.console_msg = f"\"{query}\" in {channel}"
        self.request()
    
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