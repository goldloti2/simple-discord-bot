import discord
from discord.ext import commands
import json
import asyncio
import requests
import time

from utils.log import logger
import utils.log as log
'''
* Both asyncio.ensure_future() and loop.create_task() will add the coroutines
to the loop
* If there is no await asyncio.wait(tasks), then the rest of the codes won't be blocked
* Function foo() want to be async with multiple args (a, b, c):
    await loop.run_in_executor(None, lambda: foo(a, b, c))
'''

class Test(commands.Cog):
    @log.initlog
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(hidden = True)
    @log.commandlog
    async def pong(self, ctx, *args):
        start_time = time.time()
        self.loop = asyncio.get_running_loop()
        tasks = [asyncio.ensure_future(self.request_url(i, start_time, ctx))\
                for i in range(5)]
        #await asyncio.wait(tasks)
        message = f"end time: {time.time() - start_time:.5f} sec. {id(self.loop)}"
        await self.call_pong2(ctx)
        return message
    
    @commands.command(hidden = True)
    @log.commandlog
    async def pong2(self, ctx):
        start_time = time.time()
        self.loop = asyncio.get_running_loop()
        for i in range(5):
            self.loop.create_task(self.request_url(i, start_time, ctx))
        message = f"end time: {time.time() - start_time:.5f} sec. {id(self.loop)}"
        return message
    
    async def call_pong2(self, ctx):
        message = "This is pong2()"
        await log.send_msg("call_pong2()", message, ctx)
    
    async def request_url(self, num, start_time, ctx):
        url = 'https://www.google.com.tw/search'
        t = time.time()
        message = f"\\#{num}: Request at {t - start_time:.5f} sec.\n"
        res = await self.loop.run_in_executor(None, lambda: requests.get(url, params = {"q": "python"}))
        message = f"{message}{type(res)}\n"
        t = time.time()
        message = f"{message}\\#{num}: Response at {t - start_time:.5f} sec."
        await log.send_msg("request_url()", message, ctx)


def setup(bot):
    bot.add_cog(Test(bot))