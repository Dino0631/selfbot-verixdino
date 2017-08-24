import discord
from discord.ext import commands
import asyncio
import requests
from bs4 import BeautifulSoup
from urllib import parse
from urllib.parse import parse_qs
from urllib.request import Request, urlopen
import traceback
import inspect
import textwrap
from contextlib import redirect_stdout
import io
import aiohttp
from lxml import etree
from mtranslate import translate

class Utility:
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    @commands.command(aliases=['nick'], pass_context=True, no_pm=True)
    async def nickname(self, ctx, *, nick):
        """Change your nickname on a server."""
        await self.bot.delete_message(ctx.message)
        try:
            await self.bot.change_nickname(ctx.message.author, nick)
            await self.bot.say('Changed nickname to: `{}`'.format(nick), delete_after=5)
        except:
            await self.bot.say('Unable to change nickname.', delete_after=5)
            
    @commands.command(pass_context=True, aliases=['t'])     
    async def translate(self, ctx, lang, *, text):
        """Translate text!"""       
        result = translate(text, lang)      
        await self.bot.say('{}'.format(result))   

    @commands.command(pass_context=True)
    async def raw(self, ctx, ID, chan : discord.channel=None):
    	"""Get the raw content of someones message!"""
    	channel = chan or ctx.message.channel
    	await self.bot.delete_message(ctx.message)
    	msg = None
    	async for m in self.bot.logs_from(channel, limit=1000):
    		if m.id == ID:
    			msg = m
    			break
    	out = msg.content.replace('*','\\*').replace('`','\\`').replace('~~','\\~~').replace('_','\\_').replace('<','\\<').replace('>','\\>')
    	try:
    		await self.bot.say(out)
    	except:
    		await self.bot.say('Message too long.')


    @commands.command(pass_context=True)
    async def quote(self, ctx, id : str, chan : discord.Channel=None):
    	"""Quote someone's message by ID"""
    	channel = chan or ctx.message.channel
    	await self.bot.delete_message(ctx.message)
    	msg = None
    	async for message in self.bot.logs_from(channel, limit=1000):
    		if message.id == id:
    			msg = message
    			break
    	if msg is None:
    		await self.bot.say('Could not find the message.')
    		return
    	auth = msg.author
    	channel = msg.channel
    	ts = msg.timestamp

    	em = discord.Embed(color=0x00FFFF,description=msg.clean_content,timestamp=ts)
    	em.set_author(name=str(auth),icon_url=auth.avatar_url or auth.default_avatar_url)
    	em.set_footer(text='#'+channel.name)

    	await self.bot.say(embed=em)

    @commands.command(pass_context=True, aliases=['yt', 'vid', 'video'])
    async def youtube(self, ctx, *, msg):
        """Search for videos on YouTube."""
        search = parse.quote(msg)
        response = requests.get("https://www.youtube.com/results?search_query={}".format(search)).text
        result = BeautifulSoup(response, "lxml")
        url="**Result:**\nhttps://www.youtube.com{}".format(result.find_all(attrs={'class': 'yt-uix-tile-link'})[0].get('href'))

        
    @commands.command(pass_context=True)
    async def urban(self,ctx, *, search_terms : str, definition_number : int=1):
        """Urban Dictionary search

        Definition number must be between 1 and 10"""
        await self.bot.edit_message(ctx.message, new_content=search_terms + ':')
        def encode(s):
            return quote_plus(s, encoding='utf-8', errors='replace')

        # definition_number is just there to show up in the help
        # all this mess is to avoid forcing double quotes on the user

        search_terms = search_terms.split(" ")
        try:
            if len(search_terms) > 1:
                pos = int(search_terms[-1]) - 1
                search_terms = search_terms[:-1]
            else:
                pos = 0
            if pos not in range(0, 11): # API only provides the
                pos = 0                 # top 10 definitions
        except ValueError:
            pos = 0

        search_terms = "+".join([encode(s) for s in search_terms])
        url = "http://api.urbandictionary.com/v0/define?term=" + search_terms
        try:
            async with aiohttp.get(url) as r:
                result = await r.json()
            if result["list"]:
                definition = result['list'][pos]['definition']
                example = result['list'][pos]['example']
                defs = len(result['list'])
                msg = ("**Definition #{} out of {}:**\n{}\n\n"
                       "**Example:**\n{}".format(pos+1, defs, definition,
                                                 example))
                msg = pagify(msg, ["\n"])
                pages = []
                for page in msg:
                    x = page.split('\n')
                    pages.extend(x)
                em = discord.Embed(color=discord.Color(0xE86222))
                em.set_author(name="Urban Dictionary", icon_url='http://i.imgur.com/6nJnuM4.png', url='http://www.urbandictionary.com/')
                n = 0
                prevn = n
                lastfieldname = ''
                lastfieldval = ''
                for x in pages:
                    if x.startswith('**'):
                        lastfieldname = x.replace('**','')
                        em.add_field(name=lastfieldname, value='lol')
                        n += 1
                    else:
                        if n == prevn:
                            lastfieldval += x
                            lastfieldval +='\n'
                        else:
                            prevn = n
                            lastfieldval = x
                        # print("hi")
                        # print("name={}\nvalue={}".format(lastfieldname, lastfieldval))
                        em.set_field_at(n-1, name=lastfieldname, value=lastfieldval)
                        # print("name={}\nvalue={}".format(lastfieldname, lastfieldval))
                        # print("hi2")
                await self.bot.say(embed=em)
            else:
                await self.bot.say("Your search terms gave no results.")
        except IndexError:
            await self.bot.say("There is no definition #{}".format(pos+1))
        except:
            await self.bot.say("Error.")
        await self.bot.send_message(ctx.message.channel, url)
    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
        return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)

    @commands.command(pass_context=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        '''Run python scripts on discord!'''
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'server': ctx.message.server,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = 'async def func():\n%s' % textwrap.indent(body, '  ')

        try:
            exec(to_compile, env)
        except SyntaxError as e:
            return await self.bot.say(self.get_syntax_error(e))

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await self.bot.say('```py\n{}{}\n```'.format(value, traceback.format_exc()))
        else:
            value = stdout.getvalue()
            try:
                await self.bot.add_reaction(ctx.message, '\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await self.bot.say('```py\n%s\n```' % value)
            else:
                self._last_result = ret
                await self.bot.say('```py\n%s%s\n```' % (value, ret))

    @commands.command(pass_context=True,description='Do .embed to see how to use it.')
    async def embed(self, ctx, *, msg: str = None):
        '''Embed complex rich embeds as the bot.'''
        try:
            
            if msg:
                ptext = title = description = image = thumbnail = color = footer = author = None
                timestamp = discord.Embed.Empty
                def_color = False
                embed_values = msg.split('|')
                for i in embed_values:
                    if i.strip().lower().startswith('ptext='):
                        if i.strip()[6:].strip() == 'everyone':
                            ptext = '@everyone'
                        elif i.strip()[6:].strip() == 'here':
                            ptext = '@here'
                        else:
                            ptext = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('title='):
                        title = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('description='):
                        description = i.strip()[12:].strip()
                    elif i.strip().lower().startswith('desc='):
                        description = i.strip()[5:].strip()
                    elif i.strip().lower().startswith('image='):
                        image = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('thumbnail='):
                        thumbnail = i.strip()[10:].strip()
                    elif i.strip().lower().startswith('colour='):
                        color = i.strip()[7:].strip()
                    elif i.strip().lower().startswith('color='):
                        color = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('footer='):
                        footer = i.strip()[7:].strip()
                    elif i.strip().lower().startswith('author='):
                        author = i.strip()[7:].strip()
                    elif i.strip().lower().startswith('timestamp'):
                        timestamp = ctx.message.timestamp

                    if color:
                        if color.startswith('#'):
                            color = color[1:]
                        if not color.startswith('0x'):
                            color = '0x' + color

                    if ptext is title is description is image is thumbnail is color is footer is author is None and 'field=' not in msg:
                        await self.bot.delete_message(ctx.message)
                        return await self.bot.send_message(ctx.message.channel, content=None,
                                                           embed=discord.Embed(description=msg))

                    if color:
                        em = discord.Embed(timestamp=timestamp, title=title, description=description, color=int(color, 16))
                    else:
                        em = discord.Embed(timestamp=timestamp, title=title, description=description)
                    for i in embed_values:
                        if i.strip().lower().startswith('field='):
                            field_inline = True
                            field = i.strip().lstrip('field=')
                            field_name, field_value = field.split('value=')
                            if 'inline=' in field_value:
                                field_value, field_inline = field_value.split('inline=')
                                if 'false' in field_inline.lower() or 'no' in field_inline.lower():
                                    field_inline = False
                            field_name = field_name.strip().lstrip('name=')
                            em.add_field(name=field_name, value=field_value.strip(), inline=field_inline)
                    if author:
                        if 'icon=' in author:
                            text, icon = author.split('icon=')
                            if 'url=' in icon:
                                print("here")
                                em.set_author(name=text.strip()[5:], icon_url=icon.split('url=')[0].strip(), url=icon.split('url=')[1].strip())
                            else:
                                em.set_author(name=text.strip()[5:], icon_url=icon)
                        else:
                            if 'url=' in author:
                                print("here")
                                em.set_author(name=author.split('url=')[0].strip()[5:], url=author.split('url=')[1].strip())
                            else:
                                em.set_author(name=author)

                    if image:
                        em.set_image(url=image)
                    if thumbnail:
                        em.set_thumbnail(url=thumbnail)
                    if footer:
                        if 'icon=' in footer:
                            text, icon = footer.split('icon=')
                            em.set_footer(text=text.strip()[5:], icon_url=icon)
                        else:
                            em.set_footer(text=footer)
                await self.bot.send_message(ctx.message.channel, content=ptext, embed=em)
            else:
                msg = '*Params:*\n```bf\n[title][author][desc][field][footer][thumbnail][image][timestamp][ptext]```'
                await self.bot.send_message(ctx.message.channel, msg)
            try:
                await self.bot.delete_message(ctx.message)
            except:
                pass
        except:
            await self.bot.send_message(ctx.message.channel, 'looks like something fucked up. or i dont have embed perms')
               

    def parse_google_card(self, node):
        if node is None:
            return None

        e = discord.Embed(colour=0x00FFFF)

        # check if it's a calculator card:
        calculator = node.find(".//table/tr/td/span[@class='nobr']/h2[@class='r']")
        if calculator is not None:
            e.title = 'Calculator'
            e.description = ''.join(calculator.itertext())
            return e

        parent = node.getparent()

        # check for unit conversion card
        unit = parent.find(".//ol//div[@class='_Tsb']")
        if unit is not None:
            e.title = 'Unit Conversion'
            e.description = ''.join(''.join(n.itertext()) for n in unit)
            return e

        # check for currency conversion card
        currency = parent.find(".//ol/table[@class='std _tLi']/tr/td/h2")
        if currency is not None:
            e.title = 'Currency Conversion'
            e.description = ''.join(currency.itertext())
            return e

        # check for release date card
        release = parent.find(".//div[@id='_vBb']")
        if release is not None:
            try:
                e.description = ''.join(release[0].itertext()).strip()
                e.title = ''.join(release[1].itertext()).strip()
                return e
            except:
                return None

        # check for definition card
        words = parent.find(".//ol/div[@class='g']/div/h3[@class='r']/div")
        if words is not None:
            try:
                definition_info = words.getparent().getparent()[1] # yikes
            except:
                pass
            else:
                try:
                    # inside is a <div> with two <span>
                    # the first is the actual word, the second is the pronunciation
                    e.title = words[0].text
                    e.description = words[1].text
                except:
                    return None

                # inside the table there's the actual definitions
                # they're separated as noun/verb/adjective with a list
                # of definitions
                for row in definition_info:
                    if len(row.attrib) != 0:
                        # definitions are empty <tr>
                        # if there is something in the <tr> then we're done
                        # with the definitions
                        break

                    try:
                        data = row[0]
                        lexical_category = data[0].text
                        body = []
                        for index, definition in enumerate(data[1], 1):
                            body.append('%s. %s' % (index, definition.text))

                        e.add_field(name=lexical_category, value='\n'.join(body), inline=False)
                    except:
                        continue

                return e

        # check for "time in" card
        time_in = parent.find(".//ol//div[@class='_Tsb _HOb _Qeb']")
        if time_in is not None:
            try:
                time_place = ''.join(time_in.find("span[@class='_HOb _Qeb']").itertext()).strip()
                the_time = ''.join(time_in.find("div[@class='_rkc _Peb']").itertext()).strip()
                the_date = ''.join(time_in.find("div[@class='_HOb _Qeb']").itertext()).strip()
            except:
                return None
            else:
                e.title = time_place
                e.description = '%s\n%s' % (the_time, the_date)
                return e

        # check for weather card
        # this one is the most complicated of the group lol
        # everything is under a <div class="e"> which has a
        # <h3>{{ weather for place }}</h3>
        # string, the rest is fucking table fuckery.
        weather = parent.find(".//ol//div[@class='e']")
        if weather is None:
            return None

        location = weather.find('h3')
        if location is None:
            return None

        e.title = ''.join(location.itertext())

        table = weather.find('table')
        if table is None:
            return None

        # This is gonna be a bit fucky.
        # So the part we care about is on the second data
        # column of the first tr
        try:
            tr = table[0]
            img = tr[0].find('img')
            category = img.get('alt')
            image = 'https:' + img.get('src')
            temperature = tr[1].xpath("./span[@class='wob_t']//text()")[0]
        except:
            return None # RIP
        else:
            e.set_thumbnail(url=image)
            e.description = '*%s*' % category
            e.add_field(name='Temperature', value=temperature)

        # On the 4th column it tells us our wind speeds
        try:
            wind = ''.join(table[3].itertext()).replace('Wind: ', '')
        except:
            return None
        else:
            e.add_field(name='Wind', value=wind)

        # On the 5th column it tells us our humidity
        try:
            humidity = ''.join(table[4][0].itertext()).replace('Humidity: ', '')
        except:
            return None
        else:
            e.add_field(name='Humidity', value=humidity)

        return e

    async def get_google_entries(self, query):
        params = {
            'q': query,
            'safe': 'on',
            'lr': 'lang_en',
            'hl': 'en'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'
        }

        # list of URLs
        entries = []

        # the result of a google card, an embed
        card = None

        async with aiohttp.get('https://www.google.com.au/search', params=params, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError('Google somehow failed to respond.')

            root = etree.fromstring(await resp.text(), etree.HTMLParser())

            # with open('google.html', 'w', encoding='utf-8') as f:
            #     f.write(etree.tostring(root, pretty_print=True).decode('utf-8'))

            """
            Tree looks like this.. sort of..
            <div class="g">
                ...
                <h3>
                    <a href="/url?q=<url>" ...>title</a>
                </h3>
                ...
                <span class="st">
                    <span class="f">date here</span>
                    summary here, can contain <em>tag</em>
                </span>
            </div>
            """

            card_node = root.find(".//div[@id='topstuff']")
            card = self.parse_google_card(card_node)

            search_nodes = root.findall(".//div[@class='g']")
            for node in search_nodes:
                url_node = node.find('.//h3/a')
                if url_node is None:
                    continue

                url = url_node.attrib['href']
                if not url.startswith('/url?'):
                    continue

                url = parse_qs(url[5:])['q'][0] # get the URL from ?q query string

                # if I ever cared about the description, this is how
                entries.append(url)

                # short = node.find(".//span[@class='st']")
                # if short is None:
                #     entries.append((url, ''))
                # else:
                #     text = ''.join(short.itertext())
                #     entries.append((url, text.replace('...', '')))

        return card, entries

    @commands.command(aliases=['google'])
    async def g(self, *, query):
        """Searches google and gives you top result."""
        await self.bot.type()
        try:
            card, entries = await self.get_google_entries(query)
        except RuntimeError as e:
            await self.bot.say(str(e))
        else:
            if card:
                value = '\n'.join(entries[:3])
                if value:
                    card.add_field(name='Search Results', value=value, inline=False)
                return await self.bot.say(embed=card)

            if len(entries) == 0:
                return await self.bot.say('No results found... sorry.')

            next_two = entries[1:3]
            first_entry = entries[0]
            if first_entry[-1] == ')':
                first_entry = first_entry[:-1] + '%29'

            if next_two:
                formatted = '\n'.join(map(lambda x: '<%s>' % x, next_two))
                msg = '{}\n\n**See also:**\n{}'.format(first_entry, formatted)
            else:
                msg = first_entry

            await self.bot.say(msg)

    #commands by Dino#0631

    @commands.command(pass_context=True, aliases=['googlecalc', 'gcal', 'calc'])
    async def gcalc(self, ctx,*, query):
        """Searches google and gives you top result."""
        await self.bot.type()
        try:
            card, entries = await self.get_google_entries(query)
        except RuntimeError as e:
            await self.bot.say(str(e))
        else:
            if card:
                value = '\n'.join(entries[:3])
                if value:
                    if card.title != 'Calculator':
                        card.add_field(name='Search Results', value=value, inline=False)
                await self.bot.say(embed=card)
                asyncio.sleep(2)
                await self.bot.delete_message(ctx.message)
                return 
        await self.bot.say("Error: could not calculate expression")
        await asyncio.sleep(2)
        messages = []
        async for m in self.bot.logs_from(ctx.message.channel, limit=2):
            if m.author.id == ctx.message.author.id:
                message = m
                break
        await self.bot.delete_message(ctx.message)
        await self.bot.delete_message(message)

        return



    @commands.command(pass_context=True)
    async def edit(self, ctx, *msg):
        '''edit your previous message 
        works up to 20 messages ago'''
        msg = list(msg)
        msg = ' '.join(msg)
        channel = ctx.message.channel
        # use the 2nd last message because the last message would be the command
        messages = []
        async for m in self.bot.logs_from(channel, limit=20):
            messages.append(m)
        for  m in messages[1:]:
            if m.author.id == ctx.message.author.id:
                message = m
                break
        if msg == None:
            msg = message.content
        print('{}')
        msg = msg.replace('{}', message.content)
        await self.bot.delete_message(ctx.message)
        await self.bot.edit_message(message, new_content=msg)

    @commands.command(pass_context=True)
    async def replace(self, ctx, old, *newphrase):
        '''replace one phrase to another in your previous message 
        works up to 20 messages ago'''
        new = list(newphrase)
        new = ' '.join(new)
        channel = ctx.message.channel
        # use the 2nd last message because the last message would be the command
        messages = []
        async for m in self.bot.logs_from(channel, limit=20):
            messages.append(m)
        for  m in messages[1:]:
            if m.author.id == ctx.message.author.id :
                message = m
                break
        msg =  message.content.replace(old, new)
        await self.bot.delete_message(ctx.message)
        await self.bot.edit_message(message, new_content=msg)

    @commands.command(pass_context=True)
    async def reverse(self, ctx):
        '''reverse your previous message 
        works up to 20 messages ago'''
        channel = ctx.message.channel
        # use the 2nd last message because the last message would be the command
        messages = []
        async for m in self.bot.logs_from(channel, limit=20):
            messages.append(m)
        for  m in messages[1:]:
            if m.author.id == '222925389641547776':
                message = m
                break

        await self.bot.delete_message(ctx.message)
        await self.bot.edit_message(message, new_content=message.content[::-1])

    @commands.command(pass_context=True)
    async def merge(self, ctx, msgs:int, join_with='\n'):
        if msgs>10:
            msgs = 10
        elif msgs < 2:
            msg  = await self.bot.say('can only merge 2 or more messages')
            await asyncio.sleep(2)
            await self.bot.delete_message(msg)
            return
        channel = ctx.message.channel
        messages = []
        await self.bot.delete_message(ctx.message)
        n = 0
        async for m in self.bot.logs_from(channel, limit=2*msgs+50):
            if n < msgs:
                pass
            else:
                break
            if m.author.id == ctx.message.author.id:
                messages.append(m)
                n += 1

        pastmsgs = []
        for m in list(reversed(messages)):
            pastmsgs.append(m.content)
        newmsg = join_with.join(pastmsgs)
        for m in messages[1:]:
            await self.bot.delete_message(m)
        await self.bot.edit_message(messages[0], new_content=newmsg)


def setup(bot):
	bot.add_cog(Utility(bot))

