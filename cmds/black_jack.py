from cmds.blackjack.BJ import BJDealer
import discord
from discord import app_commands
from discord.ext import commands, tasks
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
            try:
                self.check_timer.start()
            except:
                logger.error("set BJ timer failed")
            else:
                logger.debug("Set BJ timer success:10 sec")
            return message
    
    @tasks.loop(seconds = 10)
    async def check_timer(self):
        if not self.bot.is_closed():
            logger.debug("BJ timer awake")
            print(self.dealers.keys())
            for cid in list(self.dealers.keys()):
                if not self.dealers[cid].running:
                    del self.dealers[cid]
            print(self.dealers.keys())
            print(len(self.dealers))
            if len(self.dealers) == 0:
                self.check_timer.stop()
                logger.debug("BJ timer stop")
    
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

    def cog_unload(self):
        if not self.check_timer.is_being_cancelled():
            self.check_timer.cancel()
            logger.debug("BJ timer removed")


async def setup(bot: commands.Bot):
    await bot.add_cog(BlackJack(bot))