import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import random
import utils.log as log

logger = log.get_logger()

class Ruletka(commands.GroupCog):
    @log.initlog
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.games = dict()
    
    @app_commands.command(description = "Start a new rulekta in this channel")
    @app_commands.describe(magazine = "magazine size, default is 6",
                           shots = "number of ammo, default is 1")
    @log.commandlog
    async def new(self, interact: discord.Interaction,
                  magazine: Optional[int],
                  shots: Optional[int]):
        channel = interact.channel_id
        game = self._new_game(magazine, shots)
        self.games[channel] = game
        logger.info(f"(Ruletka) new {game} @{interact.channel.name}")
        message = f"I want to play a game ({game[1]}/{game[0]})"
        return message
    
    @app_commands.command(description = "take a shot")
    @log.commandlog
    async def shot(self, interact: discord.Interaction):
        channel = interact.channel_id
        if channel in self.games:
            logger.info(f"(Ruletka) before shot {self.games[channel]} @{interact.channel.name}")
            message = self._shot(channel)
        else:
            logger.info(f"(Ruletka) miss shot @{interact.channel.name}")
            message = ":sayonarashark::boom:"
        return message
    
    def _new_game(self, magazine: Optional[int], shots: Optional[int]):
        magazine = 6 if (magazine is None or magazine < 1) else magazine
        shots = 1 if (shots is None or shots < 1) else shots
        shots = shots if shots <= magazine else magazine
        ammo = random.sample(range(magazine), shots)
        game = [magazine, shots, -1, ammo]
        return game
    
    def _shot(self, channel: int):
        self.games[channel][2] += 1
        # get shot
        if self.games[channel][2] in self.games[channel][3]:
            self.games[channel][1] -= 1
            if self.games[channel][1] == 0:
                del self.games[channel]
            return ":Isthataliedog:"
        # not get shot
        else:
            return ":confidencedog:"


async def setup(bot: commands.Bot):
    await bot.add_cog(Ruletka(bot))