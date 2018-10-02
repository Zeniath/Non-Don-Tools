from discord.ext import commands
from discord.ext.commands import clean_content
import requests, random, json, psutil, aiohttp, asyncio, traceback, discord, inspect, textwrap, io, colorsys
from random import randint
from platform import python_version
from contextlib import redirect_stdout
from collections import Counter

class Fun:
    """Fun Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def big(self, ctx, text):
        """Makes your text go big!"""

        emoji_dict = {
            'a': [':a:', ':regional_indicator_a:', ':rice_ball:', ':arrow_up_small:'],
            'b': [':b:', ':regional_indicator_b:'],
            'c': [':regional_indicator_c:', '©', ':compression:'],
            'd': [':regional_indicator_d:', ':leftwards_arrow_with_hook:'],
            'e': [':regional_indicator_e:', ':three:', ':e_mail:', ':euro:'],
            'f': [':regional_indicator_f:', ':flags:'],
            'g': [':regional_indicator_g:', ':compression:', ':six:', ':nine:', ':fuelpump:'],
            'h': [':regional_indicator_h:', ':pisces:'],
            'i': [':regional_indicator_i:', ':information_source:', ':mens:', ':one:'],
            'j': [':regional_indicator_j:', ':japan:'],
            'k': [':regional_indicator_k:', ':tanabata_tree:'],
            'l': [':regional_indicator_l:', ':one:', ':regional_indicator_i:', ':boot:', ':pound:'],
            'm': [':regional_indicator_m:', ':m:', ':chart_with_downwards_trend:'],
            'n': [':regional_indicator_n:', ':capricorn:', ':musical_note:'],
            'o': [':regional_indicator_o:', ':o2:', ':zero:', ':o:', ':radio_button:', ':record_button:', ':white_circle:', ':black_circle:', ':large_blue_circle:', ':red_circle:', ':dizzy:'],
            'p': [':regional_indicator_p:', ':parking:'],
            'q': [':regional_indicator_q:', ':leo:'],
            'r': [':regional_indicator_r:', '®'],
            's': [':regional_indicator_s:', ':heavy_dollar_sign:', ':five:', ':zap:', ':moneybag:', ':dollar:'],
            't': [':regional_indicator_t:', ':cross:', ':heavy_plus_sign:', ':level_slider:', ':palm_tree:', ':seven:'],
            'u': [':regional_indicator_u:', ':ophiuchus:', ':dragon:'],
            'v': [':regional_indicator_v:', ':aries:', ':ballot_box_with_check:'],
            'w': [':regional_indicator_w:', ':wavy_dash:', ':chart_with_upwards_trend:'],
            'x': [':regional_indicator_x:', ':negative_squared_cross_mark:', ':heavy_multiplication_x:', ':x:', ':hammer_pick:'],
            'y': [':regional_indicator_y:', ':v:', ':yen:'],
            'z': [':regional_indicator_z:', ':two:'],
            ' ': [':white_small_square:'],
            '0': [':zero:', ':o2:', ':zero:', ':o:', ':radio_button:', ':record_button:', ':white_circle:', ':black_circle:', ':large_blue_circle:', ':red_circle:', ':dizzy:'],
            '1': [':one:', ':regional_indicator_i:'],
            '2': [':two:', ':regional_indicator_z:'],
            '3': [':three:'],
            '4': [':four:'],
            '5': [':five:', ':regional_indicator_s:', ':heavy_dollar_sign:', ':zap:'],
            '6': [':six:'],
            '7': [':seven:'],
            '8': [':eight:', ':8ball:', ':regional_indicator_b:', ':b:'],
            '9': [':nine:'],
            '?': [':question:'],
            '!': [':exclamation:', ':grey_exclamation:', ':warning:', ':heart_exclamation:'],
            'combination': [['cool', ':cool:'],
                        ['back', ':back:'],
                        ['soon', ':soon:'],
                        ['free', ':free:'],
                        ['end', ':end:'],
                        ['top', ':top:'],
                        ['abc', ':abc:'],
                        ['atm', ':atm:'],
                        ['new', ':new:'],
                        ['sos', ':sos:'],
                        ['100', ':100:'],
                        ['hundred', ':100:']
                        ['loo', ':100:'],
                        ['zzz', ':zzz:'],
                        ['nz', ':flag_nz:']
                        ['uk', ':flag_gb:']
                        ['...', ':speech_balloon:'],
                        ['ng', ':ng:'],
                        ['id', ':id:'],
                        ['vs', ':vs:'],
                        ['wc', ':wc:'],
                        ['ab', ':ab:'],
                        ['cl', ':cl:'],
                        ['ok', ':ok:'],
                        ['up', ':up:'],
                        ['10', ':keycap_ten:'],
                        ['11', ':pause_button:'],
                        ['ll', ':pause_button:'],
                        ['ii', ':pause_button:'],
                        ['tm', '™'],
                        ['on', ':on:'],
                        ['oo', ':koko:'],
                        ['!?', ':interrobang:'],
                        ['!!', ':bangbang:'],
                        ['21', ':date:']]

                }

        if text in emoji_dict:
            return await ctx.message.add_reaction(emoji_dict)
        else:
            await ctx.send("An error has occured")

    @commands.command(aliases=['emoj', 'randomemoji', 'emoji'])
    async def random_emoji(self, ctx, *, emoji: discord.Emoji = None):
        """Returns a random emoji of all servers the bot is in"""

        embed = discord.Embed(title=emoji.name, colour=discord.Color.blurple())
        embed.add_field(name='URL to Emoji', value=f'**[Emoji Link]({emoji.url})**')
        embed.set_thumbnail(url=emoji.url)
        await ctx.send(embed=embed)


    @commands.command(aliases=['em'])
    async def embed(self, ctx):
        """Create a customisable embed"""

        def check(message):
            return message.author.id == ctx.author.id

        await ctx.send("Hey! Here we are going to create a customisable embed! Follow these steps to learn how!"
                        "\n\nWhat would you like to set the colour as?"
                        "\nChoices are: **blue**, **dark_blue**, **white**, **blurple**, **red**, **yellow**, **green**, **gold**, **aqua**, and **orange**")
        msg = await self.bot.wait_for('message', check=check)

        if msg.content == ['exit', 'off', 'no']:
            return await ctx.send(f"You have exited the customisable embed! To do it again, please type the command `{ctx.prefix}embed`")

        elif msg.content == 'Blue'.lower():
            value = 3447003

        elif msg.content == 'Yellow'.lower():
            value = 15858191

        elif msg.content == 'Blurple'.lower():
            value = 7506394

        elif msg.content == 'Dark_blue'.lower():
            value = 2123412

        elif msg.content == 'Red'.lower():
            value = 16720640

        elif msg.content == 'Orange'.lower():
            value = 15105570

        elif msg.content == 'Gold'.lower():
            value = 15844367

        elif msg.content == 'Green'.lower():
            value = 3066993

        elif msg.content == 'Aqua'.lower():
            value = 1047261

        elif msg.content == 'White'.lower():
            value = 16777215

        elif msg.content != ['Blue', 'Yellow', 'Blurple', 'Dark_blue', 'Red', 'Orange', 'Gold', 'Green', 'Aqua', 'White', 'Exit', 'No', 'Off'.lower()]:
            return await ctx.send(f"This is an invalid colour! Please use the command `{ctx.prefix}embed` to restart")

        await ctx.send(f"Okay, I set the embed colour as **{msg.content}**")

        await ctx.send("Who would you like to set the author as?")
        msg1 = await self.bot.wait_for('message', check=check)
        if msg1.content == ['exit', 'off', 'no']:
            return await ctx.send(f"You have exited the customisable embed! To do it again, please type the command `{ctx.prefix}embed`")
        await ctx.send(f"Okay, I set the embed author as **{msg1.content}**")

        await ctx.send("What would you like to set the description as?")
        msg2 = await self.bot.wait_for('message', check=check)
        if msg2.content == ['exit', 'off', 'no']:
            return await ctx.send(f"You have exited the customisable embed! To do it again, please type the command `{ctx.prefix}embed`")
        await ctx.send(f"Okay, I set the embed description as **{msg2.content}**")

        await ctx.send("What would you like to set the footer as?")
        msg3 = await self.bot.wait_for('message', check=check)
        if msg3.content == ['exit', 'off', 'no']:
            return await ctx.send(f"You have exited the customisable embed! To do it again, please type the command `{ctx.prefix}embed`")
        await ctx.send(f"Okay, I set the embed footer as **{msg3.content}**\n\nHere is your completed embed!")

        e = discord.Embed(description=f"{msg2.content}", colour=discord.Colour(value=value))
        e.set_author(name=f"{msg1.content}", icon_url=ctx.author.avatar_url)
        e.set_footer(text=f"{msg3.content}")
        await ctx.send(embed=e)

    @embed.error
    async def embed_handler(self, ctx, error):
        import traceback; traceback.print_exception(type(error), error, error.__traceback__)

    @commands.command()
    async def poll(self, ctx, *, question):
        """Let the community answer a question"""

        values = [int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1)]
        colour = discord.Color.from_rgb(*values)

        e = discord.Embed(color=(colour))
        e.add_field(name="Poll Question", value=f"{question}")
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.message.author.avatar_url)
        e.timestamp = ctx.message.created_at
        msg = await ctx.send(embed=e)
        await msg.add_reaction(":yes:473312268998803466")
        await msg.add_reaction(":maybe:473312298312925212")
        await msg.add_reaction(":no:473312284148498442")

    @commands.command()
    async def arrest(self, ctx, user: discord.Member=None, *, reason: commands.clean_content=None):
        """Arrest someone"""

        if user is None:
            user_arrest = await ctx.send("Who are you trying to arrest?")

            def check(message):
                return message.author.id == ctx.author.id

            try:
                arrested = await self.bot.wait_for('message', check=check, timeout=180)
            except asyncio.TimeoutError:
                return await user_arrest.delete()

            return await ctx.send(f"**{arrested.clean_content}** has been arrested by **{ctx.author.name}**")

        if user == ctx.author:
            return await ctx.send("You cannot arrest yourself!")
        elif reason is None:
            return await ctx.send(f"**{user.name}** has been arrested by **{ctx.author.name}**")
        else:
            return await ctx.send(f"**{user.name}** has been arrested by **{ctx.author.name}** for {reason}!")


    @commands.command(aliases=['print', 'say'])
    async def echo(self, ctx, *, content: commands.clean_content):
        """Repeats what you say"""
        await ctx.send(content)

    @commands.command(name="8ball", aliases=['8', 'ball', 'ball8'])
    async def eight_ball(self, ctx, *, question):
        """Ask the 8ball a question"""
        possible_responses = [
            'That is a resounding no', 'It is not looking likely', 'It is quite possible', 'Definitely',
            'Definitely... not', 'Yes', 'No way', '**Of course!',
            'I have spoken to the gods... They have said Yes! :smile:',
            'I have spoken to the gods... They have said No! :rage:', 'Maybe?', 'Not at all!',
            'Not in a million years.', 'You bet ;)', 'Without a doubt', "It's your decision"
            ]

        answer = random.choice(possible_responses)
        user = ctx.author.name
        values = [int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1)]
        colour = discord.Color.from_rgb(*values)
        embed = discord.Embed(color=(colour))
        embed.add_field(name=':question: Question:', value=f"{question}?")
        embed.add_field(name=":8ball: 8ball:", value=f"{answer}")
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/e/e3/8_ball_icon.svg")
        embed.set_footer(text=f'Requested by {user}', icon_url=ctx.author.avatar_url)
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed)

    @commands.command(aliases=['choice'])
    async def choose(self, ctx, *choice):
        """Chooses between 2 choices"""
        r = random.choice(choice)
        u = ctx.author.name
        embed = discord.Embed(description=f'The choice is: **{r}**', color=4560431)
        embed.set_thumbnail(url="https://cdn.shopify.com/s/files/1/1061/1924/products/Thinking_Face_Emoji_large.png?v=1480481060")
        embed.set_footer(text=f"Requested by {u}", icon_url=ctx.author.avatar_url)
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed)

    @commands.command()
    async def clap(self, ctx, *, text: commands.clean_content):
        """Claps some text"""
        await ctx.send(':clap: '.join(f'{text}'.split()))

    @commands.command(aliases=['coin-flip', 'cf'])
    async def coinflip(self, ctx):
        """Flips a coin"""
        e = discord.Embed(title="""Flips coin... It's heads!""", color=0x00FFFF)
        e.set_thumbnail(url="https://qph.fs.quoracdn.net/main-qimg-57e97e36918b359f28e86b8cbf567436-c")
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        e.timestamp = ctx.message.created_at

        em = discord.Embed(title="""Flips coin... It's tails!""", color=0x00FFFF)
        em.set_thumbnail(url="https://random-ize.com/coin-flip/us-quarter/us-quarter-back.jpg")
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        em.timestamp = ctx.message.created_at

        embeds = [em, e]
        answer = random.choice(embeds)

        await ctx.send(embed=answer)

    @commands.command(aliases=['roll'])
    async def dice(self, ctx, n: int = 5):
        """Rolls a dice from 1 to n"""
        result = randint(1, n)
        embed = discord.Embed(description=f':game_die: You rolled the number **{result}**!', color=5703162)
        embed.set_author(name=f"{ctx.author.name}'s dice roll", icon_url=ctx.author.avatar_url)
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed)

    @commands.command(aliases=['partay'])
    async def party(self, ctx):
        """Has a party!"""
        await ctx.message.add_reaction('a:partyblob_:471910310077399061')
        await ctx.message.add_reaction(':feelsgoodman:443685135133704192')
        await ctx.message.add_reaction(':yay:451178223720595456')
        await ctx.message.add_reaction(':pepecheer:448231102382080000')
        await ctx.message.add_reaction(':dab:449375412175241216')
        await ctx.message.add_reaction(':pepehappy:455840154167541760')
        await ctx.message.add_reaction('a:partyblob:471910008637095946')

def setup(bot):
    bot.add_cog(Fun(bot))
