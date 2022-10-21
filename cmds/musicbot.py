import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
import time
import utils.log as log
import youtube_dl
from youtube_dl import YoutubeDL

logger = log.get_logger()

def dur2str(duration: int):
    sec = duration % 60
    min = duration // 60 % 60
    hr = duration // 3600
    return f"{hr:02d}:{min:02d}:{sec:02d}"


class MusicBot(commands.Cog):
    @log.initlog
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        '''yt_dl & ffmpeg option'''
        self.ytdl_opt = {"format":"bestaudio", "noplaylist":"True", "logger":log.get_logger("ytdl")}
        self.ffmpeg_opt = {"before_options":"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                           "options":"-vn"}

        self.queue = []
        self.vc = None
        self.timer_task = None
    
    def is_connected(self):
        return self.vc != None and self.vc.is_connected()
    
    '''
    def search_yt(self, args, requester):
        search = False
        with YoutubeDL(self.ytdl_opt) as ydl:
            if not args.startswith("https://"):
                args = "ytsearch:" + args
                search = True
            try:
                info = ydl.extract_info(args, download = False)
            except youtube_dl.utils.DownloadError as e:
                logger.warning(e.args[0])
                return False
            except:
                logger.error("youtube_dl error")
                logger.debug("\n", exc_info = True)
                return False
        
        if search:
            info = info["entries"][0]
        
        result = {"title":info["title"],
                  "url":info["webpage_url"],
                  "requester":requester,
                  "uploader":info["uploader"],
                  "thumbnail":info["thumbnail"],
                  "duration":info["duration"]}
        
        logger.info(f"music in queue #{len(self.queue)}: " +
                    "{}, requested by {}, {}".format(result["title"], result["requester"], result["url"]))
        embed = discord.Embed(title = result["title"], url = result["url"],
                              description = "Requested by {}".format(result["requester"].split("#")[0]))
        embed.set_author(name = result["uploader"])
        embed.set_thumbnail(url = result["thumbnail"])
        embed.add_field(name = "Duration", value = dur2str(result["duration"]), inline = True)
        embed.add_field(name = "Queue Position", value = f"#{len(self.queue)}", inline = True)

        self.queue.append(result)
        return {"embed":embed}
    
    def play_next(self):
        print("aaa is playing:", self.vc.is_playing())
        print("aaa is paused:", self.vc.is_paused())
        if len(self.queue) > 0:
            pop = self.queue.pop()
            logger.info("music now playing: {}, requested by {}, {}".format(pop["title"], pop["requester"], pop["url"]))
            nowplay = discord.FFmpegPCMAudio(pop["url"], **self.ffmpeg_opt)
            self.vc.play(nowplay, after = lambda e: self.play_next())
            print("is playing:", self.vc.is_playing())
            print("is paused:", self.vc.is_paused())
        else:
            print("vvvvv")
            self.reset_timer()
    '''
    
    @tasks.loop(seconds = 10, count = 1)
    async def inactive_timer(self):
        pass
    
    @inactive_timer.after_loop
    async def timer_stop(self):
        if self.is_connected() and not self.vc.is_playing():
            await self.vc.disconnect()
            logger.info("MusicBot disconnect from voice channel")

    def reset_timer(self):
        if not self.vc.is_playing():
            self.inactive_timer.restart()


    @app_commands.command(description = "Play music from YouTube")
    @log.commandlog
    async def play(self, interact: discord.Interaction,
                   search: str):
        if not self.is_connected():
            print("aaaaa")
            if interact.user.voice != None:
                print("bbbbb")
                try:
                    self.vc = await interact.user.voice.channel.connect(timeout = 20,
                                                                        reconnect = False)
                except asyncio.exceptions.TimeoutError:
                    err_msg = "voice channel connection timeout."
                    message = ":x:connection timeout"
                    return (message, err_msg)
                except discord.ClientException:
                    logger.info(f"MusicBot already in voice channel: {self.vc.channel}")
                except:
                    logger.error("voice channel connection error.")
                    logger.debug("\n", exc_info = True)
                    err_msg = "voice channel connection error."
                    message = ":x:connection error"
                    return (message, err_msg)
                else:
                    logger.info(f"MusicBot connect to voice channel: {self.vc.channel}")
            else:
                print("ccccc")
                err_msg = f"{interact.user} not in voice channel"
                message = ":x:you are not in any voice channel"
                return (message, err_msg)
        else:
            print("ddddd")
            if self.vc.channel != interact.user.voice.channel:
                print("eeeee")
                if not self.vc.is_playing():
                    print("fffff")
                    await self.vc.move_to(interact.user.voice.channel)
                    logger.info(f"MusicBot connect to voice channel: {self.vc.channel}")
                else:
                    print("ggggg")
                    err_msg = f"now playing in voice channel:{self.vc.channel}"
                    message = f":x:bot now playing in `{self.vc.channel}`"
                    return (message, err_msg)

        # print("hhhhh")
        # message = self.search_yt(args, str(interact.user))
        # print("iiiii")
        # if not message:
        #     message = f":x:can't find `{args}`"
        #     print("ccccc")
        #     self.reset_timer()
        # elif not self.vc.is_playing():
        #     self.play_next()
        message = "connected"
        self.inactive_timer.start()
        return message
    
    # @play.error
    # async def play_error(self, ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         err_msg = "recieve no arguments."
    #         message = ":x:`play` require YT url or keyword"
    #         await log.send_err("play", message, err_msg, ctx)
    #     else:
    #         logger.error("(play error) unhandled error")
    #         logger.debug("\n", exc_info = True)

    @app_commands.command(description = "Play music from YouTube")
    @log.commandlog
    async def stop(self, interact: discord.Interaction):
        await self.vc.disconnect()
        return ":white_check_mark:disconnected"
    
    
    
    def cog_unload(self):
        #if not self.timer_task.cancelled():
        #    self.timer_task.cancel()
        #    logger.info("twitter timer removed")
        if self.is_connected():
            asyncio.create_task(self.vc.disconnect())
            time.sleep(1)
            logger.info("MusicBot disconnect from voice channel")


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicBot(bot))