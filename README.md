# Simple-Discord-Bot
Just a simple discord bot that can search and push twitter message to your discord channel.  
只是個簡單的discord機器人，可以定時上twitter搜尋，然後推播到discord頻道中  

## Features
- Subscribe/Desubscribe to the Twitter accounts or Twitter search
- Automatically check newest tweets of the subscriptions and push to the discord channels
- Change bot game stat
- Load/Unload Cogs

## Python Environment Setup
Python version: 3.8.2  
Python 版本: 3.8.2  
  
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
- Change Twitter api library from searchtweets to requests *(Since we just need http requests!)*
- tools/gen_setting.py:
	- generate setting.json
- add some twitter api sample codes in twitter/sample
  
2021/06/17
- Now recieved commands and the response will print on the console
- Modified gen_setting.py to save Twitter bearer token in setting.json
- Rename some functions, variables, and keywords
- Working on Twitter-associate classes
	- Twitter-api ends (in twitter dir) finished but not tested yet
	- Discord-bot ends (cmds/twitter.py) still in progress
- utils.py
	- added function - print_cmd()
- cmds/test.py
	- Modified as a cog for testing async and requests
	- modified command - pong()
	- added command - pong2()
	- added function - request_url()
- cmds/twitter.py
	- Everything still in progress
	- added command - subscribe_user(), subscribe_search()
- twitter/twitter_class.py
	- added class - Twitter_Class(), Twitter_Timeline(), Twitter_Recent()
  
2021/06/18
- Fix some bugs in cmds/twitter.py and twitter/twitter_class.py
- Add more bugs in cmds/twitter.py
- Change some console messages
- cmds/twitter.py
	- fixed \_\_init\_\_()
	- fixed command - subscribe_user(), subscribe_search()
	- added command - update(), subscribed()
	- added function - call\_update() _(some bugs inside)_
  
2021/06/19
- Fix known bugs in cmds/twitter.py and twitter/twitter_class.py
- Replace simple print() with own logger
- Try to handle potential exceptions (but cannot figure out how to catch ctrl-c)
- utils.py
	- removed function - print_cmd()
- log.py
	- added function - print_cmd(), send_msg()
  
2021/06/20
- Fix send message bugs in cog_core.py
- Handle potential exceptions in main.py (except ctrl-c, _it seems like Windows problem?_)
- Handle missing argument errors in cmds/misc.py and cmds/twitter.py
- Add and change some logger messages
- Working on delete subscription commands in cmds/twitter.py
- log.py
	- added function - send_err()
  
2021/06/21 v.0.7
- Can delete subscription now
- Apply decorator over all cogs.init and commands. Now the routine logging can be done with them.
- Add comment over all commands
- logwrap.py
	- added decorator function - commandlog, initlog
- cmds/twitter.py
	- added command - delete_user(), delete_search()
  
2021/06/22
- Twitter Update Timer is online!
- Twitter cog now can remember subscriptions for each guilds (Though I don't think anyone else will use it lol)
- Combine logwrap.py into log.py
- Move cog_core.py, log.py, utils.py into utils directory
  
2021/06/23
- Hide some admin-only commands, add helps on commands, and remove some command aliases
- Some small changes about async, making everyone using bot.loop, and remove unnecessary async on request()
- Add on_guild_join and on_guild_remove events to create or remove subscription directory (though not test yet)
  
2021/06/24
- Add since_id so that the twitter query can start from the last tweets it gets
- If the subscription channel is deleted, the query will be deleted when update
- Fix some message displaying bugs
- Remove json from requirement.txt since it is the built-in module
  
2021/06/25
- Reduce some redundant code in cmds/twitter.py and twitter/twitter_class.py
- Add Windows cmd / Linux bash script for setting up the environment