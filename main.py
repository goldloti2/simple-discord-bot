import asyncio
import discord
from discord.ext import commands
import os
from shutil import rmtree
import utils.log as log
from utils.utils import load_json

log.init_logger()
logger = log.get_logger()
setting = load_json()

bot = commands.Bot(command_prefix = setting["PREFIX"],
                   intents = discord.Intents.all())
bot.setting = setting
bot.version = "v.2.2.230202"


@bot.event
async def on_ready():
    bot.tree.copy_global_to(guild = bot.guilds[0])
    await bot.tree.sync(guild = bot.guilds[0])
    game = discord.Game(bot.setting["GAME"])
    await bot.change_presence(status = discord.Status.idle, activity = game)
    logger.info(f"logged in as {bot.user}, in {[g.name for g in bot.guilds]}")

@bot.event
async def on_guild_join(guild: discord.Guild):
    os.makedirs(os.path.join("settings", str(guild.id)), exist_ok = True)

@bot.event
async def on_guild_remove(guild: discord.Guild):
    rmtree(os.path.join("settings", str(guild.id)), exist_ok = True)

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        logger.warning("recieve unknown command")
        logger.debug(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        pass
    else:
        logger.error(error)


async def main():
    logger.info("bot start...")
    async with bot:
        try:
            await bot.load_extension("utils.cog_core")
        except commands.errors.ExtensionAlreadyLoaded:
            pass
        await bot.start(bot.setting["DC_TOKEN"])

if __name__ == "__main__":
    asyncio.run(main())