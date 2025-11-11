import animec
import discord
from discord import app_commands
import requests
from settings.settings import SRA_BASE_URL

class AnimeCommands(app_commands.Group):
    @app_commands.command(name="search", description="Search for an anime")
    @app_commands.describe(query="The anime you want to search")
    async def search(self, interaction: discord.Interaction, query: str):
        try:
            get_anime = animec.Anime(query)
        except animec.errors.NoResultFound:
            embed = discord.Embed(title=":x: Error", colour=discord.Colour(0xff0000),
                                  description="No anime was found for the search query!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(title=f":goblin: Anime: {get_anime.title_english}", url=get_anime.url,
                              description=get_anime.description[:200] + "...", colour=discord.Colour(0x00ff00))
        embed.add_field(name="Episodes", value=str(get_anime.episodes))
        embed.add_field(name="Rating", value=str(get_anime.rating))
        embed.add_field(name="Broadcast", value=str(get_anime.broadcast))
        embed.add_field(name="Status", value=str(get_anime.status))
        embed.add_field(name="Type", value=str(get_anime.type))
        embed.add_field(name="NSFW", value=str(get_anime.is_nsfw()))
        embed.set_thumbnail(url=get_anime.poster)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="news", description="Get the latest anime news")
    async def news(self, interaction: discord.Interaction):
        news = animec.Aninews(3)
        embed = discord.Embed(title=":newspaper: Latest Anime News", colour=discord.Colour(0x00ff00))
        embed.set_thumbnail(url=news.images[0])
        for i in range(3):
            embed.add_field(name=f"{i + 1}) {news.titles[i]}",
                            value=f"{news.description[i][:200]}...\n[Read more]({news.links[i]})", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="gif", description="Get an anime gif")
    @app_commands.describe(topic="The topic you want to search")
    @app_commands.choices(topic=[app_commands.Choice(name="nom", value="nom"),
                                 app_commands.Choice(name="poke", value="poke"),
                                 app_commands.Choice(name="cry", value="cry"),
                                 app_commands.Choice(name="kiss", value="kiss"),
                                 app_commands.Choice(name="pat", value="pat"),
                                 app_commands.Choice(name="hug", value="hug"),
                                 app_commands.Choice(name="wink", value="wink"),
                                 app_commands.Choice(name="face palm", value="face-palm"),
                                 # app_commands.Choice(name="quote", value="quote")
                                ])
    async def gif(self, interaction: discord.Interaction, topic: discord.app_commands.Choice[str]):
        url = requests.get(f"{SRA_BASE_URL}/animu/{topic.value}").json()['link']
        embed = discord.Embed(title=f":goblin: Anime GIF: {topic.name}", url=url, colour=discord.Colour(0x00ff00))
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="waifu", description="Get a waifu")
    @app_commands.describe(category="The category of the waifu")
    # Some choices need to be commented out because discord only allows 25 choices, and there are 31 categories.
    @app_commands.choices(category=[app_commands.Choice(name="random", value="waifu"),
                                    app_commands.Choice(name="neko", value="neko"),
                                    # app_commands.Choice(name="shinobu", value="shinobu"),
                                    # app_commands.Choice(name="megumin", value="megumin"),
                                    app_commands.Choice(name="bully", value="bully"),
                                    # app_commands.Choice(name="cuddle", value="cuddle"),
                                    app_commands.Choice(name="cry", value="cry"),
                                    app_commands.Choice(name="hug", value="hug"),
                                    # app_commands.Choice(name="awoo", value="awoo"),
                                    app_commands.Choice(name="kiss", value="kiss"),
                                    app_commands.Choice(name="lick", value="lick"),
                                    app_commands.Choice(name="pat", value="pat"),
                                    # app_commands.Choice(name="smug", value="smug"),
                                    app_commands.Choice(name="bonk", value="bonk"),
                                    app_commands.Choice(name="yeet", value="yeet"),
                                    app_commands.Choice(name="blush", value="blush"),
                                    app_commands.Choice(name="smile", value="smile"),
                                    app_commands.Choice(name="wave", value="wave"),
                                    app_commands.Choice(name="highfive", value="highfive"),
                                    app_commands.Choice(name="handhold", value="handhold"),
                                    app_commands.Choice(name="nom", value="nom"),
                                    app_commands.Choice(name="bite", value="bite"),
                                    # app_commands.Choice(name="glomp", value="glomp"),
                                    app_commands.Choice(name="slap", value="slap"),
                                    app_commands.Choice(name="kill", value="kill"),
                                    app_commands.Choice(name="kick", value="kick"),
                                    app_commands.Choice(name="happy", value="happy"),
                                    app_commands.Choice(name="wink", value="wink"),
                                    # app_commands.Choice(name="poke", value="poke"),
                                    app_commands.Choice(name="dance", value="dance"),
                                    # app_commands.Choice(name="cringe", value="cringe"),
                                    ])
    async def waifu(self, interaction: discord.Interaction, category: discord.app_commands.Choice[str]):
        r = requests.get("https://api.waifu.pics/sfw/" + category.value)
        url = r.json()["url"]
        embed = discord.Embed(title=f":princess: Waifu: {category.name}", url=url, colour=discord.Colour(0x00ff00))
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    bot.tree.add_command(AnimeCommands(name="anime", description="Anime commands"))
