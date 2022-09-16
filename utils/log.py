import discord
from discord.ext import commands
import functools
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import time
from typing import Callable, Union, Optional

def init_logger():
    filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".log"
    fmt = logging.Formatter('[%(asctime)s]:[%(levelname)s]:%(name)s: %(message)s')
    
    if not os.path.isdir("log"):
        os.mkdir("log")

    dis_log_path = os.path.join("log", "discord")
    if not os.path.isdir(dis_log_path):
        os.mkdir(dis_log_path)

    dis_log = logging.getLogger("discord")
    dis_log.setLevel(logging.DEBUG)
    filepath = os.path.join(dis_log_path, filename)
    fh = TimedRotatingFileHandler(filename = filepath,
                                when = "midnight",
                                backupCount = 7,
                                encoding = 'utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    dis_log.addHandler(fh)

    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)
    filepath = os.path.join("log", filename)
    fh = TimedRotatingFileHandler(filename = filepath,
                                when = "midnight",
                                backupCount = 7,
                                encoding = 'utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

def get_logger(name = "logger"):
    return logging.getLogger(name)

logger = get_logger()

def logger_head(interact: Union[discord.Interaction, discord.TextChannel],
                cmd: str,
                mode = "info"):
    if mode == "info":
        return f"@{interact.guild.name}:({cmd})"
    elif mode == "err":
        return f"@{interact.guild.name}:({cmd} error)"

def print_cmd(cmd: str, interact: discord.Interaction, args: Optional[dict]):
    logger.info(f"{logger_head(interact, cmd)} {args}, from {interact.channel}")

async def send_msg(cmd: str,
                   message: Union[dict, str],
                   interact: Union[discord.Interaction, discord.TextChannel],
                   mode = "send"):
    head = logger_head(interact, cmd)
    return await ctx_send(head, message, interact, mode)

async def send_err(cmd: str,
                   message: Union[dict, str],
                   err_msg: str,
                   interact: discord.Interaction):
    head = logger_head(interact, cmd, "err")
    logger.warning(f"{head} {err_msg}")
    await ctx_send(head, message, interact, "response")

async def ctx_send(head: str,
                   message: Union[dict, str],
                   interact: Union[discord.Interaction, discord.TextChannel],
                   mode = "send"):
    sent = None
    if message == "":
        return sent
    if isinstance(message, str):
        message = {"content": message}
    try:
        if mode == "send":
            if isinstance(interact, discord.Interaction):
                sent = await interact.channel.send(**message)
            elif isinstance(interact, discord.TextChannel):
                sent = await interact.send(**message)
        elif mode == "response":
            if not interact.response.is_done():
                await interact.response.send_message(**message)
            else:
                await interact.followup.send(**message)
        elif mode == "edit":
            await interact.response.edit_message(**message)
    except discord.HTTPException as e:
        logger.warning(f"{head} response failed")
        logger.debug(str(e))
    except discord.InteractionResponded as e:
        logger.warning(f"{head} already responded")
        logger.debug(str(e))
    except:
        logger.error(f"{head} response error")
        logger.debug("\n", exc_info = True)
    else:
        logger.debug(f"{head} response success")
    logger.debug(f"\n{message}")
    return sent


def commandlog(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        print_cmd(func.__name__, args[1], kwargs)
        message = await func(*args, **kwargs)
        if isinstance(message, tuple):
            await send_err(func.__name__, message[0], message[1], args[1])
        elif isinstance(message, dict):
            mode = message.pop("mode", "response")
            await send_msg(func.__name__, message, args[1], mode)
        else:
            await send_msg(func.__name__, message, args[1], "response")
    return wrapper

def initlog(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        classname = func.__qualname__.split(".")[-2]
        logger.info(f"load {classname}")
        try:
            func(*args, **kwargs)
        except:
            logger.error(f"load {classname} failed")
            logger.debug("\n", exc_info = True)
        else:
            logger.debug(f"load {classname} success")
    return wrapper