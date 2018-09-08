from discord.ext import commands
import requests, random, json, psutil, aiohttp, asyncio, traceback, discord, inspect, textwrap, io, colorsys
from random import randint
from platform import python_version
from contextlib import redirect_stdout
from collections import Counter

class Fun:
    """Fun Commands"""

    def __init__(self, bot):
        self.bot = bot

    async def __error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            try:
                e = discord.Embed(title="Error <:no:473312284148498442>", description=str(error), color=16720640)
                return await ctx.send(embed=e)
            except discord.HTTPException:
                pass
        if isinstance(error, commands.CommandInvokeError):
            try:
                e = discord.Embed(title="Error <:no:473312284148498442>", description=str(error), color=16720640)
                return await ctx.send(embed=e)
            except discord.HTTPException:
                pass


    @commands.command(aliases=['em'])
    async def embed(self, ctx):
        """Create a customisable embed"""

        def check(message):
            return message.author.id == ctx.author.id

        await ctx.send("Hey! Here we are going to create a customisable embed! Follow these steps to learn how!"
                        "\n\nWhat would you like to set the colour as?"
                        "\nChoices are: **blue**, **dark_blue**, **white**, **blurple**, **red**, **yellow**, **green**, **gold**, **aqua**, and **orange**")
        msg = await self.bot.wait_for('message', check=check)

        if msg.content == 'blue':
            value = 3447003

        if msg.content == 'yellow':
            value = 15858191

        if msg.content == 'blurple':
            value = 7506394

        if msg.content == 'dark_blue':
            value = 2123412

        if msg.content == 'red':
            value = 16720640

        if msg.content == 'orange':
            value = 15105570

        if msg.content == 'gold':
            value = 15844367

        if msg.content == 'green':
            value = 3066993

        if msg.content == 'aqua':
            value = 1047261

        if msg.content == 'white':
            value = 16777215

        await ctx.send(f"Okay, I set the embed colour as **{msg.content}**")

        await ctx.send("Who would you like to set the author as?")
        msg1 = await self.bot.wait_for('message', check=check)
        await ctx.send(f"Okay, I set the embed author as **{msg1.content}**")

        await ctx.send("What would you like to set the description as?")
        msg2 = await self.bot.wait_for('message', check=check)
        await ctx.send(f"Okay, I set the embed description as **{msg2.content}**")

        await ctx.send("What would you like to set the footer as?")
        msg3 = await self.bot.wait_for('message', check=check)
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
    async def arrest(self, ctx, user: discord.Member=None, *, reason=None):
        """Arrest someone"""
        if user is None:
            await ctx.send("Who are you trying to arrest?")
        elif user == ctx.author:
            await ctx.send("You cannot arrest yourself!")
        elif reason is None:
            await ctx.send(f"**{user}** has been arrested by **{ctx.author}**")
        else:
            await ctx.send(f"**{user}** has been arrested by **{ctx.author}**: `{reason}`!")


    @commands.command(aliases=['print','say'])
    async def echo(self, ctx, *, content):
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
    async def clap(self, ctx, *, text):
        """Claps some text"""
        await ctx.send(':clap: '.join(f':clap: {text} :clap:'.split()))

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