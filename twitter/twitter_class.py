import requests
import json
import asyncio
from utils.utils import parse_twitter_msg

from utils.log import logger, send_msg

url_factory = {"timeline": "https://api.twitter.com/2/users/%s/tweets",
               "recent": "https://api.twitter.com/2/tweets/search/recent"}

class Twitter_Class():
    def __init__(self, api, headers, channel, loop):
        self.url = url_factory[api]
        self.__headers = headers
        self.channel = channel
        self.loop = loop
        self.ini = True
    
    def response_proc(self, response):
        raise NotImplementedError
    
    def req(self):
        return requests.get(self.url,
                            headers = self.__headers,
                            params = self.params)
    
    async def request(self):
        logger.debug(f"request: {self.console_msg}")
        response = await self.loop.run_in_executor(None, self.req)
        if response.status_code != 200:
            logger.error(f"failed {self.console_msg}: {response.status_code}")
            logger.debug(response.text)
            return
        res_json = response.json()
        
        res_cnt = res_json["meta"]["result_count"]
        logger.debug(f"response get: {res_cnt:2}, from {self.console_msg} ")
        if res_cnt == 0:
            return
        self.params["since_id"] = self.sub_json["since_id"] = res_json["meta"]["newest_id"]
        
        if self.ini == True:
            self.ini = False
            return
        
        messages = self.response_proc(res_json)
        for msg in messages:
            await send_msg(self.console_msg, msg, self.channel)



class Twitter_Timeline(Twitter_Class):
    def __init__(self, sub_json, headers, channel, loop):
        super().__init__("timeline", headers, channel, loop)
        self.sub_json = sub_json
        self.url = self.url % self.sub_json["id"]
        self.username = self.sub_json["username"]
        self.params = {"exclude": "retweets",
                       "max_results": 5,
                       "tweet.fields": "created_at"}
        self.console_msg = f"@{self.username} in {self.channel}"
        if "since_id" in self.sub_json.keys():
            self.params["since_id"] = self.sub_json["since_id"]
            self.ini = False
        else:
            self.loop.create_task(self.request())
        self.params["max_results"] = 50
    
    def response_proc(self, response):
        messages = []
        for data in reversed(response["data"]):
            msg = parse_twitter_msg(data["created_at"],
                                    self.username,
                                    data["id"])
            messages.append(msg)
        return messages



class Twitter_Recent(Twitter_Class):
    def __init__(self, sub_json, headers, channel, loop):
        super().__init__("recent", headers, channel, loop)
        self.sub_json = sub_json
        self.query = self.sub_json["query"]
        self.params = {"query": self.query,
                       "max_results": 10,
                       "tweet.fields": "author_id,created_at",
                       "expansions": "author_id",
                       "user.fields": "username"}
        self.console_msg = f"\"{self.query}\" in {self.channel}"
        if "since_id" in self.sub_json.keys():
            self.params["since_id"] = self.sub_json["since_id"]
            self.ini = False
        else:
            self.loop.create_task(self.request())
        self.params["max_results"] = 50
    
    def response_proc(self, response):
        messages = []
        users = {}
        for user in response["includes"]["users"]:
            users[user["id"]] = user["username"]
        for data in reversed(response["data"]):
            msg = parse_twitter_msg(data["created_at"],
                                    users[data["author_id"]],
                                    data["id"])
            messages.append(msg)
        return messages