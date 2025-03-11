import os
import discord
import yt_dlp as youtube_dl
import asyncio
import random
from dotenv import load_dotenv
from discord.ext import commands
from collections import deque
from logger import Logger, start_message_sender

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

song_queue = deque()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)

current_song = None
is_paused = False

# Configure FFmpeg
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
    'executable': 'ffmpeg'
}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    activity = discord.Activity(type=discord.ActivityType.listening, name="Music")
    await bot.change_presence(activity=activity)

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You must be in a voice channel!")

@bot.command()
async def leave(ctx):
    global is_paused, current_song

    if ctx.voice_client:
        current_song = None
        is_paused = True
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command()
async def play(ctx, url):
    """Play audio from a YouTube video or playlist"""
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel!")
        return
    
    if not ctx.voice_client:
        await ctx.invoke(join)

    try:
        if 'playlist?list=' in url:
            await play_playlist(url, ctx)
        else:
            await play_video(url, ctx)

    except youtube_dl.DownloadError as e:
        if 'video unavailable' in str(e).lower():
            await ctx.send(f"**Error:** A video in the playlist no longer exists or is blocked in your country")

    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {str(e)}")
        print(f"Unexpected error: {e}")

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

async def play_playlist(url, ctx):
    """Play audio from playlist"""
    info = await extract_playlist_info(url, ctx)

    for entry in info['entries']:
        if entry and 'url' in entry:
            song_queue.append({'url': entry['url'], 'title': entry['title']})

    if ctx.voice_client.is_playing() or is_paused:
        await ctx.send(f"**Added {len(info['entries'])} songs to the queue from the playlist:** {info['title']}")

async def play_video(url, ctx):
    """ Play audio from video"""
    info = await extract_video_info(url)
    song_queue.append({'url': info['url'], 'title': info['title']})

    if ctx.voice_client.is_playing() or is_paused:
        await ctx.send(f"**Added to queue:** {info['title']}")

async def extract_video_info(url):
    """Extract video information from YouTube"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio'}]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)
    
async def extract_playlist_info(url, ctx):
    """Extract playlist information from YouTube"""
    # Queue for download updates
    message_queue = asyncio.Queue()
    sender_task = await start_message_sender(message_queue, ctx)
    playlist_size = get_playlist_size(url)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
        'logger': Logger(message_queue, playlist_size)
    }
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL(ydl_opts).extract_info(url, download=False))       
        await message_queue.join()
        return result
    
    finally:
        sender_task.cancel()
        try:
            await sender_task
        except asyncio.CancelledError:
            pass

def get_playlist_size(playlist_url):
    """Return the playlist size"""
    ydl_opts = {
        'quiet' : True,
        'extract_flat': True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
        return len(playlist_info['entries'])

async def play_next(ctx):
    """Play the next song in the queue"""
    global is_paused, current_song
    if is_paused:
        return

    if song_queue:
        song = song_queue.popleft()
        current_song = song
        voice_channel = ctx.voice_client

        voice_channel.play(discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS), after=lambda e: bot.loop.create_task(play_next(ctx)))
        await ctx.send(f"**Now playing:** {song['title']}")
    else:
        await ctx.send("**The queue is empty**")

@bot.command()
async def skip(ctx):
    """Skip the current song."""
    if ctx.voice_client is None:
        await ctx.send("**I'm not connected to a voice channel!**")
        return

    if ctx.voice_client.is_playing():
        await ctx.send("**Skipped the current song**")
        ctx.voice_client.stop()
    else:
        await ctx.send("**No song is currently playing.**")

@bot.command()
async def queue(ctx):
    """Show the queue."""
    if song_queue:
        queue_list = "\n".join([f"{index + 1}. {song['title']}" for index, song in enumerate(song_queue)])
        await ctx.send(f"**Current queue:**\n{queue_list}")
    else:
        await ctx.send("**The queue is empty**")

@bot.command()
async def clear(ctx):
    """Clear the queue"""
    song_queue.clear()
    await ctx.send(f"**The queue has been cleared!**")

@bot.command()
async def shuffle(ctx):
    """Shuffle the queue"""
    if song_queue:
        random.shuffle(song_queue)
        await ctx.send("The queue has been shuffled!")
    else:
        await ctx.send("The queue is empty and cannot be shuffled")

@bot.command()
async def pause(ctx):
    """Pauses the current song"""
    global is_paused

    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        is_paused = True
        await ctx.send(f"**The song has been paused!**")
    else:
        await ctx.send(f"**No song is currently playing**")

@bot.command()
async def resume(ctx):
    """Resumes the current song"""
    global is_paused, current_song

    if not current_song:
        is_paused = False
        await play_next(ctx)
        return

    if is_paused:
        is_paused = False
        ctx.voice_client.resume()
        await ctx.send(f"**The song has been resumed!**")
    else:
        await ctx.send("**No song is currently paused**.")

@bot.command()
async def help(ctx):
    """Displays all available commands."""
    embed = discord.Embed(
        title="Available Commands",
        description="Here are all the commands you can use:",
        color=discord.Color.brand_red()
    )
    embed.add_field(name="`!play <url>`", value="Plays a song or playlist from a URL", inline=False)
    embed.add_field(name="`!pause`", value="Pauses the current song", inline=False)
    embed.add_field(name="`!resume`", value="Resumes the paused song or queue", inline=False)
    embed.add_field(name="`!skip`", value="Skips the current song and plays the next", inline=False)
    embed.add_field(name="`!queue`", value="Shows the current queue", inline=False)
    embed.add_field(name="`!clear`", value="Clears the queue", inline=False)
    embed.add_field(name="`!shuffle`", value="Shuffles the queue", inline=False)
    embed.add_field(name="`!join`", value="Joins the voice channel", inline=False)
    embed.add_field(name="`!leave`", value="Leaves the voice channel", inline=False)

    await ctx.send(embed=embed)

bot.run(token)