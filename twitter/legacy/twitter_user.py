''' Not in use '''

import requests
import json
from utils import parse_twitter_msg

class Twitter_User(Twitter_Class):
    def __init__(self, username, token, channel, loop):
        super.__init__(self, "user", token, channel)
        self.org_url = self.url
        self.username = username
        self.params = {}
    
    def response_proc(self, response):
        messages = []
        for data in reversed(response["data"]):
            msg = parse_twitter_msg(data["created_at"],
                                    self.username,
                                    data["id"])
            messages.append(msg)
        self.params["since_id"] = response["meta"]["newest_id"]
        return messages
    
    async def request(self, loop):
        def req():
            return requests.get(self.url,
                                headers = self.__headers,
                                params = self.params)
        response = loop.run_in_executor(None, req)
        if response.status_code != 200:
            return
        messages = self.response_proc(response.json())
        if self.ini == True:
            self.ini = False
            return
        for msg in messages:
            await self.channel.send(msg)