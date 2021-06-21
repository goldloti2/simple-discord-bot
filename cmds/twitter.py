import discord
from discord.ext import commands
import json
import asyncio
import requests
from utils import load_json, save_json
from twitter.twitter_class import Twitter_Timeline, Twitter_Recent

from log import logger, print_cmd, send_msg, send_err
import logwrap


class Twitter(commands.Cog):
    @logwrap.initlog
    def __init__(self, bot):
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
        load_user_num = f"{len(users)}/{len(sub_json['user'])}"
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
        load_query_num = f"{len(queries)}/{len(sub_json['query'])}"
        for rm in removes:
            sub_json["query"].remove(rm)
        
        self.sub_json = sub_json
        self.TW_obj = {}
        self.TW_obj["user"] = users
        self.TW_obj["query"] = queries
        logger.info(f"found {load_user_num} user, {load_query_num} query")
    
    '''
    command subscribe_user(args):
        argument:
            args (required): username to be subscribed
        send message (on success):
            ":white_check_mark:Subscribed: {current user name}@{args}"
            "{home_url}"
        function:
            try subscribe to the specific Twitter user in the current channel.
            the Twitter user can only be subscribed in 1 channel.
            on success, self.TW_obj["user"], self.sub_json["user"] and the json file will be updated.
    '''
    @commands.command(aliases = ["sub_user", "su", "SU"])
    @logwrap.commandlog
    async def subscribe_user(self, ctx, args):
        for exist_user in self.sub_json["user"]:
            if exist_user["username"] == args:
                err_msg = "user already subscribed"
                message = f":x:The user @{args} already subscribed at <#{exist_user['ch_id']}>"
                return (message, err_msg)
        
        user_fields = "user.fields=id,name"
        url = f"https://api.twitter.com/2/users/by?usernames={args}&{user_fields}"
        home_url = f"https://twitter.com/{args}"
        response = requests.get(url, headers = self.__headers)
        if response.status_code != 200:
            err_msg = "can't find user"
            message = f":x:Can't find the user @{args}"
            return (message, err_msg)
        response = response.json()["data"][0]
        user = {"username": args,
                "id": response["id"],
                "ch_id": ctx.channel.id}
        new_obj = Twitter_Timeline(user["username"],
                                   user["id"],
                                   self.__headers,
                                   ctx.channel)
        logger.info(f"add user: @{args}, in {ctx.channel}")
        self.sub_json["user"].append(user)
        self.TW_obj["user"].append(new_obj)
        message = f":white_check_mark:Subscribed: {response['name']}@{args}\n{home_url}"
        save_json(self.sub_json, self.json_path)
        return message
    
    @subscribe_user.error
    async def subscribe_user_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            err_msg = "recieve no arguments."
            message = ":x:`subscribe_user` require 1 argument"
            await send_err("subscribe_user", message, err_msg, ctx)
    
    '''
    command subscribe_search(args):
        argument:
            args (required): query to be subscribed
        send message (on success):
            ":white_check_mark:Subscribed: \"{args}\""
        function:
            try subscribe to the specific Twitter search query in the current channel.
            self.TW_obj["query"], self.sub_json["query"] and the json file will be updated.
    '''
    @commands.command(aliases = ["sub_search", "ss", "SS", "subscribe_query", "sub_query", "sq", "SQ"])
    @logwrap.commandlog
    async def subscribe_search(self, ctx, *, args):
        query = {"query": args,
                 "ch_id": ctx.channel.id}
        new_obj = Twitter_Recent(query["query"],
                                 self.__headers,
                                 ctx.channel)
        logger.info(f"add query: \"{args}\", in {ctx.channel}")
        self.sub_json["query"].append(query)
        self.TW_obj["query"].append(new_obj)
        message = f":white_check_mark:subscribed: \"{args}\""
        save_json(self.sub_json, self.json_path)
        return message
    
    @subscribe_search.error
    async def subscribe_search_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            err_msg = "recieve no arguments."
            message = ":x:`subscribe_search` require 1 argument"
            await send_err("subscribe_search", message, err_msg, ctx)
    
    '''
    command subscribed():
        argument:
        send message (on success):
            "```"
            "user:"
            "{id} {username} #{channel)" * n
            "query:"
            "{id} \"{query}\" #{channel)" * n
            "```"
        function:
            list all the subscriptions.
    '''
    @commands.command(aliases = ["sub", "s", "S"])
    @logwrap.commandlog
    async def subscribed(self, ctx):
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
        return message
    
    '''
    command update():
        argument:
        send message (on success):
            all subscribed messages
        function:
            force to check if there is any new subscribed tweets.
    '''
    @commands.command(aliases = ["U"])
    async def update(self, ctx):
        print_cmd("update", (), ctx.channel)
        await self.call_update()
    
    async def call_update(self):
        for sub_type in self.TW_obj:
            for sub in self.TW_obj[sub_type]:
                asyncio.ensure_future(sub.request())
    
    '''(timer)'''
    
    '''
    command delete_user(args):
        argument:
            args (required): user subscription index to be deleted
        send message (on success):
            ":white_check_mark:Deubscribed: @{username}"
        function:
            delete the subscription to the specific user.
            on success, self.TW_obj["user"], self.sub_json["user"] and the json file will be updated.
    '''
    @commands.command(aliases = ["del_user", "du", "DU"])
    @logwrap.commandlog
    async def delete_user(self, ctx, args):
        try:
            del_num = int(args)
        except ValueError:
            err_msg = f"invalid argument: {args}"
            message = ":x:`delete_user` require integer as argument"
            return (message, err_msg)
        
        if del_num >= len(self.TW_obj["user"]):
            err_msg = f"index out of bound: {del_num}"
            message = ":x:index out of bound"
            return (message, err_msg)
        
        self.TW_obj["user"].pop(del_num)
        username = self.sub_json["user"].pop(del_num)["username"]
        message = f":white_check_mark:Deubscribed: @{username}"
        save_json(self.sub_json, self.json_path)
        return message
    
    @delete_user.error
    async def delete_user_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            err_msg = "recieve no arguments."
            message = ":x:`delete_user` require 1 argument"
            await send_err("delete_user", message, err_msg, ctx)
    
    '''
    command delete_search(args):
        argument:
            args (required): query subscription index to be deleted
        send message (on success):
            ":white_check_mark:Deubscribed: \"{query}\""
        function:
            delete the subscription to the specific search query.
            on success, self.TW_obj["query"], self.sub_json["query"] and the json file will be updated.
    '''
    @commands.command(aliases = ["del_search", "ds", "DS", "delete_query", "del_query", "dq", "DQ"])
    @logwrap.commandlog
    async def delete_search(self, ctx, args):
        try:
            del_num = int(args)
        except ValueError:
            err_msg = f"invalid argument: {args}"
            message = ":x:`delete_search` require integer as argument"
            return (message, err_msg)
        
        if del_num >= len(self.TW_obj["query"]):
            err_msg = f"index out of bound: {del_num}"
            message = ":x:index out of bound"
            return (message, err_msg)
        
        self.TW_obj["query"].pop(del_num)
        query = self.sub_json["query"].pop(del_num)["query"]
        message = f":white_check_mark:Deubscribed: \"{query}\""
        save_json(self.sub_json, self.json_path)
        return message
    
    @delete_search.error
    async def delete_search_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            err_msg = "recieve no arguments."
            message = ":x:`delete_search` require 1 argument"
            await send_err("delete_search", message, err_msg, ctx)


def setup(bot):
    bot.add_cog(Twitter(bot))