from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import nextcord
import os

import aiohttp
from datetime import datetime

class Weather(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Retrieve current weather information for a specific location")
    async def weather(self, interaction: Interaction, location: str = SlashOption(description="Enter a location")):

        url = "https://api.weatherapi.com/v1/current.json"
        params = {
            "key": os.environ.get("WEATHERAPI"),
            "q": location
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as res:
                
                data = await res.json()

                try:
                    name = data["location"]["name"]
                except KeyError:
                    return await interaction.send(embed=nextcord.Embed(description=f"⚠️ `{location}` is not a valid location", color=0xED4245), ephemeral=True)
                
                country = data["location"]["country"]
                localtime = data["location"]["localtime"]
                last_updated_epoch = data["current"]["last_updated_epoch"]
                is_day = data["current"]["is_day"]
                condition = data["current"]["condition"]["text"]
                image_url = "http:" + data["current"]["condition"]["icon"]
                temp_c = data["current"]["temp_c"]
                temp_f = data["current"]["temp_f"]
                wind_kph = data["current"]["wind_kph"]
                wind_mph = data["current"]["wind_mph"]
                precip_mm = data["current"]["precip_mm"]
                precip_in = data["current"]["precip_in"]
                humidity = data["current"]["humidity"]
                uv = data["current"]["uv"]

                embed = nextcord.Embed(title=f"Weather for {name}, {country}", description=f"The condition in `{name}` is `{condition}`\nLocal time: `{localtime}`", timestamp=datetime.fromtimestamp(last_updated_epoch))
                embed.add_field(name="Temperature", value=f"{temp_c} °C | {temp_f} °F")
                embed.add_field(name="Humidity", value=f"{humidity}%")
                embed.add_field(name="UV Index", value=f"{uv}")
                embed.add_field(name="Wind", value=f"{wind_kph} KPH | {wind_mph} MPH")
                embed.add_field(name="Precipitation", value=f"{precip_mm} mm | {precip_in} in")
                embed.set_thumbnail(url=image_url)
                embed.set_footer(text="Last Updated")
                if is_day == 1:
                    embed.color = 0xF1C40F
                else:
                    embed.color = 0x3498DB

                await interaction.send(embed=embed)

def setup(bot):
    bot.add_cog(Weather(bot))
