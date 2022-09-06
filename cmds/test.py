import asyncio
import discord
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
        await asyncio.gather(*tasks)
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
        t1 = time.time()
        # res = await self.loop.run_in_executor(None, lambda: requests.get(url, params = {"q": "python"}))
        res = httpx.get(url, params = {"q": "python"})
        t2 = time.time()
        message = f"\\#{num}: Request at {t1 - start_time:.5f} sec.\n"
        message = f"{message}{type(res)}\n"
        message = f"{message}\\#{num}: Response at {t2 - start_time:.5f} sec."
        await log.send_msg("request_url()", message, ctx)
    
    @commands.command(hidden = True)
    @log.commandlog
    async def pong3(self, ctx):
        start_time = time.time()
        async with httpx.AsyncClient() as client:
            tasks = []
            for i in range(5):
                tasks.append(self.request_url2(i, start_time, client, ctx))
            await asyncio.gather(*tasks)
        message = f"end time: {time.time() - start_time:.5f} sec."
        return message
    
    async def request_url2(self, num, start_time, client, ctx):
        url = "https://www.youtube.com/watch"#'https://www.google.com.tw/search'
        t1 = time.time()
        res = await client.get(url = url, params = {"v": "Gdx4UwxeOik"})#{"q": "python"})
        t2 = time.time()
        message = f"\\#{num}: Request at {t1 - start_time:.5f} sec.\n"
        message = f"{message}{res.status_code}\n"
        message = f"{message}\\#{num}: Response at {t2 - start_time:.5f} sec."
        await log.send_msg("request_url()", message, ctx)


async def setup(bot):
    await bot.add_cog(Test(bot))