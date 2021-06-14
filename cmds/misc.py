import discord
from discord.ext import commands
from utils import save_setting
import json
import os

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx, *args):
        message = f"{self.bot.latency * 1000:.3f} ms, "
        message = message + f"@{ctx.channel}(#{ctx.channel.id})\n"
        message = message + f"{len(args)} arguments: {', '.join(args)}"
        await ctx.send(message)
    
    @commands.command()
    async def change_game(self, ctx, *, args):
        self.bot.setting["GAME"] = args
        game = discord.Game(self.bot.setting["GAME"])
        await self.bot.change_presence(activity = game)
        await ctx.send(":white_check_mark:Change bot game stat: " + self.bot.setting["GAME"])
        save_setting(self.bot.setting)


def setup(bot):
    bot.add_cog(Misc(bot))