#Environment variables
import os
#Dependencies
import discord
import asyncio
import youtube_dl
#Initialise client
from discord.ext import commands
client = commands.Bot(command_prefix=";.")

#intial values for data shared between commands
client.playlist={}
client.repeat_prop = False
client.ydl_opts = {"format":"249/250/251"}

# Notify when ready.
@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))

# Clear Channel (DEBUG)
@client.command()
async def purgethis(ctx):
 await ctx.channel.purge(limit=100)


# Toggle repeat property
@client.command()
async def repeat(ctx):
  await ctx.message.delete()
  if client.repeat_prop == False:
    client.repeat_prop = True
    await ctx.send("Repeat is ON", delete_after=3.0)
  else:
    client.repeat_prop = False
    await ctx.send("Repeat is OFF", delete_after=3.0)
    

#Build playlist from url link.
@client.command()
async def setup(ctx, url : str):
  with youtube_dl.YoutubeDL(client.ydl_opts) as ydl:
    temp_playlist=ydl.extract_info(url, download=False)
    for video in temp_playlist["entries"]:
      song_info={ "title":video['title'],
                  "link":video['webpage_url']}
      client.playlist[str(video['playlist_index'])]=song_info
  i=0
  for song in client.playlist:
    i+=1
    await ctx.send(str(i)+": "+client.playlist[song]["title"])


@client.command()
async def simple(ctx):
  voiceChannel = ctx.author.voice.channel
  voice = await voiceChannel.connect()

@client.command()
async def play(ctx, num : str):
  await ctx.message.delete()
  song_there=os.path.isfile("song.webm")
  try:
    if song_there:
      os.remove("song.webm")
  except PermissionError:
      await ctx.send("Wait for current music to end")
      return

  try:
    url=client.playlist[num]["link"]
    with youtube_dl.YoutubeDL(client.ydl_opts) as ydl:
      ydl.download([url])
    for file in os.listdir("./"):
      if file.endswith(".webm"):
        os.rename(file, "song.webm")
  except:
    await ctx.send("track number not found")
    return
  
  voiceChannel = ctx.author.voice.channel
  voice = await voiceChannel.connect()

  def replay(voice, audio):
    # if client.repeat_prop == True:
    voice.play(audio, after=lambda e: replay(voice, audio))
    voice.is_playing()

  if voiceChannel and not voice.is_playing():
    audio = discord.FFmpegOpusAudio("song.webm")
    voice.play(audio, after=lambda e: replay(voice, audio))
    voice.is_playing()

@client.command()
async def leave(ctx):
  voice=discord.utils.get(client.voice_clients, guild=ctx.guild)
  if voice.is_connected():
    await voice.disconnect()
  else:
    await ctx.send("Not currently in voice channel.")

@client.command()
async def pause(ctx):
  voice=discord.utils.get(client.voice_clients, guild=ctx.guild)
  if voice.is_playing():
    voice.pause()
  else:
    await ctx.send("Nothing is playing!")

@client.command()
async def resume(ctx):
  voice=discord.utils.get(client.voice_clients, guild=ctx.guild)
  if voice.is_paused():
    voice.resume()
  else:
    ctx.send("Audio is playing")

@client.command()
async def stop(ctx):
  voice=discord.utils.get(client.voice_clients, guild=ctx.guild)
  voice.stop()


client.run("ODc3OTYxMDY5MDAyMzgzMzcx.YR6O9g.Ro2m6DQWRvkABtxNRkedOjy3GsA")