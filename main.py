from discord.ext import commands, tasks
from urllib.request import urlopen
import json
import os
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='?') #define command decorator

userCommands = ['help', 'hello', 'online']

urls = {'steam': 'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=17080',
		'community': 'http://ta.kfk4ever.com:9080/status'}

responses = {'steam': '',
			 'community': ''}

responses['steam'] = json.loads(urlopen(urls['steam']).read())
responses['community'] = json.loads(urlopen(urls['community']).read())



@bot.event
async def on_message(message):
    await bot.process_commands(message)


#Show list of commands
@bot.command(pass_context=True)
async def help(ctx):
    await ctx.channel.send('[VVH] The available commands are: ')
    new_message = "" 
    for com in userCommands:
        new_message += com + ", "
    new_message += "."
    await ctx.channel.send(new_message)


#Say Hello
@bot.command(pass_context=True)
async def hello(ctx):
    await ctx.send("[VGH] Hello! I'm the Wilderzone Servers bot :wave:")


#List online players
@bot.command(pass_context=True)
async def online(ctx):
    steam = responses['steam']['response']['player_count']
    community = responses['community']['online_players']
    total = steam + community
    await ctx.send("There are currently " + total + " players online.")
    message = "HiRez Servers: " + steam
    await ctx.send(message)
    message = "Community Servers: " + community
    await ctx.send(message)




@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


bot.run(os.getenv('TOKEN'))