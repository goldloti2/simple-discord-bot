import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from enum import Enum
import os
from typing import Optional
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

def clear_queue(q: asyncio.Queue):
    for _ in range(q.qsize()):
        q.get_nowait()

class ActiveStatus(Enum):
    ALL_ACTIVE = 1
    USER_INACTIVE = 2
    PLAYER_INACTIVE = 3



class MusicPlayer():
    def __init__(self, ytdl_opt: dict, ffmpeg_opt: dict, loop: asyncio.AbstractEventLoop):
        self.ytdl = YoutubeDL(ytdl_opt)
        self.ffmpeg_opt = ffmpeg_opt
        self.loop = loop
        self.vc = None
        self.dl_queue = asyncio.Queue()
        self.pl_queue = asyncio.Queue()
        self.play_end = asyncio.Event()
        self.is_busy = asyncio.Event()
        self.is_resume = asyncio.Event()
        self.init_loop()
    
    def is_playing(self):
        return self.vc.is_playing() or self.vc.is_paused() or self.is_busy.is_set()
    
    async def terminate(self):
        if self.is_terminated:
            return
        self.is_terminated = True
        await self.vc.disconnect()
        logger.info(f"(MusicPlayer) disconnect from voice channel: {self.vc.channel}")
        await self.kill_loop()
        logger.info("(MusicPlayer) terminated")

    def init_loop(self):
        clear_queue(self.dl_queue)
        clear_queue(self.pl_queue)
        self.play_end.set()
        self.is_busy.clear()
        self.is_resume.set()
        self.music_list = {}
        self.list_cnt = 0
        self.now_play = -1
        self.now_dl = -1
        self.is_terminated = False
        self.dl_loop_task = self.loop.create_task(self.download_loop())
        self.pl_loop_task = self.loop.create_task(self.play_loop())
        logger.debug("(MusicPlayer) loops initiated")
    
    async def kill_loop(self):
        self.dl_loop_task.cancel()
        self.pl_loop_task.cancel()
        try:
            await self.dl_loop_task
        except asyncio.CancelledError:
            logger.debug("(MusicPlayer) download loop cancelled")
        try:
            await self.pl_loop_task
        except asyncio.CancelledError:
            logger.debug("(MusicPlayer) play loop cancelled")
    
    async def download_coro(self, url: str, download: bool = False):
        return await self.loop.run_in_executor(None,
                                               self.ytdl.extract_info,
                                               url, download)
    
    async def download_loop(self):
        while(1):
            logger.debug("(MusicPlayer) wait download queue")
            now_dl = await self.dl_queue.get()
            if now_dl not in self.music_list.keys():
                logger.debug(f"(MusicPlayer) remove download: #{now_dl}: {result['title']}")
                continue
            result = self.music_list[now_dl]
            self.now_dl = now_dl
            logger.debug(f"(MusicPlayer) download queue get: #{now_dl}: {result['title']}")
            self.is_busy.set()
            try:
                self.dl_task = self.loop.create_task(self.download_coro(result["url"], True))
                await self.dl_task
            except youtube_dl.utils.DownloadError as e:
                self.music_list.pop(now_dl, False)
                logger.warning(f"(MusicPlayer) {result['title']} {e.args[0]}")
                message = f"```{result['title']}\n{e.args[0]}```"
                await log.send_msg("MusicBot", message, self.tc)
            except asyncio.CancelledError:
                logger.debug(f"(MusicPlayer) #{now_dl}: {result['title']} download has been cancelled")
            except:
                self.music_list.pop(now_dl, False)
                logger.error("(MusicPlayer) youtube_dl download error")
                logger.debug("\n", exc_info = True)
                message = ":x:unexpected download error occured"
                await log.send_msg("MusicBot", message, self.tc)
            else:
                await self.pl_queue.put(now_dl)
                logger.debug(f"(MusicPlayer) downloaded: #{now_dl}: {result['title']}")
    
    async def play_loop(self):
        while(1):
            logger.debug("(MusicPlayer) wait is_play")
            await self.play_end.wait()
            logger.debug("(MusicPlayer) wait is_busy")
            try:
                await asyncio.wait_for(self.is_busy.wait(), 10)
            except asyncio.TimeoutError:
                logger.debug("(MusicPlayer) play loop timeout")
                self.loop.create_task(self.terminate())
                break
            logger.debug("(MusicPlayer) wait play queue")
            now_play = await self.pl_queue.get()
            if now_play not in self.music_list.keys():
                self.play_end.set()
                logger.debug(f"(MusicPlayer) remove play: #{now_play}: {result['title']}")
                continue
            result = self.music_list[now_play]
            self.now_play = now_play
            self.play_end.clear()
            logger.debug(f"(MusicPlayer) play queue get:  #{now_play}: {result['title']}")
            if self.pl_queue.empty() and self.dl_task.done():
                self.is_busy.clear()
                logger.debug("(MusicPlayer) play queue is empty. is_busy clear")
            await self.is_resume.wait()
            try:
                play_audio = discord.FFmpegPCMAudio(source = result["filename"], **self.ffmpeg_opt)
            except:
                self.music_list.pop(now_play, False)
                self.play_end.set()
                logger.warning("(MusicPlayer) ffmpeg error")
                logger.debug("\n", exc_info = True)
                message = ":x:unexpected ffmpeg error occured"
                await log.send_msg("MusicBot", message, self.tc)
                continue
            message = f"now play: `{result['title']}`, in #`{now_play}`"
            await log.send_msg("MusicBot", message, self.tc)
            if now_play not in self.music_list.keys():
                self.play_end.set()
                logger.debug(f"(MusicPlayer) remove play: #{now_play}: {result['title']}")
                continue
            try:
                self.vc.play(play_audio,
                             after = lambda _: self.loop.call_soon_threadsafe(self.play_end.set))
            except:
                self.music_list.pop(now_play, False)
                self.play_end.set()
                logger.warning("(MusicPlayer) vc.play error")
                logger.debug("\n", exc_info = True)
                message = ":x:unexpected play error occured"
                await log.send_msg("MusicBot", message, self.tc)
    
    async def search_yt(self, search_args: str, requester: str):
        search = False
        list_cnt = self.list_cnt
        if not search_args.startswith("https://"):
            search_args = "ytsearch:" + search_args
            search = True
        try:
            info = await self.download_coro(search_args, False)
        except youtube_dl.utils.DownloadError as e:
            err_msg = f"{result['title']} {e.args[0]}"
            message = f"```{result['title']}\n{e.args[0]}```"
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
        self.music_list[list_cnt] = result
        
        logger.info(f"(MusicPlayer) music in queue #{list_cnt}: " +
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
                        value = f"#{list_cnt}",
                        inline = True)
        embed.set_footer(text = "may take some time to download")

        await self.dl_queue.put(list_cnt)
        self.list_cnt = list_cnt + 1
        return {"embed": embed}
    
    async def new_play(self, interact: discord.Interaction, search: str):
        if self.vc == None:
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
    
    def pause_resume(self, interact: discord.Interaction):
        if self.vc != None and self.vc.channel == interact.user.voice.channel:
            if self.is_resume.is_set():
                self.is_resume.clear()
                self.vc.pause()
                message = ":pause_button: pause"
                logger.info(f"(MusicPlayer) music pause")
            else:
                self.is_resume.set()
                self.vc.resume()
                message = ":arrow_forward: resume"
                logger.info(f"(MusicPlayer) music resume")
            return message
        else:
            err_msg = f"(MusicPlayer) now playing in voice channel:{self.vc.channel}"
            message = f":x:bot now playing in `{self.vc.channel}`"
            return (message, err_msg)
    
    async def stop(self, interact: discord.Interaction):
        if self.vc != None and self.vc.channel == interact.user.voice.channel:
            if self.is_resume.is_set():
                self.is_resume.clear()
                self.vc.pause()
            await self.kill_loop()
            self.init_loop()
            return ":stop_button: stopped"
        else:
            err_msg = f"(MusicPlayer) now playing in voice channel:{self.vc.channel}"
            message = f":x:bot now playing in `{self.vc.channel}`"
            return (message, err_msg)
    
    def skip(self, interact: discord.Interaction, pos: Optional[int]):
        if self.vc != None and self.vc.channel == interact.user.voice.channel:
            if self.now_play + 1 == self.list_cnt and \
               not (self.vc.is_playing() or self.vc.is_paused()):
                message = ":x:no music in queue"
                return message
            
            if pos == None:
                pos = self.now_play
                if self.play_end.is_set():
                    pos += 1
            
            if pos < self.now_play or \
                (pos == self.now_play and self.play_end.is_set()):
                message = ":x:can't skip already played music"
            elif pos >= self.list_cnt:
                message = f":x:#{pos} out of bound"
            else:
                del_res = self.music_list.pop(pos, None)
                if del_res != None:
                    message = f"skipped: `{del_res['title']}`, in #`{pos}`"
                    if pos == self.now_play:
                        self.vc.stop()
                        if not self.is_resume.is_set():
                            self.is_resume.set()
                            self.vc.resume()
                    elif pos == self.now_dl and not self.dl_task.done():
                        self.dl_task.cancel()
                else:
                    message = f":x:#{pos} already skipped"
            return message
        else:
            err_msg = f"(MusicPlayer) now playing in voice channel:{self.vc.channel}"
            message = f":x:bot now playing in `{self.vc.channel}`"
            return (message, err_msg)
    
    def playlist(self, interact: discord.Interaction):
        if self.vc != None and self.vc.channel == interact.user.voice.channel:
            message = "```\n"
            for num in self.music_list.keys():
                if self.now_play == num:
                    message += f"*{num:2d}) "
                else:
                    message += f" {num:2d}) "
                message += self.music_list[num]["title"]
                message += f" - requested by {self.music_list[num]['requester']}\n"
            if len(self.music_list) == 0:
                message += "no music in queue\n"
            message += "```"
            return message
        else:
            err_msg = f"(MusicPlayer) now playing in voice channel:{self.vc.channel}"
            message = f":x:bot now playing in `{self.vc.channel}`"
            return (message, err_msg)



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
                         "retries": 5,
                         "quiet": True}
        self.ffmpeg_opt = {"executable": FFMpegExe}
        os.makedirs("temp", exist_ok = True)

        self.players: dict[int, MusicPlayer] = {}
        # self.inactive_timer.start()
    
    @tasks.loop(minutes = 1)
    async def inactive_timer(self):
        pass
        # logger.debug("MusicBot timer awake")
        # if self.is_idle and self.is_connected() and not self.vc.is_playing():
        #     await self.vc.disconnect()
        #     logger.info("MusicBot disconnect from voice channel")

    async def check_user_player_status(self, interact: discord.Interaction):
        await interact.response.defer()
        if interact.user.voice != None:
            gid = interact.guild_id
            if gid not in self.players.keys() or self.players[gid].is_terminated:
                err_msg = f"no MusicPlayer in {interact.guild}"
                message = ":x:no MusicPlayer here"
                return ActiveStatus.PLAYER_INACTIVE, (message, err_msg)
            else:
                message = "all green"
                return ActiveStatus.ALL_ACTIVE, message
        else:
            err_msg = f"{interact.user} not in voice channel"
            message = ":x:you are not in any voice channel"
            return ActiveStatus.USER_INACTIVE, (message, err_msg)

    @app_commands.command(description = "Play music from YouTube")
    @app_commands.describe(search = "search string or url")
    @log.commandlog
    async def play(self, interact: discord.Interaction,
                   search: str):
        status, message = await self.check_user_player_status(interact)
        gid = interact.guild_id
        if status == ActiveStatus.USER_INACTIVE:
            return message
        elif status == ActiveStatus.PLAYER_INACTIVE:
            self.players[gid] = MusicPlayer(self.ytdl_opt,
                                            self.ffmpeg_opt,
                                            self.bot.loop)
        message = await self.players[gid].new_play(interact, search)
        return message

    @app_commands.command(description = "Pause or resume music")
    @log.commandlog
    async def pause_resume(self, interact: discord.Interaction):
        status, message = await self.check_user_player_status(interact)
        gid = interact.guild_id
        if status == ActiveStatus.ALL_ACTIVE:
            message = self.players[gid].pause_resume(interact)
        return message

    @app_commands.command(description = "Stop music and clear the queue")
    @log.commandlog
    async def stop(self, interact: discord.Interaction):
        status, message = await self.check_user_player_status(interact)
        gid = interact.guild_id
        if status == ActiveStatus.ALL_ACTIVE:
            message = await self.players[gid].stop(interact)
        return message

    @app_commands.command(description = "Skip music in queue")
    @app_commands.describe(pos = "music going to skip")
    @log.commandlog
    async def skip(self, interact: discord.Interaction, pos: Optional[int]):
        status, message = await self.check_user_player_status(interact)
        gid = interact.guild_id
        if status == ActiveStatus.ALL_ACTIVE:
            message = self.players[gid].skip(interact, pos)
        return message

    @app_commands.command(description = "List music in queue")
    @log.commandlog
    async def playlist(self, interact: discord.Interaction):
        status, message = await self.check_user_player_status(interact)
        gid = interact.guild_id
        if status == ActiveStatus.ALL_ACTIVE:
            message = self.players[gid].playlist(interact)
        return message
    
    async def cog_unload(self):
        for gid in self.players.keys():
            await self.players[gid].terminate()


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicBot(bot))