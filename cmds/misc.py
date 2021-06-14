import discord
from discord.ext import commands
import json
import os

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx, *args):
        message = f"{self.bot.latency * 1000:.3f} ms, "
        message = message + f"@ {ctx.channel}(#{ctx.channel.id})\n"
        message = message + f"{len(args)} arguments: {', '.join(args)}"
        await ctx.send(message)


def setup(bot):
    bot.add_cog(Misc(bot))