import discord
from discord.ext import commands
import json
import os
from utils import save_json, print_cmd

class Misc(commands.Cog):
    def __init__(self, bot):
        print("load misc")
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx, *args):
        print_cmd("ping", args, ctx)
        message = f"{self.bot.latency * 1000:.3f} ms, "
        message = message + f"{ctx.channel}@<#{ctx.channel.id}>(#{ctx.channel.id})\n"
        message = message + f"{len(args)} arguments: {', '.join(args)}"
        await ctx.send(message)
        print(message)
    
    @commands.command()
    async def change_game(self, ctx, *, args):
        print_cmd("change_game", args, ctx)
        self.bot.setting["GAME"] = args
        game = discord.Game(self.bot.setting["GAME"])
        await self.bot.change_presence(activity = game)
        message = "Change bot game stat: " + self.bot.setting["GAME"]
        await ctx.send(":white_check_mark:" + message)
        save_json(self.bot.setting)
        print(message)


def setup(bot):
    bot.add_cog(Misc(bot))