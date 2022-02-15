from discord.ext import commands
from urllib.request import urlopen
import json
import os
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='?') #define command decorator

userCommands = ['help', 'hello', 'about', 'online']

urls = {'steam': 'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=17080',
		'community': 'http://ta.kfk4ever.com:9080/status'}

responses = {'steam': '',
			 'community': ''}

def getOnlinePlayers():
	responses['steam'] = json.loads(urlopen(urls['steam']).read())
	responses['community'] = json.loads(urlopen(urls['community']).read())



@bot.event
async def on_message(message):
	await bot.process_commands(message)


#Say Hello
@bot.command(pass_context=True)
async def hello(ctx):
	await ctx.send("[VGH] Hello! I'm the Wilderzone Servers bot :wave:")


#About this bot
@bot.command(pass_context=True)
async def introduce(ctx):
	await ctx.send("[VGH] Hello! I'm the Wilderzone Servers bot :wave:\nI can tell you how many people are playing Tribes Ascend at any time!\nJust say `?online` in any channel and I'll reply. :tada:")


#List online players
@bot.command(pass_context=True)
async def online(ctx):
	getOnlinePlayers()
	steam = responses['steam']['response']['player_count']
	community = responses['community']['online_players']
	total = steam + community
	message = "There are currently `" + str(total) + "` players online.\n"
	message += " • HiRez Servers: `" + str(steam) + "`\n"
	message += " • Community Servers: `" + str(community) + "`"
	await ctx.send(message)




@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))


bot.run(os.getenv('TOKEN'))