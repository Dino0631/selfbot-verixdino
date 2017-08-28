import discord
from discord.ext import commands
import datetime
import time
import random
import asyncio
import json
from ext.commands import Bot
from fuzzywuzzy import fuzz
from __main__ import send_cmd_help

class CannotPaginate(Exception):
    pass

class Pages:
    """Implements a paginator that queries the user for the
    pagination interface.
    Pages are 1-index based, not 0-index based.
    If the user does not reply within 2 minutes then the pagination
    interface exits automatically.
    Parameters
    ------------
    bot
        The bot instance.
    message
        The message that initiated this session.
    entries
        A list of entries to paginate.
    per_page
        How many entries show up per page.
    Attributes
    -----------
    embed: discord.Embed
        The embed object that is being used to send pagination info.
        Feel free to modify this externally. Only the description,
        footer fields, and colour are internally modified.
    permissions: discord.Permissions
        Our permissions for the channel.
    """
    def __init__(self, bot, *, message, entries, per_page=12):
        self.bot = bot
        self.entries = entries
        self.message = message
        self.author = message.author
        self.per_page = per_page
        self.embed = discord.Embed()
        self.paginating = len(entries) > per_page
        self.reaction_emojis = [
            ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}', self.first_page),
            ('\N{BLACK LEFT-POINTING TRIANGLE}', self.previous_page),
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', self.next_page),
            ('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}', self.last_page),
            ('\N{INPUT SYMBOL FOR NUMBERS}', self.numbered_page ),
            ('\N{BLACK SQUARE FOR STOP}', self.stop_pages),
            ('\N{INFORMATION SOURCE}', self.show_help),
        ]

        server = self.message.server
        if server is not None:
            self.permissions = self.message.channel.permissions_for(server.me)
        else:
            self.permissions = self.message.channel.permissions_for(self.bot.user)

        if not self.permissions.embed_links:
            raise CannotPaginate('Bot does not have embed links permission.')

        self.categs = []

        for i, e in enumerate(self.entries):
            if e.startswith('**'):
                self.categs.append(i)

        self.maximum_pages = len(self.categs)

    def get_page(self, page):
        
        base = self.categs[page-1]
        try:
            end = self.categs[page]
            return self.entries[base:end]
        except:
            return self.entries[base:]



    async def show_page(self, page, *, first=False):
        self.current_page = page
        entries = self.get_page(page)
        p = [t for t in entries]

        self.embed.set_footer(text='Page %s/%s (%s Commands)' % (page, self.maximum_pages, len(self.entries)-len(self.categs)))

        if not self.paginating:
            self.embed.clear_fields()
            self.embed.add_field(name=p[0], value='\n'.join(p[1:]))
            return await self.bot.send_message(self.message.channel, embed=self.embed)

        if not first:
            self.embed.clear_fields()
            self.embed.add_field(name=p[0], value='\n'.join(p[1:]))
            await self.bot.edit_message(self.message, embed=self.embed)
            return

        # verify we can actually use the pagination session
        if not self.permissions.add_reactions:
            raise CannotPaginate('Bot does not have add reactions permission.')

        if not self.permissions.read_message_history:
            raise CannotPaginate('Bot does not have Read Message History permission.')

        self.embed.add_field(name=p[0], value='\n'.join(p[1:]))
        self.embed.add_field(name='Confused?', value='React with \N{INFORMATION SOURCE} by typing s.i for more info')
        self.message = await self.bot.send_message(self.message.channel, embed=self.embed)
        for (reaction, _) in self.reaction_emojis:
            if self.maximum_pages == 2 and reaction in ('\u23ed', '\u23ee'):
                # no |<< or >>| buttons if we only have two pages
                # we can't forbid it if someone ends up using it but remove
                # it from the default set
                continue

            # await self.bot.add_reaction(self.message, reaction)

    async def checked_show_page(self, page):
        if page != 0 and page <= self.maximum_pages:
            await self.show_page(page)

    async def first_page(self):
        """goes to the first page (s.first)"""
        await self.show_page(1)

    async def last_page(self):
        """goes to the last page (s.last)"""
        await self.show_page(self.maximum_pages)

    async def next_page(self):
        """goes to the next page (s.next)"""
        await self.checked_show_page(self.current_page + 1)

    async def previous_page(self):
        """goes to the previous page (s.prev)"""
        await self.checked_show_page(self.current_page - 1)

    async def show_current_page(self):
        if self.paginating:
            await self.show_page(self.current_page)

    async def numbered_page(self):
        """lets you type a page number to go to (s.page)"""
        to_delete = []
        to_delete.append(await self.bot.send_message(self.message.channel, 'What page do you want to go to?'))
        msg = await self.bot.wait_for_message(author=self.author, channel=self.message.channel,
                                              check=lambda m: m.content.isdigit(), timeout=30.0)
        if msg is not None:
            page = int(msg.content)
            to_delete.append(msg)
            if page != 0 and page <= self.maximum_pages:
                await self.show_page(page)
            else:
                to_delete.append(await self.bot.say('Invalid page given. (%s/%s)' % (page, self.maximum_pages)))
                await asyncio.sleep(5)
        else:
            to_delete.append(await self.bot.send_message(self.message.channel, 'Took too long.'))
            await asyncio.sleep(5)

        try:
            for x in to_delete:
                await self.bot.delete_message(x)
        except Exception:
            pass

    async def show_help(self):
        """shows this message (s.i)"""
        e = discord.Embed()
        messages = []
        messages.append('This interactively allows you to see pages of text by navigating with ' \
                        'reactions. They are as follows:\n')

        for (emoji, func) in self.reaction_emojis:
            messages.append('%s %s' % (emoji, func.__doc__))

        e.add_field(name='Welcome to the interactive paginator!',value='\n'.join(messages))
        e.colour =  0x00FFFF #0x738bd7 # blurple
        e.set_footer(text='We were on page %s before this message.' % self.current_page)
        await self.bot.edit_message(self.message, embed=e)

        async def go_back_to_current_page():
            await asyncio.sleep(60.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())

    async def stop_pages(self):
        """stops the interactive pagination session (s.stop)"""
        await self.bot.delete_message(self.message)
        self.paginating = False

    def react_check(self, reaction, user):
        if user is None or user.id != self.author.id:
            return False

        for (emoji, func) in self.reaction_emojis:
            if reaction.emoji == emoji:
                self.match = func
                return True
        return False

    async def paginate(self):
        """Actually paginate the entries and run the interactive loop if necessary."""
        await self.show_page(1, first=True)

        while self.paginating:
            react = await self.bot.wait_for_reaction(message=self.message, check=self.react_check, timeout=120.0)
            if react is None:
                self.paginating = False
                try:
                    await self.bot.clear_reactions(self.message)
                except:
                    pass
                finally:
                    break

            try:
                await self.bot.remove_reaction(self.message, react.reaction.emoji, react.user)
            except:
                pass # can't remove it so don't bother doing so

            await self.match()

