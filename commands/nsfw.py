import discord
from discord import app_commands
from settings import NSFW_ALLOWED
import requests


class NsfwCommands(app_commands.Group):
    @app_commands.command(name="waifu", description="Get a waifu (NSFW)")
    @app_commands.describe(category="The category of the waifu")
    @app_commands.choices(category=[app_commands.Choice(name="random", value="waifu"),
                                    app_commands.Choice(name="neko", value="neko"),
                                    app_commands.Choice(name="trap", value="trap"),
                                    app_commands.Choice(name="blowjob", value="blowjob")])
    async def waifu(self, interaction: discord.Interaction, category: discord.app_commands.Choice[str]):
        if not interaction.channel.is_nsfw():
            embed = discord.Embed(title=":x: Error",
                                  description=f"{interaction.channel.mention} is not an NSFW channel!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        r = requests.get("https://api.waifu.pics/nsfw/" + category.value)
        url = r.json()["url"]
        embed = discord.Embed(title=f"Waifu: {category.name}", url=url, colour=discord.Colour(0x00ff00))
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="porn", description="lol")
    @app_commands.describe(query="The query you want to get content for (leave empty to see categories)")
    async def porn(self, interaction: discord.Interaction, query: str = None):
        if not interaction.channel.is_nsfw():
            embed = discord.Embed(title=":x: Error",
                                  description=f"{interaction.channel.mention} is not an NSFW channel!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if query is None:
            r = requests.get("https://nekobot.xyz/api/image")
            stats = r.json()['stats']
            topic_list = ""
            for name, amount in stats.items():
                topic_list = topic_list + name + ": " + str(amount) + ", "
            embed = discord.Embed(title=":peach: Porn Stats / Categories",
                                  description=topic_list)
            await interaction.response.send_message(embed=embed)
        else:
            r = requests.get("https://nekobot.xyz/api/image?type=" + query)
            embed = discord.Embed(title=f":peach: Porn: {query}", colour=discord.Colour(0x00ff00))
            embed.set_image(url=r.json()['message'])
            await interaction.response.send_message(embed=embed)


async def setup(bot):
    if NSFW_ALLOWED:
        bot.tree.add_command(NsfwCommands(name="nsfw", description="NSFW commands"))
