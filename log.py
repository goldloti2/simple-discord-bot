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


def print_cmd(cmd, args, ctx):
    logger.info(f"{cmd} {args}, from {ctx.channel}")

async def send_msg(cmd, message, ctx):
    try:
        await ctx.send(message)
    except discord.HTTPException as e:
        status = e.args[0].status if hasattr(e.args[0], "status")\
                                  else e.args[0].status_code
        logger.warning(f"{cmd} response failed, HTTP code:{status}")
    except:
        logger.error(f"{cmd} response error", exc_info = True)
    else:
        logger.info(f"{cmd} response success")
    logger.debug(message)