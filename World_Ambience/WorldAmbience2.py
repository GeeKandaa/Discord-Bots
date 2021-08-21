import asyncio
import discord
from discord.ext import commands
import youtube_dl

youtube_dl.utils.bug_reports_message = lambda: ''

####################################################################################################


ytdl_playlist_format_options = {"format":"249/250/251"}
ytdl_format_options = {
  'format': 'bestaudio/best',
  'outtmpl':'%(extractor)s-%(id)s-%(title)s.%(ext)s',
  'restrictfilenames':True,
  'noplaylist':True,
  'nocheckcertificate': True,
  'ignoreerrors': False,
  'logtostderr': False,
  'quiet': True,
  'no_warnings': True,
  'default_search': 'auto',
  'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
  'options':'-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
ytdl_playlist = youtube_dl.YoutubeDL(ytdl_playlist_format_options)

####################################################################################################
class YTDLSource(discord.PCMVolumeTransformer):
  def __init__(self, source, *, data, volume=0.2):
    super().__init__(source, volume)

    self.data = data
    self.title = data.get('title')
    self.url = data.get('url')

  @classmethod
  async def from_url(cls, url, *, loop=None, stream=False):
    loop = loop or asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

    if 'entries' in data:
      data = data['entries'][0]
    filename = data['url'] if stream else ytdl.prepare_filename(data)
    return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
####################################################################################################
class Ambience(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
    self.playlist={}
    self.repeat=True
      ########################################################################################
  @commands.command()
  async def repeat(self, ctx):
    await ctx.message.delete()
    if self.repeat==True:
      self.repeat=False
      await ctx.send("Repeat is off.", delete_after=3.0)
    else:
      self.repeat=True
      await ctx.send("Repeat is on.", delete_after=3.0)
  
  @commands.command()
  async def setup(self, ctx, url : str, keep=False):
    await ctx.message.delete()
    with youtube_dl.YoutubeDL(ytdl_playlist_format_options) as ydl:
      temp_playlist=ydl.extract_info(url, download=False)
      for video in temp_playlist["entries"]:
        song_info={ "title":video['title'],
                    "link":video['webpage_url']}
        self.playlist[str(video['playlist_index'])]=song_info
      i=0
      for song in self.playlist:
        i+=1
        if keep == True:
          await ctx.send(str(i)+": "+self.playlist[song]["title"])
      if keep == True:
        await ctx.send('------------------------------')
  
  @commands.command()
  async def play(self, ctx, *, num=0):
    await ctx.message.delete()
    async with ctx.typing():
      if not str(num) in self.playlist:
        return
      url = self.playlist[str(num)]["link"]
      player = await YTDLSource.from_url(url,loop=self.bot.loop)
      ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
      
      cont=True
      while cont == True:
        if ctx.voice_client.is_playing():
          continue
        elif self.repeat == True:
          player = await YTDLSource.from_url(url,loop=self.bot.loop)
          ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        elif self.repeat == False:
          return
      
  @commands.command()
  async def stop(self, ctx):
    await ctx.message.delete()
    await ctx.voice_client.disconnect()
  
  @play.before_invoke
  async def ensure_voice(self, ctx):
    if ctx.voice_client is None:
      if ctx.author.voice:
        await ctx.author.voice.channel.connect()
      else:
        raise commands.CommandError("Author not connected to a voice channel.")
    elif ctx.voice_client.is_playing():
      ctx.voice_client.stop()
      ########################################################################################

bot = commands.Bot(command_prefix=";.")

@bot.event
async def on_ready():
  print('Logged in as {0} ({0.id})'.format(bot.user))
  print('------')

bot.add_cog(Ambience(bot))
bot.run('ODc3OTYxMDY5MDAyMzgzMzcx.YR6O9g.Ro2m6DQWRvkABtxNRkedOjy3GsA')