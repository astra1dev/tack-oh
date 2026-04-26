import os
import peewee
from dotenv import load_dotenv
import discord
from discord import app_commands

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
SRA_API_KEY = os.getenv("SRA_API_KEY")
SRA_REQUEST_HEADERS = {
    "Authorization": f"{SRA_API_KEY}"
}
SRA_BASE_URL = "https://api.some-random-api.com"

db = peewee.SqliteDatabase("settings/settings.db")


class Settings(peewee.Model):
    guild_id: str = peewee.CharField(max_length=255, primary_key=True)
    currency: str = peewee.CharField(max_length=255, default=":taco:")
    prefix: str = peewee.CharField(max_length=255, default="!")
    module_anime = peewee.BooleanField(default=False)
    module_economy = peewee.BooleanField(default=False)
    module_fun = peewee.BooleanField(default=True)
    module_games = peewee.BooleanField(default=False)
    module_image = peewee.BooleanField(default=False)
    module_music = peewee.BooleanField(default=False)
    module_nsfw = peewee.BooleanField(default=False)

    class Meta:
        database = db
        without_rowid = True


class SettingsCommands(app_commands.Group):
    @app_commands.command(name="set", description="Set a setting")
    @app_commands.describe(setting="The setting you want to change",
                           value="The value you want to set (0/1 for modules, string for currency/prefix)")
    @app_commands.choices(setting=[app_commands.Choice(name="Anime", value="anime"),
                                   app_commands.Choice(name="Economy", value="economy"),
                                   app_commands.Choice(name="Fun", value="fun"),
                                   app_commands.Choice(name="Games", value="games"),
                                   app_commands.Choice(name="Image", value="image"),
                                   app_commands.Choice(name="Music", value="music"),
                                   app_commands.Choice(name="NSFW", value="nsfw"),
                                   app_commands.Choice(name="Currency Icon", value="currency"),
                                   app_commands.Choice(name="Prefix (will soon be removed)", value="prefix")])
    async def set(self, interaction: discord.Interaction, setting: str, value: str) -> None:
        try:
            settings = Settings.get(Settings.guild_id == interaction.guild.id)
        except peewee.DoesNotExist:
            settings = Settings.create(guild_id=interaction.guild.id)

        # Convert value to boolean if it's a module
        if setting in ["anime", "economy", "fun", "games", "image", "music", "nsfw"]:
            if value.lower() in ["enabled", "true", "1", "on"]:
                value = True
            elif value.lower() in ["disabled", "false", "0", "off"]:
                value = False
            else:
                embed = discord.Embed(title="❌ Error", colour=discord.Colour(0xff0000),
                                      description="Please provide a valid value for modules (enabled/disabled, "
                                                  "true/false, 1/0, on/off)")
                await interaction.response.send_message(embed=embed, ephemeral=True)

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

        settings.save()
        embed = discord.Embed(title="✅ Success", colour=discord.Colour(0x00ff00), description=
                              f"Setting `{setting}` has been set to {value}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="show", description="Show the current settings")
    async def show(self, interaction: discord.Interaction) -> None:
        try:
            settings = Settings.get(Settings.guild_id == interaction.guild.id)
        except peewee.DoesNotExist:
            settings = Settings.create(guild_id=interaction.guild.id)
        embed = discord.Embed(title="⚙️ Settings", colour=discord.Colour(0x00ff00),
                              description="Admins can change settings with `/settings set`")
        embed.add_field(name="Currency Icon", value=settings.currency)
        embed.add_field(name="Prefix", value=settings.prefix)
        embed.add_field(name="🔰 Anime", value=settings.module_anime)
        embed.add_field(name="🪙 Economy", value=settings.module_economy)
        embed.add_field(name="😂 Fun", value=settings.module_fun)
        embed.add_field(name="🎮 Games", value=settings.module_games)
        embed.add_field(name="🖼️ Image", value=settings.module_image)
        embed.add_field(name="🎧 Music", value=settings.module_music)
        embed.add_field(name="🍑 NSFW", value=settings.module_nsfw)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="reset", description="Reset settings to default values")
    async def reset(self, interaction: discord.Interaction) -> None:
        try:
            settings = Settings.get(Settings.guild_id == interaction.guild_id)
        except peewee.DoesNotExist:
            settings = Settings.create(guild_id=interaction.guild_id)

        # Reset settings to default values
        settings.currency = ":taco:"
        settings.prefix = "!"
        settings.module_anime = False
        settings.module_economy = False
        settings.module_fun = True
        settings.module_games = False
        settings.module_image = False
        settings.module_music = False
        settings.module_nsfw = False

        settings.save()
        embed = discord.Embed(title="✅ Success", colour=discord.Colour(0x00ff00),
                              description="Settings have been reset to default values.")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    db.create_tables([Settings])
    bot.tree.add_command(SettingsCommands(name="settings", description="Settings commands"))

# Set to true to allow 18+ content (still requires the channel to be marked as NSFW)
NSFW_ALLOWED = False
