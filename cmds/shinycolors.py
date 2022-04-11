import discord
from discord.ext import commands
import json
import asyncio
import requests
import time

from utils.log import logger, send_msg
import utils.log as log
'''
* Both asyncio.ensure_future() and loop.create_task() will add the coroutines
to the loop
* If there is no await asyncio.wait(tasks), then the rest of the codes won't be blocked
* Function foo() want to be async with multiple args (a, b, c):
    await loop.run_in_executor(None, lambda: foo(a, b, c))
'''

class ShinyColors(commands.Cog):
    @log.initlog
    def __init__(self, bot):
        self.bot = bot
        self.url_0 = "https://api.matsurihi.me/sc/v1/events/fanRanking/40008/rankings/logs/1/100"
        self.url_1 = "https://api.matsurihi.me/sc/v1/events/fanRanking/40008/rankings/logs/3/10"
        self.channel = self.bot.get_channel(897443905300201474)
        self.console_msg = "ShinyColors"
        self.send_msg = ["真乃100位", "めぐる10位"]
        
        async def update_timer():
            await self.bot.wait_until_ready()
            while not self.bot.is_closed():
                nt = time.localtime(time.time())
                sleep_sec = (30 - nt.tm_min % 30) * 60 - nt.tm_sec + 30
                await asyncio.sleep(sleep_sec)
                logger.debug("ShinyColors Timer awake")
                self.bot.loop.create_task(self.call_update())
        
        self.timer_task = self.bot.loop.create_task(update_timer())
    
    def req(self):
        return [requests.get(self.url_0), requests.get(self.url_1)]
    
    async def call_update(self):
        logger.debug(f"{self.console_msg} request")
        msg = ""
        try:
            responses = await self.bot.loop.run_in_executor(None, self.req)
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"{self.console_msg} request failed")
            logger.debug(str(e))
            return
        except:
            logger.error(f"{self.console_msg} request error")
            logger.debug("\n", exc_info = True)
            return
        for response, msg_head in zip(responses, self.send_msg):
            if response.status_code != 200:
                logger.error(f"{self.console_msg} http request failed: {response.status_code}")
                logger.debug(response.text)
                return
            latest_score = response.json()[0]["data"][-1]
            second_score = response.json()[0]["data"][-2]
            score_difference = int(latest_score['score'])-int(second_score['score']);
            msg += f"{msg_head}:\n{latest_score['score']}\n@{latest_score['summaryTime'][:-3]}\n半小時增加:{score_difference}"
        
        await send_msg(self.console_msg, msg, self.channel)


def setup(bot):
    bot.add_cog(ShinyColors(bot))