# Update

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
  - added function - call\_update() *(some bugs inside)*
  
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
- Handle potential exceptions in main.py (except ctrl-c, *it seems like Windows problem?*)
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
  
2021/06/27

- Handle the requests error (maybe)
- Reduce some codes in utils/log.py
  
2021/07/02

- Change some logging format, less information shows on stdout
- Add Windows cmd / Linux bash for clean up the log
  
2021/10/13

- cmds/shinycolors.py
  - A small cog that notify boarderline of ShinyColors event every half an hour
  - Deprecate soon
- Bug found, not fix yet
  - Coroutines won't clean up when reloading the cogs, thus notifiers will be setup multiple times.
- Remove minor redundant codes in utils/log.py
  
2021/11/30

- cmds/shinycolors.py
  - Move it into cmds/legacy/shinycolors.py. Bye shinycolors.
- Fix bug: coroutines won't clean up when reloading the cogs
- Fix bug: cmds/twitter.py won't make the directory for the new server
- Minor code changes for logging
  
2021/12/02

- Split the update log from README.md
- cmds/twitter.py
  - Change timer interval to 1 min

2021/12/03

- utils/log.py
  - Modified function - ctx_send: avoid send empty message error
- cog_core.py
  - Modified init: catch ExtensionFailed when init and stop the bot
- cmds/twitter.py
  - When subscription is empty, stop the notifiers

2021/12/04

- Redisgn logger, now the main logger is called by function rather than import from utils/log.py
- Also, required directories are created from code rather than shellscripts

2021/12/05

- cmds/twitter.py
  - Minor log change
- utils/log.py
  - Modified to accept more message type being sent, e.g. Embed

2022/09/03 v.2.0

- Upgrade Discord.py to 2.0.1
  - bot.load_extension() and bot.add_cog() changed to *coroutine*
- Work on list
  - Change all commands to slash commands
  - ~~Twitter timer rework~~ - *done at 2022/09/05-2*

2022/09/04

- Revise coding style
  - reorder import by alphabet
  - rename initlogger(), getlogger() to init_logger(), get_logger()
  - rename Twitter_Class, Twitter_Timeline, Twitter_Recent to TwitterClass, TwitterTimeline, TwitterRecent
  - rename TW_obj to twitter_obj

2022/09/05 - 1

- Change bot start method - from bot.run() to bot.start()

2022/09/05 - 2

- cmds/twitter.py
  - Timer rework: use discord.ext.tasks
  - Reduce the use of self.bot.loop
  - fix bug - subscribe.json not loaded
    - Caused by loading cog before bot login

- utils/cog_core.py
  - fix bug - "load_extension, unload_extension, reload_extension were never awaited"

2022/09/06 v.2.1

- Replace **requests** with **httpx**, which supports async

2022/09/08 dev-branch

- Start working on slash commands convertion
- utils/log.py
  - change parameter *ctx*: commands.Context to *interact*: discord.Interaction
- cmds/test.py
  - rework slash command - pong
    - bug: not working now
- TODO: ctx rename to interact (2/6) (main, cog_core, ~~log~~, cogs\*2)

2022/09/09 dev-branch, merge from main-branch

- Annotate all parameter types

2022/09/11 dev branch

- cmds/test.py
  - fix slash command - pong
    - bug: can't wait too long (2 sec max) to response? - *fix in 2022/09/12*
  - annotate interaction parameter type

2022/09/12 dev branch

- cmds/test.py
  - fix slash command - pong
    - interaction.response.send_message() wait up to 3 sec
    - use await interaction.response.defer() and interaction.followup.send()
  - rework slash command - pong2
