import discord
from discord.ext import commands
from utils.utils import save_json

import utils.log as log
logger = log.getlogger()

class Misc(commands.Cog):
    @log.initlog
    def __init__(self, bot):
        self.bot = bot
    
    '''
    command ping(*args):
        argument:
            *args (optional): test if can get multiple arguments
        send message (on success):
            "{self.bot.latency * 1000:.3f} ms, {channel}@<#{channel.id}>(#{channel.id})"
            "{len(args)} arguments: {args}"
        function:
            just a test ping
    '''
    @commands.command(help = "Send the latency of the bot, channel name and channel id"\
                             ", and the arguments you sent",
                      brief = "Ping the bot")
    @log.commandlog
    async def ping(self, ctx, *args):
        message = f"{self.bot.latency * 1000:.3f} ms, "
        message = message + f"{ctx.channel}@<#{ctx.channel.id}>(\\#{ctx.channel.id})\n"
        message = message + f"{len(args)} arguments: {', '.join(args)}"
        return message
    
    '''
    command change_game(args):
        argument:
            args (required): game name want to change
        send message (on success):
            ":white_check_mark:Change bot game stat: {args}"
        function:
            change the game stat of the bot
    '''
    @commands.command(help = "Change the game stat of the bot with the given line",
                      brief = "Change the game stat",
                      usage = "<game stat>")
    @log.commandlog
    async def change_game(self, ctx, *, args):
        self.bot.setting["GAME"] = args
        game = discord.Game(self.bot.setting["GAME"])
        await self.bot.change_presence(activity = game)
        message = ":white_check_mark:Change bot game stat: " + self.bot.setting["GAME"]
        save_json(self.bot.setting)
        return message
    
    @change_game.error
    async def change_game_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            err_msg = "recieve no arguments."
            message = ":x:`change_game` require 1 argument"
            await log.send_err("change_game", message, err_msg, ctx)


def setup(bot):
    bot.add_cog(Misc(bot))