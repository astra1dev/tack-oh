import discord
from discord import app_commands
import requests
import asyncio
import random
from settings.settings import SRA_BASE_URL


class FunCommands(app_commands.Group):
    @app_commands.command(name="animal", description="Get a random image & fact about an animal")
    @app_commands.describe(animal="The desired animal")
    @app_commands.choices(animal=[app_commands.Choice(name="birb", value="birb"),
                                  app_commands.Choice(name="bird", value="bird"),
                                  app_commands.Choice(name="cat", value="cat"),
                                  app_commands.Choice(name="dog", value="dog"),
                                  app_commands.Choice(name="fox", value="fox"),
                                  app_commands.Choice(name="kangaroo", value="kangaroo"),
                                  app_commands.Choice(name="koala", value="koala"),
                                  app_commands.Choice(name="panda", value="panda"),
                                  app_commands.Choice(name="raccoon", value="racoon"),
                                  app_commands.Choice(name="red panda", value="red_panda"),
                                  app_commands.Choice(name="whale", value="whale")])
    async def fun_animal(self, interaction: discord.Interaction, animal: discord.app_commands.Choice[str]):
        url = f"{SRA_BASE_URL}/animal/{animal.value}"
        r = requests.get(url)
        fact = r.json()["fact"]
        img = r.json()["image"]
        embed = discord.Embed(title=f":nerd: Fact: {animal.name}", description=fact, colour=discord.Colour(0x00ff00))
        embed.set_image(url=img)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pfp", description="Get a user's profile picture")
    @app_commands.describe(user="The desired user")
    async def fun_pfp(self, interaction: discord.Interaction, user: discord.Member):
        pfp_url = user.display_avatar
        embed = discord.Embed(title=f":sunset: Profile picture: {user.name}", colour=discord.Colour(0x00ff00))
        embed.set_image(url=pfp_url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hack", description="Hack someone (real)")
    @app_commands.describe(user="The desired user")
    async def fun_hack(self, interaction: discord.Interaction, user: discord.Member):
        passwords = ["12345", "iloveyou", "qwerty", "hello", "password", "nothing", "john", "cat"]
        gifs = ["https://c.tenor.com/bhbciND-xRAAAAAC/tenor.gif",
                "https://c.tenor.com/IVOOvhdE4UMAAAAC/tenor.gif",
                "https://c.tenor.com/PhnZUt2djmkAAAAC/tenor.gif",
                "https://c.tenor.com/7ErCv53FBzIAAAAC/tenor.gif",
                "https://c.tenor.com/VrzXhtoSwcsAAAAC/tenor.gif",
                "https://c.tenor.com/19Ev9JAezGEAAAAC/tenor.gif",
                "https://c.tenor.com/5Xw3hRmmtsoAAAAC/tenor.gif"]
        token = requests.get(f"{SRA_BASE_URL}/bottoken").json()['token']

        embed = discord.Embed(title=f":space_invader: [1/8] Hacking {user.name}",
                              description="Finding discord login...", colour=discord.Colour(0x00ff00))
        embed.set_image(url=random.choice(gifs))
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await asyncio.sleep(4)

        embed = discord.Embed(title=f":space_invader: [2/8] Hacking {user.name}", colour=discord.Colour(0x00ff00),
                              description=f"Login credentials found!\n\nEmail: `{user.name}@gmail.com`"
                              f"\nPassword: `{random.choice(passwords)}`\nToken: `{token}`")
        embed.set_image(url=random.choice(gifs))
        await message.edit(embed=embed)
        await asyncio.sleep(4)

        embed = discord.Embed(title=f":space_invader: [3/8] Hacking {user.name}",
                              colour=discord.Colour(0x00ff00),
                              description=f"Injecting `RedLineStealer_v13.37.exe`...")
        embed.set_image(url=random.choice(gifs))
        await message.edit(embed=embed)
        await asyncio.sleep(4)

        embed = discord.Embed(title=f":space_invader: [4/8] Hacking {user.name}",
                              colour=discord.Colour(0x00ff00),
                              description=f"Accounts found:\n- Fortnite\n- Roblox\n- Minecraft\n\nAttempting to steal...")
        embed.set_image(url=random.choice(gifs))
        await message.edit(embed=embed)
        await asyncio.sleep(4)

        embed = discord.Embed(title=f":space_invader: [5/8] Hacking {user.name}",
                              colour=discord.Colour(0x00ff00),
                              description=f"Stolen:\n- 1870 V-Bucks\n- 69 Robux")
        embed.set_image(url=random.choice(gifs))
        await message.edit(embed=embed)
        await asyncio.sleep(4)

        embed = discord.Embed(title=f":space_invader: [6/8] Hacking {user.name}",
                              colour=discord.Colour(0x00ff00),
                              description=f"IP address: `187.0.0.69`")
        embed.set_image(url=random.choice(gifs))
        await message.edit(embed=embed)
        await asyncio.sleep(4)

        embed = discord.Embed(title=f":space_invader: [7/8] Hacking {user.name}",
                              colour=discord.Colour(0x00ff00),
                              description=f"Selling data to the government...")
        embed.set_image(url=random.choice(gifs))
        await message.edit(embed=embed)
        await asyncio.sleep(4)

        embed = discord.Embed(title=f":space_invader: Finished hacking {user.name}",
                              colour=discord.Colour(0x00ff00),
                              description=f"Cleaned traces and self-destructed!")
        embed.set_image(url=random.choice(gifs))
        await message.edit(embed=embed)

    @app_commands.command(name="8ball", description="Ask the 8ball a question")
    @app_commands.describe(question="The question you want to ask")
    async def eightball(self, interaction: discord.Interaction, question: str):
        result = requests.get("https://api.popcat.xyz/8ball").json()['answer']
        embed = discord.Embed(title=":8ball: Ask the 8ball", colour=discord.Colour(0x00ff00))
        embed.add_field(name=":thinking: Question", value=f"{question}", inline=False)
        embed.add_field(name=":bulb: Answer", value=f"{result}", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="emojify", description="Turn a text into emojis")
    async def emojify(self, interaction: discord.Interaction, text: str):
        emojis = []
        for i in text.lower():
            # if a number is in the text, convert it to the corresponding emoji
            if i.isdecimal():
                num2emo = {'0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five',
                           '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'}
                emojis.append(":" + num2emo.get(i) + ":")

            # if a letter is in the text, convert it to the corresponding emoji
            elif i.isalpha():
                emojis.append(":regional_indicator_" + i + ":")

            # if any other symbol is in the text, add it (no emoji)
            else:
                emojis.append(i)

        await interaction.response.send_message(' '.join(emojis))

    @app_commands.command(name="joke", description="Tell a joke")
    async def joke(self, interaction: discord.Interaction):
        joke_text = requests.get(f"{SRA_BASE_URL}/joke").json()['joke']
        embed = discord.Embed(title=":joy: Random Joke", description=joke_text, colour=discord.Colour(0x00ff00))
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    bot.tree.add_command(FunCommands(name="fun", description="Fun commands"))
