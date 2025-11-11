import discord
from discord import app_commands
import urllib
from urllib import parse
from settings.settings import SRA_BASE_URL


class ImageCommands(app_commands.Group):
    @app_commands.command(name="effect", description="Apply an effect to the pfp of a user")
    @app_commands.describe(effect="The desired effect", member="The desired user")
    @app_commands.choices(effect=[app_commands.Choice(name="circle", value="circle"),
                                  app_commands.Choice(name="comrade", value="comrade"),
                                  app_commands.Choice(name="gay", value="gay"),
                                  app_commands.Choice(name="glass", value="glass"),
                                  app_commands.Choice(name="heart", value="heart"),
                                  app_commands.Choice(name="horny license", value="horny"),
                                  app_commands.Choice(name="jail", value="jail"),
                                  app_commands.Choice(name="lgbt", value="lgbt"),
                                  app_commands.Choice(name="lied", value="lied"),
                                  app_commands.Choice(name="lolice", value="lolice"),
                                  app_commands.Choice(name="mission passed", value="passed"),
                                  app_commands.Choice(name="simp card", value="simpcard"),
                                  app_commands.Choice(name="triggered", value="triggered"),
                                  app_commands.Choice(name="wasted", value="wasted"),])
    async def effect(self, interaction: discord.Interaction, member: discord.Member,
                     effect: discord.app_commands.Choice[str]):
        pfp_url = member.display_avatar

        try:
            # /canvas/overlay endpoints
            if effect.value in ["comrade", "gay", "glass", "jail", "passed", "triggered", "wasted"]:
                url = f"{SRA_BASE_URL}/canvas/overlay/{effect.value}?avatar={str(pfp_url)}"
                embed = discord.Embed(title="✨ ImageEffect: " + effect.name, colour=discord.Colour(0x00ff00),
                                      description=member.mention)
                embed.set_image(url=url)
                await interaction.response.send_message(embed=embed)

            # /canvas/misc endpoints
            elif effect.value in ["circle", "heart", "horny", "lgbt", "lolice", "simpcard"]:
                url = f"{SRA_BASE_URL}/canvas/misc/{effect.value}?avatar={str(pfp_url)}"
                embed = discord.Embed(title="✨ ImageEffect: " + effect.name, colour=discord.Colour(0x00ff00),
                                      description=member.mention)
                embed.set_image(url=url)
                await interaction.response.send_message(embed=embed)

            elif effect.value == "lied":
                url = f"{SRA_BASE_URL}/canvas/misc/{effect.value}?username={member.display_name}&avatar={str(pfp_url)}"
                embed = discord.Embed(title="✨ ImageEffect: " + effect.name, colour=discord.Colour(0x00ff00),
                                      description=member.mention)
                embed.set_image(url=url)
                await interaction.response.send_message(embed=embed)

        except KeyError:
            embed = discord.Embed(title=":x: Error", colour=discord.Colour(0xff0000),
                                  description="Image could not be created!")
            await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="filter", description="Apply a simple filter to the pfp of a user")
    @app_commands.describe(filter="The desired filter", member="The desired user")
    @app_commands.choices(filter=[app_commands.Choice(name="blue", value="blue"),
                                  app_commands.Choice(name="blurple", value="blurple"),
                                  app_commands.Choice(name="blurple2", value="blurple2"),
                                  app_commands.Choice(name="green", value="green"),
                                  app_commands.Choice(name="red", value="red"),
                                  app_commands.Choice(name="brightness", value="brightness"),
                                  app_commands.Choice(name="greyscale", value="greyscale"),
                                  app_commands.Choice(name="invert", value="invert"),
                                  app_commands.Choice(name="invert + greyscale", value="invertgreyscale"),
                                  app_commands.Choice(name="pixelate", value="pixelate"),
                                  app_commands.Choice(name="sepia", value="sepia"),
                                  app_commands.Choice(name="threshold", value="threshold"),])
    async def filter(self, interaction: discord.Interaction, member: discord.Member,
                     filter: discord.app_commands.Choice[str]):
        pfp_url = member.display_avatar
        try:
            url = f"{SRA_BASE_URL}/canvas/filter/{filter.value}?avatar={str(pfp_url)}"
            embed = discord.Embed(title="✨ ImageFilter: " + filter.name, colour=discord.Colour(0x00ff00),
                                  description=member.mention)
            embed.set_image(url=url)
            await interaction.response.send_message(embed=embed)
        except KeyError:
            embed = discord.Embed(title=":x: Error", colour=discord.Colour(0xff0000),
                                  description="Image could not be created!")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="compose", description="Create meme-y images")
    @app_commands.describe(effect="The desired effect", member="The desired user", text="The text to put on the image")
    @app_commands.choices(effect=[app_commands.Choice(name="youtube comment", value="youtube-comment"),
                                  app_commands.Choice(name="twitter post", value="tweet"),
                                  app_commands.Choice(name="oh no it's stupid", value="its-so-stupid")])
    async def compose(self, interaction: discord.Interaction, member: discord.Member,
                      effect: discord.app_commands.Choice[str], text: str):
        text = urllib.parse.quote(text)
        name = urllib.parse.quote(member.name)
        display_name = urllib.parse.quote(member.display_name)

        if effect.value == "youtube-comment":
            url = (f"{SRA_BASE_URL}/canvas/misc/{effect.value}?username={name}&comment={text}"
                   f"&avatar={member.display_avatar}")
            embed = discord.Embed(title="✨ ImageCompose: " + effect.name, colour=discord.Colour(0x00ff00),
                                  description=member.mention)
            embed.set_image(url=url)
            await interaction.response.send_message(embed=embed)

        elif effect.value == "tweet":
            url = (f"{SRA_BASE_URL}/canvas/misc/{effect.value}?username={name}&displayname={display_name}"
                   f"&comment={text}&avatar={member.display_avatar}")
            embed = discord.Embed(title="✨ ImageCompose: " + effect.name, colour=discord.Colour(0x00ff00),
                                  description=member.mention)
            embed.set_image(url=url)
            await interaction.response.send_message(embed=embed)

        elif effect.value == "its-so-stupid":
            url = f"{SRA_BASE_URL}/canvas/misc/{effect.value}?dog={text}&avatar={member.display_avatar}"
            embed = discord.Embed(title="✨ ImageCompose: " + effect.name, colour=discord.Colour(0x00ff00),
                                  description=member.mention)
            embed.set_image(url=url)
            await interaction.response.send_message(embed=embed)


async def setup(bot):
    bot.tree.add_command(ImageCommands(name="image", description="Image commands"))
