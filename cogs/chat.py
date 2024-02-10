from nextcord.ext import commands
import os

import aiohttp

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user.mentioned_in(message):
            async with aiohttp.ClientSession() as session:
                prompt = " ".join(word for word in message.content.split() if word != f"<@{self.bot.user.id}>")

                payload = {
                    "model": "mistralai/mistral-7b-instruct:free",
                    "messages": [{"role": "user", "content": prompt}]
                }

                headers = {"Authorization": f"Bearer {os.environ.get('CHATAPI')}"}
        
                async with session.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers) as resp:
                    response = await resp.json()
                    await message.channel.send(response["choices"][0]["message"]["content"])

def setup(bot):
    bot.add_cog(Chat(bot))
