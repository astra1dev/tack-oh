# make examples for buttons, feedback (modals) and other stuff
# https://www.youtube.com/watch?v=dxcSt9Ip63w
import discord
from discord import app_commands


class SimpleView(discord.ui.View):
    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self) -> None:
        await self.message.channel.send("Timed out!", ephemeral=True)
        await self.disable_all_items()

    @discord.ui.button(label="Hello", style=discord.ButtonStyle.success)
    async def hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("World")

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling")


@app_commands.command()
async def button(ctx):
    view = SimpleView(timeout=10)
    # button = discord.ui.Button(label="Click me")
    # view.add_item(button)
    message = await ctx.send("Click the button!", view=view)
    view.message = message
    await view.wait()


class FeedbackModal(discord.ui.Modal, title="Send us your feedback"):
    fb_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Title",
        required=False,
        placeholder="Give your feedback a title"
    )

    message = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Message",
        required=True,
        max_length=500,
        placeholder="Write your feedback here"
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(1201498462471077948) # feedback channel here
        embed = discord.Embed(title="New Feedback", description=self.message.value)
        embed.set_author(name=self.user.nick)
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Thank you, {self.user.mention}!", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction):
        pass


@app_commands.command()
async def feedback(interaction: discord.Interaction):
    feedback_modal = FeedbackModal()
    feedback_modal.user = interaction.user
    await interaction.response.send_modal(feedback_modal)


class SurveyView(discord.ui.View):
    answer1 = None
    answer2 = None

    @discord.ui.select(
        placeholder="What is your age?",
        options=[
            discord.SelectOption(label="1", value="1"),
            discord.SelectOption(label="2", value="2"),
            discord.SelectOption(label="3", value="3"),
        ],
        max_values=1
    )
    async def select_age(self, interaction: discord.Interaction, select_item : discord.ui.Select):
        self.answer1 = select_item.values


@app_commands.command()
async def survey(interaction: discord.Interaction):
    view = SurveyView()
    await interaction.response.send(view=view)
