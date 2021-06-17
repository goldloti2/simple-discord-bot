import discord
from discord.ext import commands
import json
import os
import asyncio
import requests
import time
from utils import load_json, save_json, print_cmd
from twitter/twitter_class import Twitter_Timeline, Twitter_Recent


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__headers = {"Authorization": f"Bearer {self.bot.setting["TWITTER_TOKEN"]}"}
        try:
            sub_json = load_json("settings/subscribe.json")
        except:
            sub_json = {"user": [], "query": []}
        
        removes = []
        users = []
        for user in sub_json["user"]:
            channel = self.bot.get_channel(user["ch_id"])
            if channel != None:
                users.append(Twitter_Timeline(user["username"],
                                              user["id"],
                                              self.__headers,
                                              channel))
            else:
                removes.append(user)
        for rm in removes:
            users.remove(rm)
        
        removes = []
        queries = []
        for query in self.sub_json["query"]:
            channel = self.bot.get_channel(query["ch_id"])
            if channel != None:
                queries.append(Twitter_Recent(query["query"],
                                              self.__headers,
                                              channel))
            else:
                removes.append(query)
        for rm in removes:
            queries.remove(rm)
        
        self.sub_json = sub_json
        self.users = users
        self.queries = queries
    
    @commands.command()
    async def subscribe_user(self, ctx, args):
        print_cmd("subscribe_user", args, ctx)
        user_fields = "user.fields=id,url"
        url = f"https://api.twitter.com/2/users/by?usernames={args}&{user_fields}"
        response = requests.get(url, headers = self.__headers)
        if response.status_code != 200:
            message = f":x:Can't find the user {args}"
            await ctx.send(message)
            print(message)
            return
        response = response.json()["data"][0]
        user = {"username": args,
                "id": response["id"],
                "ch_id": ctx.channel.id}
        self.sub_json["user"].append(user)
        self.users.append(Twitter_Timeline(user["username"],
                                           user["id"],
                                           self.__headers,
                                           ctx.channel))
        message = f":white_check_mark:{args} subscribed\n{response['url']}"
        await ctx.send(message)
        print(message)
    
    @commands.command()
    async def subscribe_search(self, ctx, *, args):
        print_cmd("subscribe_search", args, ctx)
        query = {"query": args,
                 "ch_id": ctx.channel.id}
        self.sub_json["query"].append(query)
        self.queries.append(Twitter_Recent(query["query"],
                                           self.__headers,
                                           channel))
        message = f":white_check_mark:keyword \"{args}\" subscribed\n"
        await ctx.send(message)
        print(message)
    
    async def request_url(self, num, start_time, ctx):
        url = 'https://www.google.com.tw/search'
        t = time.time()
        message = f"#{num}: Request at {t - start_time:.5f} sec.\n"
        res = await self.loop.run_in_executor(None, lambda: requests.get(url, params = {"q": "python"}))
        t = time.time()
        message = f"{message}#{num}: Response at {t - start_time:.5f} sec."
        await ctx.send(message)
        print(message)


def setup(bot):
    bot.add_cog(Test(bot))