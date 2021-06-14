import discord
from discord.ext import commands
import os

def ext_str(exts):
    return f"cmds.{exts}"

def create_msg(msg, head, set_exts):
	if len(set_exts) != 0:
		msg = msg + head + ": __" + "__, __".join(set_exts) + "__\n"
	return msg



class Cog_Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_cmds()
        for exts in self.list_exts:
            self.bot.load_extension(ext_str(exts))
    
    def check_cmds(self):
        list_exts = set()
        for file in os.listdir("cmds"):
            if file[-3:] == ".py":
                list_exts.add(file[:-3])
        self.list_exts = list_exts
        print("Extension found:", ", ".join(list_exts))
    
    @commands.command()
    async def load(self, ctx, *args):
        if len(args) == 0:
            await ctx.send(":x:What extension you want to load???")
        else:
            args_exts = set(args)
            if "all" in args_exts:
                args_exts = self.list_exts
            
            exts_stat = [set(), set(), set()]
            msgs_stat = [":white_check_mark:Extension loaded",
                        ":x:Extension already loaded",
                        ":x:Extension not found"]
            for exts in args_exts:
                try:
                    self.bot.load_extension(ext_str(exts))
                except commands.errors.ExtensionAlreadyLoaded as e:
                    exts_stat[1].add(exts)
                    print(e.args[0])
                except commands.errors.ExtensionNotFound as e:
                    exts_stat[2].add(exts)
                    print(e.args[0])
                else:
                    exts_stat[0].add(exts)
            
            if "all" in args and len(exts_stat[0]) != 0:
                exts_stat[1] = exts_stat[2] = []
            send_msg = ""
            for msg, exts in zip(msgs_stat, exts_stat):
                send_msg = create_msg(send_msg, msg, exts)
            await ctx.send(send_msg)

    @commands.command()
    async def unload(self, ctx, *args):
        if len(args) == 0:
            await ctx.send(":x:What extension you want to unload???")
        else:
            args_exts = set(args)
            if "all" in args_exts:
                args_exts = self.list_exts
            
            exts_stat = [set(), set()]
            msgs_stat = [":white_check_mark:Extension unloaded",
                        ":x:Extension not loaded"]
            for exts in args_exts:
                try:
                    self.bot.unload_extension(ext_str(exts))
                except commands.errors.ExtensionNotLoaded as e:
                    exts_stat[1].add(exts)
                    print(e.args[0])
                else:
                    exts_stat[0].add(exts)
            
            if "all" in args and len(exts_stat[0]) != 0:
                exts_stat[1] = []
            send_msg = ""
            for msg, exts in zip(msgs_stat, exts_stat):
                send_msg = create_msg(send_msg, msg, exts)
            await ctx.send(send_msg)

    @commands.command()
    async def reload(self, ctx, *args):
        if len(args) == 0:
            await ctx.send(":x:What extension you want to reload???")
        else:
            args_exts = set(args)
            if "all" in args_exts:
                args_exts = self.list_exts
            
            exts_stat = [set(), set(), set()]
            msgs_stat = [":white_check_mark:Extension reloaded",
                        ":x:Extension already loaded",
                        ":x:Extension not loaded"]
            for exts in args_exts:
                try:
                    self.bot.reload_extension(ext_str(exts))
                except commands.errors.ExtensionAlreadyLoaded as e:
                    exts_stat[1].add(exts)
                    print(e.args[0])
                except commands.errors.ExtensionNotLoaded as e:
                    exts_stat[2].add(exts)
                    print(e.args[0])
                else:
                    exts_stat[0].add(exts)
            
            if "all" in args and len(exts_stat[0]) != 0:
                exts_stat[1] = exts_stat[2] = []
            send_msg = ""
            for msg, exts in zip(msgs_stat, exts_stat):
                send_msg = create_msg(send_msg, msg, exts)
            await ctx.send(send_msg)
    
    @commands.command()
    async def update_cogs(self, ctx):
        self.check_cmds()
        await ctx.send(f"Find {len(self.list_exts)} extension: __{'__, __'.join(self.list_exts)}__")


def setup(bot):
    bot.add_cog(Cog_Core(bot))