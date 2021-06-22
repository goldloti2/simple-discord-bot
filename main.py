import discord
from discord.ext import commands
from utils.log import logger
from utils.utils import load_json


setting = load_json()

bot = commands.Bot(command_prefix = setting["PREFIX"])
bot.setting = setting


@bot.event
async def on_ready():
    game = discord.Game(bot.setting["GAME"])
    await bot.change_presence(status=discord.Status.idle, activity=game)
    try:
        bot.load_extension("utils.cog_core")
    except commands.errors.ExtensionAlreadyLoaded:
        pass
    logger.info(f"logged in as {bot.user}, in {[g.name for g in bot.guilds]}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        logger.warning("recieve unknown command")
        logger.debug(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        pass
    else:
        logger.error(error)


if __name__ == "__main__":
    logger.info("bot start...")
    bot.run(bot.setting["DC_TOKEN"])