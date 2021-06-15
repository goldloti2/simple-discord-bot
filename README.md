# Simple-Discord-Bot
Just a simple discord bot that can search and push twitter message on your discord channel.  
只是個簡單的discord機器人，可以定時上twitter搜尋，然後推播到discord頻道中  

## Features
- Change bot game stat
- Load/Unload Cogs

## Python Environment Setup
Python version: 3.8.2 (should be working on 3.5 or later)  
Python 版本:3.8.2 (3.5之後的應該也可以)  
  
Package required: discord.py, requests  
Package需求: discord.py, requests  
  
or just run following commands:  
或是直接執行下列命令:  
`pip install -r requirements.txt`

## Discord Bot Setup
Have to create a discord bot and get its token. (continue)  
要創建一個Discord bot然後取得它的token (待補)  
[Official Guide (English)](https://discordpy.readthedocs.io/en/stable/discord.html "Official Guide (English)")

## Twitter Api Setup
(continue)

## Generate Setting.json
Run the following command:  
執行下列命令:  
`python tools/gen_setting.py`  
and fill in the required contents  
並輸入所需的內容  

## Reference
[Discord api (Engilsh)](https://discordpy.readthedocs.io/en/stable/api.html "Discord api (Engilsh)")  
[Discord ext.commands api (English)←mainly used](https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html "Discord ext.commands api (English)←mainly used")  
[Twitter api (English)](https://developer.twitter.com/en/docs/twitter-api/early-access "Twitter api (English)")  
[Twitter api - reference index (English)](https://developer.twitter.com/en/docs/twitter-api/api-reference-index "Twitter api - reference index (English)")  
[Twitter api - fields (English)](https://developer.twitter.com/en/docs/twitter-api/fields "Twitter api - fields (English)")  
[Twitter query (English)](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query "Twitter query (English)")  
[Discord bot教學影片清單(中文)](https://www.youtube.com/watch?v=4JptXXkqiKU&list=PLSCgthA1Anif1w6mKM3O6xlBGGypXtrtN "Discord bot教學影片清單(中文)")  

## Update
2021/06/14 v.0.0
- Initial commit, cog load/unload avaliable
- main.py:
	- added event - on_ready()
- cog_core.py:
	- added command - load(), unload(), reload(), update_cogs()
- utils.py:
	- added function - load_setting(), save_setting()
- cmds/misc.py:
	- added command - ping(), change_game()
- cmds/test.py:
	- just a dumb cog.py
  
2021/06/15
- Change Twitter api library from searchtweets to requests *(Since we just need some http requests!)*
- tools/gen_setting.py:
	- generate setting.json
- add some twitter api sample codes in twitter/sample