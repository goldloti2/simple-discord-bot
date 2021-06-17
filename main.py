import discord
from discord.ext import commands
import json
import os
import time
from log import start_logging
from utils import load_json


logger = start_logging("discord", "log/discord", debug = True)

setting = load_json()

bot = commands.Bot(command_prefix = setting["PREFIX"])
bot.load_extension("cog_core")
bot.setting = setting


@bot.event
async def on_ready():
    game = discord.Game(bot.setting["GAME"])
    await bot.change_presence(status=discord.Status.idle, activity=game)
    t = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    print(f'[{t}] logged in as {bot.user}')



if __name__ == "__main__":
    bot.run(bot.setting["DC_TOKEN"])
