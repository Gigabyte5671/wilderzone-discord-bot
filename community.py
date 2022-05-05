from discord.ext import commands, tasks
from urllib.request import urlopen
import json
import os
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='?') #define command decorator

url = 'http://ta.kfk4ever.com:9080/detailed_status'

response = {'response': ''}
previous = {'prev': None}

number_of_refreshes = {'num': 0}


@bot.event
async def on_message(message):
	await bot.process_commands(message)


#Change nickname to online players number
@bot.command(pass_context=True)
async def online(ctx):
	response['response'] = json.loads(urlopen(url).read())

	community = response['response']['online_players_list']
	if 'taserverbot' in community:
		community.remove('taserverbot')
	community = len(community)

	if community != previous['prev']:
		await ctx.guild.me.edit(nick="Community: " + str(community))

	number_of_refreshes['num'] += 1
	ordinal = " times."
	if(number_of_refreshes['num'] == 1):
		ordinal = " time."
	print('Refreshed ' + str(number_of_refreshes['num']) + ordinal, end = "\r")


@tasks.loop(minutes=5)
async def getOnlinePlayers():
	response['response'] = json.loads(urlopen(url).read())

	community = response['response']['online_players_list']
	if 'taserverbot' in community:
		community.remove('taserverbot')
	community = len(community)

	if community != previous['prev']:
		for guild in bot.guilds:
			await guild.me.edit(nick="Community: " + str(community))
	
	number_of_refreshes['num'] += 1
	ordinal = " times."
	if(number_of_refreshes['num'] == 1):
		ordinal = " time."
	print('Refreshed ' + str(number_of_refreshes['num']) + ordinal, end = "\r")


@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	getOnlinePlayers.start()


bot.run(os.getenv('COMMUNITY_TOKEN'))