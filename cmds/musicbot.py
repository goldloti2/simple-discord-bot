import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import utils.log as log
import youtube_dl
from youtube_dl import YoutubeDL

FFMpegExe = ".\\env\\ffmpeg.exe"
download_path = os.path.join(".", "temp", "%(title)s.%(ext)s")

logger = log.get_logger()

def dur2str(duration: int):
    sec = duration % 60
    min = duration // 60 % 60
    hr = duration // 3600
    return f"{hr:02d}:{min:02d}:{sec:02d}"



class MusicPlayer():
    def __init__(self, ytdl_opt: dict, ffmpeg_opt: dict, loop: asyncio.AbstractEventLoop):
        self.ytdl = YoutubeDL(ytdl_opt)
        self.ffmpeg_opt = ffmpeg_opt
        self.loop = loop
        self.vc = None
        self.dl_queue = asyncio.Queue()
        self.pl_queue = asyncio.Queue()
        self.end_sig = asyncio.Event()
        self.end_sig.set()
        self.queue_cnt = 0
        self.is_terminated = False

        self.dl_task = self.loop.create_task(self.download_loop())
    
    def is_playing(self):
        return False
    
    async def terminate(self):
        self.is_terminated = True
        await self.vc.disconnect()
        logger.info(f"(MusicPlayer) disconnect from voice channel: {self.vc.channel}")
        self.dl_task.cancel()
        try:
            await self.dl_task
        except asyncio.CancelledError:
            logger.debug("(MusicPlayer) download loop cancelled")
        logger.info("(MusicPlayer) terminated")
    
    async def download_loop(self):
        while(1):
            result = await self.dl_queue.get()
            logger.debug("(MusicPlayer) queue get: " + result["title"])
            try:
                await self.loop.run_in_executor(None,
                                                self.ytdl.extract_info,
                                                result["url"])
            except youtube_dl.utils.DownloadError as e:
                logger.warning("(MusicPlayer) " + e.args[0])
                message = f"```{e.args[0]}```"
                await log.send_msg("MusicBot", message, self.tc)
            except:
                logger.error("(MusicPlayer) youtube_dl download error")
                logger.debug("\n", exc_info = True)
                message = ":x:unexpected download error occured"
                await log.send_msg("MusicBot", message, self.tc)
            else:
                logger.debug("(MusicPlayer) downloaded: " + result["title"])
    
    async def search_yt(self, search_args: str, requester: str):
        search = False
        if not search_args.startswith("https://"):
            search_args = "ytsearch:" + search_args
            search = True
        try:
            info = await self.loop.run_in_executor(None,
                                                   self.ytdl.extract_info,
                                                   search_args, False)
        except youtube_dl.utils.DownloadError as e:
            err_msg = e.args[0]
            message = f"```{e.args[0]}```"
            return (message, err_msg)
        except:
            logger.error("(MusicPlayer) youtube_dl error")
            logger.debug("\n", exc_info = True)
            message = ":x:unexpected error occured"
            return message
        if search:
            info = info["entries"][0]
        
        result = {"title":     info["title"],
                  "url":       info["webpage_url"],
                  "requester": requester,
                  "uploader":  info["uploader"],
                  "thumbnail": info["thumbnail"],
                  "duration":  info["duration"],
                  "filename":  self.ytdl.prepare_filename(info)}
        
        logger.info(f"(MusicPlayer) music in queue #{self.queue_cnt}: " +
                    result["title"] + ", requested by " +
                    result["requester"])
        
        embed = discord.Embed(title = result["title"],
                              url = result["url"],
                              description = "Requested by " + result["requester"])
        embed.set_author(name = result["uploader"])
        embed.set_thumbnail(url = result["thumbnail"])
        embed.add_field(name = "Duration",
                        value = dur2str(result["duration"]),
                        inline = True)
        embed.add_field(name = "Queue Position",
                        value = f"#{self.queue_cnt}",
                        inline = True)

        self.queue_cnt += 1
        await self.dl_queue.put(result)
        print(self.dl_queue.qsize())
        return {"embed": embed}
    
    async def new_play(self, interact: discord.Interaction, search: str):
        print("eeeee")
        if self.vc == None:
            print("fffff")
            try:
                self.vc = await interact.user.voice.channel.connect(timeout = 20,
                                                                    reconnect = False)
                self.tc = interact.channel
            except asyncio.exceptions.TimeoutError:
                err_msg = "(MusicPlayer) voice channel connection timeout."
                message = ":x:connection timeout"
                return (message, err_msg)
            except discord.ClientException:
                logger.info(f"(MusicPlayer) already in voice channel: {self.vc.channel}")
            except:
                logger.error("(MusicPlayer) voice channel connection error.")
                logger.debug("\n", exc_info = True)
                err_msg = "(MusicPlayer) voice channel connection error."
                message = ":x:connection error"
                return (message, err_msg)
            else:
                logger.info(f"(MusicPlayer) connect to voice channel: {self.vc.channel}")
        elif self.vc.channel != interact.user.voice.channel:
            print("ggggg")
            if not self.is_playing():
                await self.vc.move_to(interact.user.voice.channel)
                self.tc = interact.channel
                logger.info(f"(MusicPlayer) connect to voice channel: {self.vc.channel}")
            else:
                err_msg = f"(MusicPlayer) now playing in voice channel:{self.vc.channel}"
                message = f":x:bot now playing in `{self.vc.channel}`"
                return (message, err_msg)

        message = await self.search_yt(search, interact.user.display_name)
        return message