class Info2():


    def __init__(self, bot):
        self.bot = bot
         
    @commands.command(pass_context=True)
    async def help2(self, ctx, cog = None):
        """Shows listed help message."""
        author = ctx.message.author
        await self.bot.delete_message(ctx.message)
        n = 0
        if cog == None:
            pages = self.bot.formatter.format_help_for(ctx, self.bot, 3)
            for page in pages:
                try:
                    if(n!=0):
                        page.set_author(name='', url='')
                    if(n!=len(pages)-1):
                        page.set_footer(text='')
                    await self.bot.say(embed=page)
                    n += 1
                except:
                    await self.bot.say('I need the embed links perm.')
        else:
            pages = self.bot.formatter.format_help_for(ctx, self.bot, 1)
            cog = cog.lower()
            maxfuzrat = 0
            bestmatch = pages[0]
            currentfuzrat = 0
            for page in pages:
                pagecog = page.to_dict()['fields'][0]['name'] # cog name of page
                pagecog = pagecog[:-1].lower() #remove the colon and make it lowercase
                if '\u200b' in pagecog:
                    pagecog.replace('\u200b', '')
                currentfuzrat = fuzz.ratio(cog, pagecog)
                if  currentfuzrat > maxfuzrat:
                    # print("page cog: {}\nsearch cog: {}\nfuzz ratio: {}".format(pagecog, cog, currentfuzrat))
                    maxfuzrat = currentfuzrat
                    bestmatch = page
            await self.bot.say(embed=bestmatch)


    @commands.command(pass_context=True)
    async def help3(self, ctx, *, cmd = None):
        """Shows paginated help message."""
        await self.bot.delete_message(ctx.message)
        author = ctx.message.author
        pages = self.bot.formatter.format_help_for(ctx, self.bot, 1)
        testing = self.bot.get_channel('344184736324780032')
        pages2 = []
        n = 0
        for page in pages:
            try:
            # if(n!=0):
                # page.set_author(name='', url='')
            # if(n!=len(pages)-1):
                # page.set_footer(text='')
            # await self.bot.send_message(testing, embed=page)
            # await asyncio.sleep(.1)
            # messages = []
            # async for m in self.bot.logs_from(testing, limit=2):
            #     messages.append(m)
            # message = messages[0]
                message = page.to_dict()
                pages2.append(message)
            except:
                await self.bot.say('I need the embed links perm.')
        line = []
        for page2 in pages2:
            em = page2

            # print('hi3')
            for x in em['fields']:
                line.append('**'+x['name']+'**') #append the cog heading
                # print('hi3.1')
                val = x['value']
                # print('hi3.2')
                val = val.split('\n')
                # print('hi3.3')
                line.extend(val)
            # print('hi3.4')

        p = Pages(self.bot, message=ctx.message, entries=line)
        p.embed.set_author(name='Help - Verix-Dino Selfbot Commands', icon_url=self.bot.user.avatar_url)
        p.embed.color = 0x00FFFF
        await p.paginate()



    @commands.command(pass_context=True)
    async def react(self, ctx, *args):
        """Add reactions to a message by message id.
        
        Add reactions to a specific message id
        [p]react 123456 :uwot: :lolno: :smile: 
        
        Add reactions to the last message in channel
        [p]react :uwot: :lolno: :smile:
        """
        server = ctx.message.server
        channel = ctx.message.channel

        if not len(args):
            await send_cmd_help(ctx)
            return

        has_message_id = args[0].isdigit()

        emojis = args[1:] if has_message_id else args
        message_id = args[0] if has_message_id else None
        if has_message_id:
            try:
                message = await self.bot.get_message(channel, message_id)
            except discord.NotFound:
                await self.bot.say("Cannot find message with that id.")
                return
        else:
            # use the 2nd last message because the last message would be the command
            messages = []
            async for m in self.bot.logs_from(channel, limit=2):
                messages.append(m)
            message = messages[1]

        useremojis = list(emojis)
        new_emojis = []
        if(server == None):
            new_emojis.extend(useremojis)
        else:
            for e in useremojis:
                lastlist = new_emojis
                for x in server.emojis:
                    ename = e[e.find(':') + 1 : e.rfind(':')]
                    if(x.name == ename):
                        new_emojis.append(x)
                if(lastlist == new_emojis):
                    new_emojis.append(e)

        for emoji in new_emojis:
            try:
                await self.bot.add_reaction(message, emoji)
            except discord.HTTPException:
                # reaction add failed
                pass
            except discord.Forbidden:
                await self.bot.say(
                    "I don’t have permission to react to that message.")
                break
            except discord.InvalidArgument:
                await self.bot.say("Invalid arguments for emojis")
                break

        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True)
    async def next(self, ctx):
        '''go to next page in s.help'''
        await ctx.invoke(self.react, '▶')

    @commands.command(pass_context=True)
    async def back(self, ctx):
        '''go back a page in s.help'''
        await ctx.invoke(self.react, '◀')
        
    @commands.command(pass_context=True)
    async def i(self, ctx):
        '''go to info page in s.help'''
        await ctx.invoke(self.react, 'ℹ')
        
    @commands.command(pass_context=True)
    async def first(self, ctx):
        '''go to first page in s.help'''
        await ctx.invoke(self.react, '⏪')
        
    @commands.command(pass_context=True)
    async def last(self, ctx):
        '''go to last page in s.help'''
        await ctx.invoke(self.react, '⏩')
        
    @commands.command(pass_context=True)
    async def page(self, ctx):
        '''go to prev page in s.help'''
        await ctx.invoke(self.react, '🔢')
        
    @commands.command(pass_context=True)
    async def stop(self, ctx):
        '''stop the interactive help command'''
        await ctx.invoke(self.react, '⏹')




def setup(bot):
    bot.add_cog(Info2(bot))