from discord.ext import commands
from urllib.request import urlopen
import json
import os
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='?') #define command decorator

userCommands = ['help', 'hello', 'about', 'links', 'online']

community_links = [
	{'title': 'Wilderzone Live', 'short_title': 'Wilderzone', 'url': 'https://wilderzone.live/'},
	{'title': 'Wilderzone Servers', 'short_title': 'Wilderzone Servers', 'url': 'https://servers.wilderzone.live/'},
	{'title': 'Llamagrab Servers', 'short_title': 'Llamagrab Servers', 'url': 'https://servers.llamagrab.net/'},
	{'title': 'Tribes Launcher Sharp', 'short_title': 'Launcher', 'url': 'https://github.com/mcoot/TribesLauncherSharp/releases/latest'},
	{'title': 'TAMods', 'short_title': 'TAMods', 'url': 'https://www.tamods.org/'},
	{'title': 'TAAGC', 'short_title': 'TAAGC', 'url': 'https://taagc.org/'},
	{'title': "Dodge's Domain", 'short_title': "Dodge's Domain", 'url': 'https://www.dodgesdomain.com/'},
	{'title': 'Tribes Ascend on Steam', 'short_title': 'Steam', 'url': 'https://store.steampowered.com/app/17080/Tribes_Ascend/'},
	{'title': 'Tribes on Reddit', 'short_title': 'Subreddit', 'url': 'https://www.reddit.com/r/Tribes/'},
	{'title': 'Tribes Lore', 'short_title': 'Lore', 'url': 'https://tribes.fandom.com/wiki/Backstory_timeline'},
	{'title': 'Images from Tribes Ascend', 'short_title': 'Gallery', 'url': 'https://wilderzone.live/gallery/'},
	{'title': 'Music from Tribes Ascend', 'short_title': 'Music', 'url': 'https://www.youtube.com/playlist?list=PLBAC1B18024809938'},
	{'title': 'Tribes Universe', 'short_title': 'Tribes Universe', 'url': 'https://www.tribesuniverse.com/'}
]

urls = {'steam': 'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=17080',
		'community': 'http://ta.kfk4ever.com:9080/detailed_status'}

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


#Links
@bot.command(pass_context=True)
async def links(ctx):
	message = "**Here are some useful community links:** \n"
	for link in community_links:
		message += " • " + link['short_title'] + ": " + link['url'] + "\n"
	await ctx.send(message)


#List online players
@bot.command(pass_context=True)
async def online(ctx):
	getOnlinePlayers()
	steam = responses['steam']['response']['player_count']
	community = responses['community']['online_players_list']
	if 'taserverbot' in community:
		community.remove('taserverbot')
	community = len(community)
	total = steam + community
	if total == 1:
		message = "There is currently `" + str(total) + "` player online.\n"
	else:
		message = "There are currently `" + str(total) + "` players online.\n"
	message += " • HiRez Servers: `" + str(steam) + "`\n"
	message += " • Community Servers: `" + str(community) + "`"
	await ctx.send(message)




@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))


bot.run(os.getenv('TOKEN'))