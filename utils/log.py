import discord
import logging
import time
import os


filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".log"
fmt = logging.Formatter('[%(asctime)s]:[%(levelname)1.1s]:%(name)s: %(message)s')

dis_log = logging.getLogger("discord")
dis_log.setLevel(logging.DEBUG)
filepath = os.path.join("log", "discord", filename)
fh = logging.FileHandler(filename = filepath, encoding = 'utf-8', mode = 'w')
fh.setLevel(logging.DEBUG)
fh.setFormatter(fmt)
dis_log.addHandler(fh)

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)
filepath = os.path.join("log", filename)
fh = logging.FileHandler(filename = filepath, encoding = 'utf-8', mode = 'w')
fh.setLevel(logging.DEBUG)
fh.setFormatter(fmt)
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(fmt)
logger.addHandler(ch)

def logger_head(ctx, cmd, mode = "info"):
    if mode == "info":
        return f"@{ctx.guild.name}:({cmd})"
    elif mode == "err":
        return f"@{ctx.guild.name}:({cmd} error)"


def print_cmd(cmd, args, ctx):
    logger.info(f"{logger_head(ctx, cmd)} {args}, from {ctx.channel}")

async def send_msg(cmd, message, ctx):
    head = logger_head(ctx, cmd)
    try:
        await ctx.send(message)
    except discord.HTTPException as e:
        logger.warning(f"{head} response failed:{e}")
    except:
        logger.error(f"{head} response error", exc_info = True)
    else:
        logger.debug(f"{head} response success")
    logger.debug(f"\n{message}")

async def send_err(cmd, message, err_msg, ctx):
    head = logger_head(ctx, cmd, "err")
    logger.warning(f"{head} {err_msg}")
    try:
        await ctx.send(message)
    except discord.HTTPException as e:
        logger.warning(f"{head} response failed, HTTP code:{e}")
    except:
        logger.error(f"{head} response error", exc_info = True)
    else:
        logger.debug(f"{head} response success")
    logger.debug(f"\n{message}")


import functools

def commandlog(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        print_cmd(func.__name__, args[2:], args[1])
        message = await func(*args, **kwargs)
        if isinstance(message, str):
            await send_msg(func.__name__, message, args[1])
        else:
            await send_err(func.__name__, message[0], message[1], args[1])
    return wrapper

def initlog(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        classname = func.__qualname__.split(".")[-2]
        logger.info(f"load {classname}")
        try:
            func(*args, **kwargs)
        except:
            logger.error(f"load {classname} failed", exc_info = True)
        else:
            logger.debug(f"load {classname} success")
    return wrapper