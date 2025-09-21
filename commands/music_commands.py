import asyncio
import requests
import discord
import random

from discord.ext import commands
import yt_dlp
from commands.song_history import SongHistory

#Configurar yt-dlp
ydl_format_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
}
ffmpeg_opts = {
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ydl_format_opts)

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.song_queue = []
        self.song_history = SongHistory()
        self.is_playing = False
        self._manual_skip = False

    @commands.command()
    async def join(self, ctx):
        """Join the voice channel."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client and ctx.voice_client.is_connected():
                await ctx.send("I am already connected to a voice channel.")
            else:
                self.voice_client = await channel.connect()
                await ctx.send(f"Connected to {channel.name}")
        else:
            await ctx.send("You are not connected to a voice channel.")

    @commands.command()
    async def play(self, ctx, *, search: str = None):
        """Play a song or add itt to the queue."""
        if not ctx.voice_client or not self.voice_client.is_connected():
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                self.voice_client = await channel.connect()
                await ctx.send(f"Connected to {channel.name}")
            else:
                await ctx.send("You are not connected to a voice channel.")
                return

        # Check if the bot is paused
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed the song.")
            return

        # If no search term is provided, return an error message
        if not search:
            await ctx.send("Please provide a song to play.")
            return

        try:
            await ctx.send(f"Searching... {search}")
            # Use ytsearch to search for the song
            search_result = await self.get_youtube_info(search)
            if not search_result or 'entries' not in search_result or len(search_result['entries']) == 0:
                await ctx.send("No results found.")
                return

            # Get the first result
            info = search_result['entries'][0]
            song = {"title": info['title'], "url": info['url']}

            #Add the song to the history
            self.song_history.add_song(song)

            # Check if is there a song playing
            if self.is_playing:
                self.song_queue.append(song)
                await ctx.send(f"Added to queue: {song['title']}")
            else:
                self.is_playing = True
                self.voice_client.play(
                    discord.FFmpegPCMAudio(song['url'], **ffmpeg_opts),
                    after=lambda e: asyncio.run_coroutine_threadsafe(self.next(ctx), self.bot.loop).result()
                )
                await ctx.send(f"Now playing: {info['title']}")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")

    #Play next song in the queue
    @commands.command()
    async def next(self, ctx):
        print(f"was manual: {self._manual_skip}")
        print(f"is playing: {self.is_playing}")
        print(f"index is {self.song_history.current_index}")
        """Skip the current song."""
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            await ctx.send("The bot is not connected to a voice channel.")
            return

        # Set manual skip flag before stopping playback
        self._manual_skip = True

        if ctx.voice_client.is_playing():
            await ctx.voice_client.stop()

        # Get current index before moving to next
        current_index = self.song_history.current_index

        # Get the next song from the queue
        if current_index < len(self.song_history.history) - 1:
            next_song = self.song_history.get_next_song()
        elif self.song_queue:
            next_song = self.song_queue.pop(0)
            self.song_history.add_song(next_song)
        elif len(self.song_history.history) > 0:
            self.song_history.current_index = -1 #Reset to beginning
            next_song = self.song_history.get_next_song()
        else:
            await ctx.send("No more songs in the queue.")
            self.is_playing = False
            self._manual_skip = False
            return


        try:
            self.is_playing = True
            ctx.voice_client.play(
                discord.FFmpegPCMAudio(next_song['url'], **ffmpeg_opts),
                after=lambda e: asyncio.run_coroutine_threadsafe(self._after_song(ctx), self.bot.loop).result()
            )
            await ctx.send(f"Now playing: {next_song['title']}")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
            self.is_playing = False

        self._manual_skip = False

        # Previous song on the queue
    @commands.command()
    async def previous(self, ctx):
        print(f"was manual: {self._manual_skip}")
        print(f"is playing: {self.is_playing}")
        print(f"index is {self.song_history.current_index}")

        """Play the previous song."""
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            await ctx.send("The bot is not connected to a voice channel.")
            return

        # Set manual skip flag before stopping playback
        self._manual_skip = True

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        # Check if we have previous songs
        if self.song_history.current_index <= 0 or len(self.song_history.history) <= 1:
            await ctx.send("No previous songs in history.")
            self._manual_skip = False
            return

        # Set the index to two positions back so that get_previous_song() will move to the correct position
        self.song_history.current_index -= 1

        #Going 2 song previous so we can get the previous song
        previous_song = self.song_history.get_previous_song()

        try:
            self.is_playing = True
            ctx.voice_client.play(
                discord.FFmpegPCMAudio(previous_song['url'], **ffmpeg_opts),
                after=lambda e: asyncio.run_coroutine_threadsafe(self._after_song(ctx), self.bot.loop).result()
            )
            await ctx.send(f"Now playing: {previous_song['title']}")
        except Exception as e:
            self.is_playing = False
            await ctx.send(f"Error playing song: {str(e)}")

        # Reset manual skip flag
        self._manual_skip = False

    @commands.command()
    async def loop(self, ctx):
        """Toggle loop mode for the current song."""
        if not hasattr(self, 'loop_mode'):
            self.loop_mode = False

        self.loop_mode = not self.loop_mode
        await ctx.send(f"Loop mode {'enabled' if self.loop_mode else 'disabled'}")

    # Auxiliar function to handle the queue
    async def _after_song(self, ctx):
        if self._manual_skip:
            return

        if self.loop_mode and self.song_history.get_current_song():
            # Replay the current song
            current_song = self.song_history.get_current_song()
            ctx.voice_client.play(
                discord.FFmpegPCMAudio(current_song['url'], **ffmpeg_opts),
                after=lambda e: asyncio.run_coroutine_threadsafe(self._after_song(ctx), self.bot.loop).result()
            )
            return

        if self.song_queue:
            next_song = self.song_queue.pop(0)
            self.song_history.add_song(next_song)
            self.is_playing = True
            ctx.voice_client.play(
                discord.FFmpegPCMAudio(next_song['url'], **ffmpeg_opts),
                after=lambda e: asyncio.run_coroutine_threadsafe(self._after_song(ctx), self.bot.loop).result()
            )
            await ctx.send(f"Now playing: {next_song['title']}")
        else:
            self.is_playing = False
            await ctx.send("No more songs in the queue.")

    # Show the Queue
    @commands.command()
    async def queue(self, ctx):
        if self.song_queue:
            queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(self.song_queue)])
            await ctx.send(f"Current queue:\n{queue_list}")
        else:
            await ctx.send("The queue is empty.")

    # Pause the current song
    @commands.command(name="pause")
    async def pause(self, ctx):
        """Pause the current song."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused the song.")
        else:
            await ctx.send("No song is currently playing.")

    #Leave the voice channel
    @commands.command()
    async def leave(self, ctx):
        """Leave the voice channel."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.voice_client = None
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I am not in a voice channel.")

    async def get_youtube_info(self, search, max_retries=5):
        """Fetch YouTube info with exponential backoff retry logic."""
        retries = 0
        while retries < max_retries:
            try:
                # Use ytsearch to search for the song
                search_result = ytdl.extract_info(f"ytsearch:{search}", download=False)
                return search_result
            except Exception as e:
                if "429" in str(e):  # Too Many Requests
                    wait_time = (2 ** retries) + random.random()  # Exponential backoff
                    print(f"Rate limited, waiting {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                    retries += 1
                else:
                    raise  # Re-raise if it's not a rate limit error

        raise Exception("Maximum retries exceeded for YouTube request")

    @commands.command()
    async def volume(self, ctx, volume: int):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send("No song is currently playing.")
        if 0 > volume > 100:
            return await ctx.send("Volume must be between 0 and 100.")
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Volume set to {volume}%")

    @commands.command(name="nowplaying", aliases=["np", "current", "currentsong"])
    async def current_song(self, ctx):
        """Display information about the currently playing song"""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send("The bot is not connected to a voice channel.")

        current_song = self.song_history.get_current_song()
        if not current_song:
            return await ctx.send("No song is currently playing.")
        else:
            await ctx.send(f"Currently playing: {current_song['title']}")

    async def cross_fade(self, ctx, next_song):
        """Crossfade between songs."""
        if ctx.voice_client.is_playing():
            ctx.voice_client.source.volume = 1.0
            for i in range(10, 0, -1):
                ctx.voice_client.source.volume = i / 10
                await asyncio.sleep(0.1)
            ctx.voice_client.stop()

        ctx.voice_client.play(
            discord.FFmpegPCMAudio(next_song['url'], **ffmpeg_opts),
            after=lambda e: asyncio.run_coroutine_threadsafe(self._after_song(ctx), self.bot.loop).result()
        )
        ctx.voice_client.source.volume = 0.0
        for i in range(1, 11):
            ctx.voice_client.source.volume = i / 10
            await asyncio.sleep(0.1)

    @commands.command()
    async def lyrics(self, ctx, *, song_name: str = None):
        """Fetch lyrics for the current or specified song."""
        if not song_name:
            current_song = self.song_history.get_current_song()
            if not current_song:
                return await ctx.send("No song is currently playing.")
            song_name = current_song['title']

        try:
            # Use an API like lyrics.ovh or Genius API
            response = requests.get(f"https://api.lyrics.ovh/v1/{song_name}")
            data = response.json()
            if "lyrics" in data:
                lyrics = data["lyrics"]
                await ctx.send(f"Lyrics for {song_name}:\n{lyrics[:2000]}")  # Discord message limit
            else:
                await ctx.send("Lyrics not found.")
        except Exception as e:
            await ctx.send(f"Error fetching lyrics: {str(e)}")