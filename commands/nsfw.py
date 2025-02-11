import discord
from discord import app_commands
from settings.settings import NSFW_ALLOWED
import requests


async def is_channel_nsfw(interaction: discord.Interaction) -> bool:
    """
    Checks if the interaction channel is marked as NSFW, and sends an error message if it is not.
    """
    if not interaction.channel.is_nsfw():
        embed = discord.Embed(title=":x: Error", colour=discord.Colour(0xff0000),
                              description=f"{interaction.channel.mention} is not an NSFW channel!")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False
    return True


class NsfwCommands(app_commands.Group):
    @app_commands.command(name="waifu", description="Get a waifu (NSFW)")
    @app_commands.describe(category="The category of the waifu")
    @app_commands.choices(category=[app_commands.Choice(name="random", value="waifu"),
                                    app_commands.Choice(name="neko", value="neko"),
                                    app_commands.Choice(name="trap", value="trap"),
                                    app_commands.Choice(name="blowjob", value="blowjob")])
    async def waifu(self, interaction: discord.Interaction, category: discord.app_commands.Choice[str]) -> None:
        """
        Fetches a waifu image from the waifu.pics API and sends it in an embed if the channel is marked as NSFW
        """
        if not await is_channel_nsfw(interaction):
            return
        r = requests.get("https://api.waifu.pics/nsfw/" + category.value)
        url = r.json()["url"]
        embed = discord.Embed(title=f":hot_face: Waifu: {category.name}", url=url, colour=discord.Colour(0x00ff00))
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="porn", description="lol")
    @app_commands.describe(query="The query you want to get content for (leave empty to see categories)")
    async def porn(self, interaction: discord.Interaction, query: str = None) -> None:
        """
        Fetches a porn image from the nekobot API and sends it in an embed if the channel is marked as NSFW
        """
        if not await is_channel_nsfw(interaction):
            return
        # If no query is provided, show the categories
        if query is None:
            r = requests.get("https://nekobot.xyz/api/image")
            stats = r.json()['stats']
            topic_list = ""
            for name, amount in stats.items():
                topic_list = topic_list + name + ": " + str(amount) + ", "
            embed = discord.Embed(title=":peach: Porn Stats / Categories", colour=discord.Colour(0xff0000),
                                  description=topic_list, url="https://nekobot.xyz/api/image")
            embed.set_footer(text="Using the Nekobot API", icon_url="https://nekobot.xyz/favicon-32x32.png")
            await interaction.response.send_message(embed=embed)
        # If a query is provided, fetch the image
        else:
            r = requests.get("https://nekobot.xyz/api/image?type=" + query)
            url = r.json()['message']
            embed = discord.Embed(title=f":peach: Porn: {query}", url=url, colour=discord.Colour(0x00ff00))
            embed.set_image(url=url)
            await interaction.response.send_message(embed=embed)


async def setup(bot):
    """
    This global function is defined as the entry point on what to do when the NSFW extension is loaded.
    It adds the NSFW commands to the bot's command tree.
    """
    if NSFW_ALLOWED:
        bot.tree.add_command(NsfwCommands(name="nsfw", description="NSFW commands"))
