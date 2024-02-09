from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import nextcord
from keep_alive import keep_alive
import os

bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())
bot.remove_command("help")
keep_alive()

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord")

for fn in os.listdir("./cogs"):
    if fn.endswith(".py"):
        bot.load_extension(f"cogs.{fn[:-3]}")

@bot.slash_command(description="Reloads an extension")
async def reload(interaction: Interaction, extension: str = SlashOption(description="Enter extension name")):
    bot.reload_extension(f"cogs.{extension}")
    await interaction.send(f"Reloaded `{extension}.py`")

bot.run(os.environ.get("TOKEN"))