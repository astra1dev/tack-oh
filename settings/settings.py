import os
import peewee
from dotenv import load_dotenv
import discord
from discord import app_commands

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

db = peewee.SqliteDatabase("settings/settings.db")


class Settings(peewee.Model):
    guild_id: str = peewee.CharField(max_length=255, primary_key=True)
    currency: str = peewee.CharField(max_length=255, default=":taco:")
    prefix: str = peewee.CharField(max_length=255, default="!")
    module_anime = peewee.BooleanField(default=0)
    module_economy = peewee.BooleanField(default=0)
    module_fun = peewee.BooleanField(default=1)
    module_games = peewee.BooleanField(default=0)
    module_image = peewee.BooleanField(default=0)
    module_music = peewee.BooleanField(default=0)
    module_nsfw = peewee.BooleanField(default=0)

    class Meta:
        database = db
        without_rowid = True


class SettingsCommands(app_commands.Group):
    @app_commands.command(name="set", description="Set a setting")
    @app_commands.describe(setting="The setting you want to change",
                           value="The value you want to set (0/1 for modules, string for currency/prefix)")
    @app_commands.choices(setting=[app_commands.Choice(name="Module Anime", value="anime"),
                                   app_commands.Choice(name="Module Economy", value="economy"),
                                   app_commands.Choice(name="Module Fun", value="fun"),
                                   app_commands.Choice(name="Module Games", value="games"),
                                   app_commands.Choice(name="Module Image", value="image"),
                                   app_commands.Choice(name="Module Music", value="music"),
                                   app_commands.Choice(name="Module NSFW", value="nsfw"),
                                   app_commands.Choice(name="Currency Icon", value="currency"),
                                   app_commands.Choice(name="Prefix (will soon be removed)", value="prefix")])
    async def set(self, interaction: discord.Interaction, setting: str, value: str):
        try:
            settings = Settings.get(Settings.guild_id == interaction.guild.id)
        except peewee.DoesNotExist:
            settings = Settings.create(guild_id=interaction.guild.id)

        # Convert value to integer if setting is a module
        if setting in ["anime", "economy", "fun", "games", "image", "music", "nsfw"]:
            value = int(value)

        # Modules
        if setting == "anime":
            settings.module_anime = value
        elif setting == "economy":
            settings.module_economy = value
        elif setting == "fun":
            settings.module_fun = value
        elif setting == "games":
            settings.module_games = value
        elif setting == "image":
            settings.module_image = value
        elif setting == "music":
            settings.module_music = value
        elif setting == "nsfw":
            settings.module_nsfw = value
        # Other
        elif setting == "currency":
            settings.currency = value
        elif setting == "prefix":
            settings.prefix = value
        else:
            embed = discord.Embed(title="❌ Error", colour=discord.Colour(0xff0000),
                                  description=f"Setting `{setting}` not found!")
            await interaction.response.send_message(embed=embed)
            return

        settings.save()
        embed = discord.Embed(title="✅ Success", colour=discord.Colour(0x00ff00), description=
                              f"Setting `{setting}` has been set to {value}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="show", description="Show the current settings")
    async def show(self, interaction: discord.Interaction):
        try:
            settings = Settings.get(Settings.guild_id == interaction.guild.id)
        except peewee.DoesNotExist:
            settings = Settings.create(guild_id=interaction.guild.id)
        embed = discord.Embed(title="⚙️ Settings", colour=discord.Colour(0x00ff00),
                              description="You can change these settings with `/settings set`")
        embed.add_field(name="Currency Icon", value=settings.currency)
        embed.add_field(name="Prefix", value=settings.prefix)
        embed.add_field(name="Module Anime", value=settings.module_anime)
        embed.add_field(name="Module Economy", value=settings.module_economy)
        embed.add_field(name="Module Fun", value=settings.module_fun)
        embed.add_field(name="Module Games", value=settings.module_games)
        embed.add_field(name="Module Image", value=settings.module_image)
        embed.add_field(name="Module Music", value=settings.module_music)
        embed.add_field(name="Module NSFW", value=settings.module_nsfw)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    db.create_tables([Settings])
    bot.tree.add_command(SettingsCommands(name="settings", description="Settings commands"))

# Set to true to allow 18+ content (still requires the channel to be marked as NSFW)
NSFW_ALLOWED = False
