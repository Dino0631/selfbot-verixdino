import discord
from ext.commands import bot
from discord.ext import commands
import datetime
import time
import random
import asyncio
import json
import requests
import os
from bs4 import BeautifulSoup
from __main__ import send_cmd_help
import string
import aiohttp
from urllib.parse import quote_plus
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



def escape(text, *, mass_mentions=False, formatting=False):
    if mass_mentions:
        text = text.replace("@everyone", "@\u200beveryone")
        text = text.replace("@here", "@\u200bhere")
    if formatting:
        text = (text.replace("`", "\\`")
                    .replace("*", "\\*")
                    .replace("_", "\\_")
                    .replace("~", "\\~"))
    return text


def escape_mass_mentions(text):
    return escape(text, mass_mentions=True)

def pagify(text, delims=["\n"], *, escape=True, shorten_by=8,
           page_length=2000):
    """DOES NOT RESPECT MARKDOWN BOXES OR INLINE CODE"""
    in_text = text
    if escape:
        num_mentions = text.count("@here") + text.count("@everyone")
        shorten_by += num_mentions
    page_length -= shorten_by
    while len(in_text) > page_length:
        closest_delim = max([in_text.rfind(d, 0, page_length)
                             for d in delims])
        closest_delim = closest_delim if closest_delim != -1 else page_length
        if escape:
            to_send = escape_mass_mentions(in_text[:closest_delim])
        else:
            to_send = in_text[:closest_delim]
        yield to_send
        in_text = in_text[closest_delim:]

    if escape:
        yield escape_mass_mentions(in_text)
    else:
        yield in_text

