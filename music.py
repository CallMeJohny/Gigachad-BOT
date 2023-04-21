import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord.utils import get
import yt_dlp as youtube_dl
import logging
import asyncio
from os import getenv
from dotenv import load_dotenv

load_dotenv("discord.env")

ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "outtmpl": "song.mp3",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "verbose": True,
    "ffmpeg_location": getenv("REPOSITORY")
}
ffmpeg_options = {'options': "-vn"}


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connected = False
        self.voice_clients = {}
        self.is_paused = False

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
            self.connected = True
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command(name="play")
    async def play(self, ctx: Context, *url: str):
        if not ctx.author.voice:
            return await ctx.send("You need to be in a voice channel to use this command.")

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                if not self.connected:
                    await ctx.author.voice.channel.connect()
                    self.connected = True
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(url[0], download=False))
                song = data["url"]
                player = discord.FFmpegPCMAudio(song, **ffmpeg_options, executable="D:/Programy/ffmpeg-6.0-essentials_build/ffmpeg-6.0-essentials_build/bin/ffmpeg.exe")
                ctx.voice_client.play(player)
                await ctx.send(f"Playing: **{data['title']}**")
        except Exception as e:
            logging.error(e)
    @commands.command(name="leave")
    async def leave(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.disconnect()
            self.connected = False
            await ctx.send("Bot left the voice channel.")
        else:
            await ctx.send("Bot is not connected to the voice channel.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        voice_client = ctx.voice_client
        if voice_client:
            voice_client.stop()
            self.is_paused = True
            await ctx.send("Playback stopped.")
        else:
            await ctx.send("Bot is not connected to a voice channel.")
