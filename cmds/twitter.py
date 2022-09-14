import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
import httpx
import os
from typing import Literal
from twitter.twitter_class import TwitterTimeline, TwitterRecent
import utils.log as log
from utils.utils import load_json, save_json

logger = log.get_logger()
timer_int = 1


def json_path(guild: int, mode = "path"):
    paths = ["settings", "subscribe.json"]
    if mode == "path":
        return os.path.join(paths[0], str(guild), paths[1])
    elif mode == "dir":
        return os.path.join(paths[0], str(guild))


class Twitter(commands.GroupCog):
    @log.initlog
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.__headers = {"Authorization": f"Bearer {self.bot.setting['TWITTER_TOKEN']}"}
        self.sub_cnt = 0
        self.sub_json = {}
        self.twitter_obj = {}
        timer = self.update_timer.start()
        if timer != None:
            logger.debug(f"Set timer success:{timer_int} min")
        else:
            logger.error("set timer failed")
    
    @tasks.loop(minutes = timer_int)
    async def update_timer(self):
        if not self.bot.is_closed():
            logger.debug("Twitter timer awake")
            all_tasks = []
            if self.sub_cnt > 0:
                async with httpx.AsyncClient() as client:
                    for guild in self.bot.guilds:
                        all_tasks.append(self.call_update(guild.id, client))
                    await asyncio.gather(*all_tasks)
        
    @update_timer.before_loop
    async def init_load(self):
        '''
        sub_json (in twitter_obj, elements in "user" and "query" are TwitterClass object):
        {
            <guild id>: {
                "user": [
                    { "username":<>, "id":<>, "ch_id":<>, "since_id":<> },
                    ...
                ],
                "query": [
                    { "query":<>, "ch_id":<>, "since_id":<> },
                    ...
                ]
            },
            ...
        }
        '''
        
        await self.bot.wait_until_ready()
        readed = {"user": 0, "query": 0}
        finded = {"user": 0, "query": 0}
        for guild in self.bot.guilds:
            self.twitter_obj[guild.id] = {}
            try:
                sub_json = load_json(json_path(guild.id))
            except:
                sub_json = {"user": [], "query": []}
            
            '''check and create TwitterTimeline objects'''
            for sub_type in sub_json:
                readed[sub_type] += len(sub_json[sub_type])
                removes = []
                objs = []
                for sub in sub_json[sub_type]:
                    channel = self.bot.get_channel(sub["ch_id"])
                    if channel != None:
                        if sub_type == "user":
                            twitter_cls = TwitterTimeline
                        else:
                            twitter_cls = TwitterRecent
                        tmp = twitter_cls(sub,
                                          self.__headers,
                                          channel)
                        objs.append(tmp)
                    else:
                        removes.append(sub)
                for rm in removes:
                    sub_json[sub_type].remove(rm)
                finded[sub_type] += len(objs)
                self.twitter_obj[guild.id][sub_type] = objs
                
            self.sub_json[guild.id] = sub_json
            save_json(sub_json, json_path(guild.id))
        user_num = f"{finded['user']}/{readed['user']}"
        query_num = f"{finded['query']}/{readed['query']}"
        logger.info(f"found {user_num} user, {query_num} query")
        self.sub_cnt = finded['user'] + finded['query']

    '''
    command subscribe(type, search):
        argument:
            type ("user" or "query"): subscribe to user or query
            search (required): name or query line
        send message (on success):
            user:
                ":white_check_mark:Subscribed: {current Twitter name}@{search}"
                "{home_url}"
            query:
                ":white_check_mark:Subscribed: \"{search}\""
        function:
            user:
                try subscribe to the specific Twitter user in the current channel.
                the Twitter user can only be subscribed in 1 channel.
            query:
                try subscribe to the specific Twitter search query in the current channel.
            self.twitter_obj, self.sub_json and the json file will be updated.
    '''
    @app_commands.command(description = "Subscribe to the Twitter user or query results")
    @app_commands.describe(type = "subscribe to user or query",
                           search = "user name or query. \'-RT\' is recommended for query")
    @log.commandlog
    async def subscribe(self, interact: discord.Interaction,
                        type: Literal["user", "query"],
                        search: str):
        if type == "user":
            message = self.subscribe_user(interact, search)
        else:
            message = self.subscribe_search(interact, search)
        return message
    
    def subscribe_user(self, interact: discord.Interaction, name: str):
        guild = interact.guild.id
        for exist_user in self.sub_json[guild]["user"]:
            if exist_user["username"] == name:
                err_msg = f"user @{name} already subscribed, in {interact.guild.name}"
                message = f":x:The user @{name} already subscribed at <#{exist_user['ch_id']}>"
                return (message, err_msg)
        
        user_fields = "user.fields=id,name"
        url = f"https://api.twitter.com/2/users/by?usernames={name}&{user_fields}"
        try:
            response = httpx.get(url, headers = self.__headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            err_msg = "can't find user"
            message = f":x:Can't find the user @{name}"
            return (message, err_msg)
        
        response = response.json()["data"][0]
        user = {"username": name,
                "id": response["id"],
                "ch_id": interact.channel.id}
        new_obj = TwitterTimeline(user,
                                  self.__headers,
                                  interact.channel)
        logger.info(f"add user: @{name}, in {interact.guild.name}#{interact.channel}")
        self.sub_json[guild]["user"].append(user)
        self.twitter_obj[guild]["user"].append(new_obj)
        save_json(self.sub_json[guild], json_path(guild))
        self.sub_cnt += 1
        home_url = f"https://twitter.com/{name}"
        message = f":white_check_mark:Subscribed: {response['name']}@{name}\n{home_url}"
        return message
    
    def subscribe_search(self, interact: discord.Interaction, query_line: str):
        guild = interact.guild.id
        query = {"query": query_line,
                 "ch_id": interact.channel.id}
        new_obj = TwitterRecent(query,
                                self.__headers,
                                interact.channel)
        logger.info(f"add query: \"{query_line}\", in {interact.channel}")
        self.sub_json[guild]["query"].append(query)
        self.twitter_obj[guild]["query"].append(new_obj)
        save_json(self.sub_json[guild], json_path(guild))
        self.sub_cnt += 1
        message = f":white_check_mark:subscribed: \"{query_line}\""
        return message
    
    '''
    command subscribed():
        argument: None
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
    @app_commands.command(description = "Show all subscription with id")
    @log.commandlog
    async def subscription(self, interact: discord.Interaction):
        guild = interact.guild.id
        message = "```\n"
        message = message + "user:\n"
        for i, user in enumerate(self.sub_json[guild]["user"]):
            channel = self.bot.get_channel(user['ch_id'])
            line = "@" + user["username"]
            message = message + f"{i:>7} {line:<35} #{channel}\n"
        message = message + "query:\n"
        for i, query in enumerate(self.sub_json[guild]["query"]):
            channel = self.bot.get_channel(query['ch_id'])
            line = f"\"{query['query']}\""
            message = message + f"{i:>7} {line:<35} #{channel}\n"
        message = message + "```"
        return message
    
    '''
    command update():
        argument: None
        send message (on success):
            all subscribed messages
        function:
            Update Twitter immediately.
    '''
    @app_commands.command(description = "Update Twitter immediately")
    @log.commandlog
    async def update(self, interact: discord.Interaction):
        async with httpx.AsyncClient() as client:
            await self.call_update(interact.guild.id, client)
        return {"content": "done!", "ephemeral": True}
    
    async def call_update(self, guild: int, client: httpx.AsyncClient):
        all_tasks = []
        for sub_type in self.twitter_obj[guild]:
            no_ch = []
            for i, sub in enumerate(self.twitter_obj[guild][sub_type]):
                if self.bot.get_channel(sub.channel.id) != None:
                    all_tasks.append(sub.request(client))
                else:
                    no_ch.append(i)
                    warn_msg = f"Can't find #{sub.channel.name}, delete "
                    if sub_type == "user":
                        warn_msg = warn_msg + f"@{sub.username}"
                    else:
                        warn_msg = warn_msg + f"\"{sub.query}\""
                    logger.warning(warn_msg)
            for i in sorted(no_ch, reverse = True):
                self.sub_json[guild][sub_type].pop(i)
                self.twitter_obj[guild][sub_type].pop(i)
            self.sub_cnt -= len(no_ch)
        
        if len(all_tasks) > 0:
            await asyncio.gather(*all_tasks)
            save_json(self.sub_json[guild], json_path(guild))
        else:
            await asyncio.sleep(1)
    
    '''
    command delete_user(args):
        argument:
            type ("user" or "query"): user or query
            search (required): subscription index to be deleted
        send message (on success):
            user:
                ":white_check_mark:Deubscribed: @{username}"
            query:
                ":white_check_mark:Deubscribed: \"{query}\""
        function:
            user:
                delete the subscription to the specific user.
            query:
                delete the subscription to the specific search query.
            self.twitter_obj, self.sub_json and the json file will be updated.
    '''
    @app_commands.command(description = "Delete the Subscription of the Twitter")
    @app_commands.describe(type = "user or query",
                           id = "user or query id")
    @log.commandlog
    async def delete(self, interact: discord.Interaction,
                     type: Literal["user", "query"],
                     id: app_commands.Range[int, 0, None]):
        if type == "user":
            message = self.delete_user(interact, id)
        else:
            message = self.delete_search(interact, id)
        return message
    
    def delete_user(self, interact: discord.Interaction, id: int):
        guild = interact.guild.id
        if id >= len(self.twitter_obj[guild]["user"]):
            err_msg = f"index out of bound: {id}"
            message = ":x:index out of bound"
            return (message, err_msg)
        
        self.twitter_obj[guild]["user"].pop(id)
        self.sub_cnt -= 1
        username = self.sub_json[guild]["user"].pop(id)["username"]
        message = f":white_check_mark:Deubscribed: @{username}"
        save_json(self.sub_json[guild], json_path(guild))
        return message
    
    def delete_search(self, interact: discord.Interaction, id: int):
        guild = interact.guild.id
        if id >= len(self.twitter_obj[guild]["query"]):
            err_msg = f"index out of bound: {id}"
            message = ":x:index out of bound"
            return (message, err_msg)
        
        self.twitter_obj[guild]["query"].pop(id)
        self.sub_cnt -= 1
        query = self.sub_json[guild]["query"].pop(id)["query"]
        message = f":white_check_mark:Deubscribed: \"{query}\""
        save_json(self.sub_json[guild], json_path(guild))
        return message

    def cog_unload(self):
        if not self.update_timer.is_being_cancelled():
            self.update_timer.cancel()
            logger.debug("Twitter timer removed")
        else:
            logger.error("twitter timer not found")


async def setup(bot: commands.Bot):
    await bot.add_cog(Twitter(bot))