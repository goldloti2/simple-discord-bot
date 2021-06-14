import discord
from discord.ext import commands
from log import start_logging
import json
import os


logger = start_logging("discord", "log/discord", debug = True)

with open("setting.json", "r", encoding = "utf-8") as jfile:
    setting = json.load(jfile)

def ext_str(exts):
    return f"cmds.{exts}"
list_exts = set()
for file in os.listdir("cmds"):
    if file[-3:] == ".py":
        list_exts.add(file[:-3])


bot = commands.Bot(command_prefix = "$")

for exts in list_exts:
    bot.load_extension(ext_str(exts))
    


@bot.event
async def on_ready():
    game = discord.Game(setting["GAME"])
    await bot.change_presence(status=discord.Status.idle, activity=game)
    print("Extension found:", ", ".join(list_exts))
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def load(ctx, *args):
    if len(args) == 0:
        await ctx.send("What extension you want to load???")
    else:
        args_exts = set(args)
        unk_args = set()
        if "all" in args_exts:
            match_exts = list_exts
        else:
            match_exts = args_exts.intersection(list_exts)
            unk_args = args_exts.difference(list_exts)
        
        loaded_exts = set()
        for exts in match_exts:
            try:
                bot.load_extension(ext_str(exts))
            except commands.errors.ExtensionNotFound as e:
                print(e.args[0])
            except commands.errors.ExtensionAlreadyLoaded as e:
                print(e.args[0])
        
        msg = ""
        if len(match_exts) != 0:
            msg = "Extension loaded: " + ", ".join(match_exts) + "\n"
        if len(unk_args) != 0:
            msg = msg + "Extension not found: " + ", ".join(unk_args)
        await ctx.send(msg)



if __name__ == "__main__":
    bot.run(setting["TOKEN"])
