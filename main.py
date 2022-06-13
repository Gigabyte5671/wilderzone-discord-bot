import asyncio
from collections import namedtuple
import datetime
import json
import logging
import os
import shutil
import time

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from player_counts import steam_counter, community_counter

COMMUNITY_LINKS = [
	{'title': 'Wilderzone Live', 'short_title': 'Wilderzone', 'url': 'https://wilderzone.live/'},
	{'title': 'Wilderzone Servers', 'short_title': 'Wilderzone Servers', 'url': 'https://servers.wilderzone.live/'},
	{'title': 'Llamagrab Servers', 'short_title': 'Llamagrab Servers', 'url': 'https://llamagrab.net/'},
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

MIN_CHANGE_TO_UPDATE = 2

class NameCountsBot:
	""" A discord bot which updates its name to show player counts for a Tribes environment (steam/community)"""
	def __init__(self, name, url, url_type, token):
		self.name = name
		self.url = url
		self.token = token
		self.logger = logging.getLogger(name)
		self.last_count = None
		self.guild = None
		self.ready = False

		if url_type == 'community':
			self.fetcher = community_counter(url)
		elif url_type == 'steam':
			self.fetcher = steam_counter(url)
		else:
			raise Exception(f'url_type should be steam or community. {url_type} is not valid.')

		self.client = discord.Client()
		@self.client.event
		async def on_ready():
			# fetch_guilds does not return guild.me, we have call get_guild with the id
			shallow_guild = await self.client.fetch_guilds().next()
			self.guild = self.client.get_guild(shallow_guild.id)
			self.logger.info(f'Logged in {name} as {self.client.user} on {self.guild}')
			self.ready = True

	def start(self):
		""" Starts the bot. This should only be called once."""
		return self.client.start(self.token)

	async def get_counts(self):
		""" Returns updated player counts. If the count changed, the bot updates it nickname in
			discord.
		"""
		try:
			count = self.fetcher()
		except Exception as e:
			self.logger.error(e)
			return None

		# We only update the name if one of the following is true:
		# - this is the first run of the bot
		# - the player counts was 0 or the new player count is 0
		# - The player counts changed by more than MIN_CHANGE_TO_UPDATE (to avoid spamming changes)
		is_zero = self.last_count == 0 or count == 0
		if self.last_count is None or is_zero or abs(count - self.last_count) > MIN_CHANGE_TO_UPDATE:
			self.logger.info(f'Count changed ({self.last_count} -> {count}), updating nickname for {self.name}')
			await self.guild.me.edit(nick=f'{self.name}: {count}')
		self.last_count = count
		return count


HISTORY_FILE = 'history.json'

bot = commands.Bot(command_prefix='?') # define command decorator
name_bots = []

last_online_message = None


async def get_player_counts():
	counts = {
		name_bot.name: await name_bot.get_counts()
		for name_bot in name_bots
	}
	counts['total'] = sum(filter(None, counts.values()))
	add_counts_to_history(counts)
	return counts


def add_counts_to_history(responses: dict):
	# start with empty history if it does not exists
	if not os.path.exists(HISTORY_FILE):
		history = {}
	else:
		with open(HISTORY_FILE, 'r') as f:
			history = json.load(f)

	# key is the epoch time in seconds
	history[int(time.time())] = responses
	with open(HISTORY_FILE, 'w') as f:
		json.dump(history, f, indent=2)


@bot.event
async def on_message(message):
	await bot.process_commands(message)


#About this bot
@bot.command(pass_context=True)
async def introduce(ctx):
	logging.info('Sending introduction message.')
	await ctx.send(
		"[VGH] Hello! I'm the Wilderzone Servers bot :wave:\n"
		+ "I can tell you how many people are playing Tribes Ascend at any time!\n"
		+ "Just say `?online` in any channel and I'll reply. :tada:"
	)


#Links
@bot.command(pass_context=True)
async def links(ctx):
	message = ""
	for link in COMMUNITY_LINKS:
		message += f'• {link["short_title"]}: {link["url"]}\n'

	embed = discord.Embed(title='Useful community links:', description=message, colour=0x6DACC8)
	logging.info('Sending links message.')
	await ctx.send(content=None, embed=embed)


async def try_delete(message):
	try:
		await message.delete()
	except Exception as e:
		logging.error(f'Failed to delete {message.id}')


async def cleanup_online_messages(ctx, sent_message):
	global last_online_message
	logging.info(f'deleting trigger message {ctx.message.id}')
	await try_delete(ctx.message)
	if last_online_message:
		logging.info(f'deleting last online/offline message {last_online_message.id}')
		await try_delete(last_online_message)
	last_online_message = sent_message


#List online players
@bot.command(pass_context=True)
async def online(ctx):
	counts = await get_player_counts()
	if counts['total'] == 1:
		message = f'There is currently {counts["total"]} player online.\n'
	else:
		message = f'There are currently {counts["total"]} players online.\n'

	hirez_count = counts['HiRez'] if counts.get('HiRez') else 'unavailable'
	community_count = counts['Community'] if counts.get('Community') else 'unavailable'
	message += f' • HiRez Servers: `{hirez_count}`\n'
	message += f' • Community Servers: `{community_count}`'

	logging.info(f'Sending online message: \n{message}')
	sent_message = await ctx.send(message)
	await cleanup_online_messages(ctx, sent_message)


#List offline players
@bot.command(pass_context=True)
async def offline(ctx):
	counts = await get_player_counts()
	offline_players = 547974 - counts['total']
	if offline_players == 1:
		message = f'There is currently {offline_players} player offline... VGS'
	else:
		message = f'There are currently {offline_players} players offline... VGS'

	logging.info(f'Sending offline message: \n{message}')
	sent_message = await ctx.send(message)
	await cleanup_online_messages(ctx, sent_message)


@tasks.loop(minutes=5)
async def periodic_update():
	await get_player_counts()


@bot.event
async def on_ready():
	logging.info(f'Main bot logged in as {bot.user}')
	# wait for the name-bots to finish fetching their guild information
	while False in map(lambda b: b.ready, name_bots):
		logging.info('Main bot waiting for all bots to be ready...')
		await asyncio.sleep(2)
	periodic_update.start()


def main():
	logging.basicConfig(
		force=True,
		level=logging.DEBUG,
		format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s'
	)
	logging.getLogger('discord').setLevel(logging.ERROR)
	logging.getLogger('asyncio').setLevel(logging.ERROR)
	logging.getLogger('urllib3').setLevel(logging.ERROR)

	# load .env to read discord token
	load_dotenv()

	name_bots.extend([
		NameCountsBot(
			name='HiRez',
			url='https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=17080',
			url_type='steam',
			token=os.getenv('HIREZ_TOKEN')
		),
		NameCountsBot(
			name='Community',
			url='http://ta.kfk4ever.com:9080/detailed_status',
			url_type='community',
			token=os.getenv('COMMUNITY_TOKEN')
		),
		NameCountsBot(
			name='PUGz',
			url='http://tribes-wkume.centralus.cloudapp.azure.com:9080/detailed_status',
			url_type='community',
			token=os.getenv('PUGS_TOKEN')
		)
	])

	# backup history file
	if os.path.exists(HISTORY_FILE):
		os.makedirs('history_backup', exist_ok=True)
		now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
		shutil.copy(HISTORY_FILE, os.path.join('history_backup', f'history_{now_str}.json'))

	loop = asyncio.get_event_loop()
	for name_bot in name_bots:
		loop.create_task(name_bot.start())
	loop.create_task(bot.start(os.getenv('MAIN_TOKEN')))
	loop.run_forever()


if __name__ == '__main__':
	main()
