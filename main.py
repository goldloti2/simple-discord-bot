import discord
from discord.ext import commands
from log import start_logging
from utils import load_setting
import json
import os


logger = start_logging("discord", "log/discord", debug = True)

setting = load_setting()

bot = commands.Bot(command_prefix = setting["PREFIX"])
bot.load_extension("cog_core")
bot.setting = setting


@bot.event
async def on_ready():
    game = discord.Game(bot.setting["GAME"])
    await bot.change_presence(status=discord.Status.idle, activity=game)
    print('>>> We have logged in as {0.user}'.format(bot))



if __name__ == "__main__":
    bot.run(bot.setting["DC_TOKEN"])