class Stuff():


    def __init__(self, bot):
        self.bot = bot

    # @commands.command(pass_context=True)
    # async def command_name(self, ctx):
    #     '''custom command'''
    #     await self.bot.say("custom command words!")
    # @commands.command()
    # async def lmao(self):
    #     await self.bot.say('dont do tis')

    @commands.command(pass_context=True)
    async def gold(self, ctx, *, args):
        args = args.strip().split(' ')
        while '' in args:
            args.remove('')
        for i, a in enumerate(args):
            if a.isdigit():
                args[i] = int(a)-1
        totalgold = {'c':0,'r':0,'e':0,'l':0,}
        allgold = 0
        cardlvl = {}
        if 'c' in args and 'r' in args:
            cardlvl['c'] = args[args.index('c')+1:args.index('r')]
        elif 'c' in args:
            cardlvl['c'] = args[args.index('c')+1:]
        if 'r' in args and 'e' in args:
            cardlvl['r'] = args[args.index('r')+1:args.index('e')]
        elif 'r' in args:
            cardlvl['r'] = args[args.index('r')+1:]
        if 'e' in args and 'l' in args:
            cardlvl['e'] = args[args.index('e')+1:args.index('l')]
        elif 'e' in args:
            cardlvl['e'] = args[args.index('e')+1:]
        if 'l' in args:
            cardlvl['l'] = args[args.index('l')+1:]
        print(cardlvl)
        try:
            for rarity in cardlvl:
                for lvl in cardlvl[rarity]:
                    allgold += totalupgrades[rarity][lvl]
                    totalgold[rarity] += totalupgrades[rarity][lvl]
        except IndexError:
            await self.bot.say("Invalid card level")
        await self.bot.say("You have spent a total of {} gold on upgrading those cards".format(allgold))
        # for rarity in totalgold:
        #     await self.bot.say("You have spent a total of {} gold on upgrading {} cards".format(totalgold[rarity], rarity))

    @commands.command(pass_context=True)
    async def test(self, ctx):
        em =  discord.Embed()
        em.set_image(url='')
        await self.bot.say(embed=em)

    @commands.command(pass_context=True)
    async def sml(self, ctx):
        '''sml's emotions'''
        await self.bot.delete_message(ctx.message)
        await self.bot.say(":angry: :rage: :angry: :rage: :angry:\n"+ 
            ":rage: :angry: :rage: :angry: :rage:\n"+
            ":angry: :rage: :rage: :rage: :angry:\n"+
            ":rage: :angry: :rage: :angry: :rage:\n"+
            ":angry: :rage: :angry: :rage: :angry:")

    @commands.command(pass_context=True)
    async def smlirl(self, ctx):
        '''sml'''
        await self.bot.delete_message(ctx.message)
        l = [
            ':angry::rage::rage::rage::angry::rage::angry::angry::angry::rage::angry::rage::angry::angry::angry::angry:',
            ':angry::rage::angry::angry::angry::rage::rage::angry::rage::rage::angry::rage::angry::angry::angry::angry:',
            ':angry::rage::rage::rage::angry::rage::angry::rage::angry::rage::angry::rage::angry::angry::angry::angry:',
            ':angry::angry::angry::rage::angry::rage::angry::angry::angry::rage::angry::rage::angry::angry::angry::angry:',
            ':angry::rage::rage::rage::angry::rage::angry::angry::angry::rage::angry::rage::rage::rage::rage::angry:'
        ]
        msg = '\n'.join(l)
        await self.bot.say(msg)


    @commands.command(pass_context=True)
    async def dad(self, ctx):
        '''6dad's emotions'''
        await self.bot.delete_message(ctx.message)
        racfserver = self.bot.get_server('218534373169954816')
        dad = ''
        dadw = ''
        for x in racfserver.emojis:
            if x.name == '6dad':
                dad = x
            elif x.name == '6dadw':
                dadw = x
        await self.bot.say(("{0} {1} {0} {1} {0}\n"+
            "{1} {0} {1} {0} {1}\n"+
            "{0} {1} :rage: {1} {0}\n"+
            "{1} {0} {1} {0} {1}\n"+
            "{0} {1} {0} {1} {0}").format(dad, dadw))

    @commands.command(pass_context=True)
    async def firepoop(self, ctx):
        '''fierypoopyhead's emotions'''
        await self.bot.delete_message(ctx.message)
        racfserv = self.bot.get_server('218534373169954816')
        gitgud = ''
        woodBM = ''
        for e in racfserv.emojis:
            if(e.name == 'gitgud'):
                gitgud = e
            if(e.name == 'woodBM'):
                woodBM = e
        await self.bot.say(":poop: :fire: :poop: :fire: :poop:\n:fire: {} :fire: {} :fire:\n:poop: :fire: {} :fire: :poop:\n:fire: {} :fire: {} :fire:\n:poop: :fire: :poop: :fire: :poop:".format(gitgud, gitgud, woodBM, gitgud, gitgud))


    clock_position = list(
        ['█',
         '██',
         '███',
         '████',
         '█████',
         '██████',
         '███████',
         '████████'
        ])

    @commands.command(pass_context=True)
    async def loadingbars(self, ctx, spins:int=1):
        '''make a  loading bar n times'''
        await self.bot.delete_message(ctx.message)
        channel = ctx.message.channel
        if spins>5:
            spins = 5
        if spins<1:
            spins = 1
        await self.bot.say(self.clock_position[0])
        messages = []
        async for m in self.bot.logs_from(channel, limit=20):
            messages.append(m)
        for  m in messages:
            if m.author.id == '222925389641547776':
                message = m
                break
        for i in range(0, spins):
            for x in range(0,7):
                await asyncio.sleep(.25)
                await self.bot.edit_message(message, new_content=self.clock_position[x])
        await self.bot.delete_message(message)

    @commands.command(pass_context=True)
    async def cycle(self, ctx):
        for x in range(1, 2):
            for i in string.digits:
                await self.bot.edit_message(ctx.message, i)

    @commands.command(pass_context=True)
    async def copy(self, ctx):
        channel = ctx.message.channel
        messages = []
        async for m in self.bot.logs_from(channel, limit=2):
            messages.append(m)
        message = messages[1]
        await self.bot.say('`'+str(message.embeds[0])+'`')

    @commands.command(pass_context=True)
    async def ecksdee(self, ctx):
        await self.bot.delete_message(ctx.message)
        await self.bot.say("ecĸѕ               ecĸѕ         dee dee\n  ecĸѕ            ecĸѕ          dee       dee\n     ecĸѕ     ecĸѕ             dee         dee\n            ecĸѕ                    dee          dee\n     ecĸѕ     ecĸѕ              dee         dee\n  ecĸѕ            ecĸѕ          dee       dee\necĸѕ               ecĸѕ         dee dee\n")
    
    @commands.command(pass_context=True)
    async def abe(self, ctx):
        # embed = [0, 1, 2, 3, 4]
        await self.bot.delete_message(ctx.message)
        embed  = discord.Embed(color=discord.Color(0x6441A4))
        embed.set_author(name="Follow Abe on Social Media!", icon_url="https://cdn.discordapp.com/avatars/218790601318072321/0b047729ae9b8d46f559b6b492ee66df.webp?size=1024")
        # embed.add_field(name='Link',value='[Google!](https://google.com/)')
        embed.add_field(name="Twitch!", value='[@abeplaysgame](https://www.twitch.tv/abeplaysgame)')
        embed.add_field(name="Twitter!", value='[@AbePlaysGame](https://twitter.com/AbePlaysGame)')
        embed.add_field(name="SnapChat!", value='[@AbeWantsFame](http://www.snapchat.com/add/AbeWantsFame)')
        embed.add_field(name="Share the Discord!", value='[NounVerbNoun](https://discord.gg/YbwWgnR)')
        embed.set_image(url='http://i.imgur.com/qmlqppD.png')
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def abe2(self, ctx):
        await self.bot.delete_message(ctx.message)
        em = discord.Embed(title="Like and RT abe's tweet about his hype RPL stream!",color=discord.Color(0x6441A4), url="https://cdn.discordapp.com/avatars/218790601318072321/0b047729ae9b8d46f559b6b492ee66df.webp?size=1024")
        em.set_author(name="ABE", icon_url="https://cdn.discordapp.com/avatars/218790601318072321/0b047729ae9b8d46f559b6b492ee66df.webp?size=1024")
        em.set_thumbnail(url="https://cdn.discordapp.com/avatars/218790601318072321/0b047729ae9b8d46f559b6b492ee66df.webp?size=1024")
        await self.bot.say(embed=em)

    @commands.command(pass_context=True)
    async def bday(self, ctx, user:discord.Member=None):
        await self.bot.delete_message(ctx.message)
        author = ctx.message.author
        if user == None:
            mention = '<@!218790601318072321>'
        else:
            mention = user.mention
        em = discord.Embed(color=discord.Color(0x00bb00), description="[I wish you a happy birthday {}!](https://cdn.discordapp.com/emojis/313410780286681089.png)".format(mention))
        name = author.name if author.nick == None else author.nick
        em.set_author(name=name, icon_url=author.avatar_url)
        em.set_thumbnail(url='https://d1yn1kh78jj1rr.cloudfront.net/preview/birthday-balloons-with-rainbow-and-clouds_f1GfDFFd_M.jpg')
        await self.bot.say(embed=em)


    @commands.command(pass_context=True)
    async def flip(self, ctx, user):
        """Flips a coin... or a user.

        Defaults to coin.
        """
        if user != None:
            msg = ""
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            await self.bot.say(msg + "(╯°□°）╯︵ " + name[::-1])
        else:
            await self.bot.say("*flips a coin and... " + choice(["HEADS!*", "TAILS!*"]))



    
def setup(bot):
    bot.add_cog(Stuff(bot))