class MusicBot(commands.Cog):
    @log.initlog
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        '''yt_dl & ffmpeg option'''
        self.ytdl_opt = {"format": "bestaudio",
                         "logger": log.get_logger("ytdl"),
                         "nocheckcertificate": True,
                         "noplaylist": True,
                         "outtmpl": download_path,
                         "quiet": True}
        self.ffmpeg_opt = {"executable": FFMpegExe}
        os.makedirs("temp", exist_ok = True)

        self.players: dict[int, MusicPlayer] = {}
        # self.inactive_timer.start()
    
    def is_connected(self):
        return self.vc != None and self.vc.is_connected()
    
    def play_next(self, error = None):
        if self.vc.is_playing():
            return
        print("aaa is playing:", self.vc.is_playing())
        print("aaa is paused:", self.vc.is_paused())
        if len(self.queue) > 0:
            pop = self.queue.pop(0)
            logger.info("music now playing: " + 
                        pop["title"] + ", requested by " +
                        pop["requester"] + ", " + pop["url"])
            try:
                nowplay = discord.FFmpegPCMAudio(source = pop["filename"], **self.ffmpeg_opt)
            except:
                logger.error("ffmpeg error")
                logger.debug("\n", exc_info = True)
            try:
                self.vc.play(nowplay, after = lambda e: self.play_next())
            except:
                logger.error("vc.play error")
                logger.debug("\n", exc_info = True)
            print("is playing:", self.vc.is_playing())
            print("is paused:", self.vc.is_paused())
        else:
            self.is_idle = True
            print("vvvvv")
    
    @tasks.loop(minutes = 1)
    async def inactive_timer(self):
        pass
        # logger.debug("MusicBot timer awake")
        # if self.is_idle and self.is_connected() and not self.vc.is_playing():
        #     await self.vc.disconnect()
        #     logger.info("MusicBot disconnect from voice channel")


    @app_commands.command(description = "Play music from YouTube")
    @log.commandlog
    async def play(self, interact: discord.Interaction,
                   search: str):
        await interact.response.defer()
        if interact.user.voice != None:
            print("aaaaa")
            gid = interact.guild_id
            print(gid)
            print(gid not in self.players.keys())
            if gid not in self.players.keys() or self.players[gid].is_terminated:
                print("qqqqq")
                self.players[gid] = MusicPlayer(self.ytdl_opt,
                                                self.ffmpeg_opt,
                                                self.bot.loop)
            print("bbbbb")
            message = await self.players[gid].new_play(interact, search)
            print("ccccc")
            return message
        else:
            print("ddddd")
            err_msg = f"{interact.user} not in voice channel"
            message = ":x:you are not in any voice channel"
            return (message, err_msg)
        # if not self.is_connected():
        #     print("aaaaa")
        #     if interact.user.voice != None:
        #         print("bbbbb")
        #         try:
        #             self.vc = await interact.user.voice.channel.connect(timeout = 20,
        #                                                                 reconnect = False)
        #         except asyncio.exceptions.TimeoutError:
        #             err_msg = "voice channel connection timeout."
        #             message = ":x:connection timeout"
        #             return (message, err_msg)
        #         except discord.ClientException:
        #             logger.info(f"MusicBot already in voice channel: {self.vc.channel}")
        #         except:
        #             logger.error("voice channel connection error.")
        #             logger.debug("\n", exc_info = True)
        #             err_msg = "voice channel connection error."
        #             message = ":x:connection error"
        #             return (message, err_msg)
        #         else:
        #             self.is_idle = False
        #             logger.info(f"MusicBot connect to voice channel: {self.vc.channel}")
        #     else:
        #         print("ccccc")
        #         err_msg = f"{interact.user} not in voice channel"
        #         message = ":x:you are not in any voice channel"
        #         return (message, err_msg)
        # else:
        #     print("ddddd")
        #     if self.vc.channel != interact.user.voice.channel:
        #         print("eeeee")
        #         if not self.vc.is_playing():
        #             print("fffff")
        #             await self.vc.move_to(interact.user.voice.channel)
        #             logger.info(f"MusicBot connect to voice channel: {self.vc.channel}")
        #         else:
        #             print("ggggg")
        #             err_msg = f"now playing in voice channel:{self.vc.channel}"
        #             message = f":x:bot now playing in `{self.vc.channel}`"
        #             return (message, err_msg)

        # print("hhhhh")
        # succ, message = await self.search_yt(search, interact.user.display_name)
        # print("iiiii")
        # if succ and not self.vc.is_playing():
        #     self.play_next()
        # else:
        #     print("kkkkk")
        # return message
    
    # @play.error
    # async def play_error(self, ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         err_msg = "recieve no arguments."
    #         message = ":x:`play` require YT url or keyword"
    #         await log.send_err("play", message, err_msg, ctx)
    #     else:
    #         logger.error("(play error) unhandled error")
    #         logger.debug("\n", exc_info = True)

    @app_commands.command(description = "Stop music")
    @log.commandlog
    async def stop(self, interact: discord.Interaction):
        await self.vc.disconnect()
        self.is_idle = True
        return ":white_check_mark:disconnected"
    
    async def cog_unload(self):
        for gid in self.players.keys():
            await self.players[gid].terminate()


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicBot(bot))