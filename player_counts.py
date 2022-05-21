import requests

def steam_counter(url):
	""" Returns a function which fetches the counts from steam URL"""
	def get():
		response = requests.get(url).json()
		steam_count = response['response']['player_count']
		return steam_count
	return get

def community_counter(url):
	""" Returns a function which fetches the counts from a loginserver"""
	def get():
		response = requests.get(url).json()
		community_count = len(response['online_players_list'])
		if 'taserverbot' in response['online_players_list']:
			community_count -= 1
		return community_count
	return get
