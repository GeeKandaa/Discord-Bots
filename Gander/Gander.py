import discord
from discord.ext import commands
import os
import requests
from bs4 import BeautifulSoup
import urllib.request
###########################################################

bot = commands.Bot(command_prefix='..')
@bot.command()
async def see(ctx, *monster_names):
  monster_name = ''
  for name_part in monster_names:
    monster_name+=str(name_part)+'_'
  monster_name=monster_name[:-1]
  await ctx.message.delete()
  url="https://forgottenrealms.fandom.com/wiki/"+str(monster_name)
  print(url)
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
  page = requests.get(url,headers=headers)
  if page is None:
    print("PAGE Error")
    return
  soup = BeautifulSoup(page.content, 'html.parser')
  if soup is None:
    print("SOUP Error")
    return
  table = soup.find("figure",attrs={'class':'pi-item pi-image'})
  if table is None:
    print("TABLE Error")
    return
  imgs = table.find_all("a",class_="image image-thumbnail", href=True)
  if len(imgs) == 1:
    urllib.request.urlretrieve(imgs[0]['href'],'what-you-see.png')
    channel = bot.get_channel(856485340754739212)
    await channel.send(file=discord.File('what-you-see.png'))


############################################################

@bot.event
async def on_ready():
  print(f'{bot.user} is now online!')

bot.run('ODc4NTUxNDA2Mjg4NzE5OTEz.YSC0wQ.JmitXdTsrYmbo1Z_8UCRlIHq3tQ')