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
        self.players.append(player)
        self.start_view = StartView(dealer = self)
        self.start_embed = {"title": "Black Jack",
                            "description": f"lobby open. {len(self.players)} players",
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
        self.start_view.sent_message(sent)
    
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
        self.start_embed["description"] = f"lobby open. {len(self.players)} players"
        val = ", ".join([p.display_name for p in self.players])
        if val == "":
            val = ":x:"
        self.start_embed["fields"][0]["value"] = val


class StartView(discord.ui.View):
    def __init__(self, *, timeout: Optional[float] = 30, dealer: BJDealer):
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
        embed = self.dealer.player_join(interact.user)
        await interact.response.edit_message(embed = embed)
    
    @discord.ui.button(label = "leave",
                       style = discord.ButtonStyle.gray,
                       custom_id = "leave")
    async def leave(self, interact: discord.Interaction, button: discord.ui):
        embed = self.dealer.player_leave(interact.user)
        await send_msg("BJ leave", {"embed": embed, "view": self}, interact, "edit")
    
    def sent_message(self, sent: discord.Message):
        self.sent = sent
    
    async def on_timeout(self):
        await self.sent.delete()