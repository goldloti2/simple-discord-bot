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
- TODO: ctx rename to interact (5/6) (main, ~~cog_core~~, ~~log~~, ~~cogs\*3~~)

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

2022/09/13 dev branch - 1

- cmds/misc.py
  - rework slash command - ping
    - no argument now, since slash commands don't allow ambiguous arguments
  - rework slash command - change_game
    - no command error, since slash commands don't support
- cmd/test.py
  - modify slash command - pong, pong2
    - add description
- utils/log.py
  - modify function - print_cmd
    - rearrange argument so args can be optional
  - modify decorator - commandlog
    - correctly send argument to print_cmd

2022/09/13 dev branch - 2

- utils/cog_core.py
  - rename Cog_Core to CogCore
  - rework slash commands - load, unload, reload, update (previous update_cogs)

2022/09/14 dev branch - 1

- utils/cog_core.py
  - fix bug - commands string been split

2022/09/14 dev branch - 2

- utils/log.py
  - fix bug - TwitterClass.request() don't work

2022/09/14 dev branch - 3

- cmd/twitter.py
  - rework slash command - subscribe, subscription, update, delete
    - subscribe combine old commands: subscribe_user and subscribe_search
    - subscription rename from subscribed
    - delete combine old commands: delete_user and delete_search

2022/09/14 v.2.2

- slash command rework
- prettier style: less character per line, more readable spacing
- several typo fix

2022/10/20 music-dev branch, merge from old-music-dev branch (done in 2021/12/05)

- cmd/musicbot.py
  - Function is_connected() - done
  - Function search_yt() - done
  - Function play_next() - self.vc.play() cannot play the music
  - Coroutine inactive_timer() - done, sleep time needs to change when in actual use
  - Function reset_timer() - done
  - Command play() - done, but might have bugs
  - Command stop() - temporary for disconnect from voice channel

2022/10/20 music-dev branch - 2

- rework cmd/musicbot.py
  - Function is_connected - done
  - Command play - now can connect to voice channel
  - Command stop - temporary for disconnect from voice channel
- correct some document error when merging

2022/10/21 music-dev branch - 1

- rework cmd/musicbot.py
  - Coroutine inactive_timer - done, sleep time needs to change when in actual use

2022/10/21 music-dev branch - 2

- rework cmd/musicbot.py
  - Function search_yt - done
  - some style correction

2022/10/23 music-dev branch - 1

- rework cmd/musicbot.py
  - cog_unload - done

2022/10/23 music-dev branch - 2

- rework cmd/musicbot.py
  - Function search_yt - can download music
  - Function play_next - can play one music per time
- known bugs
  - inactive_timer works wrong when restart timer
  - downloading music takes too long, and occupying bot
  - when downloading for the first time, it can't be played
  - strange stuff occured:
    1. `/play a`
    2. connect to voice channel
    3. download `a`
    4. download complete, play music, but stop right after
    5. `/play a` again
    6. bot is not in voice channel; but indiscord, it is in.
    7. connection timeout
    8. `/play a` again
    9. play normally
    10. after play list exhausts, timer doesn't wake

2022/10/23 music-dev branch - 3

- fix bugs
  - inactive_timer now wakes up no matter if voice channel is connected (no restart)
    - *2022/10/24 note: it's an external timer, more precisely*
- cog_unload for musicbot is now a coroutine
- set ytdl download to False (consider download starting at another place)

2022/10/24 music-dev branch - 1

- add a lock to inactive_timer, preventing from disconnecting when play is called
- rename ydl to ytdl
- make search_yt as a coroutine, and ytdl.extract_info is now async

2022/10/24 music-dev branch - 2

- ytdl options added: "nocheckcertificate": True
- ready to rewrite whole MusicBot

2022/10/25 music-dev branch - 1

- rewrite MusicBot - new class `MusicPlayer` for play queue management
- basic voice connection/disconnection is done (without timeout disconnection)
- class MusicPlayer
  - coroutine new_play - add new music to queue
    - connect to voice channel
    - move to new voice channel
    - *(on schedule)*: search yt to response with music info
  - coroutine terminate - terminate instance
    - disconnect from voice channel
- cog MusicBot
  - command play - call MusicPlayer.newplay()
    - check if user is in voice channel
    - check if there is an active MusicPlayer for the guild
  - cog_unload will call MusicPlayer.terminate()

2022/10/25 music-dev branch - 2

- search music info for respond is done
- class MusicPlayer
  - coroutine new_play - add new music to queue
    - search yt to response with music info
  - coroutine search_yt - search music info
    - search music info and put into download queue

2022/10/25 music-dev branch - 3

- download music inside the queue is done
- class MusicPlayer
  - coroutine download_loop - wait queue and download music
    - loop forever and wait the queue
    - when queue has item, pop it out and download
  - coroutine terminate - terminate instance
    - cancel download_loop task
  - some log content change

2022/10/26 music-dev branch

- play loop is done, now can actually play music in queue
- command done: play
- command TODO: pause, skip, stop, list
- class MusicPlayer
  - coroutine play_loop - play musics in queue
    - get music from queue and play
    - if it's not playing nor downloading for 10 sec, self terminated

2022/10/27 music-dev branch - 1

- bug fixed: when more than 2 downloaded music are in queue, stop playing from the 2nd
- musicbot won't move to other channel if it is still playing
- remove no longer used debug prints
- typo fixed in documents

2022/10/27 music-dev branch - 2

- extract user and player active check section to be an independent function

2022/10/28 music-dev branch - 1

- change play loop process - remove unnecessary event waiting

2022/10/28 music-dev branch - 2

- command pause/resume is done
- command done: play, pause
- command TODO: skip, stop, list
- class MusicPlayer
  - function pause_resume - pause or resume music
    - act only when user and musicbot are in the same voice channel
- cog MusicBot
  - command pause_resume - call MusicPlayer.pause_resume()

2022/10/28 music-dev branch - 3

- more information send to text channel

2022/10/28 music-dev branch - 4

- make loop initialization and termination independent functions

2022/10/29 music-dev branch

- command stop is done
- command done: play, pause, stop
- command TODO: skip, list
- class MusicPlayer
  - function stop - stop music and clear the queue
    - act only when user and musicbot are in the same voice channel
- cog MusicBot
  - command stop - call MusicPlayer.stop()

2022/10/30 music-dev branch - 1

- command playlist is done
- command done: play, pause, stop, playlist
- command TODO: skip
- class MusicPlayer
  - function playlist - list music in queue
- cog MusicBot
  - command playlist - call MusicPlayer.playlist()

2022/10/30 music-dev branch - 2

- youtube_dl retries 5 times to download (no retry previously)
- more detailed log information when youtube_dl download error occurred
- fix bug: playlist won't update when download error occurred

2022/11/02 music-dev branch

- command skip is done *(tested, but so complicate that might miss some cases)*
- command done: play, pause, stop, playlist, skip
- class MusicPlayer
  - function skip - skip specific music on queue
  - coroutine download_coro - make download as an awaitable, therefore can get the task and cancel it
- cog MusicBot
  - command skip - call MusicPlayer.skip()
  - command play - add argument description

2022/11/03 music-dev branch

- add message when play list is empty
- reduce some redundant if-statements and variables
- fix minor bugs: when ffmpeg error or play error occurred, skip and play next

2022/11/07 music-dev branch

- now can enqueue whole playlist
  - add coroutine add_dl_queue - push search result to download queue
- change musicbot timeout interval to 180 sec.
