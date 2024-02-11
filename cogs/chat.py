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
                await message.channel.trigger_typing()
                
                prompt = " ".join(word for word in message.content.split() if word != f"<@{self.bot.user.id}>")

                payload = {
                    "model": "nousresearch/nous-capybara-7b:free",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 1
                }

                headers = {"Authorization": f"Bearer {os.environ.get('CHATAPI')}"}

                try:
                    async with session.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers, timeout=30) as resp:
                        response = await resp.json()
                        await message.channel.send(response["choices"][0]["message"]["content"])
                except Exception:
                    await message.reply("Sorry, I'm taking too long to respond, try again soon.")

def setup(bot):
    bot.add_cog(Chat(bot))
