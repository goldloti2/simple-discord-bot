from cmds.blackjack.BJ import BJDealer
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import utils.log as log

logger = log.get_logger()



class BlackJack(commands.GroupCog):
    @log.initlog
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dealers = {}
    
    '''
    command ping():
        send message (on success):
        function:
    '''
    @app_commands.command(name = "new", description = "start a new game")
    @log.commandlog
    async def new_game(self, interact: discord.Interaction):
        cid = interact.channel_id
        if cid in self.dealers:
            message = "already a game in the channel"
            err_message = ({"content": message, "ephemeral": True}, message)
            return err_message
        else:
            self.dealers[cid] = BJDealer(interact.channel)
            await self.dealers[cid].start_lobby(interact.user)
            message = {"content": "start a new game!", "ephemeral": True}
            return message
    
    '''
    command change_game(gamestat):
        argument:
        send message (on success):
        function:
    '''
    @app_commands.command(description = "Change the game stat")
    @app_commands.describe(gamestat = "replaced game stat string")
    @log.commandlog
    async def change_game(self, interact: discord.Interaction, gamestat: str):
        message = ":white_check_mark:Change bot game stat:"
        return message


async def setup(bot: commands.Bot):
    await bot.add_cog(BlackJack(bot))