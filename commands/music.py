import discord
from discord import app_commands
import urllib
from urllib import parse
import requests
import textwrap

from settings.settings import SRA_BASE_URL, SRA_REQUEST_HEADERS

class MusicCommands(app_commands.Group):
    @app_commands.command(name="play", description="Play a song")
    async def play(self, interaction: discord.Interaction):
        embed = discord.Embed(title=":x: Error", colour=discord.Colour(0xff0000),
                              description="Unfortunately, tack-oh does not support playing music in a voice channel.\n"
                                          "You might want to take a look at `FredBoat`, `Chip` or `Nero`.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="lyrics", description="Get the lyrics of a song")
    async def lyrics(self, interaction: discord.Interaction, search: str):
        # Defer at the start to avoid timeout because of slow API response
        await interaction.response.defer(ephemeral=True, thinking=True)
        r = requests.get(f"{SRA_BASE_URL}/lyrics?title={urllib.parse.quote(search)}", headers=SRA_REQUEST_HEADERS)
        try:
            song_lyrics = r.json()['lyrics']
            song_artist = r.json()['artist']
            song_title = r.json()['title']
            song_thumbnail = r.json()['thumbnail']
            song_link = r.json()['url']

            for chunk in textwrap.wrap(song_lyrics, 4096, replace_whitespace=False):
                embed = discord.Embed(title=song_title + " by " + song_artist, description=chunk,
                                      colour=discord.Colour(0x00ff00), url=song_link)
                embed.set_thumbnail(url=song_thumbnail)
                await interaction.followup.send(embed=embed, ephemeral=False)

        except KeyError or discord.errors.NotFound:
            embed = discord.Embed(title=":x: Error", colour=discord.Colour(0xff0000),
                                  description=f"Could not find lyrics for `{search}`!")
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    bot.tree.add_command(MusicCommands(name="music", description="Music commands"))
