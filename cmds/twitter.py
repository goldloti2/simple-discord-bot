import asyncio
from discord.ext import commands, tasks
import httpx
import os
# import requests
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


class Twitter(commands.Cog):
    @log.initlog
    def __init__(self, bot: commands.bot):
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
                    {
                    "username":<>,
                    "id":<>,
                    "ch_id":<>,
                    "since_id":<>
                    },
                    ...
                ],
                "query": [
                    {
                    "query":<>,
                    "ch_id":<>,
                    "since_id":<>
                    },
                    ...
                ]
            },
            ...
        }
        '''
        
        await self.bot.wait_until_ready()
        readed = {"user":0, "query":0}
        finded = {"user":0, "query":0}
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
    command subscribe_user(args):
        argument:
            args (required): username to be subscribed
        send message (on success):
            ":white_check_mark:Subscribed: {current user name}@{args}"
            "{home_url}"
        function:
            try subscribe to the specific Twitter user in the current channel.
            the Twitter user can only be subscribed in 1 channel.
            on success, self.twitter_obj["user"] and the json file will be updated.
    '''
    @commands.command(aliases = ["sub_user", "su", "SU"],
                      help = "Subscribe to the Twitter user if found.\n"
                             "The latest tweets will show in the channel you call this command.\n"
                             "Please give the user name (started with \"@\")",
                      brief = "Subscribe to the Twitter user",
                      usage = "<username>")
    @log.commandlog
    async def subscribe_user(self, ctx: commands.context, args: str):
        guild = ctx.guild.id
        for exist_user in self.sub_json[guild]["user"]:
            if exist_user["username"] == args:
                err_msg = f"user already subscribed in {ctx.guild.name}"
                message = f":x:The user @{args} already subscribed at <#{exist_user['ch_id']}>"
                return (message, err_msg)
        
        user_fields = "user.fields=id,name"
        url = f"https://api.twitter.com/2/users/by?usernames={args}&{user_fields}"
        home_url = f"https://twitter.com/{args}"
        response = httpx.get(url, headers = self.__headers)
        if response.status_code != 200:
            err_msg = "can't find user"
            message = f":x:Can't find the user @{args}"
            return (message, err_msg)
        response = response.json()["data"][0]
        user = {"username": args,
                "id": response["id"],
                "ch_id": ctx.channel.id}
        new_obj = TwitterTimeline(user,
                                  self.__headers,
                                  ctx.channel)
        logger.info(f"add user: @{args}, in {ctx.guild.name}#{ctx.channel}")
        self.sub_json[guild]["user"].append(user)
        self.twitter_obj[guild]["user"].append(new_obj)
        self.sub_cnt += 1
        message = f":white_check_mark:Subscribed: {response['name']}@{args}\n{home_url}"
        save_json(self.sub_json[guild], json_path(guild))
        return message
    
    @subscribe_user.error
    async def subscribe_user_error(self, ctx: commands.context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            err_msg = "recieve no arguments."
            message = ":x:`subscribe_user` require 1 argument"
            await log.send_err("subscribe_user", message, err_msg, ctx)
    
    '''
    command subscribe_search(args):
        argument:
            args (required): query to be subscribed
        send message (on success):
            ":white_check_mark:Subscribed: \"{args}\""
        function:
            try subscribe to the specific Twitter search query in the current channel.
            self.twitter_obj["query"], self.sub_json["query"] and the json file will be updated.
    '''
    @commands.command(aliases = ["sub_search", "ss", "SS"],
                      help = "Subscribe to the tweets can be found with the given query line.\n"
                             "The latest tweets will show in the channel you call this command.",
                      brief = "Subscribe to the Twitter search",
                      usage = "<query>")
    @log.commandlog
    async def subscribe_search(self, ctx: commands.context, *, args: str):
        guild = ctx.guild.id
        query = {"query": args,
                 "ch_id": ctx.channel.id}
        new_obj = TwitterRecent(query,
                                self.__headers,
                                ctx.channel)
        logger.info(f"add query: \"{args}\", in {ctx.channel}")
        self.sub_json[guild]["query"].append(query)
        self.twitter_obj[guild]["query"].append(new_obj)
        self.sub_cnt += 1
        message = f":white_check_mark:subscribed: \"{args}\""
        save_json(self.sub_json[guild], json_path(guild))
        return message
    
    @subscribe_search.error
    async def subscribe_search_error(self, ctx: commands.context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            err_msg = "recieve no arguments."
            message = ":x:`subscribe_search` require 1 argument"
            await log.send_err("subscribe_search", message, err_msg, ctx)
    
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
    @commands.command(aliases = ["sub", "s", "S"],
                      help = "Show all subscription with their id.",
                      brief = "Show all subscription")
    @log.commandlog
    async def subscribed(self, ctx: commands.context):
        guild = ctx.guild.id
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
        argument:
        send message (on success):
            all subscribed messages
        function:
            force to check if there is any new subscribed tweets.
    '''
    @commands.command(aliases = ["u", "U"],
                      help = "Force checking the latest tweets of all subscriptions",
                      brief = "Force checking update")
    async def update(self, ctx: commands.context):
        log.print_cmd("update", (), ctx)
        async with httpx.AsyncClient() as client:
            await self.call_update(ctx.guild.id, client)
    
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
            args (required): user subscription index to be deleted
        send message (on success):
            ":white_check_mark:Deubscribed: @{username}"
        function:
            delete the subscription to the specific user.
            on success, self.twitter_obj["user"], self.sub_json["user"] and the json file will be updated.
    '''
    @commands.command(aliases = ["del_user", "du", "DU"],
                      help = "Delete the Subscription of the Twitter user with the given id\n"
                             "The id can be find using subscribed command.",
                      brief = "Delete the Twitter user",
                      usage = "<id>")
    @log.commandlog
    async def delete_user(self, ctx: commands.context, args: str):
        guild = ctx.guild.id
        try:
            del_num = int(args)
        except ValueError:
            err_msg = f"invalid argument: {args}"
            message = ":x:`delete_user` require integer as argument"
            return (message, err_msg)
        
        if del_num >= len(self.twitter_obj[guild]["user"]):
            err_msg = f"index out of bound: {del_num}"
            message = ":x:index out of bound"
            return (message, err_msg)
        
        self.twitter_obj[guild]["user"].pop(del_num)
        self.sub_cnt -= 1
        username = self.sub_json[guild]["user"].pop(del_num)["username"]
        message = f":white_check_mark:Deubscribed: @{username}"
        save_json(self.sub_json[guild], json_path(guild))
        return message
    
    @delete_user.error
    async def delete_user_error(self, ctx: commands.context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            err_msg = "recieve no arguments."
            message = ":x:`delete_user` require 1 argument"
            await log.send_err("delete_user", message, err_msg, ctx)
    
    '''
    command delete_search(args):
        argument:
            args (required): query subscription index to be deleted
        send message (on success):
            ":white_check_mark:Deubscribed: \"{query}\""
        function:
            delete the subscription to the specific search query.
            on success, self.twitter_obj["query"], self.sub_json["query"] and the json file will be updated.
    '''
    @commands.command(aliases = ["del_search", "ds", "DS"],
                      help = "Delete the Subscription of the Twitter search with the given id\n"
                             "The id can be find using subscribed command.",
                      brief = "Delete the Twitter search",
                      usage = "<id>")
    @log.commandlog
    async def delete_search(self, ctx: commands.CommandError, args: str):
        guild = ctx.guild.id
        try:
            del_num = int(args)
        except ValueError:
            err_msg = f"invalid argument: {args}"
            message = ":x:`delete_search` require integer as argument"
            return (message, err_msg)
        
        if del_num >= len(self.twitter_obj[guild]["query"]):
            err_msg = f"index out of bound: {del_num}"
            message = ":x:index out of bound"
            return (message, err_msg)
        
        self.twitter_obj[guild]["query"].pop(del_num)
        self.sub_cnt -= 1
        query = self.sub_json[guild]["query"].pop(del_num)["query"]
        message = f":white_check_mark:Deubscribed: \"{query}\""
        save_json(self.sub_json[guild], json_path(guild))
        return message
    
    @delete_search.error
    async def delete_search_error(self, ctx: commands.context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            err_msg = "recieve no arguments."
            message = ":x:`delete_search` require 1 argument"
            await log.send_err("delete_search", message, err_msg, ctx)

    def cog_unload(self):
        if not self.update_timer.is_being_cancelled():
            self.update_timer.cancel()
            logger.debug("Twitter timer removed")
        else:
            logger.error("twitter timer not found")


async def setup(bot: commands.bot):
    await bot.add_cog(Twitter(bot))