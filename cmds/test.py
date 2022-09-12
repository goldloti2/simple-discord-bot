import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import httpx
import json
# import requests
import time
import utils.log as log

logger = log.get_logger()
'''
* Both asyncio.ensure_future() and loop.create_task() will add the coroutines
to the loop
* If there is no await asyncio.wait(tasks), then the rest of the codes won't be blocked
* Function foo() want to be async with multiple args (a, b, c):
    await loop.run_in_executor(None, lambda: foo(a, b, c))
'''

class Test(commands.GroupCog):
    @log.initlog
    def __init__(self, bot: commands.bot):
        self.bot = bot
    
    @app_commands.command(name = "pong")
    @log.commandlog
    async def pong(self, interact: discord.Integration):
        start_time = time.time()
        await interact.response.defer()
        await asyncio.sleep(5)
        message = f"end time: {time.time() - start_time:.5f} sec."
        return message
    
    @app_commands.command(name = "pong2")
    @log.commandlog
    async def pong2(self, interact: discord.Integration):
        start_time = time.time()
        await interact.response.defer()
        async with httpx.AsyncClient() as client:
            tasks = []
            for i in range(5):
                tasks.append(self.request_url(i, start_time, client, interact))
            await asyncio.gather(*tasks)
        message = f"end time: {time.time() - start_time:.5f} sec."
        return message
    
    async def request_url(self, num: int, start_time: float, client: httpx.AsyncClient, interact: discord.Integration):
        url = "https://www.youtube.com/watch"#'https://www.google.com.tw/search'
        t1 = time.time()
        res = await client.get(url = url, params = {"v": "Gdx4UwxeOik"})#{"q": "python"})
        t2 = time.time()
        message = f"\\#{num}: Request at {t1 - start_time:.5f} sec.\n"
        message = f"{message}{res.status_code}\n"
        message = f"{message}\\#{num}: Response at {t2 - start_time:.5f} sec."
        await log.send_msg("request_url()", message, interact)


async def setup(bot: commands.bot):
    await bot.add_cog(Test(bot))