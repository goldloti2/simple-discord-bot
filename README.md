# Simple-Discord-Bot

Just a simple discord bot that can search and push twitter message to your discord channel.  
只是個簡單的discord機器人，可以定時上twitter搜尋，然後推播到discord頻道中  

## Announcement

Because discord.py is no longer being updated and will soon be outdated (2022/4 at the latest), this project will stop too.  
However, since I was working on music bot cog at the half way when I know the news, I might keep update the cog on `dev` branch.  
Also, I will try to find another library and porting this project.

## Features

- Subscribe/Desubscribe to the Twitter accounts or Twitter search
- Automatically check newest tweets of the subscriptions and push to the discord channels
- Change bot game stat
- Load/Unload Cogs

## Python Environment Setup

Python version: 3.8.2  
Python 版本: 3.8.2  
  
Package requirement: discord.py, requests  
Package需求: discord.py, requests  
  
or just run following commands:  
或是直接執行下列命令:  
`pip install -r requirements.txt`

## Discord Bot Setup

Have to create a discord bot, get its token, and invite the bot.  
要創建一個Discord bot，取得它的token，然後邀請bot
  
1. Follow the link below to create a new application and its bot.  
依照下方連結創建新的應用與其bot  
[Official Guide (English)](https://discordpy.readthedocs.io/en/stable/discord.html "Official Guide (English)")  
  
2. Go to OAuth2→URL Generator, check scope and permission needed, then go to the generated url to invite the bot.  
到OAuth2→URL Generator，選擇對應的scope和permission，然後到產生的url邀請bot  
  
3. Fill in the token of the bot when generate setting.josn.  
產生setting.json時將bot的token填入  

## Twitter Api Setup

Press sign up in the link (continue)  
進入連結後按sign up (待補)  
[Twitter api - reference index (English)](https://developer.twitter.com/en/docs/twitter-api/api-reference-index "Twitter api - reference index (English)")  

## Generate setting.json

Run`init.cmd`(Windows) /`init.sh`(Linux)  
執行`init.cmd`(Windows) /`init.sh`(Linux)  
  
and fill in the required contents:  
並輸入所需的內容:  
Discord token (required)
Twitter token (required)
game status (optional)
command prefix (optional)

## Known Bugs

- ~~Coroutines won't clean up when reloading the cogs~~

## Future Plans

- Black Jack dealer
- Website backstage
- Music bot

## Reference

[Discord api (Engilsh)](https://discordpy.readthedocs.io/en/stable/api.html "Discord api (Engilsh)")  
[Discord ext.commands api (English)←mainly used](https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html "Discord ext.commands api (English)←mainly used")  
[Twitter api (English)](https://developer.twitter.com/en/docs/twitter-api/early-access "Twitter api (English)")  
[Twitter api - reference index (English)](https://developer.twitter.com/en/docs/twitter-api/api-reference-index "Twitter api - reference index (English)")  
[Twitter api - fields (English)](https://developer.twitter.com/en/docs/twitter-api/fields "Twitter api - fields (English)")  
[Twitter query (English)](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query "Twitter query (English)")  
[Discord bot教學影片清單(中文)](https://www.youtube.com/watch?v=4JptXXkqiKU&list=PLSCgthA1Anif1w6mKM3O6xlBGGypXtrtN "Discord bot教學影片清單(中文)")  
