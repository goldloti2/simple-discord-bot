from discord.ext import commands
import os
import sys
import utils.log as log

logger = log.get_logger()

def ext_str(exts: str):
    return f"cmds.{exts}"

def create_msg(msg: str, head: str, set_exts: set):
	if len(set_exts) != 0:
		msg = msg + head + ": __" + "__, __".join(set_exts) + "__\n"
	return msg



class Cog_Core(commands.Cog):
    @log.initlog
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.check_cmds()
    
    async def init_load(self):
        for exts in self.list_exts:
            try:
                await self.bot.load_extension(ext_str(exts))
            except commands.errors.ExtensionFailed as e:
                logger.error(f"load {exts} failed. Bot shut down.")
                logger.debug("\n", exc_info = True)
                loop = self.bot.loop
                loop.call_soon_threadsafe(loop.stop)
                sys.exit()
    
    def check_cmds(self):
        list_exts = set()
        for file in os.listdir("cmds"):
            if file[-3:] == ".py":
                list_exts.add(file[:-3])
        self.list_exts = list_exts
        logger.info(f"Extension found:{', '.join(list_exts)}")
    
    '''
    command load(*args):
        argument:
            args (optional): extension want to load
        send message (on success):
            ":white_check_mark:Extension loaded: {loaded extension}"
            (opt)":x:Extension already loaded: {already loaded extension}"
            (opt)":x:Extension not found: {not found extension}"
        function:
            load the specific extension(s).
            args leave blank or "all" means load all the found extensions.
    '''
    @commands.command(hidden = True)
    @log.commandlog
    async def load(self, ctx: commands.context, *args):
        args_exts = set(args)
        all_flag = False
        if len(args) == 0 or "all" in args:
            all_flag = True
        if all_flag:
            args_exts = self.list_exts
        
        exts_stat = [set(), set(), set()]
        msgs_stat = [":white_check_mark:Extension loaded",
                    ":x:Extension already loaded",
                    ":x:Extension not found"]
        for exts in args_exts:
            try:
                await self.bot.load_extension(ext_str(exts))
            except commands.errors.ExtensionAlreadyLoaded as e:
                exts_stat[1].add(exts)
                logger.warning(e.args[0])
            except commands.errors.ExtensionNotFound as e:
                exts_stat[2].add(exts)
                logger.warning(e.args[0])
            else:
                exts_stat[0].add(exts)
        
        if all_flag and len(exts_stat[0]) != 0:
            exts_stat[1] = exts_stat[2] = []
        message = ""
        for msg, exts in zip(msgs_stat, exts_stat):
            message = create_msg(message, msg, exts)
        return message
    
    '''
    command unload(*args):
        argument:
            args (optional): extension want to unload
        send message (on success):
            ":white_check_mark:Extension unloaded: {unloaded extension}"
            (opt)":x:Extension not loaded: {not loaded extension}"
        function:
            unload the specific extension(s).
            args leave blank or "all" means unload all the found extensions.
    '''
    @commands.command(hidden = True)
    @log.commandlog
    async def unload(self, ctx: commands.context, *args):
        args_exts = set(args)
        all_flag = False
        if len(args) == 0 or "all" in args:
            all_flag = True
        if all_flag:
            args_exts = self.list_exts
        
        exts_stat = [set(), set()]
        msgs_stat = [":white_check_mark:Extension unloaded",
                    ":x:Extension not loaded"]
        for exts in args_exts:
            try:
                await self.bot.unload_extension(ext_str(exts))
            except commands.errors.ExtensionNotLoaded as e:
                exts_stat[1].add(exts)
                logger.warning(e.args[0])
            else:
                exts_stat[0].add(exts)
        
        if "all" in args and len(exts_stat[0]) != 0:
            exts_stat[1] = []
        message = ""
        for msg, exts in zip(msgs_stat, exts_stat):
            message = create_msg(message, msg, exts)
        return message
    
    '''
    command reload(*args):
        argument:
            args (optional): extension want to reload
        send message (on success):
            ":white_check_mark:Extension reloaded: {loaded extension}"
            (opt)":x:Extension already loaded: {already loaded extension}"
            (opt)":x:Extension not loaded: {not loaded extension}"
        function:
            reload the specific extension(s).
            args leave blank or "all" means reload all the found extensions.
    '''
    @commands.command(hidden = True)
    @log.commandlog
    async def reload(self, ctx: commands.context, *args):
        args_exts = set(args)
        all_flag = False
        if len(args) == 0 or "all" in args:
            all_flag = True
        if all_flag:
            args_exts = self.list_exts
        
        exts_stat = [set(), set(), set()]
        msgs_stat = [":white_check_mark:Extension reloaded",
                    ":x:Extension already loaded",
                    ":x:Extension not loaded"]
        for exts in args_exts:
            try:
                await self.bot.reload_extension(ext_str(exts))
            except commands.errors.ExtensionAlreadyLoaded as e:
                exts_stat[1].add(exts)
                logger.warning(e.args[0])
            except commands.errors.ExtensionNotLoaded as e:
                exts_stat[2].add(exts)
                logger.warning(e.args[0])
            else:
                exts_stat[0].add(exts)
        
        if all_flag and len(exts_stat[0]) != 0:
            exts_stat[1] = exts_stat[2] = []
        message = ""
        for msg, exts in zip(msgs_stat, exts_stat):
            message = create_msg(message, msg, exts)
        return message
    
    '''
    command update_cogs():
        argument:
        send message (on success):
            "Find {len(self.list_exts)} extension: {self.list_exts}"
        function:
            check if there is any new extension file in cmds folder
    '''
    @commands.command(hidden = True)
    @log.commandlog
    async def update_cogs(self, ctx: commands.context):
        self.check_cmds()
        message = f"Find {len(self.list_exts)} extension: __{'__, __'.join(self.list_exts)}__"
        return message


async def setup(bot: commands.bot):
    cog_core = Cog_Core(bot)
    await cog_core.init_load()
    await bot.add_cog(cog_core)