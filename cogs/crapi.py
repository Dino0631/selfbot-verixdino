
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

racfclans = {
	"ALPHA" : "2CCCP",
	"BRAVO" : "2U2GGQJ",
	"CHARLIE" : "2QUVVVP",
	"DELTA" : "Y8GYCGV",
	"ECHO" : "LGVV2CG",
	"ESPORTS" : "R8PPJQG",
	"FOXTROT" : "QUYCYV8",
	"GOLF" : "GUYGVJY",
	"HOTEL" : "UGQ28YU",
	"MINI" : "22LR8JJ2",
	"MINI2" : "2Q09VJC8"
}

NUMITEMS = 9
statscr_url = "http://statsroyale.com/profile/"
crapiurl = 'http://api.cr-api.com'
statsurl = 'http://statsroyale.com'
PATH = os.path.join("data", "crapi")
SETTINGS_JSON = os.path.join(PATH, "settings.json")
BACKSETTINGS_JSON = os.path.join(PATH, "backsettings.json")
CLAN_JSON = os.path.join(PATH, "clan.json")
validChars = ['0', '2', '8', '9', 'C', 'G', 'J', 'L', 'P', 'Q', 'R', 'U', 'V', 'Y']
tags = {}
headers = {
	'User-Agent': 'Bot(Rain), (https://github.com/Dino0631/discordbot/tree/master)',
	'From': 'htmldino@gmail.com'  
}
class CRClan:

	def __init__(self):
		self.a = 1

	@classmethod
	async def create(self, tag):
		tag2id = dataIO.load_json(BACKSETTINGS_JSON)
		self.member_count = 0                           #done
		self.members = []                               #done
		self.clan_tag = tag                             #done
		self.clan_url = crapiurl + '/clan/' + tag       #done
		self.clanurl = self.clan_url.replace('api.', '', 1)#done
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
		async with aiohttp.ClientSession() as session:
			async with session.get(self.clan_url) as resp:
				datadict = await resp.json()
		

		for i, m in enumerate(datadict['members']):
			rank = str(m['currenRank'])
			name = str(m['name'])
			tag = str(m['tag'])
			url = crapiurl + tag
			level = str(m['expLevel'])
			trophy = str(m['score'])
			donations = str(m['donations'])
			role = str(m['roleName'])
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
			memberdict['formatted'] = '`'+ memberdict['role']+'` ' + memberdict['name']+' [`#'+memberdict['tag']+'`]('+memberdict['url'].replace('api.', '', 1)+')'
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

		self.clan_badge = crapiurl + datadict['badge_url']
		self.name = datadict['name']
		self.desc = datadict['description']
		d = self.desc
		d2 = d

		i = 0
		index = 0
		count = d2.lower().count('discord.')
		while i<count:
			index = d2.lower().find('discord.', index+1)
			d4 = d2.replace(d2[index:index+len('discord.')], 'discord.')
			d3 = d4[index:]
			endlink = d3[d3.find('discord.'):].find(' ')
			if endlink == -1:
				endlink = len(d3)
			discordlink = d3[d3.find('discord.'):endlink+d3.find('discord.')]
			d2 = d2.replace(d2[index:index+len(discordlink)], "[{}](https://{})".format(d2[index:index+len(discordlink)], discordlink))

			i += 1
		sym = '#'
		numtagsind2 = 0
		tagsind2 = []
		index = 0
		i = 0
		while i<d2.count(sym):
			index = d2.find(sym, index+1)
			x = ''
			i2 = 1
			thing = ''
			while x != ' ':
				thing += x
				x = d2[index+i2]
				i2 += 1
			valid = True
			for l in thing:
				if l not in validChars:
					valid=False
					break
			if valid and len(thing)>5:
				numtagsind2 += 1
				tagsind2.append(thing)
			i += 1
		for tag in tagsind2:
			d2 = d2.replace(sym+tag, '[{}]({})'.format(sym+tag, 'https://cr-api.com/clan/'+tag))
		self.desc2 =  d2
		self.clan_trophy = datadict['score']
		self.tr_req = datadict['requiredScore']
		self.donperweek = datadict['donations']
		return self







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
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)

	async def keyortag2tag(self, keyortag, ctx):
		keyortag = keyortag.upper()
		members = list(ctx.message.server.members)
		membernames = []
		memberswithdiscrim = []
		for member in members:
			membernames.append(member.name)
			memberswithdiscrim.append(member.name + '#' + str(member.discriminator))
		userid = None
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
		elif keyortag.startswith('<@'): #assume mention
			userid = keyortag[2:-1]
			userid = userid.replace('!', '')
		elif keyortag.isdigit(): #assume userid
			userid = keyortag
		elif keyortag in members or keyortag in membernames or keyortag in memberswithdiscrim:	#if user in members
			for member in members:
				name = member.name
				if keyortag == member:
					userid = member.id
				elif keyortag == name:
					userid = member.id
					break
				elif keyortag == name + '#' + member.discriminator:
					userid = member.id
					break
		else:
			await self.bot.say('`{}` is not in the database, nor is an acceptable tag.'.format(keyortag))
			return
		if userid != None:
			racfclantags = []
			try:
				usertag = self.settings[userid]
			except KeyError:
				await self.bot.say("That person is not in the database")
				return None
			for clan in self.clansettings:
				racfclantags.append(self.clansettings[clan])
			multiclanurl = crapiurl + '/clan/' + ','.join(racfclantags) + '?members=1'
			async with aiohttp.ClientSession() as session:
				async with session.get(multiclanurl) as resp:
					clans = await resp.json()
			
			for clan in clans:
				for member in clan['members']:
					if usertag == member['tag']:
						tag = clan['tag']
						break
		if tag == '':
			await self.bot.say("That person is not in RACF")
			tag =  None
		return tag


	@clan.command(name='get',pass_context=True)
	async def get_clan(self, ctx, keyortag=None):
		user = ctx.message.author
		if keyortag == None:
			keyortag = user.id
		tag = await self.keyortag2tag(keyortag, ctx)
		if tag == None:
			return
		clanurl = crapiurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = await CRClan.create(tag)
		clan_data = []
		member_data = [] # for displaying all members 
		clan_data.append(clan.desc2)
		clan_data.append(clan.leader['formatted'])
		clan_data.append("Clan Tag: [`{}`]({})".format(tag, clan.clanurl))
		clan_data.append("Clan Score: [{}](nothing)".format(clan.clan_trophy))
		clan_data.append("Trophy Requirement: [{}](nothing)".format(clan.tr_req))
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
			for member in membersection:
				memberstring = member['formatted']
				member_data[n].append(memberstring)
			n += 1


		em = []

		if len(clan_data)>0:
			em.append(discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='\n'.join(clan_data),color = discord.Color(0x50d2fe)))
		for data in member_data:
			if len(em) == 0:
				em.append(discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='\n'.join(data),color = discord.Color(0x50d2fe)))
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by {}'.format(crapiurl.replace('api.', '', 1)), icon_url='https://raw.githubusercontent.com/cr-api/cr-api-docs/master/docs/img/cr-api-logo-b.png')


		for e in em:
			await self.bot.say(embed=e)

	@clan.command(name='roster',pass_context=True)
	async def clanroster(self, ctx, keyortag=None):
		user = ctx.message.author
		if keyortag == None:
			keyortag = user.id
		tag = await self.keyortag2tag(keyortag, ctx)
		if tag == None:
			return
		clanurl = crapiurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = await CRClan.create(tag)
		clan_data = []
		member_data = [] # for displaying all members 
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
			for member in membersection:
				memberstring = member['formatted']
				member_data[n].append(memberstring)
			n += 1


		em = []

		if len(clan_data)>0:
			em.append(discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='\n'.join(clan_data),color = discord.Color(0x50d2fe)))
		for data in member_data:
			if len(em) == 0:
				em.append(discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='\n'.join(data),color = discord.Color(0x50d2fe)))
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by {}'.format(crapiurl.replace('api.', '', 1)), icon_url='https://raw.githubusercontent.com/cr-api/cr-api-docs/master/docs/img/cr-api-logo-b.png')


		for e in em:
			await self.bot.say(embed=e)


	@clan.command(name='coleaders',aliases=['cos', 'coleader'],pass_context=True)
	async def clancoleaders(self, ctx, keyortag=None):
		user = ctx.message.author
		if keyortag == None:
			keyortag = user.id
		tag = await self.keyortag2tag(keyortag, ctx)
		if tag == None:
			return
		clanurl = crapiurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = await CRClan.create(tag)
		clan_data = []
		member_data = [] # for displaying all members 
		membertype = None
		members2display = clan.coleaders
		if members2display != clan.members:
			membertype = members2display[0]['role']
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
			for member in membersection:
				memberstring = member['formatted']
				member_data[n].append(memberstring)
			n += 1


		em = []
		if membertype != None:
			currentdesc = "**{}** `{}s`\n".format(len(members2display), membertype)
		else:
			currentdesc = ''
		if len(clan_data)>0:
			e = discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='{}{}'.format(currentdesc, '\n'.join(data)),color = discord.Color(0x50d2fe))
			em.append(e)

		for data in member_data:
			if len(em) == 0:
				e = discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='{}{}'.format(currentdesc, '\n'.join(data)),color = discord.Color(0x50d2fe))
				em.append(e)
				
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		# em[0].
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by {}'.format(crapiurl.replace('api.', '', 1)), icon_url='https://raw.githubusercontent.com/cr-api/cr-api-docs/master/docs/img/cr-api-logo-b.png')


		for e in em:
			await self.bot.say(embed=e)



	@clan.command(name='elders',aliases=['elder'],pass_context=True)
	async def clanelders(self, ctx, keyortag=None):
		user = ctx.message.author
		if keyortag == None:
			keyortag = user.id
		tag = await self.keyortag2tag(keyortag, ctx)
		if tag == None:
			return
		clanurl = crapiurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = await CRClan.create(tag)
		clan_data = []
		member_data = [] # for displaying all members 
		membertype = None
		members2display = clan.elders
		if members2display != clan.members:
			membertype = members2display[0]['role']
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
			for member in membersection:
				memberstring = member['formatted']
				member_data[n].append(memberstring)
			n += 1


		em = []
		if membertype != None:
			currentdesc = "**{}** `{}s`\n".format(len(members2display), membertype)
		else:
			currentdesc = ''
		if len(clan_data)>0:
			e = discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='{}{}'.format(currentdesc, '\n'.join(data)),color = discord.Color(0x50d2fe))
			em.append(e)
		for data in member_data:
			if len(em) == 0:
				e = discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='{}{}'.format(currentdesc, '\n'.join(data)),color = discord.Color(0x50d2fe))
				em.append(e)
				
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		# em[0].
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by {}'.format(crapiurl.replace('api.', '', 1)), icon_url='https://raw.githubusercontent.com/cr-api/cr-api-docs/master/docs/img/cr-api-logo-b.png')


		for e in em:
			await self.bot.say(embed=e)




	@clan.command(name='norole',aliases=['members'],pass_context=True)
	async def clannorole(self, ctx, keyortag=None):
		user = ctx.message.author
		if keyortag == None:
			keyortag = user.id
		tag = await self.keyortag2tag(keyortag, ctx)
		if tag == None:
			return
		clanurl = crapiurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = await CRClan.create(tag)
		clan_data = []
		member_data = [] # for displaying all members 
		
		membertype = None
		members2display = clan.norole
		if members2display != clan.members:
			membertype = members2display[0]['role']
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
			for member in membersection:
				memberstring = member['formatted']
				member_data[n].append(memberstring)
			n += 1


		em = []
		if membertype != None:
			currentdesc = "**{}** `{}s`\n".format(len(members2display), membertype)
		else:
			currentdesc = ''
		if len(clan_data)>0:
			e = discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='{}{}'.format(currentdesc, '\n'.join(data)),color = discord.Color(0x50d2fe))
			em.append(e)
		for data in member_data:
			if len(em) == 0:
				e = discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='{}{}'.format(currentdesc, '\n'.join(data)),color = discord.Color(0x50d2fe))
				em.append(e)
				
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by {}'.format(crapiurl.replace('api.', '', 1)), icon_url='https://raw.githubusercontent.com/cr-api/cr-api-docs/master/docs/img/cr-api-logo-b.png')


		for e in em:
			await self.bot.say(embed=e)


	@clan.command(name='info',pass_context=True)
	async def claninfo(self, ctx, keyortag=None):
		user = ctx.message.author
		if keyortag == None:
			keyortag = user.id
		tag = await self.keyortag2tag(keyortag, ctx)
		if tag == None:
			return
		clanurl = crapiurl + '/clan/' + tag
		await self.async_refresh(clanurl+ '/refresh')
		clan = await CRClan.create(tag)
		clan_data = []
		member_data = [] # for displaying all members 
		clan_data.append(clan.desc2)
		clan_data.append(clan.leader['formatted'])
		clan_data.append("Clan Tag: [`{}`]({})".format(tag, clan.clanurl))
		clan_data.append("Clan Score: [{}](nothing)".format(clan.clan_trophy))
		clan_data.append("Trophy Requirement: [{}](nothing)".format(clan.tr_req))


		em = []

		if len(clan_data)>0:
			em.append(discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='\n'.join(clan_data),color = discord.Color(0x50d2fe)))
		for data in member_data:
			if len(em) == 0:
				em.append(discord.Embed(url=clan.clanurl, title="{}".format(clan.name), description='\n'.join(data),color = discord.Color(0x50d2fe)))
			else:
				em.append(discord.Embed(description='\n'.join(data),color = discord.Color(0x50d2fe)))
		try:
			discordname = user.name if user.nick is None else user.nick
		except:
			discordname = user.name
		em[0].set_author(icon_url=user.avatar_url,name=discordname)
		em[0].set_thumbnail(url=clan.clan_badge)
		em[len(em)-1].set_footer(text='Data provided by {}'.format(crapiurl.replace('api.', '', 1)), icon_url='https://raw.githubusercontent.com/cr-api/cr-api-docs/master/docs/img/cr-api-logo-b.png')


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
		if valid: 
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



	def statsvalid(self, tag):
		for letter in tag:
			if letter not in validChars:
				return False
		return True

	async def async_refresh(self,url):
		async with aiohttp.get(url) as r:
			response = await r.json()
			return response



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
