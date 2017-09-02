
"""
The MIT License (MIT)
Copyright (c) 2017 Dino
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __main__ import send_cmd_help
import requests
import os
import time
import discord
from discord.ext import commands
import json
from bs4 import BeautifulSoup
import urllib
import urllib.request 
import asyncio
import aiohttp
from ext.commands.dataIO import dataIO
import locale

NUMITEMS = 9
statscr_url = "http://statsroyale.com/profile/"
statsurl = 'http://statsroyale.com'
PATH = os.path.join("data", "crtags")
SETTINGS_JSON = os.path.join(PATH, "settings.json")
BACKSETTINGS_JSON = os.path.join(PATH, "backsettings.json")
CLAN_JSON = os.path.join(PATH, "clan.json")
SET_JSON = os.path.join(PATH, "set.json")
validChars = ['0', '2', '8', '9', 'C', 'G', 'J', 'L', 'P', 'Q', 'R', 'U', 'V', 'Y']
tags = {}
headers = {
	'User-Agent': 'Bot(Rain), (https://github.com/Dino0631/discordbot/tree/master)',
	'From': 'htmldino@gmail.com'  
}
class CRClan:

	def __init__(self, tag, ctx):
		tag2id = dataIO.load_json(BACKSETTINGS_JSON)
		self.member_count = 0                           #done
		self.members = []                               #done
		self.clan_tag = tag                             #done
		self.clan_url = statsurl + '/clan/' + tag       #done
		self.tr_req = '0'                               #done
		self.clan_trophy = ''                           #done
		self.name = ''                                  #done
		self.donperweek = ''							#done
		self.desc = ''									#done
		self.clan_badge = ''							#done
		self.leader = {}								#done
		self.size = 0									#done
		self.coleaders = []								#done
		self.elders = []								#done
		self.norole = []								#done
		r = requests.get(self.clan_url, headers=headers)
		html_doc = r.content
		soup = BeautifulSoup(html_doc, "html.parser")
		htmlmembers = soup.find_all('div',{'class': 'clan__rowContainer'})
		for i, m in enumerate(htmlmembers):
			data = m.find_all('div', {'class': 'clan__row'})
			rank = data[0].get_text()
			name = data[1].get_text()
			tag = data[1].find('a').attrs['href']
			url = statsurl + tag
			tag = tag[tag.find('profile/')+len('profile/'):]
			level = data[2].find('span', {'class':'clan__playerLevel'}).get_text()
			trophy = data[4].find('div', {'class': 'clan__cup'}).get_text()
			donations = data[5].get_text()
			role = data[6].get_text()
			if tag in tag2id:
				userid = tag2id[tag]
			else:
				userid = ''
			memberdict = {
				'name' : name.strip(),
				'rank' : rank.strip(),
				'tag' : tag.strip(),
				'userid': userid.strip(),
				'url' : url.strip(),
				'level' : level.strip(),
				'trophy' : trophy.strip(),
				'donations' : donations.strip(),
				'role' : role.strip()
			}
			memberdict['formatted'] = '`'+ memberdict['role']+'` ' + memberdict['name']+' [`#'+memberdict['tag']+'`]('+memberdict['url']+')'
			if memberdict['userid'] != '':
				try:
					memberdict['formatted'] += ' <@!'+memberdict['userid'] + '>'
				except:
					pass
			if memberdict['role'] == 'Co-Leader':
				self.coleaders.append(memberdict)
			if memberdict['role'] == 'Member':
				self.norole.append(memberdict)
			if memberdict['role'] == 'Elder':
				self.elders.append(memberdict)
			if memberdict['role'] == 'Leader':
				self.leader = memberdict
			self.size += 1
			self.members.append(memberdict)

		clanhead = soup.find('div', {'class':'clan__name'})
		self.clan_badge = statsurl + clanhead.find('img').attrs['src']
		info = clanhead.find('div', {'class':'clan__clanInfo'})
		self.name = info.find('div', {'class':'ui__headerMedium clan__clanName'}).get_text().strip()
		self.desc = info.find('div', {'class':'ui__mediumText'}).get_text().strip()
		info2 = soup.find('div', {'class':'clan__statistics'})
		trophy = info2.find_all('div', {'class':'clan__metricContent'})
		self.clan_trophy = trophy[0].find('div', {'class':'ui__headerMedium'}).get_text().strip()
		self.tr_req = trophy[1].find('div', {'class':'ui__headerMedium'}).get_text().strip()
		self.donperweek = trophy[2].find('div', {'class':'ui__headerMedium'}).get_text().strip()


class CRPlayer:


	async def async_refresh(self,url):
		async with aiohttp.get(url) as r:
			response = await r.json()
			return response

	def __init__(self, tag):
		self.clan_badge = ''                 #done

		self.name = ''                       #done
		self.level = ''                      #done
		self.clan = ''                       #done
		self.prevseasontrophy = ''           #done
		self.crown3 = ''                     #done
		self.prevseasonpb = ''               #done
		self.wins = ''                       #done
		self.cardswon = ''                   #done
		self.losses = ''                     #done
		self.league = ''                     #done
		self.prevseasonrank = ''             #done
		self.donations = ''                  #done
		self.trophy = ''                     #done
		self.tcardswon = ''                  #done
		self.pb = ''                         #done
		self.chests = ''                     #done

		asyncio.sleep(1)
		user_url = 'http://statsroyale.com/profile/'+tag
		r = requests.get(user_url, headers=headers)
		html_doc = r.content
		soup = BeautifulSoup(html_doc, "html.parser")
		html_doc = r.content
		chests_queue = soup.find('div', {'class':'chests__queue'})
		chests = chests_queue.get_text().split()
		for index, item in enumerate(chests):
			if item.startswith('+') and item.endswith(':'):
				del chests[index]
			elif item == 'Chest':
				del chests[index]
			if item == 'Super':
				chests[index] = 'SMC'
			elif item == 'Magic':
				chests[index] = 'Magical'

		for index, chest in enumerate(chests):
			if str(chest) == 'Magic':
				chests[index] = 'Magical'
			elif str(chest) == 'Super':
				chests[index] = 'SMC'
		new_chests = []
		x = 0
		while x<len(chests):
			new_chests.append(chests[x:x+2])
			x += 2
		chests = []


		for index, chest in enumerate(new_chests):
			chests.append(': '.join(chest))

		self.chests = '\n'.join(chests)

		soup = BeautifulSoup(html_doc, "html.parser")
		profilehead = soup.find_all("div", "profileHeader profile__header")
		statistics = soup.find_all("div", "statistics profile__statistics")
		profilehead = profilehead[0]
		statistics = statistics[0]
		thing2 = statistics.get_text()
		thing2 = thing2.replace('\n', ' ')
		thing2 = thing2.split('   ')
		for index, item in enumerate(thing2):
			thing2[index] = item.strip()
		statsdict = {}
		for index, item in enumerate(thing2):
			if item[:item.find(' ')].isdigit():
				thing2[index] = item[item.find(' ')+1:]+ ': '+item[:item.find(' ')]
				statsdict[item[item.find(' ')+1:].strip()] = item[:item.find(' ')] 
			else:
				statsdict[item.strip()] = ' '
			thing2[index].strip()

		pb = thing2[0]
		trophy = thing2[1]
		cardswon = thing2[2]
		tcardswon = thing2[3]
		donations = thing2[4]
		prevseasonrank = thing2[5]
		prevseasontrophy = thing2[6]
		prevseasonpb = thing2[7]
		wins = thing2[8]
		losses = thing2[9]
		crown3 = thing2[10]
		league = thing2[11]
		clan_url = statsurl + str(profilehead.find('a').attrs['href'])
		playerLevel = profilehead.find('span', 'profileHeader__userLevel')
		playerLevel = playerLevel.text
		playerName = profilehead.find('div', 'ui__headerMedium profileHeader__name').text.strip()
		playerName = playerName.replace(playerLevel, '').strip()
		playerClan = profilehead.find('a', 'ui__link ui__mediumText profileHeader__userClan').text.strip()
		playerTag = tag
		clan_badge = profilehead.find('img').attrs['src']
		clan_badge = statsurl + clan_badge
		self.clan_badge = clan_badge
		player_data = []
		player_data.append('[#{}]({})'.format(tag, user_url))
		for x in statsdict:
			if(statsdict[x].isdigit()):
				statsdict[x] = '[' + statsdict[x] + '](nothing)'
		for x in statsdict:
			if 'League' in x:
				self.league = x
			elif 'Highest trophies' in x:
				self.pb = x+ ': ' + statsdict[x]
			elif'Last known trophies' in x:
				self.trophy = x+ ': ' + statsdict[x]
			elif 'Challenge cards won' in x:
				self.cardswon = x+ ': ' + statsdict[x]
			elif 'Tourney cards won' in x:
				self.tcardswon = x+ ': ' + statsdict[x]
			elif 'Total donations' in x:
				self.donations = x+ ': ' + statsdict[x]
			elif 'Prev season rank' in x:
				self.prevseasonrank = x+ ': ' + statsdict[x]
			elif 'Prev season trophies' in x:
				self.prevseasontrophy = x+ ': ' + statsdict[x]
			elif 'Prev season highest' in x:
				self.prevseasonpb = x+ ': ' + statsdict[x]
			elif 'Wins' in x:
				self.wins = x+ ': ' + statsdict[x]
			elif 'Loses' in x:
				self.losses = x+ ': ' + statsdict[x]
			elif '3 crown wins' in x:
				self.crown3 = x+ ': ' + statsdict[x]
		self.name = playerName
		self.level = playerLevel
		self.clan = playerClan
		self.clan_url = clan_url


class InvalidRarity(Exception):
	pass
numcards = {}
numcards['c'] = 20
numcards['r'] = 21
numcards['e'] = 22
numcards['l'] = 13
maxcards = {
	'c':13,
	'r':11,
	'e':8,
	'l':5
}
tourneycards = {
	'c':9,
	'r':7,
	'e':4,
	'l':1
}


upgrades = {}
upgrades['c'] = [
	5,
	20,
	50,
	150,
	400,
	1000,
	2000,
	4000,
	8000,
	20000,
	50000,
	100000
]
upgrades['r'] = upgrades['c'][2:]
upgrades['e'] = upgrades['r'][3:]
upgrades['e'][upgrades['e'].index(1000)] = 400
upgrades['l'] = upgrades['e'][3:]
upgrades['l'][upgrades['l'].index(8000)] = 5000
for rarity in upgrades:
	upgrades[rarity].insert(0, 0)


# print(upgrades)
totalupgrades = {}
for rarity in upgrades:
	totalupgrades[rarity] = []
	for index, cost in enumerate(upgrades[rarity]):
		totalupgrades[rarity].append(sum(upgrades[rarity][:index+1]))

class CRTags:

	def __init__(self, bot):
		self.settings = dataIO.load_json(SETTINGS_JSON)
		self.backsettings = dataIO.load_json(BACKSETTINGS_JSON)
		self.clansettings = dataIO.load_json(CLAN_JSON)
		self.bot = bot

	@commands.group(pass_context=True)
	async def clan(self, ctx):
		"""get clan info
		"""
		# racfserver = self.bot.get_server('218534373169954816')
		# await self.bot.say(racfserver.get_member('222925389641547776').mention)
		# await self.bot.say(server.get_member('222925389641547776').mention)
		# print(dir(CRClan('QUYCYV8', ctx)))
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)

	@clan.command(name='get',pass_context=True)
	async def get_clan(self, ctx, keyortag):
		user = ctx.message.author
		keyortag = keyortag.upper()
		tag = ''
		valid = True
		for letter in keyortag:
			if letter not in validChars:
				valid = False
				break
		if keyortag in self.clansettings:
			tag = self.clansettings[keyortag]
		elif valid:
			tag = keyortag
		else:
			await self.bot.say('`{}` is not in the database, nor is an acceptable tag.'.format(keyortag))
			return
		clanurl = statsurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = CRClan(tag, ctx)
		clan_data = []
		member_data = [] # for displaying all members 
		clan_data.append(clan.desc)
		clan_data.append(clan.leader['formatted'])
		clan_data.append("Clan Tag: [`{}`]({})".format(tag, clan.clan_url))
		clan_data.append("Clan Score: [{}](nothing)".format(clan.clan_trophy))
		clan_data.append("Trophy Requirement: [{}](nothing)".format(clan.tr_req))
		# clan_data.append("")
		# n = 0
		# while n<len(clan.members):
		#     await self.bot.say(clan.members[n])
		#     n += 1
		# return
		members2display = clan.members
		n = 0
		members_per_embed = 13
		member_data = [] # for displaying all members
		while n<int(len(members2display)/members_per_embed+1):
			member_data.append([])
			n += 1

		n = 0
		while n<int(len(members2display)/members_per_embed+1):
			try:
				membersection = members2display[(n)*members_per_embed:(n+1)*members_per_embed]
			except:
				membersection = members2display[(n)*members_per_embed:]
			# await self.bot.say(membersection)
			for member in membersection:
				memberstring = member['formatted']
				member_data[n].append(memberstring)
			n += 1


		em = []

		if len(clan_data)>0:
			em.append(discord.Embed(title=clan.name, description='\n'.join(clan_data),color = discord.Color(0x50d2fe)))
		for data in member_data:
			if len(em) == 0:
				em.append(discord.Embed(title=clan.name, description='\n'.join(data),color = discord.Color(0x50d2fe)))
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')


		for e in em:
			await self.bot.say(embed=e)

	@clan.command(name='roster',pass_context=True)
	async def clanroster(self, ctx, keyortag):
		user = ctx.message.author
		keyortag = keyortag.upper()
		tag = ''
		valid = True
		for letter in keyortag:
			if letter not in validChars:
				valid = False
				break
		if keyortag in self.clansettings:
			tag = self.clansettings[keyortag]
		elif valid:
			tag = keyortag
		else:
			await self.bot.say('`{}` is not in the database, nor is an acceptable tag.'.format(keyortag))
			return
		clanurl = statsurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = CRClan(tag, ctx)
		clan_data = []
		member_data = [] # for displaying all members 
		# clan_data.append(clan.desc)
		# clan_data.append(clan.leader['formatted'])
		# clan_data.append("Clan Tag: [`{}`]({})".format(tag, clan.clan_url))
		# clan_data.append("Clan Score: [{}](nothing)".format(clan.clan_trophy))
		# clan_data.append("Trophy Requirement: [{}](nothing)".format(clan.tr_req))
		# clan_data.append("")
		# n = 0
		# while n<len(clan.members):
		#     await self.bot.say(clan.members[n])
		#     n += 1
		# return
		members2display = clan.members
		n = 0
		members_per_embed = 13
		member_data = [] # for displaying all members
		while n<int(len(members2display)/members_per_embed+1):
			member_data.append([])
			n += 1

		n = 0
		while n<int(len(members2display)/members_per_embed+1):
			try:
				membersection = members2display[(n)*members_per_embed:(n+1)*members_per_embed]
			except:
				membersection = members2display[(n)*members_per_embed:]
			# await self.bot.say(membersection)
			for member in membersection:
				memberstring = member['formatted']
				member_data[n].append(memberstring)
			n += 1


		em = []

		if len(clan_data)>0:
			em.append(discord.Embed(title=clan.name, description='\n'.join(clan_data),color = discord.Color(0x50d2fe)))
		for data in member_data:
			if len(em) == 0:
				em.append(discord.Embed(title=clan.name, description='\n'.join(data),color = discord.Color(0x50d2fe)))
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')


		for e in em:
			await self.bot.say(embed=e)


	@clan.command(name='coleaders',aliases=['cos', 'coleader'],pass_context=True)
	async def clancoleaders(self, ctx, keyortag):
		user = ctx.message.author
		keyortag = keyortag.upper()
		tag = ''
		valid = True
		for letter in keyortag:
			if letter not in validChars:
				valid = False
				break
		if keyortag in self.clansettings:
			tag = self.clansettings[keyortag]
		elif valid:
			tag = keyortag
		else:
			await self.bot.say('`{}` is not in the database, nor is an acceptable tag.'.format(keyortag))
			return
		clanurl = statsurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = CRClan(tag, ctx)
		clan_data = []
		member_data = [] # for displaying all members 
		# clan_data.append(clan.desc)
		# clan_data.append(clan.leader['formatted'])
		# clan_data.append("Clan Tag: [`{}`]({})".format(tag, clan.clan_url))
		# clan_data.append("Clan Score: [{}](nothing)".format(clan.clan_trophy))
		# clan_data.append("Trophy Requirement: [{}](nothing)".format(clan.tr_req))
		# clan_data.append("")
		# n = 0
		# while n<len(clan.members):
		#     await self.bot.say(clan.members[n])
		#     n += 1
		# return
		members2display = clan.coleaders
		n = 0
		members_per_embed = 13
		member_data = [] # for displaying all members
		while n<int(len(members2display)/members_per_embed+1):
			member_data.append([])
			n += 1

		n = 0
		while n<int(len(members2display)/members_per_embed+1):
			try:
				membersection = members2display[(n)*members_per_embed:(n+1)*members_per_embed]
			except:
				membersection = members2display[(n)*members_per_embed:]
			# await self.bot.say(membersection)
			for member in membersection:
				memberstring = member['formatted']
				member_data[n].append(memberstring)
			n += 1


		em = []

		if len(clan_data)>0:
			em.append(discord.Embed(title=clan.name, description='\n'.join(clan_data),color = discord.Color(0x50d2fe)))
		for data in member_data:
			if len(em) == 0:
				em.append(discord.Embed(title=clan.name, description='\n'.join(data),color = discord.Color(0x50d2fe)))
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')


		for e in em:
			await self.bot.say(embed=e)



	@clan.command(name='elders',aliases=['elder'],pass_context=True)
	async def clanelders(self, ctx, keyortag):
		user = ctx.message.author
		keyortag = keyortag.upper()
		tag = ''
		valid = True
		for letter in keyortag:
			if letter not in validChars:
				valid = False
				break
		if keyortag in self.clansettings:
			tag = self.clansettings[keyortag]
		elif valid:
			tag = keyortag
		else:
			await self.bot.say('`{}` is not in the database, nor is an acceptable tag.'.format(keyortag))
			return
		clanurl = statsurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = CRClan(tag, ctx)
		clan_data = []
		member_data = [] # for displaying all members 
		# clan_data.append(clan.desc)
		# clan_data.append(clan.leader['formatted'])
		# clan_data.append("Clan Tag: [`{}`]({})".format(tag, clan.clan_url))
		# clan_data.append("Clan Score: [{}](nothing)".format(clan.clan_trophy))
		# clan_data.append("Trophy Requirement: [{}](nothing)".format(clan.tr_req))
		# clan_data.append("")
		# n = 0
		# while n<len(clan.members):
		#     await self.bot.say(clan.members[n])
		#     n += 1
		# return
		members2display = clan.elders
		n = 0
		members_per_embed = 13
		member_data = [] # for displaying all members
		while n<int(len(members2display)/members_per_embed+1):
			member_data.append([])
			n += 1

		n = 0
		while n<int(len(members2display)/members_per_embed+1):
			try:
				membersection = members2display[(n)*members_per_embed:(n+1)*members_per_embed]
			except:
				membersection = members2display[(n)*members_per_embed:]
			# await self.bot.say(membersection)
			for member in membersection:
				memberstring = member['formatted']
				member_data[n].append(memberstring)
			n += 1


		em = []

		if len(clan_data)>0:
			em.append(discord.Embed(title=clan.name, description='\n'.join(clan_data),color = discord.Color(0x50d2fe)))
		for data in member_data:
			if len(em) == 0:
				em.append(discord.Embed(title=clan.name, description='\n'.join(data),color = discord.Color(0x50d2fe)))
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')


		for e in em:
			await self.bot.say(embed=e)




	@clan.command(name='norole',aliases=['members'],pass_context=True)
	async def clannorole(self, ctx, keyortag):
		user = ctx.message.author
		keyortag = keyortag.upper()
		tag = ''
		valid = True
		for letter in keyortag:
			if letter not in validChars:
				valid = False
				break
		if keyortag in self.clansettings:
			tag = self.clansettings[keyortag]
		elif valid:
			tag = keyortag
		else:
			await self.bot.say('`{}` is not in the database, nor is an acceptable tag.'.format(keyortag))
			return
		clanurl = statsurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = CRClan(tag, ctx)
		clan_data = []
		member_data = [] # for displaying all members 
		# clan_data.append(clan.desc)
		# clan_data.append(clan.leader['formatted'])
		# clan_data.append("Clan Tag: [`{}`]({})".format(tag, clan.clan_url))
		# clan_data.append("Clan Score: [{}](nothing)".format(clan.clan_trophy))
		# clan_data.append("Trophy Requirement: [{}](nothing)".format(clan.tr_req))
		# clan_data.append("")
		# n = 0
		# while n<len(clan.members):
		#     await self.bot.say(clan.members[n])
		#     n += 1
		# return
		members2display = clan.norole
		n = 0
		members_per_embed = 13
		member_data = [] # for displaying all members
		while n<int(len(members2display)/members_per_embed+1):
			member_data.append([])
			n += 1

		n = 0
		while n<int(len(members2display)/members_per_embed+1):
			try:
				membersection = members2display[(n)*members_per_embed:(n+1)*members_per_embed]
			except:
				membersection = members2display[(n)*members_per_embed:]
			# await self.bot.say(membersection)
			for member in membersection:
				memberstring = member['formatted']
				member_data[n].append(memberstring)
			n += 1


		em = []

		if len(clan_data)>0:
			em.append(discord.Embed(title=clan.name, description='\n'.join(clan_data),color = discord.Color(0x50d2fe)))
		for data in member_data:
			if len(em) == 0:
				em.append(discord.Embed(title=clan.name, description='\n'.join(data),color = discord.Color(0x50d2fe)))
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')


		for e in em:
			await self.bot.say(embed=e)


	@clan.command(name='info',pass_context=True)
	async def claninfo(self, ctx, keyortag):
		user = ctx.message.author
		keyortag = keyortag.upper()
		tag = ''
		valid = True
		for letter in keyortag:
			if letter not in validChars:
				valid = False
				break
		if keyortag in self.clansettings:
			tag = self.clansettings[keyortag]
		elif valid:
			tag = keyortag
		else:
			await self.bot.say('`{}` is not in the database, nor is an acceptable tag.'.format(keyortag))
			return
		clanurl = statsurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = CRClan(tag, ctx)
		clan_data = []
		member_data = [] # for displaying all members 
		clan_data.append(clan.desc)
		clan_data.append(clan.leader['formatted'])
		clan_data.append("Clan Tag: [`{}`]({})".format(tag, clan.clan_url))
		clan_data.append("Clan Score: [{}](nothing)".format(clan.clan_trophy))
		clan_data.append("Trophy Requirement: [{}](nothing)".format(clan.tr_req))


		em = []

		if len(clan_data)>0:
			em.append(discord.Embed(title=clan.name, description='\n'.join(clan_data),color = discord.Color(0x50d2fe)))
		for data in member_data:
			if len(em) == 0:
				em.append(discord.Embed(title=clan.name, description='\n'.join(data),color = discord.Color(0x50d2fe)))
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')


		for e in em:
			await self.bot.say(embed=e)


	@clan.command(name='set', pass_context=True)
	async def clansettag(self, ctx, tag, *, key):
		author = ctx.message.author
		key = key.upper()
		tag = tag.upper()
		tag.replace('O', '0')
		valid = True
		for letter in tag:
			if letter not in validChars:
				valid = False
		if valid: #self.is_valid(tag):
			self.clansettings[key] = str(tag)
			dataIO.save_json(CLAN_JSON, self.clansettings)
			await self.bot.say("Saved {} for {}".format(tag, key))
		else:
			await self.bot.say("Invalid tag {}, it must only have the following characters {}".format(author.mention), validChars)


	def goldcalc(self, cardlvl):
		allgold = 0
		for rarity in cardlvl:
			for lvl in cardlvl[rarity]:
				allgold += totalupgrades[rarity][lvl]
				# totalgold[rarity] += totalupgrades[rarity][lvl]
		return allgold

	def lvlsdict(self, args):
		currentrarity = 'c'
		cardlvl = {
			'c':[],
			'r':[],
			'e':[],
			'l':[]
		}
		for x in args:
			if str(x).isalpha():
				if x in ['c', 'r', 'e', 'l']:
					currentrarity = x
				else:
					ex = InvalidRarity()
					raise ex
			elif str(x).isdigit():
				cardlvl[currentrarity].append(x)
		return cardlvl
	@commands.command(pass_context=True)
	async def gold(self, ctx, *, args):
		totalgold = {'c':0,'r':0,'e':0,'l':0,}
		allgold = 0
		cardlvl = {
			'c':[],
			'r':[],
			'e':[],
			'l':[]
		}
		msg = "It would cost a total of"
		msg2 = "gold to upgrade those cards"
		args = args.strip().split(' ')
		if 'max' in args:
			msg2 = "gold to upgrade all cards to max"
			args = []
			n = 0
			for rarity in numcards:
				args.append(rarity)
				while n < numcards[rarity]:
					args.append(str(maxcards[rarity]))
					n += 1
				n = 0
		if 'tourney' in args:
			msg2 = "gold to upgrade all cards to tourney standard"
			args = []
			n = 0
			for rarity in numcards:
				args.append(rarity)
				while n < numcards[rarity]:
					args.append(str(tourneycards[rarity]))
					n += 1
				n = 0
		if args.count('-') >1:
			await self.bot.say("too many minuses, limit is 1")
			return
		elif args.count('-') == 1:
			cardlvl = []
			allgold = []
			args = ' '.join(args).split('-')
			for index, arg in enumerate(args):
				args[index] = arg.strip().split(' ')
			for arg in args:
				while '' in arg:
					arg.remove('')

				for i, a in enumerate(arg):
					if a.isdigit():
						arg[i] = int(a)-1
			for arg in args:
				try:
					cardlvl.append(self.lvlsdict(arg))
				except InvalidRarity:
					await self.bot.say("Invalid Rarity")
			for c in cardlvl:
				try:
					allgold.append(self.goldcalc(c))
				except IndexError:
					await self.bot.say("Invalid card level")
			formattedgold = locale.format("%d", allgold[0]-allgold[1], grouping=True)
		else:
			while '' in args:
				args.remove('')

			for i, a in enumerate(args):
				if a.isdigit():
					args[i] = int(a)-1
			currentrarity = 'c'
			try:
				cardlvl = self.lvlsdict(args)
			except InvalidRarity:
				await self.bot.say("Invalid Rarity")
				return
			print(cardlvl)
			try:
				allgold = self.goldcalc(cardlvl)
			except IndexError:
				await self.bot.say("Invalid card level")
			print(allgold)
			locale.setlocale(locale.LC_ALL, 'US')
			formattedgold = locale.format("%d", allgold, grouping=True)
		await self.bot.say("{} {} {}".format(msg, formattedgold, msg2))
		# for rarity in totalgold:
		#     await self.bot.say("You have spent a total of {} gold on upgrading {} cards".format(totalgold[rarity], rarity))

	def savetag(self, userid, tag):
		try:
			if not userid.isdigit():
				print("must save userid, tag not backwards")
				return
		except:
			return
		self.settings[userid] = str(tag)
		self.backsettings[str(tag)] = userid
		dataIO.save_json(SETTINGS_JSON, self.settings)
		dataIO.save_json(BACKSETTINGS_JSON, self.backsettings)

	def statsvalid(self, tag):
		for letter in tag:
			if letter not in validChars:
				return False
		return True

	async def async_refresh(self,url):
		async with aiohttp.get(url) as r:
			response = await r.json()
			return response

	async def refresh(self, tag):
		await self.async_refresh('http://statsroyale.com/profile/'+tags[user.id]+'/refresh')

	@commands.command(pass_context=True)
	async def myid(self, ctx, user: discord.Member):
		"""show your discord ID"""
		if user == None:
			user=ctx.message.author
		await self.bot.say("ID: {}".format(user.id))

	@commands.command(pass_context=True)
	async def copysettings2back(self, ctx):
		for x in self.settings:
			self.backsettings[self.settings[x]] = x
		print(self.backsettings)
		dataIO.save_json(BACKSETTINGS_JSON, self.backsettings)


	@commands.command(pass_context=True)
	async def settag(self, ctx, tag):
		"""Save user tag. If not given a user, save tag to author"""
		tag = tag.upper()
		tag.replace('O', '0')
		valid = True
		for letter in tag:
			if letter not in validChars:
				valid = False
		if valid: #self.is_valid(tag):
			author = ctx.message.author
			self.savetag(author.id, tag)
			await self.bot.say("Saved {} for {}".format(tag, author.display_name))
		else:
			await self.bot.say("Invalid tag {}, it must only have the following characters {}".format(author.mention), validChars)

	@commands.command(pass_context=True)
	async def mergejsons(self, ctx):
		tags1 = dataIO.load_json(SETTINGS_JSON)
		tags2 = dataIO.load_json(SETTINGS2_JSON)
		tags3 = {}
		for x in tags1:
			tags3[x] = tags1[x]
		for x in tags2:
			tags3[x] = tags2[x]
		list3 = sorted(tags3)

		tags4 = {}
		for x in list3:
			tags4[x] = tags3[x]
		for x in tags4:
			self.settings[x] = tags4[x]
			dataIO.save_json(SET_JSON, self.settings)
		print(len(self.settings))
		dataIO.save_json(SET_JSON, self.settings)

	@commands.command(pass_context=True)
	async def setusertag(self, ctx, user: discord.Member, tag):
		"""Save user tag. If not given a user, save tag to author"""
		if user == None:
			user = ctx.message.author
		tag = tag.upper()
		tag.replace('O', '0')
		valid = True
		for letter in tag:
			if letter not in validChars:
				valid = False
		if valid: #self.is_valid(tag):
			author = ctx.message.author
			await self.bot.say("Saving {} for {}".format(tag, user.display_name))
			self.savetag(user.id, tag)
		else:
			await self.bot.say("Invalid tag {}, it must only have the following characters {}".format(ctx.message.author.mention, validChars))
	# @commands.command(pass_context=True)
	# async def initall(self, ctx):
	#     racfserver = self.bot.get_server('218534373169954816')
	#     auditchannel = self.bot.get_channel('268769178234781696')
	#     members = racfserver.members
	#     n = 0
	#     for member in members:
	#         m = await self.bot.send_message(auditchannel, '!crprofile gettag '+member.id)
	#         await asyncio.sleep(4)
	#         await self.bot.delete_message(m)
	#         messages = []
	#         async for m in self.bot.logs_from(auditchannel, limit=10):
	#             if(m.author.id == '280936035536338945'):
	#                 messages.append(m)
	#                 break
	#         message = messages[0].content
	#         if(message.find('#') == -1):
	#             pass
	#         else:
	#             tag = message[message.find('#')+1:]
	#             self.settings[str(member.id)] = tag

	#             # await self.bot.send_message(auditchannel, member.display_name + ' ' + tag)
	#         n += 1
	#         print(n)
	#     dataIO.save_json(SETTINGS_JSON, self.settings)


	# @commands.command(pass_context=True)
	# async def racfinitall(self, ctx):
	#     """macro for s.racfinit"""
	#     await self.bot.say('s.racfinit alpha', delete_after=1)
	#     await self.bot.say('s.racfinit bravo', delete_after=1)
	#     await self.bot.say('s.racfinit charlie', delete_after=1)
	#     await self.bot.say('s.racfinit delta', delete_after=1)
	#     await self.bot.say('s.racfinit echo', delete_after=1)
	#     await self.bot.say('s.racfinit foxtrot', delete_after=1)
	#     await self.bot.say('s.racfinit golf', delete_after=1)
	#     await self.bot.say('s.racfinit hotel', delete_after=1)
	#     await self.bot.say('s.racfinit esports', delete_after=1)
	#     await self.bot.say('s.racfinit mini', delete_after=1)
	#     await self.bot.say('s.racfinit mini2', delete_after=1)

	# @commands.command(pass_context=True)
	# async def racfinit(self,ctx, clan:str):
	#     """Save user tag. If not given a user, save tag to author"""
	#     racfaudits = self.bot.get_channel('268769178234781696')
	#     await self.bot.send_message(racfaudits, '!crclan roster '+clan, delete_after=5)
	#     await asyncio.sleep(5)
	#     messages = []
	#     async for m in self.bot.logs_from(racfaudits, limit=10):
	#         if(m.author.id == '280936035536338945'):
	#             messages.append(m)
	#     messages = messages[:2]
	#     # for m in messages:
	#     # print(messages)
	#     # await self.bot.say()
	#     playerids = []
	#     playertags = []
	#     for index, message in enumerate(messages):
	#         for i, person in enumerate(messages[index].embeds[0]['fields']):
	#             messages[index].embeds[0]['fields'][i]['name'] =  ''
	#         for i, person in enumerate(messages[index].embeds[0]['fields']):
	#             messages[index].embeds[0]['fields'][i]['value'] =  messages[index].embeds[0]['fields'][i]['value'].replace('\u2193','').replace('\u2191','').replace('`','').replace('League','')
	#             value = messages[index].embeds[0]['fields'][i]['value']
	#             # print(value)
	#             messages[index].embeds[0]['fields'][i]['value'] = messages[index].embeds[0]['fields'][i]['value'][messages[index].embeds[0]['fields'][i]['value'].find('<@')+len('<@'):]
	#             value = messages[index].embeds[0]['fields'][i]['value']
	#             # print(value)
	#             try:
	#                 playerid = int(value[:value.find('>')].replace('!',''))
	#                 playerids.append(playerid)
	#                 playertags.append(value[value.find('#')+len('#'):])
	#             except:
	#                 pass
	#     print(260577636957421568 in playerids)
	#     print(playerids)
	#     print(playertags)
	#     for x in range(0, len(playerids)):
	#         self.settings[str(playerids[x])] = playertags[x]
	#         dataIO.save_json(SETTINGS_JSON, self.settings)
	#     await self.bot.say("initalized", delete_after=1)
	#     await self.bot.delete_message(ctx.message)
	#     return

	@commands.command(pass_context=True)
	async def gettag(self, ctx, user: discord.Member=None):
		"""Get user tag. If not given a user, get author's tag"""
		tags = dataIO.load_json(SETTINGS_JSON)
		try:
			test = tags[user.id]
		except(KeyError):
			await self.bot.say("{} does not have a tag set.".format(user.display_name))
			return
		if(user==None):
			if tags[ctx.message.author.id]:
				await self.bot.say("Your tag is {}.".format(tags[ctx.message.author.id]))
			else:
				await self.bot.say("You, {} do not have a tag set.".format(ctx.message.author.display_name))
		else:
			if tags[user.id]:
				await self.bot.say("{}'s tag is {}.".format(user.mention, tags[user.id]))
			else:
				await self.bot.say("User {} does not have a tag set.".format(user.display_name))
		# #update profile
		# driver = webdriver.Firefox()
		# driver.get(user_url)#put here the adress of your page
		# try:
		#     driver.find_element_by_xpath(".//*[@id='refreshProfile']").click()
		# except:
		#     pass
		# # print(elem.get_attribute("class"))
		# try:
		#     driver.find_element_by_xpath(".//*[@id='refreshBattles']").click()
		# except:
		#     pass
		# driver.close()

	@commands.group(aliases=["stats"], pass_context=True)
	async def clashroyale(self, ctx):
		"""Display CR profiles."""
		await self.bot.delete_message(ctx.message)
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)


	# @clashroyale.command(pass_context=True)
	# async def profile(self, ctx, user: discord.Member=None):
	#     """Get user profile. If not given a user, get author's profile"""
	#     tags = dataIO.load_json(SETTINGS_JSON)
	#     if user == None:
	#         user = ctx.message.author
	#     try:
	#         user_url = (statscr_url+ tags[user.id])
	#     except(KeyError):
	#         await self.bot.say("{} does not have a tag set.".format(user.display_name))
	#         return
	#     button = []
	#     battleButton = ""
	#     await self.async_refresh('http://statsroyale.com/profile/'+tags[user.id]+'/refresh')
	#     r = requests.get(user_url, headers=headers)
	#     html_doc = r.content
	#     soup = BeautifulSoup(html_doc, "html.parser")
	#     statsurl = 'http://statsroyale.com'
	#     html_doc = r.content
	#     chests_queue = soup.find('div', {'class':'chests__queue'})
	#     self.chests = chests_queue.get_text().split()
	#     for index, item in enumerate(self.chests):
	#         if item.startswith('+') and item.endswith(':'):
	#             del self.chests[index]
	#         elif item == 'Chest':
	#             del self.chests[index]
	#         if item == 'Super':
	#             self.chests[index] = 'SMC'
	#         elif item == 'Magic':
	#             self.chests[index] = 'Magical'

	#     for index, chest in enumerate(self.chests):
	#         if str(chest) == 'Magic':
	#             self.chests[index] = 'Magical'
	#         elif str(chest) == 'Super':
	#             self.chests[index] = 'SMC'
	#     new_chests = []
	#     x = 0
	#     while x<len(chests):
	#         new_chests.append(chests[x:x+2])
	#         x += 2
	#     chests = []


	#     for index, chest in enumerate(new_chests):
	#         chests.append(': '.join(chest))

	#     chests = '\n'.join(chests)

	#     soup = BeautifulSoup(html_doc, "html.parser")
	#     profilehead = soup.find_all("div", "profileHeader profile__header")
	#     statistics = soup.find_all("div", "statistics profile__statistics")
	#     profilehead = profilehead[0]
	#     statistics = statistics[0]
	#     thing2 = statistics.get_text()
	#     thing2 = thing2.replace('\n', ' ')
	#     thing2 = thing2.split('   ')
	#     for index, item in enumerate(thing2):
	#         thing2[index] = item.strip()
	#     statsdict = {}
	#     for index, item in enumerate(thing2):
	#         if item[:item.find(' ')].isdigit():
	#             thing2[index] = item[item.find(' ')+1:]+ ': '+item[:item.find(' ')]
	#             statsdict[item[item.find(' ')+1:].strip()] = item[:item.find(' ')] 
	#         else:
	#             statsdict[item.strip()] = ' '
	#         thing2[index].strip()

	#     pb = thing2[0]
	#     trophy = thing2[1]
	#     cardswon = thing2[2]
	#     tcardswon = thing2[3]
	#     donations = thing2[4]
	#     prevseasonrank = thing2[5]
	#     prevseasontrophy = thing2[6]
	#     prevseasonpb = thing2[7]
	#     wins = thing2[8]
	#     losses = thing2[9]
	#     crown3 = thing2[10]
	#     league = thing2[11]
	#     # thing3 = []
	#     # a  = ''
	#     # for x in thing2:
	#     #     a += ''
	#     clan_url = statsurl + str(profilehead.find('a').attrs['href'])
	#     playerLevel = profilehead.find('span', 'profileHeader__userLevel')
	#     playerLevel = playerLevel.text
	#     playerName = profilehead.find('div', 'ui__headerMedium profileHeader__name').text.strip()
	#     playerName = playerName.replace(playerLevel, '').strip()
	#     playerClan = profilehead.find('a', 'ui__link ui__mediumText profileHeader__userClan').text.strip()
	#     playerTag = tags[user.id]
	#     player_data = []
	#     player_data.append('[#{}]({})'.format(tags[user.id], user_url))
	#     player_data.append('Level {}'.format(playerLevel))
	#     player_data.append('Clan: [{}]({})'.format(playerClan, clan_url))
	#     for x in statsdict:
	#         if(statsdict[x].isdigit()):
	#             statsdict[x] = '[' + statsdict[x] + '](nothing)'
	#     for x in statsdict:
	#         if(x=='Prev season rank' and statsdict[x]=='0'):
	#             pass
	#         elif(statsdict[x]==' '):
	#             a = x
	#             a = a.replace('crown', 'crown👑')
	#             player_data.append(a)
	#         else:
	#             a = x+': '+statsdict[x]
	#             a = a.replace('crown', 'crown👑')
	#             if 'troph' in a:
	#                 a += '🏆'
	#             player_data.append(a)
	#     # player_data.append(chests)
	#     clan_badge = profilehead.find('img').attrs['src']
	#     clan_badge = statsurl + clan_badge
	#     if clan_badge == 'http://statsroyale.com/images/badges/16000167.png':
	#         clan_badge = 'http://cr-api.com/badge/A_Char_Rocket_02.png'
	#     em = discord.Embed(title=playerName, description='\n'.join(player_data),color = discord.Color(0x50d2fe))
	#     em.set_author(icon_url=user.avatar_url,name=user.display_name)
	#     em.set_thumbnail(url=clan_badge)
	#     em.set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')
	#     await self.bot.say(embed=em)
		# return
		# d = soup.find_all("div", "description")
		# c = soup.find_all("div", "content")
		# b = soup.find_all("span", "supercell")
		# misc = []
		# desc = []
		# cont = []

		# for w in b:
		#     # print("(misc)Type: {}, contents: {}".format(type(w.text), w.text))
		#     misc.append(w.text)
		# print("Misc: {}".format(misc))
		# for x in d:
		#     # print("(description)Type: {}, contents: {}".format(type(x.text), x.text))
		#     desc.append(x.text)
		# for y in c:
		#     # print("(content)Type: {}, contents: {}".format(type(y.text), y.text))
		#     cont.append(y.text)
		# data = discord.Embed(description="", colour=user.colour)
		# data.add_field(name="CR Name: ", value=name)
		# data.add_field(name="Level: ", value=misc[0])
		# for i in range(1, NUMITEMS):
		#     data.add_field(name=desc[i]+":", value=cont[i], inline=True)
		# data.set_footer(text="Tag: {}".format(tags[user.id]))

		# name = str(user)
		# name = " ~ ".join((name, user.nick)) if user.nick else name

		# if user.avatar_url:
		#     data.set_author(name=name, url=user.avatar_url)
		#     data.set_thumbnail(url=user.avatar_url)
		# else:
		#     data.set_author(name=name)

		# try:
		#     await self.bot.say(embed=data)
		# except discord.HTTPException:
		#     await self.bot.say("I need the `Embed links` permission "
		#                        "to send this")

		
	@clashroyale.command(name='trophy', aliases=['tr'],  pass_context=True)
	async def _trophy(self, ctx, userortag=None):
		"""Get user trophies. If not given a user, get author's data"""
		tags = dataIO.load_json(SETTINGS_JSON)
		tag = None
		userid = None
		valid=False
		if userortag != None:
			valid = True
			for letter in userortag.upper():
				if letter not in validChars:
					valid = False
		if userortag == None: #assume author if none
			userid = ctx.message.author.id
		elif userortag.startswith('<@'): #assume mention
			userid = userortag[2:-1]
		elif userortag.isdigit(): #assume userid
			userid = userortag
		elif valid: #assume it is a tag
			tag = userortag.upper()
		else:	#assume member name
			for member in list(ctx.message.server.members):
				name = member.name
				if userortag == name:
					userid = member.id
				elif userortag == name + '#' + member.discriminator:
					userid = member.id
		if userid != None:
			user = ctx.message.server.get_member(userid)
		if tag == None:
			if userid in tags:
				tag = tags[userid]
			else:
				await self.bot.say("{} does not have a tag set.".format(user.display_name))
				return
		
		user_url = (statscr_url+ tag)
		things = CRPlayer(tag)
		player_data  = []
		player_data.append('[{}]({})'.format(tag, user_url))
		# player_data.append(things.pb)
		player_data.append(things.trophy)
		# player_data.append(things.cardswon)
		# player_data.append(things.tcardswon)
		# player_data.append(things.donations)
		# player_data.append(things.prevseasonrank)
		# player_data.append(things.prevseasontrophy)
		# player_data.append(things.prevseasonpb)
		# player_data.append(things.wins)
		# player_data.append(things.losses)
		# player_data.append(things.crown3)
		# player_data.append(things.league)
		# player_data.append(things.chests)
		em = discord.Embed(title=things.name, description='\n'.join(player_data),color = discord.Color(0x50d2fe))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em.set_author(icon_url=user.avatar_url,name=discordname)
		em.set_thumbnail(url=things.clan_badge)
		em.set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')
		await self.bot.say(embed=em)

		
	@clashroyale.command(name='chests',  pass_context=True)
	async def _chests(self, ctx, userortag=None):
		"""Get user trophies. If not given a user, get author's data"""
		tags = dataIO.load_json(SETTINGS_JSON)
		tag = None
		userid = None
		valid=False
		if userortag != None:
			valid = True
			for letter in userortag.upper():
				if letter not in validChars:
					valid = False
		if userortag == None: #assume author if none
			userid = ctx.message.author.id
		elif userortag.startswith('<@'): #assume mention
			userid = userortag[2:-1]
		elif userortag.isdigit(): #assume userid
			userid = userortag
		elif valid: #assume it is a tag
			tag = userortag.upper()
		else:	#assume member name
			for member in list(ctx.message.server.members):
				name = member.name
				if userortag == name:
					userid = member.id
				elif userortag == name + '#' + member.discriminator:
					userid = member.id
		if userid != None:
			user = ctx.message.server.get_member(userid)
		if tag == None:
			if userid in tags:
				tag = tags[userid]
			else:
				await self.bot.say("{} does not have a tag set.".format(user.display_name))
				return
		
		user_url = (statscr_url+ tag)
		things = CRPlayer(tag)
		player_data  = []
		player_data.append('[{}]({})'.format(tag, user_url))
		# player_data.append(things.pb)
		# player_data.append(things.trophy)
		# player_data.append(things.cardswon)
		# player_data.append(things.tcardswon)
		# player_data.append(things.donations)
		# player_data.append(things.prevseasonrank)
		# player_data.append(things.prevseasontrophy)
		# player_data.append(things.prevseasonpb)
		# player_data.append(things.wins)
		# player_data.append(things.losses)
		# player_data.append(things.crown3)
		# player_data.append(things.league)
		player_data.append(things.chests)
		em = discord.Embed(title=things.name, description='\n'.join(player_data),color = discord.Color(0x50d2fe))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em.set_author(icon_url=user.avatar_url,name=discordname)
		em.set_thumbnail(url=things.clan_badge)
		em.set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')
		await self.bot.say(embed=em)


	@clashroyale.command(name='cardswon', aliases=['cards'],  pass_context=True)
	async def _cardswon(self, ctx, userortag=None):
		"""Get user trophies. If not given a user, get author's data"""
		tags = dataIO.load_json(SETTINGS_JSON)
		tag = None
		userid = None
		valid=False
		if userortag != None:
			valid = True
			for letter in userortag.upper():
				if letter not in validChars:
					valid = False
		if userortag == None: #assume author if none
			userid = ctx.message.author.id
		elif userortag.startswith('<@'): #assume mention
			userid = userortag[2:-1]
		elif userortag.isdigit(): #assume userid
			userid = userortag
		elif valid: #assume it is a tag
			tag = userortag.upper()
		else:	#assume member name
			for member in list(ctx.message.server.members):
				name = member.name
				if userortag == name:
					userid = member.id
				elif userortag == name + '#' + member.discriminator:
					userid = member.id
		if userid != None:
			user = ctx.message.server.get_member(userid)
		if tag == None:
			if userid in tags:
				tag = tags[userid]
			else:
				await self.bot.say("{} does not have a tag set.".format(user.display_name))
				return
		
		user_url = (statscr_url+ tag)
		things = CRPlayer(tag)
		player_data  = []
		player_data.append('[{}]({})'.format(tag, user_url))
		# player_data.append(things.pb)
		# player_data.append(things.trophy)
		player_data.append(things.cardswon)
		player_data.append(things.tcardswon)
		# player_data.append(things.donations)
		# player_data.append(things.prevseasonrank)
		# player_data.append(things.prevseasontrophy)
		# player_data.append(things.prevseasonpb)
		# player_data.append(things.wins)
		# player_data.append(things.losses)
		# player_data.append(things.crown3)
		# player_data.append(things.league)
		player_data.append(things.chests)
		em = discord.Embed(title=things.name, description='\n'.join(player_data),color = discord.Color(0x50d2fe))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em.set_author(icon_url=user.avatar_url,name=discordname)
		em.set_thumbnail(url=things.clan_badge)
		em.set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')
		await self.bot.say(embed=em)


	@clashroyale.command(pass_context=True)
	async def profile(self, ctx, userortag=None):
		"""Get user trophies. If not given a user, get author's data"""
		tags = dataIO.load_json(SETTINGS_JSON)
		tag = None
		userid = None
		valid=False
		if userortag != None:
			valid = True
			for letter in userortag.upper():
				if letter not in validChars:
					valid = False
		if userortag == None: #assume author if none
			userid = ctx.message.author.id
		elif userortag.startswith('<@'): #assume mention
			userid = userortag[2:-1]
		elif userortag.isdigit(): #assume userid
			userid = userortag
		elif valid: #assume it is a tag
			tag = userortag.upper()
		else:	#assume member name
			for member in list(ctx.message.server.members):
				name = member.name
				if userortag == name:
					userid = member.id
				elif userortag == name + '#' + member.discriminator:
					userid = member.id
		if userid != None:
			user = ctx.message.server.get_member(userid)
		if tag == None:
			if userid in tags:
				tag = tags[userid]
			else:
				await self.bot.say("{} does not have a tag set.".format(user.display_name))
				return
		
		user_url = (statscr_url+ tag)
		things = CRPlayer(tag)
		player_data  = []
		player_data.append('[{}]({})'.format(tag, user_url))
		player_data.append('[{}]({})'.format(things.clan,things.clan_url))
		player_data.append(things.pb)
		player_data.append(things.trophy)
		player_data.append(things.cardswon)
		player_data.append(things.tcardswon)
		player_data.append(things.donations)
		player_data.append(things.prevseasonrank)
		player_data.append(things.prevseasontrophy)
		player_data.append(things.prevseasonpb)
		player_data.append(things.wins)
		player_data.append(things.losses)
		player_data.append(things.crown3)
		player_data.append(things.league)
		# player_data.append(things.chests)
		em = discord.Embed(title=things.name, description='\n'.join(player_data),color = discord.Color(0x50d2fe))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em.set_author(icon_url=user.avatar_url,name=discordname)
		em.set_thumbnail(url=things.clan_badge)
		em.set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')
		await self.bot.say(embed=em)

	@clashroyale.command(name='pb', pass_context=True)
	async def _pb(self, ctx, userortag=None):
		"""Get user trophies. If not given a user, get author's data"""
		tags = dataIO.load_json(SETTINGS_JSON)
		tag = None
		userid = None
		valid=False
		if userortag != None:
			valid = True
			for letter in userortag.upper():
				if letter not in validChars:
					valid = False
		if userortag == None: #assume author if none
			userid = ctx.message.author.id
		elif userortag.startswith('<@'): #assume mention
			userid = userortag[2:-1]
		elif userortag.isdigit(): #assume userid
			userid = userortag
		elif valid: #assume it is a tag
			tag = userortag.upper()
		else:	#assume member name
			for member in list(ctx.message.server.members):
				name = member.name
				if userortag == name:
					userid = member.id
				elif userortag == name + '#' + member.discriminator:
					userid = member.id
		if userid != None:
			user = ctx.message.server.get_member(userid)
		if tag == None:
			if userid in tags:
				tag = tags[userid]
			else:
				await self.bot.say("{} does not have a tag set.".format(user.display_name))
				return
		
		user_url = (statscr_url+ tag)
		things = CRPlayer(tag)
		player_data  = []
		player_data.append('[{}]({})'.format(tag, user_url))
		player_data.append(things.pb)
		# player_data.append(things.trophy)
		# player_data.append(things.cardswon)
		# player_data.append(things.tcardswon)
		# player_data.append(things.donations)
		# player_data.append(things.prevseasonrank)
		# player_data.append(things.prevseasontrophy)
		# player_data.append(things.prevseasonpb)
		# player_data.append(things.wins)
		# player_data.append(things.losses)
		# player_data.append(things.crown3)
		# player_data.append(things.league)
		# player_data.append(things.chests)
		em = discord.Embed(title=things.name, description='\n'.join(player_data),color = discord.Color(0x50d2fe))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em.set_author(icon_url=user.avatar_url,name=discordname)
		em.set_thumbnail(url=things.clan_badge)
		em.set_footer(text='Data provided by StatsRoyale', icon_url='http://i.imgur.com/17R3DVU.png')
		await self.bot.say(embed=em)



def check_folder():
	if not os.path.exists(PATH):
		os.makedirs(PATH)

def check_file():
	defaults = {}
	if not dataIO.is_valid_json(SETTINGS_JSON):
		dataIO.save_json(SETTINGS_JSON, defaults)
	if not dataIO.is_valid_json(CLAN_JSON):
		dataIO.save_json(CLAN_JSON, defaults)
	if not dataIO.is_valid_json(BACKSETTINGS_JSON):
		dataIO.save_json(BACKSETTINGS_JSON, defaults)

def setup(bot):
	check_folder()
	check_file()
	bot.add_cog(CRTags(bot))
