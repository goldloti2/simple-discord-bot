from log import logger, print_cmd, send_msg, send_err

import functools

def commandlog(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        print_cmd(func.__name__, args[2:], args[1].channel)
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
        func(*args, **kwargs)
        logger.info(f"load {classname} success")
    return wrapper