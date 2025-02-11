#!/usr/bin/python

r"""
  _                _                   _
 | |              | |                 | |
 | |_  __ _   ___ | | __ ______  ___  | |__
 | __|/ _` | / __|| |/ /|______|/ _ \ | '_ \
 | |_| (_| || (__ |   <        | (_) || | | |
  \__|\__,_| \___||_|\_\        \___/ |_| |_|

 v2.0 created by Astral, github.com/astra1dev
"""

# -------------------- IMPORTS -------------------- #
import discord
from discord.ext import commands, tasks
from discord import app_commands
# from discord.utils import get

from settings import settings
from connect4 import Board

import asyncio
import math
import time
import datetime
import psutil

# -------------------- VARIABLES -------------------- #
bot = commands.Bot(command_prefix='!', help_command=None, intents=discord.Intents.all(),
                   activity=discord.Activity(type=discord.ActivityType.listening, name="your commands"),
                   status=discord.Status.online)

# connect4
player_piece = 'R'
ai_piece = 'Y'
emotes = {'1️⃣': 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3, '5️⃣': 4, '6️⃣': 5, '7️⃣': 6, '🏳': 'F'}
board_slots = '```1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n🔻🔻🔻🔻🔻🔻🔻\n----------------\n'
game_sessions = {}
board, player_1, player_2, current_piece, timer, channel = 0, 1, 2, 3, 4, 5
player_dict = {True: [player_1, 'R', discord.Colour.red()],
               False: [player_2, 'Y', discord.Colour.gold()]}

# for uptime calculation
start_time = time.time()

# -------------------- FUNCTIONS -------------------- #
@bot.event
async def on_ready():
    i = 0
    print(f"\n{45*'-'}\n"
          f"[✅] {bot.user.name}#{bot.user.discriminator} (ID: {bot.user.id}, Display Name: {bot.user.display_name})  "
          f"\n    is connected to the following servers:")
    for _ in bot.guilds:
        print(f"{str(i + 1)}: {str(bot.guilds[i].name)}, ID: {str(bot.guilds[i].id)}")
        i = i + 1
    print(f"{45*'-'}\n")

    # Load commands from other files
    try:
        await bot.load_extension("commands.anime")
        await bot.load_extension("economy.economy")
        await bot.load_extension("commands.fun")
        await bot.load_extension("commands.games")
        await bot.load_extension("commands.image")
        await bot.load_extension("commands.music")
        await bot.load_extension("commands.nsfw")
        await bot.load_extension("settings.settings")
    except discord.ext.commands.errors.ExtensionAlreadyLoaded:
        pass

    # Load slash commands
    await bot.tree.sync()
    afk.start()
    print("[✅] Slash commands loaded.")


