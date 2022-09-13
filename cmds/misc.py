import discord
from discord import app_commands
from discord.ext import commands
from utils.utils import save_json
import utils.log as log

logger = log.get_logger()

class Misc(commands.Cog):
    @log.initlog
    def __init__(self, bot: commands.bot):
        self.bot = bot
    
    '''
    command ping():
        send message (on success):
            "{self.bot.latency * 1000:.3f} ms, {channel}@<#{channel.id}>(#{channel.id})"
        function:
            Ping the bot and show the latency
    '''
    @app_commands.command(description = "Ping the bot and show the latency")
    @log.commandlog
    async def ping(self, interact: discord.Integration):
        message = f"{self.bot.latency * 1000:.3f} ms, "
        message = message + f"{interact.channel}@<#{interact.channel.id}>(\\#{interact.channel.id})\n"
        return message
    
    '''
    command change_game(gamestat):
        argument:
            gamestat (required): game name want to change
        send message (on success):
            ":white_check_mark:Change bot game stat: {gamestat}"
        function:
            change the game stat of the bot
    '''
    @app_commands.command(description = "Change the game stat")
    @app_commands.describe(gamestat = "replaced game stat string")
    @log.commandlog
    async def change_game(self, interact: discord.Integration, gamestat: str):
        self.bot.setting["GAME"] = gamestat
        game = discord.Game(self.bot.setting["GAME"])
        await self.bot.change_presence(activity = game)
        message = ":white_check_mark:Change bot game stat: " + self.bot.setting["GAME"]
        save_json(self.bot.setting)
        return message


async def setup(bot: commands.bot):
    await bot.add_cog(Misc(bot))