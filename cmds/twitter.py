import discord
from discord.ext import commands
import json
import asyncio
import requests
from utils import load_json, save_json, print_cmd
from twitter.twitter_class import Twitter_Timeline, Twitter_Recent


class Twitter(commands.Cog):
    def __init__(self, bot):
        print("load twitter")
        self.bot = bot
        self.json_path = "settings/subscribe.json"
        self.__headers = {"Authorization": f"Bearer {self.bot.setting['TWITTER_TOKEN']}"}
        try:
            sub_json = load_json(self.json_path)
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
            sub_json["user"].remove(rm)
        
        removes = []
        queries = []
        for query in sub_json["query"]:
            channel = self.bot.get_channel(query["ch_id"])
            if channel != None:
                queries.append(Twitter_Recent(query["query"],
                                              self.__headers,
                                              channel))
            else:
                removes.append(query)
        for rm in removes:
            sub_json["query"].remove(rm)
        
        self.sub_json = sub_json
        self.users = users
        self.queries = queries
    
    @commands.command(aliases = ["sub_user", "su", "SU"])
    async def subscribe_user(self, ctx, args):
        print_cmd("subscribe_user", args, ctx)
        for exist_user in self.sub_json["user"]:
            if exist_user["username"] == args:
                message = f":x:The user @{args} already subscribed at <#{exist_user['ch_id']}>"
                await ctx.send(message)
                print(message + f"({self.bot.get_channel(exist_user['ch_id'])})")
                return
        
        user_fields = "user.fields=id,name"
        url = f"https://api.twitter.com/2/users/by?usernames={args}&{user_fields}"
        home_url = f"https://twitter.com/{args}"
        response = requests.get(url, headers = self.__headers)
        if response.status_code != 200:
            message = f":x:Can't find the user @{args}"
            await ctx.send(message)
            print(message)
            return
        response = response.json()["data"][0]
        user = {"username": args,
                "id": response["id"],
                "ch_id": ctx.channel.id}
        print(f"add user: @{args}, in {ctx.channel}")
        self.sub_json["user"].append(user)
        self.users.append(Twitter_Timeline(user["username"],
                                           user["id"],
                                           self.__headers,
                                           ctx.channel))
        message = f":white_check_mark:Subscribed: {response['name']}@{args}\n{home_url}"
        await ctx.send(message)
        print(message)
        save_json(self.sub_json, self.json_path)
    
    @commands.command(aliases = ["sub_search", "ss", "SS", "subscribe_query", "sq", "SQ"])
    async def subscribe_search(self, ctx, *, args):
        print_cmd("subscribe_search", args, ctx)
        query = {"query": args,
                 "ch_id": ctx.channel.id}
        print(f"add query: \"{args}\", in {ctx.channel}")
        self.sub_json["query"].append(query)
        self.queries.append(Twitter_Recent(query["query"],
                                           self.__headers,
                                           ctx.channel))
        message = f":white_check_mark:subscribed: \"{args}\""
        await ctx.send(message)
        print(message)
        save_json(self.sub_json, self.json_path)
    
    @commands.command(aliases = ["U"])
    async def update(self, ctx):
        print_cmd("update", [], ctx)
        await self.call_update()
    
    async def call_update(self):
        for sub_type in self.sub_json:
            for sub in self.sub_json[sub_type]:
                asyncio.ensure_future(sub.request())
    
    @commands.command(aliases = ["sub", "s", "S"])
    async def subscribed(self, ctx):
        print_cmd("subscribed", [], ctx)
        message = "```\n"
        message = message + "user:\n"
        for i, user in enumerate(self.sub_json["user"]):
            channel = self.bot.get_channel(user['ch_id'])
            line = "@" + user["username"]
            message = message + f"{i:>7} {line:<35} #{channel}\n"
        message = message + "query:\n"
        for i, query in enumerate(self.sub_json["query"]):
            channel = self.bot.get_channel(query['ch_id'])
            line = f"\"{query['query']}\""
            message = message + f"{i:>7} {line:<35} #{channel}\n"
        message = message + "```"
        await ctx.send(message)
        print(message)


def setup(bot):
    bot.add_cog(Twitter(bot))