import discord
import httpx
import utils.log as log
from utils.utils import parse_twitter_msg

logger = log.get_logger()

url_factory = {"timeline": "https://api.twitter.com/2/users/%s/tweets",
               "recent": "https://api.twitter.com/2/tweets/search/recent"}

class TwitterClass():
    def __init__(self, api: str, headers: dict, channel: discord.TextChannel):
        self.url = url_factory[api]
        self.__headers = headers
        self.channel = channel
        self.ini = True
    
    def response_proc(self, response: dict):
        raise NotImplementedError
    
    async def request(self, client: httpx.AsyncClient):
        logger.debug(f"request: {self.console_msg}")
        try:
            response = await client.get(self.url,
                                        headers = self.__headers,
                                        params = self.params)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"failed {self.console_msg}: {response.status_code}")
            logger.debug(str(e))
            return
        except httpx.HTTPError as e:
            logger.warning(f"request failed: {e.request.url}")
            logger.debug(str(e))
            return
        except:
            logger.error(f"request error")
            logger.debug("\n", exc_info = True)
            return
        res_json = response.json()
        
        res_cnt = res_json["meta"]["result_count"]
        logger.debug(f"response get: {res_cnt:2}, from {self.console_msg} ")
        if res_cnt == 0:
            return
        self.params["since_id"] = res_json["meta"]["newest_id"]
        self.sub_json["since_id"] = res_json["meta"]["newest_id"]
        
        if self.ini == True:
            self.ini = False
            self.params["max_results"] = 100
            return
        
        messages = self.response_proc(res_json)
        for msg in messages:
            await log.send_msg(self.console_msg, msg, self.channel)



class TwitterTimeline(TwitterClass):
    def __init__(self, sub_json: dict,
                 headers: dict,
                 channel: discord.TextChannel):
        super().__init__("timeline", headers, channel)
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
    
    def response_proc(self, response):
        messages = []
        for data in reversed(response["data"]):
            msg = parse_twitter_msg(data["created_at"],
                                    self.username,
                                    data["id"])
            messages.append(msg)
        return messages



class TwitterRecent(TwitterClass):
    def __init__(self, sub_json: dict,
                 headers: dict,
                 channel: discord.TextChannel):
        super().__init__("recent", headers, channel)
        self.sub_json = sub_json
        self.query = self.sub_json["query"]
        self.params = {"query": self.query,
                       "max_results": 20,
                       "tweet.fields": "author_id,created_at",
                       "expansions": "author_id",
                       "user.fields": "username"}
        self.console_msg = f"\"{self.query}\" in {self.channel}"
        if "since_id" in self.sub_json.keys():
            self.params["since_id"] = self.sub_json["since_id"]
            self.ini = False
    
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