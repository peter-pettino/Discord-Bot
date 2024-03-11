from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import nextcord

import nextwave
import datetime
from pytube import YouTube

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.node_connect())

    async def node_connect(self):
        await self.bot.wait_until_ready()
        await nextwave.NodePool.create_node(bot=self.bot, host="lavalink.devamop.in", port=80, password="DevamOP")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member != self.bot.user:
            if before.channel is not None and len(before.channel.members) == 1:
                vc = before.channel.guild.voice_client
                await vc.stop()
                await vc.disconnect()
        
    @commands.Cog.listener()
    async def on_nextwave_track_end(self, player: nextwave.Player, track: nextwave.Track, reason):
        interaction = player.interaction
        vc: player = interaction.guild.voice_client

        if vc.loop:
            return await vc.play(track)

        if not vc.queue.is_empty:
            next_song = vc.queue.get()
            await vc.play(next_song)

    @staticmethod
    async def check_voice_state(interaction: Interaction):
        if not getattr(interaction.user.voice, "channel", None):
            await interaction.send(embed=nextcord.Embed(description=f"🚫 You must be connected to a voice channel to use this command", color=0xED4245), ephemeral=True)
            return False
        elif not interaction.guild.voice_client:
            await interaction.send(embed=nextcord.Embed(description=f"🚫 The player must already be in a voice channel to use this command", color=0xED4245), ephemeral=True)
            return False
        elif interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.send(embed=nextcord.Embed(description=f"🚫 You must be connected to `{interaction.guild.voice_client.channel}` to use this command", color=0xED4245), ephemeral=True)
            return False
        else:
            return True

    @nextcord.slash_command(description="Play a track by providing a link or search query")
    async def play(self, interaction: Interaction, search: str = SlashOption(description="Enter YouTube link or search query")):
        try:
            search = await nextwave.YouTubeTrack.search(query=search, return_first=True)
        except IndexError:
            return await interaction.send(embed=nextcord.Embed(description=f"⚠️ `{search}` is not a valid link or search query", color=0xED4245), ephemeral=True)

        if not getattr(interaction.user.voice, "channel", None):
            return await interaction.send(embed=nextcord.Embed(description=f"🚫 You must be connected to a voice channel to use this command", color=0xED4245), ephemeral=True)
        elif not interaction.guild.voice_client:
            vc: nextwave.Player = await interaction.user.voice.channel.connect(cls=nextwave.Player)
        elif interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.send(embed=nextcord.Embed(description=f"🚫 You must be connected to `{interaction.guild.voice_client.channel}` to use this command", color=0xED4245), ephemeral=True)
        else:
            vc: nextwave.Player = interaction.guild.voice_client

        if vc.queue.is_empty and not vc.is_playing():
            await vc.play(search)
            embed = nextcord.Embed(title=f"Now Playing", color=0x1DB954)
        else:
            await vc.queue.put_wait(search)
            embed = nextcord.Embed(title=f"Added to the Queue", color=0x1DB954)

        thumbnail = YouTube(search.uri).thumbnail_url
        embed.add_field(name=f"{search.title}", value=f"Artist: `{search.author}`\nDuration: `{datetime.timedelta(seconds=search.length)}`\nURL: {search.uri}")
        embed.set_thumbnail(thumbnail)
        await interaction.send(embed=embed)

        vc.interaction = interaction
        setattr(vc, "loop", False)

    @nextcord.slash_command(description="Pause the current track")
    async def pause(self, interaction: Interaction):
        if not await self.check_voice_state(interaction):
            return
        vc: nextwave.Player = interaction.guild.voice_client

        if not vc.is_playing():
            await interaction.send(embed=nextcord.Embed(description=f"🚫 The player is currently not playing anything", color=0xED4245), ephemeral=True)
        elif vc.is_paused():
            await interaction.send(embed=nextcord.Embed(description=f"🚫 The player is currently paused", color=0xED4245), ephemeral=True)
        else:
            await vc.pause()
            await interaction.send(embed=nextcord.Embed(description=f"⏸️ Player has been paused", color=0x1DB954))

    @nextcord.slash_command(description="Resume the current track")
    async def resume(self, interaction: Interaction):
        if not await self.check_voice_state(interaction):
            return
        vc: nextwave.Player = interaction.guild.voice_client

        if not vc.is_playing():
            await interaction.send(embed=nextcord.Embed(description=f"🚫 The player is currently not playing anything", color=0xED4245), ephemeral=True)
        elif not vc.is_paused():
            await interaction.send(embed=nextcord.Embed(description=f"🚫 The player is currently playing", color=0xED4245), ephemeral=True)
        else:
            await vc.resume()
            await interaction.send(embed=nextcord.Embed(description=f"▶️ Player has been resumed", color=0x1DB954))

    @nextcord.slash_command(description="Skip the current track")
    async def skip(self, interaction: Interaction):
        if not await self.check_voice_state(interaction):
            return
        vc: nextwave.Player = interaction.guild.voice_client

        if not vc.is_playing():
            await interaction.send(embed=nextcord.Embed(description=f"🚫 The player is currently not playing anything", color=0xED4245), ephemeral=True)
        else:
            await interaction.send(embed=nextcord.Embed(description=f"⏭️ `{vc.track}` has been skipped", color=0x1DB954))
            setattr(vc, "loop", False)
            await vc.stop()

    @nextcord.slash_command(description=f"Disconnect the player from the current voice channel")
    async def disconnect(self, interaction: Interaction):
        if not await self.check_voice_state(interaction):
            return
        vc: nextwave.Player = interaction.guild.voice_client

        await interaction.send(embed=nextcord.Embed(description=f"⏏️ Player has been disconnected from `{interaction.guild.voice_client.channel}`", color=0x1DB954))
        await vc.stop()
        await vc.disconnect()
    
    @nextcord.slash_command(description=f"Loop the current track")
    async def loop(self, interaction: Interaction):
        if not await self.check_voice_state(interaction):
            return
        vc: nextwave.Player = interaction.guild.voice_client

        try:
            vc.loop ^= True
        except Exception:
            setattr(vc, "loop", False)

        if not vc.is_playing():
            await interaction.send(embed=nextcord.Embed(description=f"🚫 The player is currently not playing anything", color=0xED4245), ephemeral=True)
        elif vc.loop:
            await interaction.send(embed=nextcord.Embed(description=f"🔁 Loop is enabled for `{vc.track}`", color=0x1DB954))
        else:
            await interaction.send(embed=nextcord.Embed(description=f"🔁 Loop is disabled for `{vc.track}`", color=0x1DB954))
    
    @nextcord.slash_command(description=f"View the tracks currently in queue")
    async def queue(self, interaction: Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send(embed=nextcord.Embed(description=f"🚫 The player must already be in a voice channel to use this command", color=0xED4245), ephemeral=True)
        vc: nextwave.Player = interaction.guild.voice_client

        if vc.queue.is_empty:
            return await interaction.send(embed=nextcord.Embed(description="🚫 The queue is empty", color=0xED4245), ephemeral=True)
        
        embed = nextcord.Embed(title="Current Queue", color=0x1DB954)
        queue = vc.queue.copy()
        song_num = 0
        for song in queue:
            song_num += 1
            embed.add_field(name=f"{song_num}. {song}", value=f"Artist: `{song.author}`\nDuration: `{datetime.timedelta(seconds=song.length)}`\nURL: {song.uri}", inline=False)

        await interaction.send(embed=embed)
    
    @nextcord.slash_command(description=f"View the current track")
    async def nowplaying(self, interaction: Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send(embed=nextcord.Embed(description=f"🚫 The player must already be in a voice channel to use this command", color=0xED4245), ephemeral=True)
        vc: nextwave.Player = interaction.guild.voice_client

        if not vc.is_playing():
            return await interaction.send(embed=nextcord.Embed(description="🚫 The player is currently not playing anything", color=0xED4245), ephemeral=True)
        
        thumbnail = YouTube(vc.track.uri).thumbnail_url
        embed = nextcord.Embed(title=f"Now Playing", color=0x1DB954)
        embed.add_field(name=f"{vc.track.title}", value=f"Artist: `{vc.track.author}`\nDuration: `{datetime.timedelta(seconds=vc.track.length)}`\nURL: {vc.track.uri}")
        embed.set_thumbnail(thumbnail)
        await interaction.send(embed=embed)

def setup(bot):
    bot.add_cog(Music(bot))
