from discord.ext import commands
import requests
import json
import aiohttp
import random
from random import randint
import colorsys
from platform import python_version
import asyncio
import traceback
import discord

class API:
    """API Commands"""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    @commands.command(aliases=['foxxy', 'foxie']) 
    async def fox(self, ctx):
        """Sends a picture of a Fox"""
        await ctx.trigger_typing()
        author = ctx.message.author
        avatar = ctx.message.author.avatar_url
        async with aiohttp.ClientSession() as cs:
            async with cs.get('http://randomfox.ca/floof/') as r:
                res = await r.json()
                embed = discord.Embed(color=discord.Colour.gold())
                embed.set_image(url=res['image'])
                embed.set_author(name='Fox \U0001f98a')
                embed.set_footer(text=f'Requested by {author}', icon_url=avatar)
                embed.timestamp = ctx.message.created_at
                await ctx.send(embed=embed)

    @commands.command(aliases=['kitty']) 
    async def cat(self, ctx):
        """Sends a picture of a Cat"""
        await ctx.trigger_typing()
        author = ctx.message.author
        avatar = ctx.message.author.avatar_url
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://catapi.glitch.me/random') as r:
                res = await r.json()
                embed = discord.Embed(color=discord.Colour.gold())
                embed.set_image(url=res['url'])
                embed.set_author(name='Cat \U0001f431')
                embed.set_footer(text=f'Requested by {author}', icon_url=avatar)
                embed.timestamp = ctx.message.created_at
                await ctx.send(embed=embed)

    @commands.command(aliases=["doggie"])
    async def dog(self, ctx):
        '''Sends a picture of a Dog'''
        await ctx.trigger_typing()
        author = ctx.message.author
        avatar = ctx.message.author.avatar_url
        async with aiohttp.ClientSession() as cs:
            async with cs.get('http://dog.ceo/api/breeds/image/random') as r:
                res = await r.json()
                embed = discord.Embed(color=discord.Colour.gold())
                embed.set_image(url=res['message'])
                embed.set_author(name='Dog \U0001f436')
                embed.set_footer(text=f'Requested by {author}', icon_url=avatar)
                embed.timestamp = ctx.message.created_at
                await ctx.send(embed=embed)

    @commands.command(aliases=['cat_fact', 'catfacts'])
    async def catfact(self, ctx):
        '''Sends a fact about Cats'''
        await ctx.trigger_typing()
        author = ctx.message.author
        avatar = ctx.message.author.avatar_url
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://catfact.ninja/fact') as r:
                res = await r.json()
                embed = discord.Embed(color=discord.Colour.gold())
                embed.add_field(name="Catfact \U0001f431", value=f"""```fix\n{res["fact"]}```""")
                embed.set_footer(text=f'Requested by {author}', icon_url=avatar)
                embed.timestamp = ctx.message.created_at
                await ctx.send(embed=embed)

    @commands.command(aliases=['dog_fact', 'dogfacts'])
    async def dogfact(self, ctx):
        '''Sends a fact about Dogs'''
        await ctx.trigger_typing()
        author = ctx.message.author
        avatar = ctx.message.author.avatar_url
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://fact.birb.pw/api/v1/dog') as r:
                res = await r.json()
                embed = discord.Embed(color=discord.Colour.gold())
                embed.add_field(name="Dogfact \U0001f436", value=f"""```fix\n{res["string"]}```""")
                embed.set_footer(text=f'Requested by {author}', icon_url=avatar)
                embed.timestamp = ctx.message.created_at
                await ctx.send(embed=embed)

    @commands.command()
    async def urban(self, ctx, *, question):
        """Shows a question from the Urban Dictionary"""
        await ctx.trigger_typing()
        author = ctx.message.author
        link = '+'.join(question.split())
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://api.urbandictionary.com/v0/define?term={question}") as r:
                res = await r.json()
                definition = res['list']
                first_def = definition[0]
                sec_def = definition[1]
                third_def = definition[2]
                embed = discord.Embed(color=0x00FFCC, description=f"[Definition of {question}]({first_def['permalink']})")
                embed.set_author(name="Urban Dictionary")
                embed.set_thumbnail(url="https://s3.amazonaws.com/pushbullet-uploads/ujxPklLhvyK-RGDsDKNxGPDh29VWVd5iJOh8hkiBTRyC/urban_dictionary.jpg?w=188&h=188&fit=crop")
                embed.add_field(name="Word:", value=first_def['word'], inline=True)
                embed.add_field(name="Author:", value=first_def['author'], inline=True)
                embed.add_field(name="Definition:", value=first_def['definition'], inline=False)
                embed.add_field(name="Example:", value=first_def['example'], inline=False)
                embed.add_field(name=":thumbsup:", value=first_def['thumbs_up'], inline=True)
                embed.add_field(name=":thumbsdown:", value=first_def['thumbs_down'], inline=True)
                embed.set_footer(text=f'Requested by {author}', icon_url=ctx.message.author.avatar_url)
                embed.timestamp = ctx.message.created_at
                await ctx.send(embed=embed)

    @commands.command(aliases=["bc"])
    async def bitcoin(self, ctx):
        """Shows the price of Bitcoin"""
        await ctx.trigger_typing()
        url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
        response = requests.get(url)
        value = response.json()['bpi']['USD']['rate']
        embed = discord.Embed(description=f'Bitcoin price is: **${value}**', color=4737156)
        embed.set_thumbnail(url='https://www.cryptocompare.com/media/19633/btc.png')
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed)

    @commands.command()
    async def dadjoke(self, ctx):
        '''Sends a Dad Joke'''
        await ctx.trigger_typing()
        author = ctx.message.author
        avatar = ctx.message.author.avatar_url
        async with aiohttp.ClientSession() as cs:
            headers = {"Accept": "application/json"}
            async with cs.get('https://icanhazdadjoke.com', headers=headers) as r:
                res = await r.json()
                embed = discord.Embed(color=discord.Colour.gold())
                embed.add_field(name="Dad Joke \U0001f935", value=f"""```fix\n{res["joke"]}```""")
                embed.set_footer(text=f'Requested by {author}', icon_url=avatar)
                embed.timestamp = ctx.message.created_at
                await ctx.send(embed=embed)

    @commands.group(aliases=['h'], hidden=True)
    async def hypixel(self, ctx, username: str):
        """Shows your Hypixel Stats"""
        author = ctx.message.author
        avatar = ctx.message.author.avatar_url
        e = discord.Embed(title=f"https://hypixel.net/player/{username}/", color=discord.Color.gold())
        e.set_thumbnail(url=f"https://hypixel.net/player/{username}/")
        await ctx.send(embed=e)

    @hypixel.command(hidden=True)
    async def uhc(self, ctx, username: str):
        """Shows your Hypixel UHC Stats"""
        pass

    @commands.command(aliases=['minecraft_skin'])
    async def mcskin(self, ctx, username):
        """Looks up your minecraft skin"""

        username = username
        async with aiohttp.ClientSession() as sessionMojang:
            async with sessionMojang.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as rMojang:
                d = await rMojang.json()
        e = discord.Embed(title=f"{username}'s Minecraft Skin", color=discord.Color.gold())
        e.set_image(url=f"https://crafatar.com/avatars/{d['id']}")
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(API(bot))