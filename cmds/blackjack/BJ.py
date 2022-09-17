import discord
from discord import app_commands
from typing import Optional
import utils.log as log
from utils.log import send_msg

logger = log.get_logger()

class BJDealer(object):
    def __init__(self, channel: discord.TextChannel):
        self.channel = channel
        self.players = []
    
    async def start_lobby(self, player: discord.Member):
        self.running = True
        self.players.append(player)
        self.start_view = StartView(dealer = self)
        self.start_embed = {"title": "Black Jack",
                            "description": f"{len(self.players)} players in lobby",
                            "type": "rich",
                            "fields": [
                                    {"name": "player:",
                                     "value": ", ".join([p.display_name for p in self.players]),
                                     "inline": True}
                                ]}
        embed = discord.Embed.from_dict(self.start_embed)
        sent = await send_msg("BJ lobby",
                              {"embed": embed, "view": self.start_view},
                              self.channel)
        self.start_view.set_sent_message(sent)
    
    def player_join(self, player: discord.Member):
        if not player in self.players:
            self.players.append(player)
            self.player_update()
        return discord.Embed.from_dict(self.start_embed)
    
    def player_leave(self, player: discord.Member):
        if player in self.players:
            self.players.remove(player)
            self.player_update()
        return discord.Embed.from_dict(self.start_embed)

    def player_update(self):
        self.start_embed["description"] = f"{len(self.players)} players in lobby"
        val = ", ".join([p.display_name for p in self.players])
        if val == "":
            val = ":x:"
        self.start_embed["fields"][0]["value"] = val
    
    def is_joined(self, player: discord.Member):
        return player in self.players



class StartView(discord.ui.View):
    def __init__(self, *, timeout: Optional[float] = 10, dealer: BJDealer):
        super().__init__(timeout = timeout)
        self.dealer = dealer
    
    @discord.ui.button(label = "join",
                       style = discord.ButtonStyle.green,
                       custom_id = "join")
    async def join(self, interact: discord.Interaction, button: discord.ui):
        embed = self.dealer.player_join(interact.user)
        await send_msg("BJ join", {"embed": embed, "view": self}, interact, "edit")
    
    @discord.ui.button(label = "start",
                       style = discord.ButtonStyle.blurple,
                       custom_id = "start")
    async def start(self, interact: discord.Interaction, button: discord.ui):
        if self.dealer.is_joined(interact.user):
            embeds = interact.message.embeds
            await send_msg("BJ join", {"embeds": embeds, "view": None}, interact, "edit")
            self.stop()
        else:
            message = {"content": "you are not in the game!", "ephemeral": True}
            await send_msg("BJ start", message, interact, "response")
    
    @discord.ui.button(label = "leave",
                       style = discord.ButtonStyle.gray,
                       custom_id = "leave")
    async def leave(self, interact: discord.Interaction, button: discord.ui):
        embed = self.dealer.player_leave(interact.user)
        await send_msg("BJ leave", {"embed": embed, "view": self}, interact, "edit")
    
    def set_sent_message(self, sent: discord.Message):
        self.sent = sent
    
    async def on_timeout(self):
        try:
            if len(self.dealer.players) != 0:
                await self.sent.edit(embeds = self.sent.embeds, view = None)
            else:
                await self.sent.delete()
                self.dealer.running = False
        except discord.HTTPException as e:
            logger.error("BJ start timeout response failed")
            logger.debug(str(e))
        except:
            logger.error("BJ start timeout response error")
            logger.debug("\n", exc_info = True)
        else:
            logger.debug("BJ start timeout success")