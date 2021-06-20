import requests
import json
import asyncio
from utils import parse_twitter_msg

from log import logger, print_cmd, send_msg

url_factory = {"timeline": "https://api.twitter.com/2/users/%s/tweets",
               "recent": "https://api.twitter.com/2/tweets/search/recent"}

class Twitter_Class():
    def __init__(self, api, headers, channel):
        self.url = url_factory[api]
        self.__headers = headers
        self.channel = channel
    
    def response_proc(self, response):
        raise NotImplementedError
    
    def req(self):
        return requests.get(self.url,
                            headers = self.__headers,
                            params = self.params)
    
    def init_req(self):
        logger.debug(f"init request: {self.console_msg}")
        response = self.req()
        if response.status_code != 200:
            logger.warning(f"init {self.console_msg}: {response.status_code}")
            logger.warning(response.url)
            return
        res_json = response.json()
        res_cnt = res_json["meta"]["result_count"]
        logger.debug(f"init response get: {res_cnt:2}, {self.console_msg}")
        if res_cnt == 0:
            return
        self.params["since_id"] = res_json["meta"]["newest_id"]
    
    async def request(self):
        loop = asyncio.get_running_loop()
        logger.debug(f"request: {self.console_msg}")
        response = await loop.run_in_executor(None, self.req)
        if response.status_code != 200:
            logger.warning(f"{self.console_msg}: {response.status_code}")
            logger.warning(response.url)
            return
        res_json = response.json()
        res_cnt = res_json["meta"]["result_count"]
        logger.debug(f"response get: {res_cnt:2}, from {self.console_msg} ")
        if res_cnt == 0:
            return
        messages = self.response_proc(res_json)
        self.params["since_id"] = res_json["meta"]["newest_id"]
        for msg in messages:
            await send_msg(self.console_msg, msg, ctx)



class Twitter_Timeline(Twitter_Class):
    def __init__(self, username, id, headers, channel):
        super().__init__("timeline", headers, channel)
        self.url = self.url % id
        self.username = username
        self.params = {"exclude": "retweets",
                       "max_results": 5,
                       "tweet.fields": "created_at"}
        self.console_msg = f"@{username} in {channel}"
        self.init_req()
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
    def __init__(self, query, headers, channel):
        super().__init__("recent", headers, channel)
        self.query = query
        self.params = {"query": query,
                       "max_results": 10,
                       "tweet.fields": "author_id,created_at",
                       "expansions": "author_id",
                       "user.fields": "username"}
        self.console_msg = f"\"{query}\" in {channel}"
        self.init_req()
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