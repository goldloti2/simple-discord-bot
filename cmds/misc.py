import discord
from discord.ext import commands
from utils import save_json
from log import logger, print_cmd, send_msg, send_err

class Misc(commands.Cog):
    def __init__(self, bot):
        logger.info("load misc")
        self.bot = bot
        logger.info("load misc success")
    
    @commands.command()
    async def ping(self, ctx, *args):
        print_cmd("ping", args, ctx)
        message = f"{self.bot.latency * 1000:.3f} ms, "
        message = message + f"{ctx.channel}@<#{ctx.channel.id}>(#{ctx.channel.id})\n"
        message = message + f"{len(args)} arguments: {', '.join(args)}"
        await send_msg("ping", message, ctx)
    
    @commands.command()
    async def change_game(self, ctx, *, args):
        print_cmd("change_game", args, ctx)
        self.bot.setting["GAME"] = args
        game = discord.Game(self.bot.setting["GAME"])
        await self.bot.change_presence(activity = game)
        message = ":white_check_mark:Change bot game stat: " + self.bot.setting["GAME"]
        await send_msg("change_game", message, ctx)
        save_json(self.bot.setting)
    
    @change_game.error
    async def change_game_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            err_msg = "recieve no arguments."
            message = ":x:`change_game` require 1 argument"
            await send_err("change_game", message, err_msg, ctx)


def setup(bot):
    bot.add_cog(Misc(bot))