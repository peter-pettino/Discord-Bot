from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import nextcord

class Buttons(nextcord.ui.View):
    def __init__(self, player1, player2):
        super().__init__(timeout=30)
        self.player1 = player1
        self.player2 = player2
        self.choice1 = None
        self.choice2 = None

    @nextcord.ui.button(label="👊 Rock", style=nextcord.ButtonStyle.blurple)
    async def rock(self, button: nextcord.ui.Button, interaction: Interaction):
        if interaction.user == self.player1:
            self.choice1 = "👊"
        elif interaction.user == self.player2:
            self.choice2 = "👊"
        
        if self.choice1 is not None and self.choice2 is not None:
            self.stop()

    @nextcord.ui.button(label="✋ Paper", style=nextcord.ButtonStyle.blurple)
    async def paper(self, button: nextcord.ui.Button, interaction: Interaction):
        if interaction.user == self.player1:
            self.choice1 = "✋"
        elif (interaction.user == self.player2):
            self.choice2 = "✋"
        
        if self.choice1 is not None and self.choice2 is not None:
            self.stop()

    @nextcord.ui.button(label="✌️ Scissors", style=nextcord.ButtonStyle.blurple)
    async def scissors(self, button: nextcord.ui.Button, interaction: Interaction):
        if interaction.user == self.player1:
            self.choice1 = "✌️"
        elif interaction.user == self.player2:
            self.choice2 = "✌️"

        if self.choice1 is not None and self.choice2 is not None:
            self.stop()

class RPS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Challenge a user to a game of Rock Paper Scissors")
    async def rps(self, interaction: Interaction, opponent: nextcord.Member = SlashOption(description="Enter user to challenge")):
        user = interaction.user.guild.get_member(opponent.id)
        if user == None:
            return await interaction.send(embed=nextcord.Embed(description=f"❌ `{opponent}` must be in the same server", color=0xED4245), ephemeral=True)
        elif interaction.user == opponent:
            return await interaction.send(embed=nextcord.Embed(description=f"❌ You cannot challenge yourself", color=0xED4245), ephemeral=True)
        elif opponent.bot:
            return await interaction.send(embed=nextcord.Embed(description=f"❌ You cannot challenge bots", color=0xED4245), ephemeral=True)

        embed = nextcord.Embed(title="Rock Paper Scissors", description=f"🎲 {interaction.user.mention} has challenged you to a game of **Rock Paper Scissors**", color=0xF1C40F)
        embed.set_footer(text=f"{interaction.user} vs {opponent}")
        view = Buttons(interaction.user, opponent)
        message = await interaction.send(f"{interaction.user.mention} {opponent.mention}", embed=embed, view=view)
        await view.wait()

        outcomes = {
            ("👊", "✌️"): view.player1,
            ("✋", "👊"): view.player1,
            ("✌️", "✋"): view.player1,
            ("✌️", "👊"): view.player2,
            ("👊", "✋"): view.player2,
            ("✋", "✌️"): view.player2,
        }

        choice1= view.choice1 if view.choice1 is not None else "❓"
        choice2= view.choice2 if view.choice2 is not None else "❓"
        embed.add_field(name=view.player1, value=choice1)
        embed.add_field(name="VS", value="⚡")
        embed.add_field(name=view.player2, value=choice2)
        
        if view.choice1 == view.choice2:
            embed.description = f"😱 Game ended in a draw"
            return await message.edit(embed=embed, view=None)
        elif view.choice1 == None or view.choice2 == None:
            embed.description = f"😴 {view.player1.mention if view.choice1 is None else view.player2.mention} did not respond in time"
            return await message.edit(embed=embed, view=None)
        else:
            winner = outcomes[(view.choice1, view.choice2)]
            embed.description = f"🥳 {winner.mention} has won the game"
            await message.edit(embed=embed, view=None)

def setup(bot):
    bot.add_cog(RPS(bot))
