import logging
import time
import os

def start_logging(target, log_dir, debug = False):
    filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    filename = os.path.join(log_dir, filename + ".log")
    
    logger = logging.getLogger(target)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = logging.FileHandler(filename=filename, encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    return logger


# print(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))