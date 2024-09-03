import discord
from discord import app_commands
import peewee
import random
from datetime import datetime, timedelta

db = peewee.SqliteDatabase("economy.db")
currency = ":taco:"


class Account(peewee.Model):
    guild_id: str = peewee.CharField(max_length=255, primary_key=True)
    user_id: str = peewee.CharField(max_length=255)
    amount: int = peewee.IntegerField()

    class Meta:
        database = db
        without_rowid = True

    @staticmethod
    def fetch(interaction):
        try:
            account = Account.get(Account.user_id == interaction.user.id, Account.guild_id == interaction.guild.id)
        except peewee.DoesNotExist:
            account = Account.create(user_id=interaction.user.id, guild_id=interaction.guild.id, amount=0)
        return account

    @staticmethod
    async def win_message(interaction, account):
        embed = discord.Embed(title=":coin: Coinflip", colour=discord.Colour(0x00ff00),
                              description=f"You won! You now have {account.amount} {currency}.")
        await interaction.response.send_message(embed=embed)

    @staticmethod
    async def lose_message(interaction, account):
        embed = discord.Embed(title=":coin: Coinflip", colour=discord.Colour(0x00ff00),
                              description=f"You lost! You now have {account.amount} {currency}.")
        await interaction.response.send_message(embed=embed)


class EconomyCommands(app_commands.Group):
    @app_commands.command(name="balance", description="Get your balance")
    async def economy_balance(self, interaction):
        account = Account.fetch(interaction)
        embed = discord.Embed(title=":chart_with_upwards_trend: Balance", colour=discord.Colour(0x00ff00),
                              description=f"You have {account.amount} {currency}.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="daily", description="Claim your daily reward")
    @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id, i.user.id))
    async def economy_daily(self, interaction: discord.Interaction):
        account = Account.fetch(interaction)
        account.amount += random.randrange(500, 2000)
        account.save()
        embed = discord.Embed(title=":calendar: Daily Reward", colour=discord.Colour(0x00ff00),
                              description=f"You have claimed your daily reward!\nYou now have {account.amount} {currency}")
        await interaction.response.send_message(embed=embed)

    @economy_daily.error
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            ts = int((datetime.now() + timedelta(seconds=error.retry_after)).timestamp())
            embed = discord.Embed(title=":x: Error", colour=discord.Colour(0xff0000),
                                  description=f"You have already claimed your daily reward!\nTry again <t:{ts}:R>")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error

    @app_commands.command(name="leaderboard", description="Get the leaderboard")
    async def economy_leaderboard(self, interaction: discord.Interaction):
        pass

    @app_commands.command(name="pay", description="Pay someone")
    async def economy_pay(self, interaction: discord.Interaction):
        pass

    @app_commands.command(name="shop", description="Get the shop")
    async def economy_shop(self, interaction: discord.Interaction):
        pass

    @app_commands.command(name="slots", description="Play slots")
    async def economy_slots(self, interaction: discord.Interaction):
        pass

    @app_commands.command(name="coinflip", description="Flip a coin")
    @app_commands.describe(amount="The amount of coins you want to bet", choice="Heads or tails")
    @app_commands.choices(choice=[app_commands.Choice(name="heads", value="heads"),
                                  app_commands.Choice(name="tails", value="tails")])
    async def coinflip(self, interaction: discord.Interaction, amount: app_commands.Range[int, 10, 100000],
                       choice: str):
        account = Account.fetch(interaction)

        if amount > account.amount:
            embed = discord.Embed(title=":x: Error", colour=discord.Colour(0xff0000),
                                  description=f"You do not have enough {currency} to do that!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        heads = random.randint(0, 1)
        if heads and choice == "heads":
            account.amount += amount
            account.save()
            await Account.win_message(interaction, account)
        elif not heads and choice == "tails":
            account.amount += amount
            account.save()
            await Account.win_message(interaction, account)
        else:
            account.amount -= amount
            account.save()
            await Account.lose_message(interaction, account)


async def setup(bot):
    db.create_tables([Account])
    bot.tree.add_command(EconomyCommands(name="economy", description="Economy commands"))
