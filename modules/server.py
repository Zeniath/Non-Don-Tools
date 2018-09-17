from discord.ext import commands
from utils.SimplePaginator import SimplePaginator
import discord, json, requests, sys, traceback, ast, psutil, json, pprint, aiohttp, asyncio, inspect, io, random
from datetime import datetime
from platform import python_version
from contextlib import redirect_stdout
from collections import Counter
import itertools
import inspect
import re

class Server:
    """Server Commands"""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.MissingPermissions):
            try:
                e = discord.Embed(title="Error <:no:473312284148498442>", description=str(error), color=16720640)
                return await ctx.send(embed=e)
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title='Error <:no:473312284148498442>', description=str(error), color=16720640)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            try:
                e = discord.Embed(title="Error <:no:473312284148498442>", description=str(error), color=16720640)
                return await ctx.send(embed=e)
            except discord.HTTPException:
                pass

    async def on_member_join(self, member):
        """Welcomes a member to the server"""
        channel = self.bot.get_channel(448373356291686410)
        fmt = f'Welcome {member.mention} to **{member.guild}**. Thanks to you for joining, we now have **{len(member.guild.members)}** members in the server! Hope you enjoy your stay!'
        if member.guild.id == 302689712617816064:
            await channel.send(''.join(fmt)) 
        else:
            return

    async def on_member_remove(self, member):
        """Says goodbye to whoever left the server"""
        channel = self.bot.get_channel(448049826307899393)
        fmt = f'{member.mention} has left **{member.guild}**. Cya, you non!'
        if member.guild.id == 302689712617816064:
            await channel.send(''.join(fmt)) 
        else:
            return

    @commands.command(aliases=['auto_role'], hidden=True)
    @checks.has_permissions(manage_roles=True)
    async def autorole(self, ctx, *, role: discord.Role):
        """Automatically sets a role for a new member

        You must have the Manage Role permission to use this command"""

        await ctx.send("")

        self.bot.db.execute("INSERT INTO autorole ($1, $2);", role.id, ctx.guild.id)

        e = discord.Embed(color=discord.Color.purple())
        e.set_thumbnail(url=ctx.guild.icon_url)
        e.add_field(name="Auto Role <:yes:473312268998803466>", value=f"Successfully set **{role.content}** as the server auto role!")
        e.set_footer(text=f'Server Name: {ctx.guild.name} | Server ID: {ctx.guild.id}', icon_url=ctx.guild.icon_url)
        await ctx.send(embed=e)

    @commands.command(aliases=['member_count', 'membercount'])
    async def members(self, ctx):
        """Shows the Discord's members"""
        await SimplePaginator(entries=ctx.guild.members, colour=discord.Color.blurple(), title=f"Members of {ctx.guild.name}", length=10).paginate(ctx)

    @commands.command(aliases=['discrim'], hidden=True)
    async def discriminator(self, ctx, discriminator):
        """Shows users with the chosen discriminator"""

    @commands.command()
    async def role(self, ctx, *, role: discord.Role):
        """Shows information about a Role"""
        e = discord.Embed(color=role.colour)
        e.set_thumbnail(url=ctx.author.avatar_url)
        e.add_field(name='Role Name:', value=role.name, inline=True)
        e.add_field(name='Role ID:', value=role.id, inline=True)
        e.add_field(name='Users in Role:', value=len(role.members), inline=True)
        e.add_field(name='Colour:', value=role.colour, inline=True)
        e.add_field(name='Mentionable:', value=role.mentionable, inline=True)
        e.add_field(name='Hoisted:', value=role.hoist, inline=True)
        e.add_field(name='Created at:', value=f"{role.created_at.strftime('%b, %d %Y')}", inline=True)
        e.set_footer(text=f'Server Name: {ctx.guild.name} | Server ID: {ctx.guild.id}', icon_url=ctx.guild.icon_url)
        await ctx.send(embed=e)

    @commands.command(aliases=['user'])
    async def userinfo(self, ctx, *, user: discord.Member=None):
        """Shows information about a User"""

        if user is None:
            user = ctx.author

        roles = [role.mention for role in user.roles if not role.is_default()]

        voice = user.voice
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = f'In {vc.name} with {other_people} other(s)' if other_people else f'In {vc.name} all by themselves'
        else:
            voice = 'Not connected'

        pos = sorted(ctx.guild.members, key=lambda m: m.joined_at).index(user)+1

        e = discord.Embed(color=user.color)
        e.set_thumbnail(url=user.avatar_url)
        e.add_field(name='User:', value=f"{user}")
        e.add_field(name='User ID:', value=f"{user.id}")
        e.add_field(name='Status:', value=f"{user.status}".title())
        e.add_field(name='Join Position:', value=f"#{pos}")
        e.add_field(name='Created at:', value=f"{user.created_at.strftime('%b %d, %Y')}")
        e.add_field(name='Joined server at:', value=f"{user.joined_at.strftime('%b %d, %Y')}")
        e.add_field(name='Voice:', value=f"{voice}")
        e.add_field(name=f'Roles: ({len(roles)})', value=f"{chr(173)}{', '.join(roles)}" if len(roles) < 15 else f"{len(roles)} Roles")
        await ctx.send(embed=e)

    @commands.command(aliases=['useravatar'])
    async def avatar(self, ctx, *, user: discord.User=None):
        """Shows a User's Avatar"""
        if user is None:
            user = ctx.author

        e = discord.Embed(title=f"{user.name}'s Avatar", color=discord.Color.dark_blue())
        e.set_image(url=user.avatar_url)
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Server(bot))