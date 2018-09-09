from discord.ext import commands
import discord, json, requests, sys, traceback, ast, psutil, json, pprint, aiohttp, asyncio, inspect, io, random
from datetime import datetime
from platform import python_version
from contextlib import redirect_stdout
from collections import Counter
import itertools
from .utils import checks
import inspect
import re
import speedtest

class Information:
    """Informative Commands"""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def do_st(self):
        s = speedtest.Speedtest()
        s.get_best_server()
        dl = s.download()
        ul = s.upload()

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.MissingPermissions):
            try:
                e = discord.Embed(title="Error <:no:473312284148498442>", description=str(error), color=16720640)
                return await ctx.send(embed=e)
            except discord.HTTPException:
                pass

    @commands.command(aliases=['speedt'])
    async def speedtest(self, ctx):
        async with ctx.typing():
            dl, ul = await self.bot.loop.run_in_executor(None, self.do_st)
            await ctx.send(f":arrow_down: Download: **{int(dl/1024/1024)} MB/s**\n:arrow_up: Upload: **{int(ul/1024/1024)} MB/s**")


    @commands.command(aliases= ["ms"])
    async def ping(self, ctx):
        """Shows the bot's latency"""
        colors = [discord.Colour.purple(), discord.Colour.blue(), discord.Colour.red(), discord.Colour.gold(), discord.Colour.green(), discord.Colour.orange(), discord.Colour.blurple()]
        embed = discord.Embed(color=random.choice(colors))
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Pong!", value=":ping_pong:", inline=True)
        embed.add_field(name="MS", value=f'This took: **{ctx.bot.latency * 1000:,.0f}ms**', inline=True)
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        """Shows the bot's uptime"""
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if not days:
            await ctx.send(f"Uptime: **{hours} hours, {minutes} minutes and {seconds} seconds**")
        elif not hours:
            await ctx.send(f"Uptime: **{minutes} minutes and {seconds} seconds**")
        elif not minutes:
            await ctx.send(f"Uptime: **{seconds} seconds**")
        else:
            await ctx.send(f"Uptime: **{days} days, {hours} hours, {minutes} minutes and {seconds} seconds**")

    @commands.command(aliases=["information", "about"])
    async def info(self, ctx):
        """Shows information about the bot"""

        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not days:
            fmt = f"{hours} hours, {minutes} minutes and {seconds} seconds"
        elif not hours:
            fmt = f"{minutes} minutes and {seconds} seconds"
        elif not minutes:
            fmt = f"{seconds} seconds"
        else:
            fmt = f"{days} days, {hours} hours, {minutes} minutes and {seconds} seconds"

        value = await self.bot.db.fetchrow("SELECT commandcount FROM commands;")
        v = value['commandcount']

        prefixes = await self.bot.db.fetchrow("SELECT prefix FROM prefixes WHERE guildid=$1;", ctx.guild.id)
        if prefixes:
            p = prefixes['prefix']
        else:
            p = 'non '

        e = discord.Embed(title="About the bot", description="[Support Server](https://discord.gg/g7qJU8H) | [Invite The Bot](https://discordapp.com/api/oauth2/authorize?client_id=448038812048949253&permissions=8&scope=bot) | [Upvote](https://discordbots.org/bot/448038812048949253) | [Source](https://github.com/Zeniath/Non-Don-Tools)", color=discord.Colour.blue())
        e.set_author(name="Non Dons Information", icon_url="https://cdn.discordapp.com/avatars/448038812048949253/03ceac8c243b9ded4287049b59aa987b.webp?size=1024")
        e.add_field(name="Coder:", value="Zeniath#4729", inline=True)
        e.add_field(name="Python Version:", value=f"{python_version()}", inline=True)
        e.add_field(name="Prefix:", value=f"{p}", inline=False)
        e.add_field(name="Ping:", value=f"{ctx.bot.latency * 1000:,.0f}ms", inline=True)
        e.add_field(name="Commands Invoked:", value=f"{v}", inline=True)
        e.add_field(name="Uptime: ", value=f"{fmt}", inline=False)
        e.add_field(name="Servers:", value=f"{len(self.bot.guilds)}", inline=True)
        e.add_field(name="Members:", value=f"{len(self.bot.users)}", inline=True)
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        e.set_thumbnail(url="https://png2.kisspng.com/sh/671707122a6c9a94565465af8f26f573/L0KzQYm3VMAzN6JqfZH0aYP2gLBuTgB6fJl0hp91b3fyPbTzjBp2epYygtNBYYPmgrr3lL06NWZme6QAY0K5cYfqhvI4Nmo1TqIEMkS6QYa5UsY5P2E2TKgDM0OxgLBu/kisspng-python-logo-clojure-javascript-9-5ac25c26a6cfb7.9060924715226870146833.png")
        await ctx.send(embed=e)

    @commands.command(aliases=['statistics'])
    async def stats(self, ctx):
        """Shows the bot's stats"""

        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        online = (len(set([m for m in self.bot.get_all_members() if m.status == discord.Status.online and not m.bot])))
        away = (len(set([m for m in self.bot.get_all_members() if m.status == discord.Status.idle and not m.bot])))
        dnd = (len(set([m for m in self.bot.get_all_members() if m.status == discord.Status.dnd and not m.bot])))
        offline = (len(set([m for m in self.bot.get_all_members() if m.status == discord.Status.offline and not m.bot])))

        p = psutil.Process()

        prefixes = await self.bot.db.fetchrow("SELECT prefix FROM prefixes WHERE guildid=$1;", ctx.guild.id)
        if prefixes:
            pre = prefixes['prefix']
        else:
            pre = 'non '

        memory_percent = psutil.virtual_memory()[2]

        value = await self.bot.db.fetchrow("SELECT commandcount FROM commands;")
        v = value['commandcount']

        e = discord.Embed(description="[Support Server](https://discord.gg/g7qJU8H) | [Invite The Bot](https://discordapp.com/api/oauth2/authorize?client_id=448038812048949253&permissions=8&scope=bot) | [Upvote](https://discordbots.org/bot/448038812048949253) | [Source](https://github.com/Zeniath/Non-Don-Tools)", color=discord.Color.dark_blue())
        e.set_author(name="Non Don Stats", icon_url="https://cdn.discordapp.com/avatars/448038812048949253/03ceac8c243b9ded4287049b59aa987b.webp?size=1024")
        e.add_field(name="Member Stats", value=f"<:online:482652775214481409>{online}" 
                                                f"<:away:482652813936295937>{away}" 
                                                f"<:DnD:482652826351173648>{dnd}" 
                                                f"<:offline:482652799188860931>{offline}")
        e.add_field(name="Bot Stats", value=f"**Owner:** <@249750282324410368>\n"
                                            f"**Commands:** {len(self.bot.commands)}\n"
                                            f"**Cogs:** {len(self.bot.cogs)}\n"
                                            f"**Commands Invoked:** {v}", inline=False)
        e.add_field(name="Discord Stats", value=f"**Prefix:** {pre}\n"
                                                f"**Uptime:** {days} days, {hours} hours, {minutes} minutes, {seconds} seconds\n"
                                                f"**Ping:** {ctx.bot.latency * 1000:,.0f}ms\n"
                                                f"**Guilds:** {len(self.bot.guilds)}\n"
                                                f"**Users:** {len(self.bot.users)}\n"
                                                f"**Version:** 1.0.0a1510+g8ccb98d", inline=False)
        e.add_field(name="PC Stats", value=f"**Python Version:** {python_version()}\n"
                                            f"**Memory:** {int(p.memory_info()[0]/1024/1024)}mb ({memory_percent}%)\n"
                                            f"**CPU:** {psutil.cpu_percent()}%", inline=False)
        await ctx.send(embed=e)

    @commands.command(aliases=["pref"])
    async def prefix(self, ctx):
        """Shows the current prefix"""

        data = await self.bot.db.fetchrow("SELECT prefix FROM prefixes WHERE guildid=$1;", ctx.guild.id)
        if not data:
            data = {'prefix': 'non '}

        e = discord.Embed(color=discord.Colour.dark_blue())
        e.set_author(name=f"{ctx.guild.name}'s Prefixes")
        e.set_thumbnail(url=ctx.guild.icon_url)
        e.add_field(name="Default Prefix:", value="`non`")
        e.add_field(name="Server Prefix:", value=f"`{data['prefix']}`")
        await ctx.send(embed=e)

    @commands.command(aliases=['add_prefix'])
    @checks.has_permissions(manage_guild=True)
    async def set_prefix(self, ctx, prefix):
        """Change the current prefix"""

        data = await self.bot.db.fetchrow("SELECT prefix FROM prefixes WHERE guildid=$1;", ctx.guild.id)
        if not data:
            data = {'prefix': 'non '}

        if prefix == ctx.prefix:
            return await ctx.send(f"The prefix **{ctx.prefix}**you attempted to change the prefix too, is already the current prefix")

        if isinstance(data, dict):
            await self.bot.db.execute("INSERT INTO prefixes VALUES ($1, $2);", ctx.guild.id, prefix)
        else:
            await self.bot.db.execute("UPDATE prefixes SET prefix=$1 WHERE guildid=$2;", prefix, ctx.guild.id)
        e = discord.Embed(color=discord.Colour.dark_blue())
        e.add_field(name="Prefix Changed <:yes:473312268998803466>", value=f'The new server prefix is: "**{prefix}**"')
        e.set_footer(text=f'The old server prefix was: {ctx.prefix}', icon_url=ctx.guild.icon_url_as(format="png"))
        await ctx.send(embed=e)

    @set_prefix.error
    async def set_error(self, ctx, error):
        import traceback; traceback.print_exception(type(error), error, error.__traceback__)

    @commands.command(aliases=['inv'])
    async def invite(self, ctx):
        """Gives an invite link"""
        embed = discord.Embed(title='Invite the bot!', url='https://discordapp.com/api/oauth2/authorize?client_id=448038812048949253&permissions=8&scope=bot', description='Want to support the server? Want to give suggestions?\nJoin my server! https://discord.gg/g7qJU8H', color=4737156)
        embed.set_footer(text='If you have any questions, feel free to message the creator of this bot, Zeniath#4729')
        embed.set_author(name='Non Dons Bot', icon_url='https://cdn.discordapp.com/icons/302689712617816064/b20f858ff835ec4ea181d1710ff66a93.webp?size=1024')
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Information(bot))
