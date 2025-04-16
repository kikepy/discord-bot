import asyncio
import discord
from discord.ext import commands
import yt_dlp

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

class SongHistory:
    def __init__(self):
        self.history = []
        self.current_index = -1

    def add_song(self, song):
        self.history.append(song)
        self.current_index = len(self.history) - 1

    def get_previous_song(self):
        if self.current_index > 0:
            self.current_index -= 1
            return self.history[self.current_index]
        return None

    def get_next_song(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]
        return None
    def is_empty(self):
        return len(self.history) == 0

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.song_queue = []
        self.song_history = SongHistory()
        self.is_playing = False

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
            search_result = ytdl.extract_info(f"ytsearch:{search}", download=False)
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
        """Skip the current song."""
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            await ctx.send("The bot is not connected to a voice channel.")
            return

        if ctx.voice_client.is_playing():
            await ctx.voice_client.stop()

        # Get the next song from the queue
        next_song = self.song_history.get_next_song()

        if not next_song:
            if not self.song_queue:
                await ctx.send("No more songs in the queue.")
                self.is_playing = False
                return
            next_song = self.song_queue.pop(0)

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
            await self.next(ctx)

        # Previous song on the queue
    @commands.command()
    async def previous(self, ctx):
        """Play the previous song."""
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            await ctx.send("The bot is not connected to a voice channel.")
            return

        if self.song_history.is_empty():
            await ctx.send("No previous songs in history.")
            return

        # Get the previous song from the history
        previous_song = self.song_history.get_previous_song()
        if previous_song is None:
            await ctx.send("No previous songs in history.")
            return

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()


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

    # Auxiliar function to handle the queue
    async def _after_song(self, ctx):
        if self.is_playing and self.song_queue:
            current_song = self.song_queue.pop(0)
            self.song_history.add_song(current_song)

        if self.song_queue:
            await asyncio.sleep(1)
            await self.next(ctx)
        elif self.song_history.get_next_song():
            await asyncio.sleep(1)
            await self.next(ctx)
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