from discord.ext import commands, tasks
import discord
from urllib.request import urlopen
import json
import os
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='?') #define command decorator
intents = discord.Intents.default()
client = discord.Client(guild_subscriptions=True, intents=intents)

url = 'http://ta.kfk4ever.com:9080/detailed_status'

response = {'response': ''}


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
	await ctx.guild.me.edit(nick="Community: " + str(community))


@tasks.loop(minutes=5)
async def getOnlinePlayers():
	response['response'] = json.loads(urlopen(url).read())
	print(response)
	#guild = await client.get_guild(631438713183797258)
	#member = await guild.get_member(943660216707321866)
	#await  member.edit(nick="HiRez: " + str(steam))


@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	#getOnlinePlayers.start()


bot.run(os.getenv('TOKEN'))