class ChallengeView(discord.ui.View):
    def __init__(self, player1, player2, board_slots, board, game_sessions, bot):
        super().__init__(timeout=60)
        self.player1 = player1
        self.player2 = player2
        self.board_slots = board_slots
        self.board = board
        self.game_sessions = game_sessions
        self.bot = bot
        self.message = None

    async def on_timeout(self) -> None:
        embed = discord.Embed(title=":crossed_swords: Challenge: connect4", colour=discord.Colour(0xff0000),
                              description=f"{self.player1.mention} challenged {self.player2.mention} to a game of "
                                          f"connect4!\nIt was cancelled because{self.player2.mention} did not respond "
                                          f"in time.")
        await self.message.edit(embed=embed, view=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.player2:
            return True
        else:
            embed = discord.Embed(title=":x: Error", colour=discord.Colour(0xff0000),
                                  description="You are not the challenged player.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False

    @discord.ui.button(label="Accept", emoji="✅", style=discord.ButtonStyle.success)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.interaction_check(interaction):
            return

        embed = discord.Embed(title=":video_game: Game: connect4", colour=discord.Colour(0x00ff00),
                              description=f"{self.board_slots}{self.board.print_board()}\nCurrent Player: {self.player1.mention}\n"
                                          f":flag_white:: Forfeit")
        embed.add_field(name=f":red_circle: {self.player1.name}", value="", inline=True)
        embed.add_field(name=f":yellow_circle: {self.player2.name}", value="", inline=True)
        await self.message.edit(embed=embed, view=None)
        for emoji in emotes:
            await self.message.add_reaction(emoji)
        self.game_sessions[self.message.id] = [self.board, self.player1, self.player2, 'R', 0, interaction.channel]

    @discord.ui.button(label="Decline", emoji="❌", style=discord.ButtonStyle.danger)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.interaction_check(interaction):
            return

        embed = discord.Embed(title=":video_game: Game: connect4", colour=discord.Colour(0xff0000),
                              description=f"{self.player2.mention} declined the challenge.")
        await self.message.edit(embed=embed, view=None)
        await interaction.response.defer()


def create_connect4_embed(title: str, description: str, curr_player: discord.Member, other_player: discord.Member) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, colour=discord.Colour(0x00ff00))
    embed.add_field(name=f":red_circle: {curr_player.name}", value="", inline=True)
    embed.add_field(name=f":yellow_circle: {other_player.name}", value="", inline=True)
    return embed


@bot.event
async def on_reaction_add(reaction, user) -> None:
    # if the reaction was not on a message with a game or the bot reacted, do nothing
    if reaction.message.id not in game_sessions or user == bot.user:
        return None
    current_session = game_sessions[reaction.message.id]
    curr_channel = current_session[channel]
    curr_piece = current_session[current_piece]
    curr_board = current_session[board]
    player_red = True if curr_piece == 'R' else False
    curr_player = current_session[player_dict[player_red][0]]
    other_player = current_session[player_dict[not player_red][0]]
    await reaction.remove(user)
    # if the reaction was not a valid move or another person reacted (not playing), do nothing
    if reaction.emoji not in emotes.keys() or (user != curr_player and user != other_player):
        return None
    # if the reaction was a forfeit, end the game
    if emotes[reaction.emoji] == 'F':
        del game_sessions[reaction.message.id]
        embed = discord.Embed(title=":video_game: Game: connect4",
                              description=f"{board_slots}{curr_board.print_board()}\n{user.mention} forfeited!",
                              colour=discord.Colour(0x00ff00))
        embed.add_field(name=f":red_circle: {curr_player.name}", value="", inline=True)
        embed.add_field(name=f":yellow_circle: {other_player.name}", value="", inline=True)
        await reaction.message.edit(embed=embed)
        await reaction.message.clear_reactions()
        return None
    # Check if the section of the board is not already filled
    if not curr_board.is_valid_location(0, emotes[reaction.emoji]):
        return None
    if user != curr_player:
        return None
    current_session[current_piece] = player_dict[not player_red][1]
    r = 5
    while not curr_board.is_valid_location(r, emotes[reaction.emoji]):
        r -= 1
    curr_board.drop_piece(r, emotes[reaction.emoji], curr_piece)
    current_session[timer] = 0
    if len(curr_board.get_valid_locations()) == 0:
        del game_sessions[reaction.message.id]
        embed = discord.Embed(title=":video_game: Game: connect4",
                              description=f"{board_slots}{curr_board.print_board()}\nIt's a tie!",
                              colour=discord.Colour(0x00ff00))
        embed.add_field(name=f":red_circle: {curr_player.name}", value="", inline=True)
        embed.add_field(name=f":yellow_circle: {other_player.name}", value="", inline=True)
        await reaction.message.edit(embed=embed)
        await reaction.message.clear_reactions()
        return None
    if curr_board.is_win(curr_piece):
        embed = discord.Embed(title=":video_game: Game: connect4",
                              description=f"{board_slots}{curr_board.print_board()}\n{curr_player.mention} won!",
                              colour=discord.Colour(0x00ff00))
        embed.add_field(name=f":red_circle: {curr_player.name}", value="", inline=True)
        embed.add_field(name=f":yellow_circle: {other_player.name}", value="", inline=True)
        await reaction.message.edit(embed=embed)
        await reaction.message.clear_reactions()
        del game_sessions[reaction.message.id]
        return None
    else:
        embed = discord.Embed(title=":video_game: Game: connect4",
                              description=f"{board_slots}{curr_board.print_board()}\nCurrent Player: {other_player.mention}"
                                          f"\n:flag_white:: Forfeit",
                              colour=discord.Colour(0x00ff00))
        embed.add_field(name=f":red_circle: {curr_player.name}", value="", inline=True)
        embed.add_field(name=f":yellow_circle: {other_player.name}", value="", inline=True)
        await reaction.message.edit(embed=embed)
    # if the player is playing against the bot (AI), run minimax algorithm and drop the piece
    if other_player.bot:
        await asyncio.sleep(1)
        col, minimax_score = curr_board.minimax(6, -math.inf, math.inf, True)
        row = curr_board.get_valid_locations()[col]
        curr_board.drop_piece(row, col, ai_piece)
        current_session[timer] = 0
        if curr_board.is_win(current_session[current_piece]):
            embed = discord.Embed(title=":video_game: Game: connect4",
                                  description=f"{board_slots}{curr_board.print_board()}\n{other_player.mention} won!",
                                  colour=discord.Colour(0x00ff00))
            embed.add_field(name=f":red_circle: {curr_player.name}", value="", inline=True)
            embed.add_field(name=f":yellow_circle: {other_player.name}", value="", inline=True)
            await reaction.message.edit(embed=embed)
            await reaction.message.clear_reactions()
            del game_sessions[reaction.message.id]
        else:
            embed = discord.Embed(title=":video_game: Game: connect4",
                                  description=f"{board_slots}{curr_board.print_board()}\nCurrent Player:"
                                              f"{curr_player.mention}\n:flag_white:: Forfeit",
                                  colour=discord.Colour(0x00ff00))
            embed.add_field(name=f":red_circle: {curr_player.name}", value="", inline=True)
            embed.add_field(name=f":yellow_circle: {other_player.name}", value="", inline=True)
            await reaction.message.edit(embed=embed)
        current_session[current_piece] = curr_piece


@bot.tree.command(name="info", description="Shows the bot's status and latency")
async def info(interaction):
    # Calculate uptime
    uptime_seconds = time.time() - start_time
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        uptime = f"{int(days)} day{'s' if days > 1 else ''}, {int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    else:
        uptime = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    connected_since = datetime.datetime.fromtimestamp(start_time, datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
    creation_time = bot.user.created_at.strftime("%Y-%m-%d %H:%M:%S")

    shard_id = bot.shard_id if bot.shard_id is not None else "Not Sharded"

    # Get CPU and RAM usage
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_total = ram.total / (1024 ** 3)  # Convert bytes to GB
    ram_used = ram.used / (1024 ** 3)
    ram_usage = ram.percent

    embed = discord.Embed(title=":pencil: Bot Information", colour=discord.Colour(0x00ff00),
                          timestamp=datetime.datetime.now(datetime.UTC))
    embed.add_field(name="⏱️ Latency", value=f"{str(round(bot.latency * 1000))}ms")
    embed.add_field(name="🌍 Servers", value=f"{str(len(bot.guilds))}")
    embed.add_field(name="👥 Users", value=f"{str(len([member for guild in bot.guilds for member in guild.members]))}")
    embed.add_field(name="⏳ Uptime", value=f"{uptime}")
    embed.add_field(name="🕰️ Connected Since", value=f"{connected_since}")
    embed.add_field(name="🗓️ Creation Time", value=f"{creation_time}")
    embed.add_field(name="💻 CPU Usage", value=f"{cpu_usage}%")
    embed.add_field(name="💻 RAM Usage", value=f"{ram_usage}% ({ram_used:.2f} GB / {ram_total:.2f} GB)")
    embed.add_field(name="⚙️ Shards", value=f"{shard_id} / {bot.shard_count}")
    embed.set_footer(text="created by Astral",
                           icon_url="https://cdn.discordapp.com/avatars/951884381209890877"
                                    "/ad9abec491fb314fc796b14d6f2edf83.png")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# to restrict this command to admins / specific role only:
# Server Settings > Integrations > tack-oh > /say > Add roles or Members
@bot.tree.command(name="say", description="Says something")
@app_commands.describe(channel="The channel you want to send the message to", message="The message you want to send")
async def say(interaction, channel: discord.TextChannel, message: str):
    channel = bot.get_channel(channel.id)
    await channel.send(str(message))
    await interaction.response.send_message(f"Message sent! {channel.mention}", ephemeral=True)


# Context menu to see join date of other members
# @bot.tree.context_menu(name="Show join date")
# async def get_joined_date(interaction: discord.Interaction, member: discord.Member):
#     await interaction.response.send_message(f"{member.mention} joined at {discord.utils.format_dt(member.joined_at)}",
#                                             ephemeral=True)


# Report a message
# @bot.tree.context_menu(name="Report message")
# async def report_message(interaction: discord.Interaction, message: discord.Message):
#     await interaction.response.send_message(f"Message reported: {str(message)}", ephemeral=True)


@bot.command()
async def connect4(ctx, *, player2: discord.Member = None):
    if player2 is None:
        player2 = bot.user
    elif player2 == ctx.author:
        embed = discord.Embed(title=":x: Error", colour=discord.Colour(0xff0000),
                              description="You cannot play against yourself.")
        await ctx.send(embed=embed)
        return None
    # player2 is now either the bot or another user
    player1 = ctx.author
    board = Board()
    if player2 == bot.user:
        embed = discord.Embed(title=":video_game: Game: connect4", colour=discord.Colour(0x00ff00),
                              description=f"{board_slots}{board.print_board()}\nCurrent Player: {player1.mention}\n"
                                          f":flag_white:: Forfeit")
        embed.add_field(name=f":red_circle: {player1.name}", value="", inline=True)
        embed.add_field(name=f":yellow_circle: {player2.name}", value="", inline=True)
        message = await ctx.send(embed=embed)
        for emoji in emotes:
            await message.add_reaction(emoji)
        # add the game to the dictionary of active games
        game_sessions[message.id] = [board, player1, player2, 'R', 0, ctx.channel]
    # create "challenge" message
    else:
        embed = discord.Embed(title="⚔️ Challenge: connect4", colour=discord.Colour(0x00ff00),
                              description=f"{player1.mention} challenged {player2.mention} to a game of connect4!"
                              f"\n{player2.mention} has 60 seconds to accept or decline.")
        view = ChallengeView(player1, player2, board_slots, board, game_sessions, bot)
        message = await ctx.send(embed=embed, view=view)
        view.message = message
        # await view.wait()


@tasks.loop(seconds=60)
async def afk():
    remove = []
    # check if the timer has reached the timeout for each game session
    for key in game_sessions:
        current_session = game_sessions[key]
        if current_session[timer] >= 120:
            chan = current_session[channel]
            curr_piece = current_session[current_piece]
            curr_board = current_session[board]
            game_msg = await chan.fetch_message(key)
            player_red = True if curr_piece == 'R' else False
            curr_player = current_session[player_dict[player_red][0]]
            other_player = current_session[player_dict[not player_red][0]]
            embed = discord.Embed(title=":video_game: Game: connect4",
                                  description=f"{board_slots}{curr_board.print_board()}\n{other_player.mention} won!\n"
                                              f"{curr_player.mention} did not make a move after 3 minutes!",
                                  colour=discord.Colour(0x00ff00))
            embed.add_field(name=f":red_circle: {curr_player.name}", value="", inline=True)
            embed.add_field(name=f":yellow_circle: {other_player.name}", value="", inline=True)
            await game_msg.edit(embed=embed)
            await game_msg.clear_reactions()
            remove.append(key)
        else:
            current_session[timer] += 60
    for key in remove:
        del game_sessions[key]

bot.run(settings.DISCORD_API_SECRET)
