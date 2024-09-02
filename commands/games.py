import discord
from discord import app_commands
import random


class GameCommands(app_commands.Group):
    @app_commands.command(name="dice", description="Throw the dice")
    async def games_dice(self, interaction: discord.Interaction):
        number = random.randrange(1, 7)
        embed = discord.Embed(title=":video_game: Game: Dice",
                              description=f"{number}:game_die: - alea iacta est.",
                              colour=discord.Colour(0x00ff00))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rps", description="Play a game of rock paper scissors against the bot")
    @app_commands.describe(item="your choice")
    @app_commands.choices(item=[app_commands.Choice(name="🪨 rock", value="🪨 rock"),
                                app_commands.Choice(name="🧻 paper", value="🧻 paper"),
                                app_commands.Choice(name="✂️ scissors", value="✂️ scissors"),])
    async def dice(self, interaction: discord.Interaction, item: discord.app_commands.Choice[str]):
        bot_item = random.choice(["🪨 rock", "🧻 paper", "✂️ scissors"])
        outcomes = {
            "🪨 rock": {"win": "✂️ scissors", "lose": "🧻 paper"},
            "🧻 paper": {"win": "🪨 rock", "lose": "✂️ scissors"},
            "✂️ scissors": {"win": "🧻 paper", "lose": "🪨 rock"}
        }

        if bot_item == item.value:
            embed = discord.Embed(title=":video_game: Game: rock, paper, scissors", colour=discord.Colour(0x00ff00),
                                  description=f"Tie! We both picked **{item.name}**")
            await interaction.response.send_message(embed=embed)
        elif bot_item == outcomes[item.value]["win"]:
            embed = discord.Embed(title=":video_game: Game: rock, paper, scissors", colour=discord.Colour(0x00ff00),
                                  description=f"You win! I picked **{bot_item}** and you picked **{item.name}**")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title=":video_game: Game: rock, paper, scissors", colour=discord.Colour(0x00ff00),
                                  description=f"I win! I picked **{bot_item}** and you picked **{item.name}**")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="connect4", description="Play connect4 against another user or the bot")
    async def connect4(self, interaction: discord.Interaction):
        pass


async def setup(bot):
    bot.tree.add_command(GameCommands(name="game", description="Game commands"))
